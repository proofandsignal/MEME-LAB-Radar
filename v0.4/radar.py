"""MEME LAB Meta Radar v0.4 — read-only, auditable research collector.

No token launches, execution, wallet signing or investment recommendations.
Python 3.11+, standard library only. External observations must be sourced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

HORIZONS_MINUTES = (5, 15, 30, 60, 360, 1440, 10080)
SCHEMA_VERSION = "0.4.0"

SCHEMA = """
CREATE TABLE IF NOT EXISTS observations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  observed_at TEXT NOT NULL,
  chain TEXT NOT NULL,
  pool_address TEXT NOT NULL,
  base_token TEXT NOT NULL,
  quote_token TEXT NOT NULL,
  stock_symbol TEXT,
  source TEXT NOT NULL,
  source_record_id TEXT NOT NULL,
  fetched_at TEXT NOT NULL,
  price_usd REAL,
  liquidity_usd REAL,
  volume_24h_usd REAL,
  txns_24h INTEGER,
  raw_sha256 TEXT NOT NULL,
  raw_json TEXT NOT NULL,
  UNIQUE(source, source_record_id, observed_at, raw_sha256)
);
CREATE INDEX IF NOT EXISTS idx_observations_pool_time
ON observations(chain,pool_address,observed_at);
CREATE TABLE IF NOT EXISTS token_registry (
  chain TEXT NOT NULL,
  token_address TEXT NOT NULL,
  stock_symbol TEXT NOT NULL,
  issuer TEXT NOT NULL,
  instrument_type TEXT NOT NULL,
  verification_status TEXT NOT NULL CHECK(
    verification_status IN ('UNVERIFIED','REVIEW','VERIFIED')
  ),
  evidence_url TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY(chain,token_address)
);
CREATE TABLE IF NOT EXISTS collector_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at TEXT NOT NULL,
  completed_at TEXT NOT NULL,
  source TEXT NOT NULL,
  status TEXT NOT NULL,
  inserted INTEGER NOT NULL,
  error TEXT
);
"""

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def init_db(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    con.commit()
    return con

def positive_number(value: Any, field: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    x = float(value)
    if not 0 <= x < float("inf"):
        raise ValueError(f"{field} must be finite and nonnegative")
    return x

def validate_record(record: dict[str, Any]) -> dict[str, Any]:
    mandatory = ("observed_at", "chain", "pool_address", "base_token",
                 "quote_token", "source", "source_record_id")
    for key in mandatory:
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise ValueError(f"missing/invalid {key}")
    dt = datetime.fromisoformat(record["observed_at"].replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("observed_at must include timezone")
    r = {k: record[k].strip() for k in mandatory}
    r["observed_at"] = dt.astimezone(timezone.utc).isoformat()
    for key in ("price_usd", "liquidity_usd", "volume_24h_usd"):
        r[key] = positive_number(record.get(key), key)
    txns = record.get("txns_24h")
    if txns is not None and (type(txns) is not int or txns < 0):
        raise ValueError("txns_24h must be nonnegative integer")
    r["txns_24h"] = txns
    stock_symbol = record.get("stock_symbol")
    r["stock_symbol"] = stock_symbol.strip().upper() if isinstance(stock_symbol, str) and stock_symbol.strip() else None
    return r

def ingest(con: sqlite3.Connection, records: list[dict[str, Any]],
           *, source: str = "manual") -> dict[str, Any]:
    start = utc_now()
    inserted = 0
    errors: list[str] = []
    for index, raw in enumerate(records):
        try:
            if not isinstance(raw, dict):
                raise ValueError("record must be object")
            r = validate_record(raw)
            digest = hashlib.sha256(canonical(raw).encode("utf-8")).hexdigest()
            before = con.total_changes
            con.execute("""INSERT OR IGNORE INTO observations
              (observed_at,chain,pool_address,base_token,quote_token,
               stock_symbol,source,source_record_id,fetched_at,price_usd,
               liquidity_usd,volume_24h_usd,txns_24h,raw_sha256,raw_json)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
              (r["observed_at"],r["chain"],r["pool_address"],r["base_token"],
               r["quote_token"],r["stock_symbol"],r["source"],
               r["source_record_id"],utc_now(),r["price_usd"],
               r["liquidity_usd"],r["volume_24h_usd"],r["txns_24h"],
               digest,canonical(raw)))
            inserted += con.total_changes - before
        except (ValueError, TypeError, KeyError) as exc:
            errors.append(f"record[{index}]: {exc}")
    status = "OK" if not errors else "VERIFY"
    con.execute("INSERT INTO collector_runs (started_at,completed_at,source,status,inserted,error) VALUES (?,?,?,?,?,?)",
                (start,utc_now(),source,status,inserted,"; ".join(errors) or None))
    con.commit()
    return {"status":status,"inserted":inserted,"rejected":len(errors),"errors":errors}

def register_token(con: sqlite3.Connection, obj: dict[str, Any]) -> None:
    for field in ("chain","token_address","stock_symbol","issuer","instrument_type","evidence_url"):
        if not isinstance(obj.get(field), str) or not obj[field].strip():
            raise ValueError(f"registry: missing {field}")
    # Never automatically assign VERIFIED from user-provided metadata.
    con.execute("""INSERT INTO token_registry VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(chain,token_address) DO UPDATE SET
        stock_symbol=excluded.stock_symbol,issuer=excluded.issuer,
        instrument_type=excluded.instrument_type,
        verification_status='REVIEW',evidence_url=excluded.evidence_url,
        updated_at=excluded.updated_at""",
        (obj["chain"],obj["token_address"],obj["stock_symbol"].upper(),
         obj["issuer"],obj["instrument_type"],"REVIEW",obj["evidence_url"],utc_now()))
    con.commit()

def survival(con: sqlite3.Connection, chain: str, pool: str) -> dict[str, Any]:
    rows = con.execute("""SELECT observed_at,liquidity_usd FROM observations
          WHERE chain=? AND pool_address=? ORDER BY observed_at""",(chain,pool)).fetchall()
    if not rows:
        return {"status":"NO_DATA","horizons":{}}
    launch = datetime.fromisoformat(rows[0]["observed_at"])
    latest = datetime.fromisoformat(rows[-1]["observed_at"])
    out: dict[str, Any] = {}
    for minutes in HORIZONS_MINUTES:
        target = launch + timedelta(minutes=minutes)
        key = f"{minutes}m"
        if latest < target:
            out[key] = "PENDING"
        else:
            matched = [r for r in rows if datetime.fromisoformat(r["observed_at"]) >= target]
            # Observation after horizon is not proof the pool was active at that horizon.
            # Keep uncertain unless snapshot is within 5 minutes of horizon.
            near = next((r for r in matched if datetime.fromisoformat(r["observed_at"]) <= target + timedelta(minutes=5)), None)
            if near is None or near["liquidity_usd"] is None:
                out[key] = "UNKNOWN"
            else:
                out[key] = "OBSERVED_ACTIVE" if near["liquidity_usd"] > 0 else "OBSERVED_ZERO_LIQUIDITY"
    return {"status":"OBSERVED","first_seen":launch.isoformat(),"last_seen":latest.isoformat(),
            "horizons":out,"note":"first_seen is not verified launch time; observations do not prove token safety"}

def heatmap(con: sqlite3.Connection) -> list[dict[str, Any]]:
    # Use latest observation per pool, not sum of snapshots.
    rows = con.execute("""SELECT stock_symbol,COUNT(*) AS pools,
      SUM(COALESCE(liquidity_usd,0)) AS liquidity_usd,
      SUM(COALESCE(volume_24h_usd,0)) AS volume_24h_usd
      FROM observations o WHERE stock_symbol IS NOT NULL
      AND id=(SELECT id FROM observations x WHERE
        x.chain=o.chain AND x.pool_address=o.pool_address
        ORDER BY x.observed_at DESC,x.id DESC LIMIT 1)
      GROUP BY stock_symbol ORDER BY liquidity_usd DESC""").fetchall()
    return [dict(r) for r in rows]

def read_input(path: str) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("input must be a JSON array")
    return payload

def fetch_json(url: str) -> Any:
    req = Request(url, headers={"User-Agent":"MEME-LAB-Research/0.4","Accept":"application/json"})
    with urlopen(req, timeout=12) as response:
        return json.load(response)

def main() -> int:
    p = argparse.ArgumentParser(description="MEME LAB v0.4 — read-only radar")
    p.add_argument("--db",default="radar.sqlite3")
    sub = p.add_subparsers(dest="cmd",required=True)
    sub.add_parser("init")
    imp = sub.add_parser("ingest")
    imp.add_argument("--file",required=True)
    imp.add_argument("--source",default="manual")
    reg = sub.add_parser("register")
    reg.add_argument("--file",required=True)
    surv = sub.add_parser("survival")
    surv.add_argument("--chain",required=True)
    surv.add_argument("--pool",required=True)
    sub.add_parser("heatmap")
    args = p.parse_args()
    con = init_db(args.db)
    try:
        if args.cmd == "init":
            result = {"status":"OK","schema":SCHEMA_VERSION}
        elif args.cmd == "ingest":
            result = ingest(con,read_input(args.file),source=args.source)
        elif args.cmd == "register":
            register_token(con,json.loads(Path(args.file).read_text(encoding="utf-8")))
            result = {"status":"REVIEW","message":"registry claim requires independent verification"}
        elif args.cmd == "survival":
            result = survival(con,args.chain,args.pool)
        else:
            result = {"status":"OK","heatmap":heatmap(con)}
        print(json.dumps(result,indent=2))
        return 0 if result.get("status") != "VERIFY" else 2
    except (ValueError,OSError,sqlite3.Error) as exc:
        print(json.dumps({"status":"ERROR","message":str(exc)}),file=sys.stderr)
        return 1
    finally:
        con.close()

if __name__ == "__main__":
    raise SystemExit(main())
