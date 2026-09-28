from __future__ import annotations

import copy
import unittest

from tools.execution_contract import parse_card_result
from tools.worker_evidence_contract import validate_worker_evidence
from tools.worker_scope_contract import (
    WorkerScopeError,
    scope_status,
    validate_worker_scope,
)


def scope_record() -> dict:
    return {
        "card_id": "M02R-T13",
        "accepted_scope": "bind worker implementation to accepted card authority under REQ-132",
        "items": [
            {
                "description": "validate accepted need against card authority before implementing",
                "kind": "accepted_need",
                "accepted_authority": True,
            }
        ],
        "post_green_refactor": None,
    }


def refactor_record() -> dict:
    record = scope_record()
    record["post_green_refactor"] = {
        "summary": "rename scope helper internals without changing accepted behavior",
        "adds_new_scope": False,
        "disclosed": True,
        "local_green_check": "python3 -m unittest tests.test_worker_scope_contract",
        "local_green_evidence": "evidence/M02R-T13-local-green.md: scope suite GREEN before refactor",
        "renewed_check": "python3 -m unittest tests.test_worker_scope_contract",
        "renewed_evidence": "evidence/M02R-T13-renewed-green.md: same scope suite GREEN after refactor",
    }
    return record


def dry_item(
    *,
    resolution: str = "keep_duplication",
    adds_coupling_or_risk: bool = True,
    accepted_authority: bool = False,
) -> dict:
    return {
        "description": "share scope text helpers across worker contract modules",
        "kind": "dry_abstraction",
        "accepted_authority": accepted_authority,
        "adds_coupling_or_risk": adds_coupling_or_risk,
        "resolution": resolution,
    }


class WorkerScopeContractTests(unittest.TestCase):
    def test_genuine_accepted_need_is_allowed(self) -> None:
        normalized = validate_worker_scope(scope_record())
        self.assertEqual(normalized["card_id"], "M02R-T13")
        self.assertEqual(
            scope_status(scope_record(), expected_card_id="M02R-T13"),
            "in_scope_green",
        )

    def test_multiple_accepted_items_are_allowed(self) -> None:
        record = scope_record()
        record["items"].append(
            {
                "description": "reject adjacent product work lacking card authority",
                "kind": "accepted_need",
                "accepted_authority": True,
            }
        )
        normalized = validate_worker_scope(record)
        self.assertEqual(len(normalized["items"]), 2)

    def test_bounded_post_green_refactor_with_renewed_verification_is_allowed(self) -> None:
        normalized = validate_worker_scope(refactor_record())
        refactor = normalized["post_green_refactor"]
        self.assertEqual(refactor["renewed_check"], refactor["local_green_check"])
        self.assertNotEqual(refactor["renewed_evidence"], refactor["local_green_evidence"])

    def test_scope_binds_same_card_as_falsification_evidence(self) -> None:
        evidence = {
            "card_id": "M02R-T13",
            "outcome_class": "code",
            "baseline": {
                "kind": "automated_check",
                "check": "python3 -m unittest tests.test_worker_scope_contract",
                "status": "red",
                "subject": {"repository": "elmakus/project_workflow_v2", "commit": "a" * 40},
                "evidence": "evidence/M02R-T13-baseline-red.md: scope contract missing",
            },
            "implementation": {
                "subject": {"repository": "elmakus/project_workflow_v2", "commit": "b" * 40},
                "summary": "add runtime-neutral worker scope discipline contract",
            },
            "verification": {
                "check": "python3 -m unittest tests.test_worker_scope_contract",
                "status": "green",
                "subject": {"repository": "elmakus/project_workflow_v2", "commit": "b" * 40},
                "evidence": "evidence/M02R-T13-verification-green.md: scope suite GREEN",
            },
            "sequence": {"baseline": 1, "implementation": 2, "verification": 3},
            "observable_justification": None,
        }
        validate_worker_evidence(evidence)
        self.assertEqual(
            scope_status(scope_record(), expected_card_id=evidence["card_id"]),
            "in_scope_green",
        )

    def test_speculative_functionality_is_forbidden(self) -> None:
        record = scope_record()
        record["items"] = [
            {
                "description": "add speculative dashboard nobody on the card requested",
                "kind": "speculative_functionality",
                "accepted_authority": False,
            }
        ]
        with self.assertRaisesRegex(WorkerScopeError, "forbidden"):
            validate_worker_scope(record)

    def test_future_proofing_abstraction_is_forbidden(self) -> None:
        record = scope_record()
        record["items"] = [
            {
                "description": "build generic plugin framework for imagined future cards",
                "kind": "future_proofing_abstraction",
                "accepted_authority": False,
            }
        ]
        with self.assertRaisesRegex(WorkerScopeError, "forbidden"):
            validate_worker_scope(record)

    def test_adjacent_scope_is_forbidden(self) -> None:
        record = scope_record()
        record["items"] = [
            {
                "description": "redesign neighboring milestone review workflow",
                "kind": "adjacent_scope",
                "accepted_authority": False,
            }
        ]
        with self.assertRaisesRegex(WorkerScopeError, "forbidden"):
            validate_worker_scope(record)

    def test_forbidden_kind_cannot_be_laundered_with_authority_flag(self) -> None:
        for kind in ("speculative_functionality", "future_proofing_abstraction", "adjacent_scope"):
            with self.subTest(kind=kind):
                record = scope_record()
                record["items"] = [
                    {
                        "description": "claim authority for out-of-card work item here",
                        "kind": kind,
                        "accepted_authority": True,
                    }
                ]
                with self.assertRaisesRegex(WorkerScopeError, "forbidden"):
                    validate_worker_scope(record)

    def test_accepted_need_without_authority_fails(self) -> None:
        record = scope_record()
        record["items"][0]["accepted_authority"] = False
        with self.assertRaisesRegex(WorkerScopeError, "accepted authority"):
            validate_worker_scope(record)

    def test_non_boolean_authority_flag_fails(self) -> None:
        record = scope_record()
        record["items"][0]["accepted_authority"] = "yes"
        with self.assertRaisesRegex(WorkerScopeError, "must be a boolean"):
            validate_worker_scope(record)

    def test_unknown_item_kind_fails(self) -> None:
        record = scope_record()
        record["items"][0]["kind"] = "speculative_hardening"
        with self.assertRaisesRegex(WorkerScopeError, r"items\[0\]\.kind"):
            validate_worker_scope(record)

    def test_dry_cannot_force_abstraction_under_coupling_or_risk(self) -> None:
        record = scope_record()
        record["items"] = [dry_item(resolution="abstract", adds_coupling_or_risk=True)]
        with self.assertRaisesRegex(WorkerScopeError, "coupling"):
            validate_worker_scope(record)

    def test_local_duplication_may_remain_when_abstraction_adds_risk(self) -> None:
        record = scope_record()
        record["items"] = [dry_item()]
        normalized = validate_worker_scope(record)
        self.assertEqual(normalized["items"][0]["resolution"], "keep_duplication")

    def test_safe_dry_abstraction_still_requires_accepted_authority(self) -> None:
        record = scope_record()
        record["items"] = [
            dry_item(resolution="abstract", adds_coupling_or_risk=False, accepted_authority=False)
        ]
        with self.assertRaisesRegex(WorkerScopeError, "accepted authority"):
            validate_worker_scope(record)
        record["items"] = [
            dry_item(resolution="abstract", adds_coupling_or_risk=False, accepted_authority=True)
        ]
        normalized = validate_worker_scope(record)
        self.assertEqual(normalized["items"][0]["resolution"], "abstract")

    def test_dry_resolution_must_be_explicit(self) -> None:
        record = scope_record()
        item = dry_item()
        item["resolution"] = "maybe_later"
        record["items"] = [item]
        with self.assertRaisesRegex(WorkerScopeError, "resolution"):
            validate_worker_scope(record)

    def test_refactor_adding_new_scope_is_forbidden(self) -> None:
        record = refactor_record()
        record["post_green_refactor"]["adds_new_scope"] = True
        with self.assertRaisesRegex(WorkerScopeError, "new scope"):
            validate_worker_scope(record)

    def test_concealed_refactor_is_forbidden(self) -> None:
        record = refactor_record()
        record["post_green_refactor"]["disclosed"] = False
        with self.assertRaisesRegex(WorkerScopeError, "disclosed"):
            validate_worker_scope(record)

    def test_refactor_must_renew_the_same_local_green_check(self) -> None:
        record = refactor_record()
        record["post_green_refactor"]["renewed_check"] = "python3 -m unittest tests.test_other_suite"
        with self.assertRaisesRegex(WorkerScopeError, "same local GREEN check"):
            validate_worker_scope(record)

    def test_refactor_requires_distinct_renewed_evidence(self) -> None:
        record = refactor_record()
        refactor = record["post_green_refactor"]
        refactor["renewed_evidence"] = refactor["local_green_evidence"]
        with self.assertRaisesRegex(WorkerScopeError, "distinct renewed evidence"):
            validate_worker_scope(record)

    def test_refactor_evidence_matching_only_by_whitespace_fails(self) -> None:
        record = refactor_record()
        refactor = record["post_green_refactor"]
        refactor["renewed_evidence"] = "  " + refactor["local_green_evidence"] + "  "
        with self.assertRaisesRegex(WorkerScopeError, "distinct renewed evidence"):
            validate_worker_scope(record)

    def test_generic_and_short_scope_claims_fail(self) -> None:
        for generic in ("yagni", "in scope", "works", "TBD", "n/a"):
            with self.subTest(generic=generic):
                record = scope_record()
                record["accepted_scope"] = generic
                record["items"][0]["description"] = generic
                with self.assertRaisesRegex(
                    WorkerScopeError, "generic claim|specific falsifiable"
                ):
                    validate_worker_scope(record)

    def test_generic_claim_punctuation_and_spacing_variants_fail(self) -> None:
        for variant in ("in scope.", "IN SCOPE!", "  yagni  ", "(works)", "tbd."):
            with self.subTest(variant=variant):
                record = scope_record()
                record["items"][0]["description"] = variant
                with self.assertRaisesRegex(WorkerScopeError, "generic claim|specific falsifiable"):
                    validate_worker_scope(record)

    def test_placeholder_scope_text_fails(self) -> None:
        record = scope_record()
        record["accepted_scope"] = "bind worker to <card authority> for this outcome"
        with self.assertRaisesRegex(WorkerScopeError, "must not carry a placeholder"):
            validate_worker_scope(record)

    def test_minimum_length_boundary(self) -> None:
        record = scope_record()
        record["items"][0]["description"] = "12345678"
        record["accepted_scope"] = "12345678"
        normalized = validate_worker_scope(record)
        self.assertEqual(normalized["items"][0]["description"], "12345678")
        record["items"][0]["description"] = "1234567"
        with self.assertRaisesRegex(WorkerScopeError, "specific falsifiable"):
            validate_worker_scope(record)

    def test_empty_items_prove_no_bounded_scope(self) -> None:
        record = scope_record()
        record["items"] = []
        with self.assertRaisesRegex(WorkerScopeError, "at least one"):
            validate_worker_scope(record)

    def test_missing_and_extra_keys_fail_closed(self) -> None:
        record = scope_record()
        del record["accepted_scope"]
        with self.assertRaisesRegex(WorkerScopeError, "invalid top-level keys"):
            validate_worker_scope(record)
        record = scope_record()
        record["telemetry"] = "worker-7"
        with self.assertRaisesRegex(WorkerScopeError, "invalid top-level keys|telemetry key"):
            validate_worker_scope(record)
        record = scope_record()
        del record["items"][0]["kind"]
        with self.assertRaisesRegex(WorkerScopeError, "invalid keys"):
            validate_worker_scope(record)

    def test_card_id_rejects_arbitrary_identifiers(self) -> None:
        for bad_id in ("M02", "", "-T13", "M02R-", "M02R_T13", "M02R T13", "card <id>"):
            with self.subTest(card_id=bad_id):
                record = scope_record()
                record["card_id"] = bad_id
                with self.assertRaisesRegex(WorkerScopeError, "concrete Card id"):
                    validate_worker_scope(record)

    def test_multi_dash_card_id_accepted(self) -> None:
        record = scope_record()
        record["card_id"] = "CUBC-M01-T01"
        normalized = validate_worker_scope(record)
        self.assertEqual(normalized["card_id"], "CUBC-M01-T01")

    def test_telemetry_identity_is_non_canonical(self) -> None:
        record = scope_record()
        record["worker_id"] = "worker-7"
        with self.assertRaisesRegex(WorkerScopeError, "telemetry key|invalid top-level keys"):
            validate_worker_scope(record)
        nested = scope_record()
        nested["items"][0]["session"] = "session-9"
        with self.assertRaisesRegex(WorkerScopeError, "telemetry key"):
            validate_worker_scope(nested)

    def test_absent_scope_is_legacy_compatible_not_retrospective(self) -> None:
        self.assertEqual(scope_status(None), "legacy_compatible")
        self.assertEqual(scope_status(None, expected_card_id="M02R-T13"), "legacy_compatible")

    def test_scope_card_binding_must_match_active_card(self) -> None:
        with self.assertRaisesRegex(WorkerScopeError, "does not match the active Card"):
            scope_status(scope_record(), expected_card_id="M02R-T12")

    def test_historical_card_result_shape_remains_valid(self) -> None:
        text = (
            "# Card Result\n"
            "- Card ID: M03-T02\n"
            "- Implementation subject: owner/repo@commit:" + ("a" * 40) + "\n"
            "- Evidence refs: implementation/workstreams/sample-workstream/evidence/build.md\n"
            "- Tests/readback summary: implementation and verification GREEN\n"
        )
        parsed = parse_card_result(text, "M03-T02", "sample-workstream")
        self.assertEqual(parsed["card_id"], "M03-T02")
        self.assertEqual(scope_status(None), "legacy_compatible")

    def test_valid_record_is_not_mutated_by_validation(self) -> None:
        record = refactor_record()
        snapshot = copy.deepcopy(record)
        validate_worker_scope(record)
        self.assertEqual(record, snapshot)


if __name__ == "__main__":
    unittest.main()
