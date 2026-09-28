import unittest
from tools.pwv22_native_foundation import NativeFoundationError
from tools.pwv22_recovery import *

OFFICIAL={"official":True,"epoch":"e1","commit":"a"*40}
BASE={"generation":"pwv2.2-native","epoch":"e1","phase":"execution"}

class RecoveryTests(unittest.TestCase):
 def test_reconstructs_exact_owner(self):
  self.assertEqual(reconstruct_owner(BASE,OFFICIAL),"execution")
  self.assertEqual(reconstruct_owner({**BASE,"phase":"review","return_pending":{"owner":"planning"}},OFFICIAL),"planning")
 def test_consumed_pending_return_fails_closed(self):
  with self.assertRaises(NativeFoundationError):
   reconstruct_owner({**BASE,"return_pending":{"owner":"planning"},"return_consumed":True},OFFICIAL)
 def test_mechanical_vs_owner_choice(self):
  self.assertEqual(classify_repair({"kind":"derived_readiness"}),{"class":"mechanical","operation":"recompute"})
  self.assertEqual(classify_repair({"kind":"strategy","owner":"planning"}),{"class":"owner_choice","owner":"planning"})
  with self.assertRaises(NativeFoundationError): classify_repair({"kind":"derived_readiness","semantic_change":True})
 def test_finding_blocking_is_local(self):
  fs=[{"finding_id":"f1","impact":"acceptance_falsifying","affected_results":["r1"]},
      {"finding_id":"f2","impact":"safe_deferred","affected_results":["r2"],"safe_continuation_proof":"safe","latest_safe_boundary":"S20"},
      {"finding_id":"f3","impact":"unknown","affected_results":["r4"]}]
  self.assertEqual(recovery_blocked_results(fs),{"r1","r4"})
 def test_durable_result_is_not_replayed(self):
  self.assertFalse(durable_result_replay_allowed("r1",["r1"]))
  with self.assertRaises(NativeFoundationError):
   recovery_action(BASE,OFFICIAL,{"kind":"derived_readiness"},[],result_id="r1",durable_result_ids=["r1"])
 def test_owner_choice_remains_semantic(self):
  out=recovery_action(BASE,OFFICIAL,{"kind":"factual","owner":"research"},[])
  self.assertEqual((out["action"],out["owner"]),("return_to_owner","research"))
 def test_wrong_epoch_fails_closed(self):
  with self.assertRaises(NativeFoundationError): reconstruct_owner({**BASE,"epoch":"wrong"},OFFICIAL)

if __name__=="__main__": unittest.main()
