import unittest
from anchored_pool import inspect
P="0x"+"1"*40
A="0x"+"2"*40
B="0x"+"3"*40
F="0x"+"4"*40
H="0x"+"a"*64
def word(address):return "0x"+"0"*24+address[2:]
def fake(method,params):
 if method=="eth_chainId":return "0x1237"
 if method=="eth_getBlockByNumber":return {"number":"0x10","hash":H}
 if method=="eth_getCode":return "0x6000"
 if method=="eth_call":
  return word({"0x0dfe1681":A,"0xd21220a7":B,"0xc45a0155":F}[params[0]["data"]])
 raise ValueError(method)
class AnchorTests(unittest.TestCase):
 def test_anchor_reads_only(self):
  r=inspect(P,fake)
  self.assertEqual(r["status"],"BLOCK_ANCHORED_READ")
  self.assertEqual(r["anchor"]["number"],"0x10")
  self.assertFalse(r["liquidity_verified"])
  self.assertFalse(r["factory_provenance_verified"])
 def test_block_hash_mismatch_blocks(self):
  calls=[0]
  def change(method,params):
   if method=="eth_getBlockByNumber":
    calls[0]+=1
    if calls[0]==2:return {"number":"0x10","hash":"0x"+"b"*64}
   return fake(method,params)
  self.assertEqual(inspect(P,change)["status"],"VERIFY")
 def test_403_reports_method(self):
  def deny(method,params):
   if method=="eth_call":raise ValueError("RPC_HTTP_ERROR method=eth_call status=403")
   return fake(method,params)
  r=inspect(P,deny)
  self.assertEqual(r["status"],"VERIFY")
  self.assertEqual(r["read_trace"][-1]["method"],"eth_call")
if __name__=="__main__":unittest.main()
