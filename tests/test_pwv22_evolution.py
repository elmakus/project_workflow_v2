import unittest
from tools.pwv22_native_foundation import NativeFoundationError
from tools.pwv22_evolution import *

class EvolutionTests(unittest.TestCase):
 def test_preserve_unaffected(self):
  self.assertEqual(classify_evolution(current_epoch="e1",candidate_epoch="e1",changed_properties=["x"],result_properties=["y"],impact_known=True,implementation_changed=False),"preserve")
 def test_revalidate_changed_property_unchanged_implementation(self):
  self.assertEqual(classify_evolution(current_epoch="e1",candidate_epoch="e1",changed_properties=["x"],result_properties=["x"],impact_known=True,implementation_changed=False),"revalidate")
 def test_changed_implementation_is_stale(self):
  self.assertEqual(classify_evolution(current_epoch="e1",candidate_epoch="e1",changed_properties=["x"],result_properties=["x"],impact_known=True,implementation_changed=True),"stale")
 def test_unknown_impact_routes_recovery(self):
  self.assertEqual(classify_evolution(current_epoch="e1",candidate_epoch="e1",changed_properties=["x"],result_properties=["x"],impact_known=False,implementation_changed=False),"recovery")
 def test_mixed_epoch_rejected(self):
  with self.assertRaises(NativeFoundationError): classify_evolution(current_epoch="e1",candidate_epoch="e0",changed_properties=[],result_properties=[],impact_known=True,implementation_changed=False)
 def test_revalidation_retains_result_identity(self):
  r={"result_id":"r1","subject":"same"}; out=revalidation_attachment(r,disposition="revalidate",implementation_changed=False,acceptance_evidence={"review":"green"})
  self.assertEqual(out["result_id"],"r1"); self.assertEqual(out["result"],r)
 def test_changed_implementation_cannot_reuse_result(self):
  with self.assertRaises(NativeFoundationError): revalidation_attachment({"result_id":"r1"},disposition="preserve",implementation_changed=True)
 def test_activation_epoch(self):
  self.assertTrue(activation_allowed(official_epoch="e1",lineage_epoch="e1")); self.assertFalse(activation_allowed(official_epoch="e1",lineage_epoch="e0"))

if __name__=="__main__": unittest.main()
