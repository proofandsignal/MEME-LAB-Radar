import unittest
from live_adapter import normalize,metric

PAIR={"chainId":"ethereum","pairAddress":"0xPOOL",
      "baseToken":{"address":"0xBASE","symbol":"NVDA"},
      "quoteToken":{"address":"0xQUOTE","symbol":"USDC"},
      "priceUsd":"1.50","liquidity":{"usd":123.0},
      "volume":{"h24":1500},"txns":{"h24":{"buys":2,"sells":3}}}
class AdapterTests(unittest.TestCase):
    def test_candidate_not_verified_from_ticker(self):
        records,bad=normalize({"pairs":[PAIR]},"2026-10-15T06:00:00Z")
        self.assertEqual(bad,[])
        self.assertEqual(records[0]["stock_symbol"],None)
        self.assertEqual(records[0]["discovery_status"],"UNVERIFIED")
        self.assertEqual(records[0]["txns_24h"],5)
        self.assertEqual(records[0]["source"],"dexscreener")
    def test_reject_bad_provider_payload(self):
        with self.assertRaises(ValueError):normalize({})
        records,bad=normalize({"pairs":[{**PAIR,"priceUsd":"NaN"}]},"2026-10-15T06:00:00Z")
        self.assertEqual(len(records),0)
        self.assertEqual(len(bad),1)
    def test_no_fabricated_missing_numbers(self):
        pair={**PAIR,"liquidity":None,"volume":None,"txns":None,"priceUsd":None}
        r,_=normalize({"pairs":[pair]},"2026-10-15T06:00:00Z")
        self.assertIsNone(r[0]["price_usd"])
        self.assertIsNone(r[0]["liquidity_usd"])
        self.assertIsNone(r[0]["txns_24h"])
    def test_invalid_metric(self):
        with self.assertRaises(ValueError):metric(-1,"liquidity")
        with self.assertRaises(ValueError):metric(True,"volume")
if __name__=="__main__":
    unittest.main()
