import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from radar import init_db, ingest, heatmap, survival, register_token

T0 = datetime(2026, 10, 9, 8, 0, tzinfo=timezone.utc)

def record(minute=0, liquidity=1000, pool="0xPOOL", symbol="NVDA"):
    return {
        "observed_at":(T0+timedelta(minutes=minute)).isoformat(),
        "chain":"testnet","pool_address":pool,"base_token":"0xMEME",
        "quote_token":"0xSTOCK","stock_symbol":symbol,
        "source":"fixture","source_record_id":f"{pool}-{minute}",
        "liquidity_usd":liquidity,"volume_24h_usd":500,"txns_24h":5
    }

class RadarTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.con=init_db(str(Path(self.tmp.name)/"radar.db"))
    def tearDown(self):
        self.con.close()
        self.tmp.cleanup()
    def test_immutable_idempotent(self):
        r=record()
        self.assertEqual(ingest(self.con,[r,r])["inserted"],1)
        self.assertEqual(ingest(self.con,[r])["inserted"],0)
    def test_invalid_data_fail_visible(self):
        r=record()
        r["liquidity_usd"]=-1
        out=ingest(self.con,[r])
        self.assertEqual(out["status"],"VERIFY")
        self.assertEqual(out["rejected"],1)
    def test_survival_not_falsely_assumed(self):
        ingest(self.con,[record(0),record(60)])
        result=survival(self.con,"testnet","0xPOOL")
        self.assertEqual(result["horizons"]["5m"],"UNKNOWN")
        self.assertEqual(result["horizons"]["60m"],"OBSERVED_ACTIVE")
        self.assertEqual(result["horizons"]["360m"],"PENDING")
    def test_heatmap_latest_only(self):
        ingest(self.con,[record(0,1000),record(5,2000)])
        self.assertEqual(heatmap(self.con)[0]["liquidity_usd"],2000)
    def test_registry_never_self_verifies(self):
        obj={"chain":"testnet","token_address":"0xSTOCK","stock_symbol":"NVDA",
          "issuer":"example","instrument_type":"unknown","evidence_url":"https://example.org"}
        register_token(self.con,obj)
        row=self.con.execute("SELECT verification_status FROM token_registry").fetchone()
        self.assertEqual(row[0],"REVIEW")

if __name__ == "__main__":
    unittest.main()
