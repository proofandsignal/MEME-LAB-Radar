import unittest
from quote_metadata import evaluate,SELECTORS
H="0x"+"a"*64
def enc(value):return "0x"+hex(value)[2:].zfill(64)
def fake(method,params):
 if method=="eth_chainId":return "0x1237"
 if method=="eth_getBlockByNumber":return {"number":"0x10","hash":H}
 if method=="eth_getCode":return "0x6000"
 if method=="eth_call":
  selector=params[0]["data"]
  if selector==SELECTORS["symbol"]:return "0x"+("USDG".encode().hex().ljust(64,"0"))
  if selector==SELECTORS["decimals"]:return enc(6)
  if selector==SELECTORS["totalSupply"]:return enc(10000000)
 raise ValueError(method)
class TestQuoteMetadata(unittest.TestCase):
 def test_match_not_economic_validation(self):
  out=evaluate(fake)
  self.assertEqual(out["status"],"ONCHAIN_METADATA_MATCH")
  self.assertFalse(out["price_verified"])
  self.assertEqual(out["metadata"]["decimals"],6)
 def test_wrong_decimals(self):
  def altered(method,params):
   if method=="eth_call" and params[0]["data"]==SELECTORS["decimals"]:return enc(18)
   return fake(method,params)
  self.assertEqual(evaluate(altered)["status"],"VERIFY")
 def test_failed_rpc(self):
  def fail(method,params):raise ValueError("RPC_HTTP_ERROR method=eth_chainId status=403")
  self.assertEqual(evaluate(fail)["status"],"VERIFY")
if __name__=="__main__":unittest.main()
