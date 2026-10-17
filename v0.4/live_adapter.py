"""BUILD-002 alpha: DEX Screener read-only discovery and evidence capture.

All observations are UNVERIFIED candidates. A ticker is NOT a verified stock token.
No trading; no contract verification; no fabricated prices on API failures.
"""
from __future__ import annotations
import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from radar import init_db, ingest, utc_now

BASE = "https://api.dexscreener.com/latest/dex/search?q="
SOURCE = "dexscreener"
MAX_PAIRS = 30

def metric(value, field):
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value,(str,int,float)):
        raise ValueError(field+" invalid type")
    try:
        x=float(value)
    except (ValueError,OverflowError) as e:
        raise ValueError(field+" invalid number") from e
    if not math.isfinite(x) or x < 0:
        raise ValueError(field+" must be nonnegative finite")
    return x

def normalize(payload, observed_at=None):
    if not isinstance(payload,dict) or not isinstance(payload.get("pairs"),list):
        raise ValueError("missing pairs list")
    observed_at=observed_at or utc_now()
    records=[]
    rejected=[]
    for i,pair in enumerate(payload["pairs"][:MAX_PAIRS]):
        try:
            if not isinstance(pair,dict):
                raise ValueError("not object")
            base=pair.get("baseToken") or {}
            quote_token=pair.get("quoteToken") or {}
            chain=pair.get("chainId")
            pool=pair.get("pairAddress")
            base_addr=base.get("address")
            quote_addr=quote_token.get("address")
            if not all(isinstance(x,str) and x.strip() for x in (chain,pool,base_addr,quote_addr)):
                raise ValueError("missing chain or pool or token address")
            volume=pair.get("volume") or {}
            liquidity=pair.get("liquidity") or {}
            txns=pair.get("txns") or {}
            h24=txns.get("h24") or {}
            buys=h24.get("buys")
            sells=h24.get("sells")
            if any(type(n) is not int or n<0 for n in (buys,sells) if n is not None):
                raise ValueError("invalid transactions")
            record={
                "observed_at":observed_at,
                "chain":chain,
                "pool_address":pool,
                "base_token":base_addr,
                "quote_token":quote_addr,
                "source":SOURCE,
                "source_record_id":chain+":"+pool,
                "stock_symbol":None, # Never infer stock-token legitimacy from ticker text.
                "price_usd":metric(pair.get("priceUsd"),"priceUsd"),
                "liquidity_usd":metric(liquidity.get("usd"),"liquidity.usd"),
                "volume_24h_usd":metric(volume.get("h24"),"volume.h24"),
                "txns_24h":sum(n or 0 for n in (buys,sells)) if buys is not None and sells is not None else None,
                "discovery_status":"UNVERIFIED",
                "raw_provider_pair":pair,
            }
            records.append(record)
        except (ValueError,AttributeError,TypeError) as error:
            rejected.append({"index":i,"reason":str(error)})
    return records,rejected

def fetch_search(query,timeout=12):
    if not isinstance(query,str) or not 1 <= len(query.strip()) <= 100:
        raise ValueError("query must contain 1..100 characters")
    url=BASE+quote(query.strip(),safe="")
    req=Request(url,headers={"Accept":"application/json","User-Agent":"MEME-LAB-Radar/0.4-live-research"})
    try:
        with urlopen(req,timeout=timeout) as response:
            return json.load(response),url
    except (HTTPError,URLError,TimeoutError,json.JSONDecodeError) as e:
        raise RuntimeError("Upstream failure (VERIFY): "+str(e)) from e

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--db",default="radar.sqlite3")
    parser.add_argument("--query",required=True,help="Exploratory DEX pair search; NOT verified stock exposure")
    parser.add_argument("--evidence-out",required=True)
    args=parser.parse_args()
    try:
        payload,url=fetch_search(args.query)
        records,rejected=normalize(payload)
        evidence={"source":SOURCE,"endpoint":url,"fetched_at":utc_now(),
          "data_gate":"UNVERIFIED","request_query":args.query,
          "upstream_records":len(payload["pairs"]),"normalized_records":len(records),
          "rejected":rejected,"provider_payload":payload}
        # Save raw response and diagnostics before database mutation.
        Path(args.evidence_out).write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        with init_db(args.db) as con:
            result=ingest(con,records,source=SOURCE)
        print(json.dumps({"result":result,"evidence_file":args.evidence_out,
          "data_gate":"UNVERIFIED","provider_rejections":len(rejected)},indent=2))
        return 0 if not rejected and result["status"]=="OK" else 2
    except (RuntimeError,ValueError,OSError) as e:
        print(json.dumps({"status":"VERIFY","message":str(e)}))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
