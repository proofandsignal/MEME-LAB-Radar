import unittest
from issuer_rpc import assess,deployments,chain_probe
A="0x"+"a"*40
ASSETS={"assets":[{"tokenSymbol":"NVDA","status":"ASSET_STATUS_ACTIVE","deployments":[{"chainId":4663,"contractAddress":A}]}]}
def fake_rpc(url,payload=None):
    if payload["method"]=="eth_chainId":return {"result":"0x1237"}
    return {"result":"0x6000"}
class IssuerRPCTest(unittest.TestCase):
    def test_matching_deployment_and_bytecode(self):
        r=assess(A,ASSETS,fake_rpc)
        self.assertEqual(r["status"],"ISSUER_DEPLOYMENT_AND_CODE_MATCH")
        self.assertFalse(r["pool_verified"])
    def test_no_ticker_fallback(self):
        self.assertEqual(assess("0x"+"b"*40,ASSETS,fake_rpc)["status"],"UNVERIFIED")
    def test_wrong_chain_rejected(self):
        def wrong(url,payload=None):return {"result":"0x1"}
        self.assertEqual(chain_probe(A,wrong)["status"],"VERIFY")
    def test_missing_code_blocks(self):
        def no_code(url,payload=None):
            return {"result":"0x1237" if payload["method"]=="eth_chainId" else "0x"}
        self.assertEqual(assess(A,ASSETS,no_code)["status"],"VERIFY")
    def test_unexpected_registry_shape(self):
        with self.assertRaises(ValueError):deployments({"unexpected":[]})
if __name__=="__main__":unittest.main()
