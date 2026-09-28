import unittest
from tools.pwv22_native_foundation import NativeFoundationError
from tools.pwv22_effects import *

class EffectsTests(unittest.TestCase):
 def intent(self,request_id="req-1"): return effect_intent(obligation_id="o1",subject={"acceptance":"a1"},target="fixture",request_id=request_id)
 def test_intent_attempt_readback_success(self):
  a=record_attempt(self.intent(),attempt_id="a1"); k=record_readback(a,observed=True,evidence={"target":"yes"})
  self.assertTrue(effect_complete(k)); self.assertEqual(k["state"],"known")
 def test_unknown_forbids_blind_retry(self):
  u=record_readback(record_attempt(self.intent(),attempt_id="a1"),observed=None,evidence={"timeout":True})
  self.assertEqual(u["state"],"UNKNOWN"); self.assertFalse(retry_allowed(u,target_supports_idempotency=True))
 def test_attempt_without_readback_forbids_retry(self):
  self.assertFalse(retry_allowed(record_attempt(self.intent(),attempt_id="a1"),target_supports_idempotency=True))
 def test_supported_idempotency_requires_request_id(self):
  self.assertTrue(retry_allowed(self.intent(),target_supports_idempotency=True))
  self.assertFalse(retry_allowed(self.intent(None),target_supports_idempotency=True))
 def test_known_not_applied_can_retry(self):
  k=record_readback(record_attempt(self.intent(),attempt_id="a1"),observed=False,evidence={"absent":True})
  self.assertTrue(retry_allowed(k,target_supports_idempotency=False))
 def test_secret_key_rejected(self):
  with self.assertRaises(NativeFoundationError):
   effect_intent(obligation_id="o",subject={"secret_token":"x"},target="fixture")

if __name__=="__main__": unittest.main()
