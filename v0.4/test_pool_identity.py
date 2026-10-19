import unittest
from pool_identity import assess_pair
A="0x"+"a"*40; B="0x"+"b"*40; P="0x"+"c"*40; F="0x"+"d"*40
def fake(method,params):
 if method=="eth_chainId":return "0x1237"
 if method=="eth_getCode":return "0x6000"
 return "0x"+"0"*24+F[2:]
class PoolIdentityTests(unittest.TestCase):
 def test_official_leg_but_no_pool_verification(self):
  out=assess_pair(A,B,P,{A.lower():{"symbol":"STOCK"}},fake)
  self.assertEqual(out["issuer_legs"]["base"]["issuer_registry_status"],"OFFICIAL_DEPLOYMENT_MATCH")
  self.assertEqual(out["issuer_legs"]["quote"]["issuer_registry_status"],"NOT_IN_REGISTRY")
  self.assertEqual(out["factory"]["status"],"FACTORY_ADDRESS_HAS_CODE")
  self.assertFalse(out["pool_verified"])
  self.assertFalse(out["factory"]["verified_protocol"])
 def test_factory_failure_is_verify(self):
  def fail(method,params):
   if method=="eth_call": raise ValueError("RPC_HTTP_ERROR method=eth_call status=403")
   return fake(method,params)
  self.assertEqual(assess_pair(A,B,P,{},fail)["factory"]["status"],"VERIFY")
 def test_wrong_chain(self):
  def wrong(method,params):
   if method=="eth_chainId":return "0x1"
   return fake(method,params)
  self.assertEqual(assess_pair(A,B,P,{},wrong)["factory"]["status"],"VERIFY")
if __name__=="__main__": unittest.main()
