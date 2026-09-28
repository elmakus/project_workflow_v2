import hashlib
import json
import unittest
from tools.pwv22_native_foundation import NativeFoundationError
from tools.pwv22_parallel import *
I=lambda n:{"repository":"R","commit":n*40,"path":"p","blob":n*40}
A=I("a"); B=I("b"); ADM=I("c"); ACC=I("d"); RED=I("e"); STALE=I("f"); AACC=I("g"); BACC=I("h"); CA=I("i"); CB=I("j")
def admission(cards=("a","b"),revoked=(),subjects=None,owners=None):
 subjects={"a":CA,"b":CB} if subjects is None else subjects
 owners={"a":"main","b":"main"} if owners is None else owners
 return {"type":"pwv2.2-admission","admission_id":"x","cards":list(cards),"subjects":{cid:subjects[cid] for cid in cards},"mutating_owners":{cid:owners[cid] for cid in cards},"revoked":list(revoked)}
def claims(card,owner="main",writes=("w",),resources=("r",),semantics=("s",),effects=("e",),subject=None):
 subject={"a":CA,"b":CB}.get(card,I("k")) if subject is None else subject
 return {"card_id":card,"subject":subject,"mutating_owner":owner,"writes":list(writes),"resources":list(resources),"semantics":list(semantics),"effects":list(effects)}
def result(rid,artifact):
 return {"type":"pwv2.2-result","result_id":rid,"result_artifact":artifact,"implementation_subject":artifact,"material_inputs":[]}
def acc(subject): return {"verdict":"green","subject":subject}
DURABLE={tuple(ACC.values()):acc(ADM),tuple(RED.values()):{"verdict":"red","subject":ADM},tuple(STALE.values()):acc(A),tuple(AACC.values()):acc(A),tuple(BACC.values()):acc(B)}
DURABLE_ADMISSIONS={tuple(ADM.values()):admission()}
def read_admission(identity):
 key=tuple(identity[k] for k in ("repository","commit","path","blob"))
 if key not in DURABLE_ADMISSIONS: raise NativeFoundationError("admission artifact not durable")
 return DURABLE_ADMISSIONS[key]
def read_acceptance(identity):
 key=tuple(identity[k] for k in ("repository","commit","path","blob"))
 if key not in DURABLE: raise NativeFoundationError("acceptance artifact not durable")
 return DURABLE[key]
def verify(i):
 if i not in (A,B,ADM,CA,CB): raise NativeFoundationError("bad identity")
def legal(left,right,adm_ref=ADM,adm_acc=ACC):
 return parallel_legal(left,right,adm_ref,read_admission,adm_acc,read_acceptance,verify)
def fan(card_ids=("a","b"),adm_ref=ADM,adm_acc=ACC,compatibility=lambda xs:True,sibling_accs=None):
 rs=[result("ra",A),result("rb",B)]
 sibling_accs={"ra":AACC,"rb":BACC} if sibling_accs is None else sibling_accs
 return compatible_fan_in(card_ids,{cid:{"a":CA,"b":CB}.get(cid,I("k")) for cid in card_ids},[A,B],rs,sibling_accs,adm_ref,read_admission,adm_acc,read_acceptance,verify,compatibility)

class ParallelTests(unittest.TestCase):
 def test_explicit_finite_admission_and_revocation(self):
  self.assertTrue(admitted("a",CA,admission()))
  self.assertFalse(admitted("a",CA,admission(revoked=("a",))))
  with self.assertRaises(NativeFoundationError):
   typed_admission({"type":"pwv2.2-admission","admission_id":"x","cards":[]})
 def test_hashable_admission_payload_is_bound_by_external_locator(self):
  payload=admission()
  raw=json.dumps(payload,sort_keys=True,separators=(",",":")).encode()
  blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\\0"+raw).hexdigest()
  identity={"repository":"R","commit":"1"*40,"path":"admission.json","blob":blob}
  acceptance_identity=I("2")
  def read_real(ref):
   self.assertEqual(ref,identity)
   actual=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\\0"+raw).hexdigest()
   if actual!=ref["blob"]: raise NativeFoundationError("admission blob mismatch")
   return payload
  def read_real_acceptance(ref):
   if ref!=acceptance_identity: raise NativeFoundationError("acceptance artifact not durable")
   return acc(identity)
  def verify_real(ref):
   if ref not in (identity,CA,CB): raise NativeFoundationError("bad identity")
  self.assertEqual(accepted_admission(identity,read_real,acceptance_identity,read_real_acceptance,verify_real),payload)
  tampered=dict(identity,blob="3"*40)
  with self.assertRaises(NativeFoundationError):
   accepted_admission(tampered,read_real,acceptance_identity,read_real_acceptance,verify_real)
 def test_unaccepted_or_stale_admission_rejected(self):
  with self.assertRaises(NativeFoundationError): legal(claims("a"),claims("b",writes=("w2",),resources=("r2",),semantics=("s2",),effects=("e2",)),adm_acc=RED)
  with self.assertRaises(NativeFoundationError): legal(claims("a"),claims("b",writes=("w2",),resources=("r2",),semantics=("s2",),effects=("e2",)),adm_acc=STALE)
 def test_fabricated_in_memory_green_cannot_authorize(self):
  fabricated=I("9")
  with self.assertRaises(NativeFoundationError): legal(claims("a"),claims("b",writes=("w2",),resources=("r2",),semantics=("s2",),effects=("e2",)),adm_acc=fabricated)
  with self.assertRaises(NativeFoundationError): fan(adm_acc=fabricated)
 def test_fabricated_admission_membership_cannot_authorize(self):
  fabricated=I("9")
  with self.assertRaises(NativeFoundationError): legal(claims("a"),claims("z",writes=("w2",),resources=("r2",),semantics=("s2",),effects=("e2",)),adm_ref=fabricated)
  with self.assertRaises(NativeFoundationError): fan(card_ids=("a","z"),adm_ref=fabricated)
 def test_fabricated_admitted_card_subject_rejected(self):
  fabricated=I("9")
  prior=DURABLE_ADMISSIONS[tuple(ADM.values())]
  DURABLE_ADMISSIONS[tuple(ADM.values())]=admission(subjects={"a":fabricated,"b":CB})
  try:
   with self.assertRaises(NativeFoundationError):
    legal(claims("a",subject=fabricated),claims("b",writes=("w2",),resources=("r2",),semantics=("s2",),effects=("e2",)))
   with self.assertRaises(NativeFoundationError):
    compatible_fan_in(("a","b"),{"a":fabricated,"b":CB},[A,B],[result("ra",A),result("rb",B)],{"ra":AACC,"rb":BACC},ADM,read_admission,ACC,read_acceptance,verify,lambda xs:True)
  finally:
   DURABLE_ADMISSIONS[tuple(ADM.values())]=prior
 def test_stale_card_subject_rejected(self):
  self.assertFalse(legal(claims("a",subject=I("z")),claims("b",writes=("w2",),resources=("r2",),semantics=("s2",),effects=("e2",))))
  with self.assertRaises(NativeFoundationError):
   compatible_fan_in(("a","b"),{"a":I("z"),"b":CB},[A,B],[result("ra",A),result("rb",B)],{"ra":AACC,"rb":BACC},ADM,read_admission,ACC,read_acceptance,verify,lambda xs:True)
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
 def test_durable_admission_owner_rejects_later_different_mutator(self):
  self.assertTrue(legal(claims("a","main"),claims("b","main",writes=("w2",),resources=("r2",),semantics=("s2",),effects=("e2",))))
  self.assertFalse(legal(claims("a","other"),claims("b","main",writes=("w2",),resources=("r2",),semantics=("s2",),effects=("e2",))))
 def test_admission_owner_binding_is_exact_and_nonempty(self):
  with self.assertRaises(NativeFoundationError): typed_admission(admission(owners={"a":"","b":"main"}))
  with self.assertRaises(NativeFoundationError): typed_admission({**admission(),"mutating_owners":{"a":"main"}})
 def test_exact_ordered_fan_in(self):
  out=fan(compatibility=lambda xs:[x["result_id"] for x in xs]==["ra","rb"])
  self.assertEqual([x["result_id"] for x in out],["ra","rb"])
 def test_incompatible_fan_in_rejected(self):
  with self.assertRaises(NativeFoundationError): fan(compatibility=lambda xs:False)
 def test_revoked_or_nonadmitted_sibling_cannot_fan_in(self):
  with self.assertRaises(NativeFoundationError): fan(adm_ref=I("9"))
  with self.assertRaises(NativeFoundationError): fan(card_ids=("a","z"))
 def test_unaccepted_admission_cannot_fan_in(self):
  with self.assertRaises(NativeFoundationError): fan(adm_acc=RED)
 def test_stale_sibling_acceptance_rejected(self):
  with self.assertRaises(NativeFoundationError): fan(sibling_accs={"ra":AACC,"rb":STALE})
 def test_fabricated_sibling_green_cannot_authorize(self):
  fabricated=I("9")
  with self.assertRaises(NativeFoundationError): fan(sibling_accs={"ra":AACC,"rb":fabricated})

if __name__=="__main__": unittest.main()
