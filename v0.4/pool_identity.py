"""Narrow, read-only pool leg and factory identity evidence.

Factory bytecode is not protocol endorsement. Issuer registry comparison is exact
address+chain, never symbol. Failure is VERIFY, not VERIFIED.
"""
import json
import re
from issuer_rpc import request_json,ASSETS_URL,deployments
from pool_probe import rpc, decode_address

FACTORY_SELECTOR="0xc45a0155"
ADDRESS=re.compile(r"^0x[0-9a-fA-F]{40}$")

def assess_pair(base,quote,pool,registry,call=rpc):
    if not all(isinstance(x,str) and ADDRESS.fullmatch(x) for x in (base,quote,pool)):
        return {"status":"VERIFY","reason":"invalid address"}
    issuer_matches={}
    for name,address in (("base",base),("quote",quote)):
        entry=registry.get(address.lower())
        issuer_matches[name]={"address":address,"issuer_registry_status":"OFFICIAL_DEPLOYMENT_MATCH" if entry else "NOT_IN_REGISTRY","issuer_entry":entry}
    factory={"status":"VERIFY","verified_protocol":False}
    try:
        if call("eth_chainId",[])!="0x1237":
            raise ValueError("unexpected chain ID")
        word=call("eth_call",[{"to":pool,"data":FACTORY_SELECTOR},"latest"])
        address=decode_address(word)
        code=call("eth_getCode",[address,"latest"])
        if not isinstance(code,str) or not re.fullmatch(r"0x(?:[0-9a-fA-F]{2})*",code) or code=="0x":
            raise ValueError("factory bytecode absent or malformed")
        factory={"status":"FACTORY_ADDRESS_HAS_CODE","address":address,
                 "verified_protocol":False,"verified_factory_provenance":False}
    except (ValueError,TypeError,KeyError,TimeoutError,OSError) as error:
        factory={"status":"VERIFY","reason":str(error),"verified_protocol":False}
    return {"issuer_legs":issuer_matches,"factory":factory,
            "pool_verified":False,"provider_independence_verified":False}

def main():
    import argparse
    from pathlib import Path
    p=argparse.ArgumentParser()
    p.add_argument("--base",required=True)
    p.add_argument("--quote",required=True)
    p.add_argument("--pool",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    report={"status":"VERIFY","issuer_source":ASSETS_URL}
    try:
        payload=request_json(ASSETS_URL)
        report["registry_snapshot"]=payload
        registry=deployments(payload)
        report["evaluation"]=assess_pair(a.base,a.quote,a.pool,registry)
        report["status"]="OBSERVED_UNVERIFIED"
    except Exception as exc:
        report["error"]=repr(exc)
    Path(a.out).write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"status":report["status"],"evaluation":report.get("evaluation"),"error":report.get("error")},indent=2))
    return 0 if report["status"]=="OBSERVED_UNVERIFIED" else 2

if __name__=="__main__":
    raise SystemExit(main())
