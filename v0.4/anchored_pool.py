"""BUILD-002 block-pinned, read-only V2 pool inspection.
A successful inspection does not prove trusted factory, reserve valuation or audit.
"""
import argparse
import json
import re
from datetime import datetime,timezone
from pathlib import Path
from pool_probe import rpc,decode_address,TOKEN0,TOKEN1
from pool_identity import FACTORY_SELECTOR

ADDR=re.compile(r"0x[0-9a-fA-F]{40}")
HEX=re.compile(r"0x[0-9a-fA-F]+")
def inspect(pool,call=rpc):
    if not isinstance(pool,str) or not ADDR.fullmatch(pool):
        raise ValueError("invalid pool address")
    trace=[]
    def read(method,params):
        try:
            result=call(method,params)
            trace.append({"method":method,"status":"OK"})
            return result
        except Exception as e:
            trace.append({"method":method,"status":"VERIFY","error":str(e)})
            raise
    report={"status":"VERIFY","pool":pool,"read_trace":trace,
            "issuer_verified":False,"factory_provenance_verified":False,
            "liquidity_verified":False}
    try:
        chain=read("eth_chainId",[])
        if chain!="0x1237":raise ValueError("unexpected chain")
        block=read("eth_getBlockByNumber",["latest",False])
        if not isinstance(block,dict): raise ValueError("missing block")
        height=block.get("number")
        h=block.get("hash")
        if not isinstance(height,str) or not HEX.fullmatch(height) or not isinstance(h,str) or not re.fullmatch("0x[0-9a-fA-F]{64}",h):
            raise ValueError("invalid anchor block")
        report["anchor"]={"number":height,"hash":h}
        code=read("eth_getCode",[pool,height])
        if not isinstance(code,str) or code=="0x" or not re.fullmatch("0x(?:[0-9a-fA-F]{2})*",code):
            raise ValueError("missing pool bytecode")
        legs=[decode_address(read("eth_call",[{"to":pool,"data":selector},height]))
              for selector in (TOKEN0,TOKEN1)]
        if legs[0]==legs[1]:raise ValueError("duplicate legs")
        report["legs"]=legs
        factory=decode_address(read("eth_call",[{"to":pool,"data":FACTORY_SELECTOR},height]))
        report["factory"]=factory
        factory_code=read("eth_getCode",[factory,height])
        report["factory_bytecode_present"]=isinstance(factory_code,str) and bool(re.fullmatch("0x(?:[0-9a-fA-F]{2})+",factory_code))
        repeated=read("eth_getBlockByNumber",[height,False])
        if not isinstance(repeated,dict) or repeated.get("hash")!=h:
            raise ValueError("block hash changed between reads")
        report["status"]="BLOCK_ANCHORED_READ" if report["factory_bytecode_present"] else "VERIFY"
    except (ValueError,TypeError,KeyError,TimeoutError,OSError) as e:
        report["reason"]=str(e)
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pool",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    result=inspect(args.pool)
    evidence={"observed_at":datetime.now(timezone.utc).isoformat(),"result":result,
              "data_gate":"UNVERIFIED"}
    Path(args.out).write_text(json.dumps(evidence,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"anchor":result.get("anchor"),
                      "reason":result.get("reason")}))
    return 0 if result["status"]=="BLOCK_ANCHORED_READ" else 2

if __name__=="__main__":raise SystemExit(main())
