import json
import tempfile
import unittest
from pathlib import Path
from radar import init_db, ingest, export_snapshot

ROOT=Path(__file__).resolve().parent.parent
class CompatibilityTests(unittest.TestCase):
    def test_static_entrypoint_assets_exist(self):
        html=(ROOT/"index.html").read_text(encoding="utf-8")
        for asset in ("app.js","styles.css"):
            self.assertIn(asset,html)
            self.assertTrue((ROOT/asset).is_file(),asset)
    def test_export_matches_ui_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=init_db(str(Path(tmp)/"test.sqlite3"))
            try:
                r={"observed_at":"2026-10-09T08:00:00Z",
                   "chain":"testnet","pool_address":"0xEXAMPLE",
                   "base_token":"0xMEME","quote_token":"0xASSET",
                   "source":"fixture","source_record_id":"test1",
                   "stock_symbol":"NVDA","liquidity_usd":100.0}
                self.assertEqual(ingest(db,[r])["inserted"],1)
                payload=export_snapshot(db)
                restored=json.loads(json.dumps(payload))
                self.assertEqual(restored["schema_version"],"0.4.0")
                self.assertEqual(restored["data_gate"],"UNVERIFIED")
                self.assertEqual(len(restored["observations"]),1)
                self.assertEqual(restored["observations"][0]["source"],"fixture")
                self.assertEqual(restored["observations"][0]["pool_address"],"0xEXAMPLE")
                self.assertEqual(restored["observations"][0]["liquidity_usd"],100.0)
                self.assertEqual(len(restored["observations"][0]["raw_sha256"]),64)
            finally:
                db.close()
if __name__=="__main__":
    unittest.main()
