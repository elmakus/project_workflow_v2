import unittest
from pathlib import Path
from unittest.mock import patch
from tools.pwv22_native_foundation import NativeFoundationError
from tools.pwv22_native_routing import *

SUB={"repository":"R","commit":"1"*40,"path":"x","blob":"2"*40}
OFFICIAL={"official":True,"epoch":"2.2.0","commit":"3"*40}
STATE={"generation":"pwv2.2-native","epoch":"2.2.0"}
REPO=Path("/fixture")

class NativeRoutingTests(unittest.TestCase):
 def test_owner_routing_requires_native_admission(self):
  self.assertEqual(route_owner({**STATE,"phase":"intake"},OFFICIAL),"intake")
  self.assertEqual(route_owner({**STATE,"phase":"planning","research_required":True},OFFICIAL),"research")
  self.assertEqual(route_owner({**STATE,"phase":"definition","question_or_alternative":True},OFFICIAL),"brainstorming")
  with self.assertRaises(NativeFoundationError): route_owner({"phase":"planning"},OFFICIAL)
  with self.assertRaises(NativeFoundationError): route_owner({"generation":"legacy","epoch":"2.2.0","phase":"planning"},OFFICIAL)
  with self.assertRaises(NativeFoundationError): route_owner({**STATE,"phase":"planning"},{**OFFICIAL,"epoch":"2.2.1"})
  with self.assertRaises(NativeFoundationError): route_owner({**STATE,"phase":"planning","return_consumed":True,"return_pending":True},OFFICIAL)
  with self.assertRaises(NativeFoundationError): route_owner({**STATE,"phase":"unknown"},OFFICIAL)

 def test_simplification_requires_owner_disposition(self):
  self.assertTrue(simplification_ready({"material_findings":["f1"],"owner_dispositions":{"f1":"accept"}}))
  self.assertFalse(simplification_ready({"material_findings":["f1"],"owner_dispositions":{}}))
  with self.assertRaises(NativeFoundationError): simplification_ready({"material_findings":["f1"],"owner_dispositions":{"f1":"later"}})

 @patch("tools.pwv22_native_routing.exact_blob")
 def test_exact_gates_use_s05_identity_validation(self,validate):
  for gate in GATES:
   self.assertTrue(satisfy_gate(gate,SUB,SUB,repo=REPO,actual_repository="R")["satisfied"])
  self.assertGreaterEqual(validate.call_count,8)
  stale=dict(SUB); stale["blob"]="4"*40
  with self.assertRaises(NativeFoundationError): satisfy_gate("D",SUB,stale,repo=REPO,actual_repository="R")
  with self.assertRaises(NativeFoundationError): satisfy_gate("X",SUB,SUB,repo=REPO,actual_repository="R")

 @patch("tools.pwv22_native_routing.exact_blob",side_effect=NativeFoundationError("invalid exact identity"))
 def test_gate_fails_closed_when_s05_rejects_identity(self,validate):
  malformed={**SUB,"commit":"not-a-commit"}
  with self.assertRaises(NativeFoundationError):
   satisfy_gate("A",malformed,malformed,repo=REPO,actual_repository="R")

 def test_initial_prep_eager_and_jit_reason(self):
  seams=[{"id":"S1","classification":"materialization_ready"},{"id":"S2","classification":"jit_dependent","future_fact":"accepted predecessor Result"}]
  self.assertEqual(initial_prep(seams),{"materialize":["S1"],"jit":["S2"]})
  with self.assertRaises(NativeFoundationError): initial_prep([{"id":"S2","classification":"jit_dependent"}])

 @patch("tools.pwv22_native_routing.exact_blob")
 def test_d_requires_validated_prepared_readback(self,validate):
  self.assertEqual(premium_d_subject(SUB,SUB,repo=REPO,actual_repository="R")["gate"],"D")
  stale=dict(SUB); stale["commit"]="4"*40
  with self.assertRaises(NativeFoundationError):
   premium_d_subject(SUB,stale,repo=REPO,actual_repository="R")

 def test_routing_fingerprint_requires_admission(self):
  self.assertEqual(len(routing_fingerprint({**STATE,"phase":"planning"},OFFICIAL,[SUB])),64)
  with self.assertRaises(NativeFoundationError): routing_fingerprint({"phase":"planning"},OFFICIAL,[SUB])

 def test_final_qualification_is_mandatory_and_ordered(self):
  done=[]
  for item in QUALIFICATION:
   self.assertEqual(next_qualification(done),item); done.append(item)
  self.assertEqual(next_qualification(done),"done")
  with self.assertRaises(NativeFoundationError): next_qualification(["handoff","targeted_bug_hunt"])

if __name__=="__main__": unittest.main()
