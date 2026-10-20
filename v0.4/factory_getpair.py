"""Block-pinned V2 factory getPair evidence; not factory provenance attestation."""
import argparse,json,re
from pathlib import Path
from datetime import datetime,timezone
from pool_probe import rpc,decode_address

FACTORY="0x5481864ddd46a2d798df0925c23b7846e776e5e3"
POOL="0x0092f73B6821098F66eEa758cf7eeB0F834C2303"
BASE="0xd0601CE157Db5bdC3162BbaC2a2C8aF5320D9EEC"
QUOTE="0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168"
SELECTOR="0xe6a43905"  # getPair(address,address)
def encoded(addr):return "0"*24+addr[2:].lower()
def investigate(call=rpc):
    report={"status":"VERIFY","factory":FACTORY,"pool":POOL,
            "factory_provenance_verified":False,"protocol_verified":False,
            "liquidity_verified":False,"trace":[]}
    def read(method,params):
        try:
            value=call(method,params)
            report["trace"].append({"method":method,"status":"OK"})
            return value
        except Exception as exc:
            report["trace"].append({"method":method,"status":"VERIFY","reason":str(exc)})
            raise
    try:
        if read("eth_chainId",[])!="0x1237":raise ValueError("unexpected chain")
        block=read("eth_getBlockByNumber",["latest",False])
        number=block["number"];hash_=block["hash"]
        if not re.fullmatch("0x[0-9a-fA-F]+",number) or not re.fullmatch("0x[0-9a-fA-F]{64}",hash_):
            raise ValueError("invalid block anchor")
        report["anchor"]={"number":number,"hash":hash_}
        answers=[]
        for first,second in ((BASE,QUOTE),(QUOTE,BASE)):
            data=SELECTOR+encoded(first)+encoded(second)
            answer=read("eth_call",[{"to":FACTORY,"data":data},number])
            answers.append(decode_address(answer))
        report["getpair_addresses"]=answers
        stable=read("eth_getBlockByNumber",[number,False])
        if stable.get("hash")!=hash_:raise ValueError("block hash changed")
        report["status"]="FACTORY_GETPAIR_MATCH" if all(a==POOL.lower() for a in answers) else "MISMATCH"
    except (ValueError,TypeError,KeyError,OSError,TimeoutError) as exc:
        report["reason"]=str(exc)
    return report
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);a=p.parse_args()
    r=investigate()
    Path(a.out).write_text(json.dumps({"observed_at":datetime.now(timezone.utc).isoformat(),"result":r},indent=2)+"\n")
    print(json.dumps({"status":r["status"],"reason":r.get("reason")}))
    raise SystemExit(0 if r["status"] in ("FACTORY_GETPAIR_MATCH","MISMATCH") else 2)
