"""BUILD-002 guarded Robinhood issuer deployment and onchain bytecode probe.

A match means issuer-declared deployment + RPC bytecode present, NOT verified
pool ownership, source-code audit, liquidity, rights, or tradeability.
"""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ASSETS_URL = "https://api.robinhood.com/rhj/assets"
RPC_URL = "https://rpc.mainnet.chain.robinhood.com"
CHAIN_ID = 4663
ADDR = re.compile(r"^0x[0-9a-fA-F]{40}$")

def request_json(url, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers={"Accept":"application/json","User-Agent":"MEME-LAB-Radar/0.4"}
    if data is not None: headers["Content-Type"]="application/json"
    with urlopen(Request(url,data=data,headers=headers),timeout=15) as response:
        return json.load(response)

def deployments(payload):
    """Fail closed for unexpected issuer API shape."""
    if not isinstance(payload,dict) or not isinstance(payload.get("assets"),list):
        raise ValueError("issuer assets schema not recognized")
    result={}
    for asset in payload["assets"]:
        if not isinstance(asset,dict): continue
        for d in asset.get("deployments") or []:
            if not isinstance(d,dict) or d.get("chainId") != CHAIN_ID: continue
            addr=d.get("contractAddress")
            if not isinstance(addr,str) or not ADDR.fullmatch(addr): continue
            key=addr.lower()
            descriptor={"symbol":asset.get("tokenSymbol"),"status":asset.get("status"),"address":addr}
            if key in result and result[key]!=descriptor:
                raise ValueError("conflicting issuer deployment for address")
            result[key]=descriptor
    return result

def chain_probe(address, requester=request_json):
    if not isinstance(address,str) or not ADDR.fullmatch(address):
        raise ValueError("invalid EVM address")
    chain=requester(RPC_URL,{"jsonrpc":"2.0","id":1,"method":"eth_chainId","params":[]})
    if not isinstance(chain,dict) or chain.get("result")!="0x1237":
        return {"status":"VERIFY","reason":"unexpected chain ID"}
    code=requester(RPC_URL,{"jsonrpc":"2.0","id":2,"method":"eth_getCode","params":[address,"latest"]})
    if not isinstance(code,dict) or not isinstance(code.get("result"),str):
        return {"status":"VERIFY","reason":"RPC bytecode unavailable"}
    value=code["result"]
    if not re.fullmatch(r"0x(?:[0-9a-fA-F]{2})*",value):
        return {"status":"VERIFY","reason":"invalid RPC bytecode"}
    return {"status":"BYTECODE_PRESENT" if value!="0x" else "NO_CODE",
            "chain_id":CHAIN_ID,"address":address,"rpc":RPC_URL}

def assess(address, issuer_payload, requester=request_json):
    registry=deployments(issuer_payload)
    if not isinstance(address,str) or not ADDR.fullmatch(address):
        return {"status":"VERIFY","reason":"invalid EVM address"}
    issuer=registry.get(address.lower())
    if issuer is None:
        return {"status":"UNVERIFIED","reason":"address absent from official issuer deployments"}
    rpc=chain_probe(address,requester=requester)
    return {"status":"ISSUER_DEPLOYMENT_AND_CODE_MATCH" if rpc["status"]=="BYTECODE_PRESENT" else "VERIFY",
            "issuer":issuer,"onchain":rpc,"pool_verified":False,
            "underlying_rights_verified":False,"code_audited":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--address",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    try:
        issuer=request_json(ASSETS_URL)
        outcome=assess(args.address,issuer)
        record={"fetched_at":datetime.now(timezone.utc).isoformat(),
                "source":ASSETS_URL,"rpc":RPC_URL,"result":outcome,
                "issuer_payload":issuer,"data_gate":"UNVERIFIED_FOR_TRADING"}
        Path(args.out).write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
        print(json.dumps({"result":outcome,"evidence_path":args.out}))
        return 0 if outcome["status"]=="ISSUER_DEPLOYMENT_AND_CODE_MATCH" else 2
    except (HTTPError,URLError,TimeoutError,ValueError,TypeError,KeyError,OSError) as error:
        print(json.dumps({"status":"VERIFY","reason":str(error)}))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
