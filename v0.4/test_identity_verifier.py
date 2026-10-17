import unittest
from identity_verifier import verify_pair_echo,match_official_token
A={"chainId":"robinhood","pairAddress":"0x"+"1"*40,
"baseToken":{"address":"0x"+"2"*40},"quoteToken":{"address":"0x"+"3"*40}}
class IdentityTest(unittest.TestCase):
 def test_echo_not_onchain_proof(self):
  v=verify_pair_echo(A,{"pairs":[dict(A)]})
  self.assertEqual(v["status"],"PROVIDER_ECHO_MATCH")
  self.assertFalse(v["independent_onchain_verified"])
 def test_mismatch_is_block(self):
  x=dict(A);x["quoteToken"]={"address":"0x"+"4"*40}
  self.assertEqual(verify_pair_echo(A,{"pairs":[x]})["status"],"MISMATCH")
 def test_absent_not_verified(self):
  self.assertEqual(verify_pair_echo(A,{"pairs":[]})["status"],"VERIFY")
 def test_ticker_never_establishes_official(self):
  self.assertEqual(match_official_token(A,{})["status"],"UNVERIFIED")
 def test_curated_address_match_only_reference(self):
  addr="0x"+"2"*40
  v=match_official_token(A,{addr:{"symbol":"NVDA"}})
  self.assertEqual(v["status"],"OFFICIAL_REFERENCE_MATCH")
  self.assertFalse(v["onchain_verified"])
 def test_wrong_chain(self):
  p=dict(A);p["chainId"]="solana"
  self.assertEqual(match_official_token(p,{})["status"],"UNSUPPORTED_CHAIN")
if __name__=="__main__":unittest.main()
