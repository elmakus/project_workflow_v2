import unittest
from unittest.mock import patch

from tools.pwv22_native_foundation import NativeFoundationError
from tools.pwv22_lifecycle import integrated_lifecycle
from tools.pwv22_native_routing import QUALIFICATION

def I(n):
    return {"repository":"R","commit":n*40,"path":"p","blob":n*40}

A=I("a"); B=I("b"); SURFACE=I("c"); REVIEW=I("d")

def result(rid, identity):
    return {"type":"pwv2.2-result","result_id":rid,"result_artifact":identity,
            "implementation_subject":identity,"material_inputs":[]}

def acceptance(identity):
    return {"verdict":"green","subject":identity}

def attempt(verdict="GREEN", author=False):
    return {"type":"pwv2.2-review-attempt","attempt_id":"R06","subject":REVIEW,
            "acceptance_surface":SURFACE,"verdict":verdict,"evidence":I("e"),
            "material_author_or_repairer":author}

def close(effect_state="known", applied=True, finding=None, disposition="preserve"):
    findings=[] if finding is None else [finding]
    return {"trigger":"approved_scope_completion","integration_confirmed":True,
            "publication_confirmed":True,"effects":[{"state":effect_state,"applied":applied}],
            "findings":findings,"evolution_disposition":disposition,"durable_confirmation":True}

def evolution(changed=(), known=True, implementation_changed=False):
    return {"current_epoch":"2.2","candidate_epoch":"2.2","changed_properties":list(changed),
            "result_properties":["core"],"impact_known":known,
            "implementation_changed":implementation_changed}

def base(**overrides):
    kw={"expected_results":[A,B],"results":[result("a",A),result("b",B)],
        "constituent_acceptances":[acceptance(A),acceptance(B)],
        "verify_identity":lambda x: None,"review_attempt":attempt(),
        "expected_review_subject":REVIEW,"expected_acceptance_surface":SURFACE,
        "findings":[],"qualification_completed":list(QUALIFICATION),"repair_issue":None,
        "evolution":evolution(),"close_record":close()}
    kw.update(overrides)
    return kw

class LifecycleTests(unittest.TestCase):
    def test_complete_lifecycle_closes(self):
        out=integrated_lifecycle(**base())
        self.assertEqual(out["state"],"closed")
        self.assertEqual(out["accepted_result_ids"],["a","b"])

    def test_missing_or_stale_constituent_fails(self):
        with self.assertRaises(NativeFoundationError):
            integrated_lifecycle(**base(results=[result("a",A)]))
        with self.assertRaises(NativeFoundationError):
            integrated_lifecycle(**base(constituent_acceptances=[acceptance(A),acceptance(I("f"))]))

    def test_incompatible_multi_result_fan_in_fails(self):
        fan={"expected_card_ids":["a","b"],"expected_card_subjects":{"a":A,"b":B},
             "acceptance_identities":{},"sibling_claims":[],"admission_identity":A,
             "read_admission":lambda x:{}, "admission_acceptance_identity":B,
             "read_acceptance":lambda x:{}, "compatibility":lambda xs:False}
        with patch("tools.pwv22_lifecycle.compatible_fan_in", side_effect=NativeFoundationError("integrated sibling incompatibility")):
            with self.assertRaises(NativeFoundationError):
                integrated_lifecycle(**base(fan_in=fan))

    def test_integrated_review_must_be_green_and_independent(self):
        with self.assertRaises(NativeFoundationError):
            integrated_lifecycle(**base(review_attempt=attempt("RED")))
        with self.assertRaises(NativeFoundationError):
            integrated_lifecycle(**base(review_attempt=attempt("GREEN",True)))

    def test_blocking_finding_fails_closed(self):
        finding={"finding_id":"F","impact":"acceptance_falsifying","affected_results":[]}
        with self.assertRaises(NativeFoundationError):
            integrated_lifecycle(**base(findings=[finding],close_record=close(finding=finding)))

    def test_skipped_qualification_fails(self):
        with self.assertRaises(NativeFoundationError):
            integrated_lifecycle(**base(qualification_completed=list(QUALIFICATION[:-1])))

    def test_semantic_repair_returns_to_owner(self):
        issue={"kind":"strategy","owner":"planning"}
        with self.assertRaises(NativeFoundationError):
            integrated_lifecycle(**base(repair_issue=issue))

    def test_unknown_or_stale_evolution_fails(self):
        with self.assertRaises(NativeFoundationError):
            integrated_lifecycle(**base(evolution=evolution(known=False),close_record=close(disposition="recovery")))
        with self.assertRaises(NativeFoundationError):
            integrated_lifecycle(**base(evolution=evolution(changed=["core"],implementation_changed=True),
                                        close_record=close(disposition="stale")))

    def test_unknown_or_unapplied_effect_fails(self):
        with self.assertRaises(NativeFoundationError):
            integrated_lifecycle(**base(close_record=close(effect_state="UNKNOWN",applied=False)))
        with self.assertRaises(NativeFoundationError):
            integrated_lifecycle(**base(close_record=close(applied=False)))

    def test_branch_end_cannot_close(self):
        bad=close(); bad["trigger"]="branch_end"
        with self.assertRaises(NativeFoundationError):
            integrated_lifecycle(**base(close_record=bad))

if __name__=="__main__":
    unittest.main()
