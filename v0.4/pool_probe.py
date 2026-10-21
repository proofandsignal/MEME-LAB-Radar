"""Guarded V2-compatible pool-leg cross-check (not a pool audit).

Does not infer verified protocol, liquidity, issuer, price, or safety.
Unsupported ABIs fail closed to VERIFY.
"""
import json
import re
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

RPC="https://rpc.mainnet.chain.robinhood.com"
ADDRESS=re.compile(r"^0x[0-9a-fA-F]{40}$")
TOKEN0="0x0dfe1681"
TOKEN1="0xd21220a7"

def rpc(method,params):
    payload=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    try:
        with urlopen(Request(RPC,data=payload,headers={"Content-Type":"application/json","Accept":"application/json","User-Agent":"MEME-LAB-Radar/0.4"}),timeout=12) as resp:
            reply=json.load(resp)
    except HTTPError as exc:
        raise ValueError(f"RPC_HTTP_ERROR method={method} status={exc.code}") from exc
    except (URLError, TimeoutError) as exc:
        raise ValueError(f"RPC_TRANSPORT_ERROR method={method} kind={type(exc).__name__}") from exc
    if not isinstance(reply,dict):
        raise ValueError(f"RPC_MALFORMED_REPLY method={method}")
    if "error" in reply:
        error=reply["error"]
        code=error.get("code") if isinstance(error,dict) else None
        message=error.get("message") if isinstance(error,dict) else None
        # A bounded classification only: do not persist arbitrary provider error
        # bodies, URLs, request payloads, headers or possible secrets.
        known=("execution reverted","method not found","invalid params","unsupported","rate limit")
        label=next((v.replace(" ","_") for v in known if isinstance(message,str) and v in message.lower()),"other")
        code=code if type(code) is int and -99999 <= code <= 99999 else "unknown"
        raise ValueError(f"RPC_JSON_ERROR method={method} code={code} category={label}")
    if "result" not in reply:
        raise ValueError(f"RPC_MISSING_RESULT method={method}")
    return reply["result"]

def decode_address(word):
    if not isinstance(word,str) or re.fullmatch(r"0x[0-9a-fA-F]{64}",word) is None:
        raise ValueError("ABI response malformed")
    if int(word[2:26],16)!=0:
        raise ValueError("noncanonical ABI address encoding")
    addr="0x"+word[-40:].lower()
    if int(addr[2:],16)==0:
        raise ValueError("zero contract address")
    return addr

def check_pool(pool, base, quote, call=rpc):
    if any(not isinstance(x,str) or ADDRESS.fullmatch(x) is None for x in (pool,base,quote)):
        return {"status":"VERIFY","reason":"invalid address"}
    try:
        if call("eth_chainId",[]) != "0x1237":
            return {"status":"VERIFY","reason":"wrong RPC chain"}
        code=call("eth_getCode",[pool,"latest"])
        if not isinstance(code,str) or re.fullmatch(r"0x(?:[0-9a-fA-F]{2})*",code) is None or code=="0x":
            return {"status":"VERIFY","reason":"pool bytecode absent or malformed"}
        a=decode_address(call("eth_call",[{"to":pool,"data":TOKEN0},"latest"]))
        b=decode_address(call("eth_call",[{"to":pool,"data":TOKEN1},"latest"]))
        if a==b:
            return {"status":"VERIFY","reason":"duplicate pool token legs"}
        if {a,b}!={base.lower(),quote.lower()}:
            return {"status":"MISMATCH","onchain_legs":[a,b],"reason":"DEX provider token legs differ from pool"}
        return {"status":"V2_LEGS_MATCH","onchain_legs":[a,b],
                "verified_protocol":False,"verified_liquidity":False,
                "verified_issuer":False,"verified_pool_audit":False,
                "block_tag":"latest"}
    except (ValueError,TypeError,KeyError,TimeoutError,OSError) as exc:
        return {"status":"VERIFY","reason":str(exc)}
