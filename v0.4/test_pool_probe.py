import unittest
from pool_probe import check_pool
P="0x"+"1"*40;A="0x"+"2"*40;B="0x"+"3"*40
def word(addr): return "0x"+"0"*24+addr[2:]
def fake(method,params):
 if method=="eth_chainId":return "0x1237"
 if method=="eth_getCode":return "0x6000"
 return word(A) if params[0]["data"]=="0x0dfe1681" else word(B)
class PoolTest(unittest.TestCase):
 def test_leg_match_is_not_pool_certification(self):
  r=check_pool(P,A,B,fake)
  self.assertEqual(r["status"],"V2_LEGS_MATCH")
  self.assertFalse(r["verified_liquidity"])
 def test_leg_mismatch(self):
  self.assertEqual(check_pool(P,A,"0x"+"4"*40,fake)["status"],"MISMATCH")
 def test_unsupported_abi(self):
  def bad(method,params):
   if method=="eth_call":return "0x"
   return fake(method,params)
  self.assertEqual(check_pool(P,A,B,bad)["status"],"VERIFY")
 def test_wrong_chain(self):
  def wrong(method,params):
   if method=="eth_chainId":return "0x1"
   return fake(method,params)
  self.assertEqual(check_pool(P,A,B,wrong)["status"],"VERIFY")
 def test_invalid_address(self):
  self.assertEqual(check_pool("bad",A,B,fake)["status"],"VERIFY")
if __name__=="__main__": unittest.main()
