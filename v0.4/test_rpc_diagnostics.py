import unittest
from unittest.mock import patch
from io import BytesIO
from pool_probe import rpc

class Response:
 def __init__(self,body): self.body=BytesIO(body)
 def __enter__(self):return self
 def __exit__(self,*args):return False
 def read(self,*args):return self.body.read(*args)

class RPCDiagnosticsTest(unittest.TestCase):
 def test_revert_is_classified_without_raw_text(self):
  with patch("pool_probe.urlopen",return_value=Response(b'{"jsonrpc":"2.0","id":1,"error":{"code":-32000,"message":"execution reverted: private detail"}}')):
   with self.assertRaisesRegex(ValueError,"RPC_JSON_ERROR method=eth_call code=-32000 category=execution_reverted") as ctx:
    rpc("eth_call",[])
   self.assertNotIn("private detail",str(ctx.exception))
 def test_missing_result(self):
  with patch("pool_probe.urlopen",return_value=Response(b'{"jsonrpc":"2.0","id":1}')):
   with self.assertRaisesRegex(ValueError,"RPC_MISSING_RESULT method=eth_call"):
    rpc("eth_call",[])
 def test_nonobject_error(self):
  with patch("pool_probe.urlopen",return_value=Response(b'{"error":"secret"}')):
   with self.assertRaisesRegex(ValueError,"code=unknown category=other"):
    rpc("eth_call",[])
if __name__=="__main__": unittest.main()
