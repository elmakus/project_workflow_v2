import unittest
from tools.pwv22_native_foundation import NativeFoundationError
from tools.pwv22_native_results import *

I=lambda n:{"repository":"R","commit":n*40,"path":"p","blob":n*40}
A=I("a"); B=I("b"); C=I("c")
def result(rid,artifact,subject=A,materials=None):
 return {"type":"pwv2.2-result","result_id":rid,"result_artifact":artifact,
         "implementation_subject":subject,"material_inputs":materials or []}
def acceptance(subject,verdict="green"): return {"verdict":verdict,"subject":subject}
def verify(identity):
 if identity.get("repository")!="R" or identity.get("path")!="p" or identity.get("commit") not in {A["commit"],B["commit"],C["commit"]} or identity.get("blob")!=identity.get("commit"):
  raise NativeFoundationError("unverifiable identity")

class NativeResultTests(unittest.TestCase):
 def test_exact_dependency_and_done_without_result(self):
  r=result("r1",A,materials=[B])
  self.assertEqual(accepted_dependency(A,r,acceptance(A),verify)["result_id"],"r1")
  self.assertFalse(readiness([A],[],{},verify))
 def test_wrong_repo_path_blob_fail_closed(self):
  r=result("r1",A)
  for k,v in [("repository","X"),("path","q"),("blob","d"*40)]:
   wrong=dict(A); wrong[k]=v
   with self.assertRaises(NativeFoundationError): accepted_dependency(wrong,r,acceptance(A),verify)
 def test_stale_acceptance_rejected(self):
  with self.assertRaises(NativeFoundationError): accepted_dependency(A,result("r1",A),acceptance(B),verify)
  with self.assertRaises(NativeFoundationError): accepted_dependency(A,result("r1",A),acceptance(A,"red"),verify)
 def test_consistently_forged_locator_fails_closed(self):
  forged={"repository":"R","commit":"d"*40,"path":"p","blob":"d"*40}
  with self.assertRaises(NativeFoundationError):
   accepted_dependency(forged,result("r1",forged,subject=A),acceptance(forged),verify)
 def test_material_local_freshness_preserves_unrelated(self):
  r1=result("r1",A,materials=[B]); r2=result("r2",B,materials=[C])
  self.assertEqual(affected_results([r1,r2],[B]),["r1"])
  self.assertTrue(material_fresh(r2,[C]))
  self.assertFalse(material_fresh(r1,[C]))
 def test_frontier_is_derived(self):
  r=result("r1",A)
  self.assertEqual(frontier([{"id":"x","dependencies":[A]},{"id":"y","dependencies":[B]}],[r],{"r1":acceptance(A)},verify),["x"])
 def test_history_immutable_and_revalidation_retains_result(self):
  r=result("r1",A,subject=B)
  with self.assertRaises(NativeFoundationError): append_result([r],result("r1",C,subject=C))
  with self.assertRaises(NativeFoundationError): append_result([r],result("r2",C,subject=B))
  self.assertEqual(result_fingerprint(r),result_fingerprint(r))
 def test_invalid_typed_payload(self):
  with self.assertRaises(NativeFoundationError): typed_result({"type":"legacy"})
  with self.assertRaises(NativeFoundationError): typed_result({"type":"pwv2.2-result","result_id":"x","implementation_subject":A,"material_inputs":"bad"})

if __name__=="__main__": unittest.main()
