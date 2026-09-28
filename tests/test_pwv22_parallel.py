import unittest
from tools.pwv22_native_foundation import NativeFoundationError
from tools.pwv22_parallel import *
I=lambda n:{"repository":"R","commit":n*40,"path":"p","blob":n*40}
A=I("a"); B=I("b")
def admission(cards=("a","b"),revoked=()):
 return {"type":"pwv2.2-admission","admission_id":"x","cards":list(cards),"revoked":list(revoked)}
def claims(card,owner="main",writes=("w",),resources=("r",),semantics=("s",),effects=("e",)):
 return {"card_id":card,"mutating_owner":owner,"writes":list(writes),"resources":list(resources),"semantics":list(semantics),"effects":list(effects)}
def result(rid,artifact):
 return {"type":"pwv2.2-result","result_id":rid,"result_artifact":artifact,"implementation_subject":artifact,"material_inputs":[]}
def acc(subject): return {"verdict":"green","subject":subject}
def verify(i):
 if i not in (A,B): raise NativeFoundationError("bad identity")

class ParallelTests(unittest.TestCase):
 def test_explicit_finite_admission_and_revocation(self):
  self.assertTrue(admitted("a",admission()))
  self.assertFalse(admitted("a",admission(revoked=("a",))))
  with self.assertRaises(NativeFoundationError): typed_admission({"type":"pwv2.2-admission","admission_id":"x","cards":[]})
 def test_disjoint_claims_parallel(self):
  self.assertTrue(parallel_legal(claims("a"),claims("b",writes=("w2",),resources=("r2",),semantics=("s2",),effects=("e2",)),admission()))
 def test_overlap_serializes(self):
  self.assertFalse(parallel_legal(claims("a"),claims("b"),admission()))
 def test_unknown_effect_serializes(self):
  self.assertFalse(parallel_legal(claims("a"),claims("b",writes=("w2",),resources=("r2",),semantics=("s2",),effects=()),admission()))
 def test_semantic_mismatch_even_when_text_disjoint_serializes(self):
  self.assertFalse(parallel_legal(claims("a",writes=("file-a",),semantics=("schema",)),claims("b",writes=("file-b",),resources=("r2",),semantics=("schema",),effects=("e2",)),admission()))
 def test_one_mutating_owner(self):
  self.assertTrue(one_mutating_owner([claims("a","x"),claims("a","x")]))
  self.assertFalse(one_mutating_owner([claims("a","x"),claims("a","y")]))
 def test_exact_ordered_fan_in(self):
  rs=[result("ra",A),result("rb",B)]
  out=compatible_fan_in([A,B],rs,{"ra":acc(A),"rb":acc(B)},verify,lambda xs:[x["result_id"] for x in xs]==["ra","rb"])
  self.assertEqual([x["result_id"] for x in out],["ra","rb"])
 def test_incompatible_fan_in_rejected(self):
  rs=[result("ra",A),result("rb",B)]
  with self.assertRaises(NativeFoundationError): compatible_fan_in([A,B],rs,{"ra":acc(A),"rb":acc(B)},verify,lambda xs:False)
 def test_stale_sibling_acceptance_rejected(self):
  rs=[result("ra",A),result("rb",B)]
  with self.assertRaises(NativeFoundationError): compatible_fan_in([A,B],rs,{"ra":acc(A),"rb":acc(A)},verify,lambda xs:True)

if __name__=="__main__": unittest.main()
