import unittest
from tools.pwv22_native_foundation import NativeFoundationError
from tools.pwv22_close import *

E={"state":"known","applied":True}
BASE=dict(integration_confirmed=True,publication_confirmed=True,effects=[E],findings=[],evolution_disposition="preserve",durable_confirmation=True)

class CloseTests(unittest.TestCase):
 def test_complete_close(self): self.assertTrue(close_ready(**BASE))
 def test_missing_integration_or_publication_blocks(self):
  self.assertFalse(close_ready(**{**BASE,"integration_confirmed":False}))
  self.assertFalse(close_ready(**{**BASE,"publication_confirmed":False}))
 def test_unknown_or_unapplied_effect_blocks(self):
  self.assertFalse(close_ready(**{**BASE,"effects":[{"state":"UNKNOWN"}]}))
  self.assertFalse(close_ready(**{**BASE,"effects":[{"state":"known","applied":False}]}))
 def test_blocking_finding_blocks(self):
  f={"finding_id":"f","impact":"unknown","affected_results":["r"]}
  self.assertFalse(close_ready(**{**BASE,"findings":[f]}))
 def test_stale_or_recovery_blocks(self):
  self.assertFalse(close_ready(**{**BASE,"evolution_disposition":"stale"}))
  self.assertFalse(close_ready(**{**BASE,"evolution_disposition":"recovery"}))
 def test_branch_end_is_not_close(self):
  with self.assertRaises(NativeFoundationError): close_transition({"trigger":"branch_end",**BASE})
 def test_scope_completion_transition(self):
  self.assertEqual(close_transition({"trigger":"approved_scope_completion",**BASE})["state"],"closed")

if __name__=="__main__": unittest.main()
