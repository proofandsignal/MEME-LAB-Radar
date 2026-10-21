"""Read-only, block-pinned USDG ERC20 metadata probe; never verifies backing or price."""
import argparse,json,re
from pathlib import Path
from datetime import datetime,timezone
from pool_probe import rpc,decode_address
USDG="0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168"
SELECTORS={"symbol":"0x95d89b41","decimals":"0x313ce567","totalSupply":"0x18160ddd"}
def evaluate(call=rpc):
    report={"status":"VERIFY","token":USDG,"source":"Robinhood Chain RPC",
            "issuer_attested":False,"reserves_verified":False,"price_verified":False,"trace":[]}
    def read(method,params):
        try:
            result=call(method,params)
            report["trace"].append({"method":method,"status":"OK"})
            return result
        except Exception as exc:
            report["trace"].append({"method":method,"status":"VERIFY","error":str(exc)})
            raise
    try:
        if read("eth_chainId",[])!="0x1237":raise ValueError("chain id mismatch")
        block=read("eth_getBlockByNumber",["latest",False])
        height=block["number"];hash_=block["hash"]
        if not isinstance(height,str) or not re.fullmatch("0x[0-9a-fA-F]+",height):
            raise ValueError("invalid block height")
        if not isinstance(hash_,str) or not re.fullmatch("0x[0-9a-fA-F]{64}",hash_):
            raise ValueError("invalid block hash")
        report["anchor"]={"number":height,"hash":hash_}
        code=read("eth_getCode",[USDG,height])
        if not isinstance(code,str) or code=="0x" or not re.fullmatch("0x(?:[0-9a-fA-F]{2})+",code):
            raise ValueError("no token contract bytecode")
        def raw(selector):
            word=read("eth_call",[{"to":USDG,"data":selector},height])
            if not isinstance(word,str) or not re.fullmatch("0x(?:[0-9a-fA-F]{2})+",word):
                raise ValueError("bad ABI response")
            return bytes.fromhex(word[2:])
        def symbol_decode(data):
            if len(data)==32:
                return data.rstrip(bytes([0])).decode("ascii")
            if len(data)<96: raise ValueError("symbol dynamic ABI too short")
            offset=int.from_bytes(data[:32],"big")
            if offset+32>len(data):raise ValueError("symbol offset invalid")
            length=int.from_bytes(data[offset:offset+32],"big")
            if length>64 or offset+32+length>len(data):raise ValueError("symbol length invalid")
            return data[offset+32:offset+32+length].decode("ascii")
        symbol=symbol_decode(raw(SELECTORS["symbol"]))
        decimals_data=raw(SELECTORS["decimals"])
        supply_data=raw(SELECTORS["totalSupply"])
        if len(decimals_data)!=32 or len(supply_data)!=32:raise ValueError("numeric ABI not 32 bytes")
        decimals=int.from_bytes(decimals_data,"big")
        supply=int.from_bytes(supply_data,"big")
        report["metadata"]={"symbol":symbol,"decimals":decimals,"total_supply_raw":str(supply)}
        if symbol!="USDG" or decimals!=6:raise ValueError("USDG metadata inconsistent with documented reference")
        again=read("eth_getBlockByNumber",[height,False])
        if again.get("hash")!=hash_:raise ValueError("block hash changed")
        report["status"]="ONCHAIN_METADATA_MATCH"
    except (ValueError,TypeError,KeyError,TimeoutError,OSError,UnicodeDecodeError) as exc:
        report["error"]=str(exc)
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    a=p.parse_args()
    result=evaluate()
    Path(a.out).write_text(json.dumps({"observed_at":datetime.now(timezone.utc).isoformat(),"result":result},indent=2)+"\n")
    print(json.dumps({"status":result["status"],"metadata":result.get("metadata"),"error":result.get("error")}))
    raise SystemExit(0 if result["status"]=="ONCHAIN_METADATA_MATCH" else 2)
