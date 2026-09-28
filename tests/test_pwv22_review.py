import unittest
from tools.pwv22_native_foundation import NativeFoundationError
from tools.pwv22_review import *

I=lambda n:{"repository":"R","commit":n*40,"path":"p","blob":n*40}
S=I("a"); A=I("b"); E=I("c")
def attempt(aid="r1",verdict=None,author=False,subject=S,acceptance=A):
 r={"type":"pwv2.2-review-attempt","attempt_id":aid,"subject":subject,"acceptance_surface":acceptance,
    "verdict":verdict,"material_author_or_repairer":author}
 if verdict is not None:r["evidence"]=E
 return r
def finding(fid="f",impact="safe_deferred",affected=("r1",),proof="proved",boundary="before-x"):
 return {"finding_id":fid,"impact":impact,"affected_results":list(affected),
         "safe_continuation_proof":proof,"latest_safe_boundary":boundary}

class ReviewTests(unittest.TestCase):
 def test_exact_subject_binary_attempt(self):
  self.assertEqual(typed_attempt(attempt(verdict="GREEN"))["subject"],S)
  with self.assertRaises(NativeFoundationError): typed_attempt(attempt(verdict="CONDITIONAL"))
 def test_author_or_repairer_excluded_without_runtime_identity(self):
  with self.assertRaises(NativeFoundationError): typed_attempt(attempt(author=True))
  self.assertNotIn("runtime",typed_attempt(attempt()))
 def test_append_only_attempts(self):
  h=[attempt("r1","RED")]
  self.assertEqual(len(append_attempt(h,attempt("r2"))),2)
  with self.assertRaises(NativeFoundationError): append_attempt(h,attempt("r1","GREEN"))
 def test_reviewer_narrow_publication(self):
  out=reviewer_publication(attempt(),attempt(verdict="GREEN"))
  self.assertEqual(out["verdict"],"GREEN")
  with self.assertRaises(NativeFoundationError):
   reviewer_publication(attempt(),attempt(verdict="GREEN",subject=I("z")))
 def test_finalizer_is_mechanical_and_fenced(self):
  self.assertEqual(deterministic_finalization(attempt(verdict="GREEN"),S,A,"review_pending"),"done")
  self.assertEqual(deterministic_finalization(attempt(verdict="RED"),S,A,"review_pending"),"repair_required")
  with self.assertRaises(NativeFoundationError):
   deterministic_finalization(attempt(verdict="GREEN"),I("z"),A,"review_pending")
 def test_acceptance_falsifying_and_unknown_forbid_done(self):
  self.assertFalse(completion_allowed([finding(impact="acceptance_falsifying")]))
  self.assertFalse(completion_allowed([finding(impact="unknown")]))
 def test_safe_deferral_requires_positive_proof_and_boundary(self):
  self.assertTrue(completion_allowed([finding()]))
  with self.assertRaises(NativeFoundationError): completion_allowed([finding(proof="")])
 def test_local_blocking(self):
  fs=[finding(impact="acceptance_falsifying",affected=("x",))]
  self.assertEqual(blocked_results(fs),{"x"})
  self.assertNotIn("y",blocked_results(fs))
 def test_safe_deferral_first_consumption_or_boundary(self):
  f=finding(affected=("x",),boundary="B")
  self.assertFalse(must_repair_before(f,("y",)))
  self.assertTrue(must_repair_before(f,("x",)))
  self.assertTrue(must_repair_before(f,("y",),reached_boundary="B"))
 def test_convergence_ceilings_change_mode_never_accept(self):
  self.assertEqual(convergence_mode("local",4,0),"continue")
  self.assertEqual(convergence_mode("local",5,0),"change_mode")
  self.assertEqual(convergence_mode("integration",4,0),"change_mode")
  self.assertEqual(convergence_mode("final",3,0),"change_mode")
  self.assertEqual(convergence_mode("local",1,3),"escalate")
 def test_material_repair_requires_fresh_closure_reviewer(self):
  self.assertTrue(fresh_closure_required(True,True))
  self.assertFalse(fresh_closure_required(True,False))

if __name__=="__main__": unittest.main()
