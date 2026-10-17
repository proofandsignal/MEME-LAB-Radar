"""BUILD-002: provider pool recheck and official-contract comparison.

No automatic VERIFIED status: issuer sources and independent onchain reads are
separate mandatory gates. This module reports evidence levels only.
"""
import argparse
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote

EVM = re.compile(r"^0x[0-9a-fA-F]{40}$")
API = "https://api.dexscreener.com/latest/dex/pairs/{}/{}"
OFFICIAL = "https://docs.robinhood.com/chain/contracts/"

def evm_address(value):
    return isinstance(value, str) and EVM.fullmatch(value) is not None

def match_official_token(pair, registry):
    """Registry must be curated from issuer's official registry; never from DEX."""
    if not isinstance(registry, dict):
        raise ValueError("registry not object")
    chain = pair.get("chainId")
    if chain != "robinhood":
        return {"status":"UNSUPPORTED_CHAIN","official_reference":OFFICIAL}
    matches = []
    for leg in ("baseToken","quoteToken"):
        token=pair.get(leg) or {}
        address=token.get("address")
        if not evm_address(address):
            return {"status":"VERIFY","reason":"invalid token address"}
        entry=registry.get(address.lower())
        if entry is not None:
            matches.append({"leg":leg,"address":address,"official_registry_entry":entry})
    return {"status":"OFFICIAL_REFERENCE_MATCH" if matches else "UNVERIFIED",
            "matches":matches,"official_reference":OFFICIAL,
            "onchain_verified":False,"issuer_verified":False}

def verify_pair_echo(original, response):
    """A provider re-query confirms its own consistency, not independent onchain truth."""
    if not isinstance(response, dict) or not isinstance(response.get("pairs"),list):
        return {"status":"VERIFY","reason":"malformed provider response"}
    oldchain=original.get("chainId")
    oldpool=original.get("pairAddress")
    if not isinstance(oldchain,str) or not isinstance(oldpool,str):
        return {"status":"VERIFY","reason":"missing original locator"}
    expected=(oldchain.lower(),oldpool.lower())
    candidates=[p for p in response["pairs"] if isinstance(p,dict) and
         (str(p.get("chainId","")).lower(),str(p.get("pairAddress","")).lower())==expected]
    if len(candidates)!=1:
        return {"status":"VERIFY","reason":"pool absent or ambiguous in provider re-query"}
    current=candidates[0]
    for leg in ("baseToken","quoteToken"):
        a=(original.get(leg) or {}).get("address")
        b=(current.get(leg) or {}).get("address")
        if not isinstance(a,str) or not isinstance(b,str) or a.lower()!=b.lower():
            return {"status":"MISMATCH","reason":leg+" contract changed"}
    return {"status":"PROVIDER_ECHO_MATCH","independent_onchain_verified":False,
            "pool_contract_verified":False}

def fetch_pair(chain,pool):
    if not isinstance(chain,str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,40}",chain):
        raise ValueError("invalid chain")
    if not isinstance(pool,str) or not re.fullmatch(r"[a-zA-Z0-9]{20,80}",pool):
        raise ValueError("invalid pool")
    url=API.format(quote(chain,safe=""),quote(pool,safe=""))
    with urlopen(Request(url,headers={"Accept":"application/json","User-Agent":"MEME-LAB-Radar/0.4"}),timeout=12) as r:
        return json.load(r),url

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--evidence",required=True)
    parser.add_argument("--index",type=int,default=0)
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    try:
        evidence=json.loads(Path(args.evidence).read_text())
        pairs=evidence["provider_payload"]["pairs"]
        original=pairs[args.index]
        response,url=fetch_pair(original["chainId"],original["pairAddress"])
        report={"pool":original["pairAddress"],"chain":original["chainId"],
          "requery_url":url,"provider_check":verify_pair_echo(original,response),
          "official_contract_check":{"status":"PENDING_REGISTRY_READ"},
          "onchain_check":{"status":"PENDING_RPC"},
          "raw_provider_response":response}
        Path(args.out).write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps({"provider_check":report["provider_check"],"out":args.out}))
        return 0 if report["provider_check"]["status"]=="PROVIDER_ECHO_MATCH" else 2
    except (OSError,ValueError,KeyError,IndexError,TypeError) as exc:
        print(json.dumps({"status":"VERIFY","reason":str(exc)}))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
