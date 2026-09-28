import unittest
from tools.pwv22_native_foundation import NativeFoundationError
from tools.pwv22_native_routing import *

SUB={"repository":"R","commit":"1"*40,"path":"x","blob":"2"*40}

class NativeRoutingTests(unittest.TestCase):
 def test_owner_routing_and_returns(self):
  self.assertEqual(route_owner({"phase":"intake"}),"intake")
  self.assertEqual(route_owner({"phase":"planning","research_required":True}),"research")
  self.assertEqual(route_owner({"phase":"definition","question_or_alternative":True}),"brainstorming")
  with self.assertRaises(NativeFoundationError): route_owner({"phase":"planning","return_consumed":True,"return_pending":True})
  with self.assertRaises(NativeFoundationError): route_owner({"phase":"unknown"})

 def test_simplification_requires_owner_disposition(self):
  self.assertTrue(simplification_ready({"material_findings":["f1"],"owner_dispositions":{"f1":"accept"}}))
  self.assertFalse(simplification_ready({"material_findings":["f1"],"owner_dispositions":{}}))
  with self.assertRaises(NativeFoundationError): simplification_ready({"material_findings":["f1"],"owner_dispositions":{"f1":"later"}})

 def test_exact_gates_reject_stale_subject(self):
  for gate in GATES: self.assertTrue(satisfy_gate(gate,SUB,SUB)["satisfied"])
  stale=dict(SUB); stale["blob"]="3"*40
  with self.assertRaises(NativeFoundationError): satisfy_gate("D",SUB,stale)
  with self.assertRaises(NativeFoundationError): satisfy_gate("X",SUB,SUB)

 def test_initial_prep_eager_and_jit_reason(self):
  seams=[{"id":"S1","classification":"materialization_ready"},{"id":"S2","classification":"jit_dependent","future_fact":"accepted predecessor Result"}]
  self.assertEqual(initial_prep(seams),{"materialize":["S1"],"jit":["S2"]})
  with self.assertRaises(NativeFoundationError): initial_prep([{"id":"S2","classification":"jit_dependent"}])

 def test_d_requires_prepared_readback(self):
  self.assertEqual(premium_d_subject(SUB,SUB)["gate"],"D")
  stale=dict(SUB); stale["commit"]="4"*40
  with self.assertRaises(NativeFoundationError): premium_d_subject(SUB,stale)

 def test_final_qualification_is_mandatory_and_ordered(self):
  done=[]
  for item in QUALIFICATION:
   self.assertEqual(next_qualification(done),item); done.append(item)
  self.assertEqual(next_qualification(done),"done")
  with self.assertRaises(NativeFoundationError): next_qualification(["handoff","targeted_bug_hunt"])

if __name__=="__main__": unittest.main()
