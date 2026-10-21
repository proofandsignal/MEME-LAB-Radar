import unittest
from factory_getpair import investigate,POOL
H="0x"+"a"*64
def stub(method,params):
 if method=="eth_chainId":return "0x1237"
 if method=="eth_getBlockByNumber":return {"number":"0x99","hash":H}
 if method=="eth_call":return "0x"+"0"*24+POOL[2:].lower()
 raise ValueError("unsupported")
class FactoryTests(unittest.TestCase):
 def test_match_is_not_provenance(self):
  result=investigate(stub)
  self.assertEqual(result["status"],"FACTORY_GETPAIR_MATCH")
  self.assertFalse(result["factory_provenance_verified"])
 def test_mismatch(self):
  def other(method,params):
   return "0x"+"0"*24+"2"*40 if method=="eth_call" else stub(method,params)
  self.assertEqual(investigate(other)["status"],"MISMATCH")
 def test_rpc_denial(self):
  def denial(method,params):
   if method=="eth_call":raise ValueError("RPC_HTTP_ERROR method=eth_call status=403")
   return stub(method,params)
  self.assertEqual(investigate(denial)["status"],"VERIFY")
if __name__=="__main__":unittest.main()
