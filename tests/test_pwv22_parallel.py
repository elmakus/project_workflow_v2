import unittest
from tools.pwv22_native_foundation import NativeFoundationError
from tools.pwv22_parallel import *
I=lambda n:{"repository":"R","commit":n*40,"path":"p","blob":n*40}
A=I("a"); B=I("b"); ADM=I("c")
def admission(cards=("a","b"),revoked=()):
 return {"type":"pwv2.2-admission","admission_id":"x","subject":ADM,"cards":list(cards),"revoked":list(revoked)}
def claims(card,owner="main",writes=("w",),resources=("r",),semantics=("s",),effects=("e",)):
 return {"card_id":card,"mutating_owner":owner,"writes":list(writes),"resources":list(resources),"semantics":list(semantics),"effects":list(effects)}
def result(rid,artifact):
 return {"type":"pwv2.2-result","result_id":rid,"result_artifact":artifact,"implementation_subject":artifact,"material_inputs":[]}
def acc(subject): return {"verdict":"green","subject":subject}
def verify(i):
 if i not in (A,B,ADM): raise NativeFoundationError("bad identity")
def legal(left,right,adm=None,adm_acc=None):
 adm=admission() if adm is None else adm
 adm_acc=acc(ADM) if adm_acc is None else adm_acc
 return parallel_legal(left,right,adm,adm_acc,verify)
def fan(card_ids=("a","b"),adm=None,adm_acc=None,compatibility=lambda xs:True):
 rs=[result("ra",A),result("rb",B)]
 adm=admission() if adm is None else adm
 adm_acc=acc(ADM) if adm_acc is None else adm_acc
 return compatible_fan_in(card_ids,[A,B],rs,{"ra":acc(A),"rb":acc(B)},adm,adm_acc,verify,compatibility)

class ParallelTests(unittest.TestCase):
 def test_explicit_finite_admission_and_revocation(self):
  self.assertTrue(admitted("a",admission()))
  self.assertFalse(admitted("a",admission(revoked=("a",))))
  with self.assertRaises(NativeFoundationError):
   typed_admission({"type":"pwv2.2-admission","admission_id":"x","subject":ADM,"cards":[]})
 def test_unaccepted_or_stale_admission_rejected(self):
  with self.assertRaises(NativeFoundationError): legal(claims("a"),claims("b",writes=("w2",),resources=("r2",),semantics=("s2",),effects=("e2",)),adm_acc={"verdict":"red","subject":ADM})
  with self.assertRaises(NativeFoundationError): legal(claims("a"),claims("b",writes=("w2",),resources=("r2",),semantics=("s2",),effects=("e2",)),adm_acc=acc(A))
 def test_disjoint_claims_parallel(self):
  self.assertTrue(legal(claims("a"),claims("b",writes=("w2",),resources=("r2",),semantics=("s2",),effects=("e2",))))
 def test_overlap_serializes(self):
  self.assertFalse(legal(claims("a"),claims("b")))
 def test_unknown_effect_serializes(self):
  self.assertFalse(legal(claims("a"),claims("b",writes=("w2",),resources=("r2",),semantics=("s2",),effects=())))
 def test_semantic_mismatch_even_when_text_disjoint_serializes(self):
  self.assertFalse(legal(claims("a",writes=("file-a",),semantics=("schema",)),claims("b",writes=("file-b",),resources=("r2",),semantics=("schema",),effects=("e2",))))
 def test_one_mutating_owner(self):
  self.assertTrue(one_mutating_owner([claims("a","x"),claims("a","x")]))
  self.assertFalse(one_mutating_owner([claims("a","x"),claims("a","y")]))
 def test_exact_ordered_fan_in(self):
  out=fan(compatibility=lambda xs:[x["result_id"] for x in xs]==["ra","rb"])
  self.assertEqual([x["result_id"] for x in out],["ra","rb"])
 def test_incompatible_fan_in_rejected(self):
  with self.assertRaises(NativeFoundationError): fan(compatibility=lambda xs:False)
 def test_revoked_or_nonadmitted_sibling_cannot_fan_in(self):
  with self.assertRaises(NativeFoundationError): fan(adm=admission(revoked=("a",)))
  with self.assertRaises(NativeFoundationError): fan(card_ids=("a","z"))
 def test_unaccepted_admission_cannot_fan_in(self):
  with self.assertRaises(NativeFoundationError): fan(adm_acc={"verdict":"red","subject":ADM})
 def test_stale_sibling_acceptance_rejected(self):
  rs=[result("ra",A),result("rb",B)]
  with self.assertRaises(NativeFoundationError):
   compatible_fan_in(("a","b"),[A,B],rs,{"ra":acc(A),"rb":acc(A)},admission(),acc(ADM),verify,lambda xs:True)

if __name__=="__main__": unittest.main()
