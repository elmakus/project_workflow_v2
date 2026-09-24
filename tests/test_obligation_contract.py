from __future__ import annotations

import copy
import json
import unittest

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from pathlib import Path

from tools.obligation_contract import (
    ExecutionEnvelopeError,
    compile_execution_obligation,
    external_effect_retry_decision,
    freshness_fingerprint,
    git_blob_sha,
    reconcile_execution_result,
    serialize_obligation,
    serialize_result,
    validate_execution_obligation,
    validate_execution_result,
    verify_mutation_preconditions,
    verify_mutation_readback,
)
from tools.policy_kernel import PolicyKernel

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "policy" / "mechanical_policy.json"
OBLIGATION_SCHEMA = ROOT / "schemas" / "EXECUTION_OBLIGATION.schema.json"
RESULT_SCHEMA = ROOT / "schemas" / "EXECUTION_RESULT.schema.json"
OBLIGATION_GOLDEN = ROOT / "tests" / "fixtures" / "execution_contracts" / "obligation-v1.json"
RESULT_GOLDEN = ROOT / "tests" / "fixtures" / "execution_contracts" / "result-v1.json"

AUTHORITY_CONTENT = {
    "requirements/R.md": b"# Requirements\naccepted\n",
    "decisions/A.md": b"# Decision\naccepted\n",
}


class TypedExecutionContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.authority_refs = [
            self.ref("requirements/R.md", AUTHORITY_CONTENT["requirements/R.md"], "a" * 40),
            self.ref("decisions/A.md", AUTHORITY_CONTENT["decisions/A.md"], "a" * 40),
        ]
        self.subject = {
            "repository": "owner/project",
            "commit": "b" * 40,
            "path": "implementation/cards/M02-T01.md",
            "blob": "c" * 40,
        }

    def ref(self, path: str, content: bytes, commit: str) -> dict[str, str]:
        return {
            "repository": "owner/project",
            "commit": commit,
            "path": path,
            "blob": git_blob_sha(content),
        }

    def reader(self, ref: dict[str, str]) -> bytes:
        return AUTHORITY_CONTENT[ref["path"]]

    def obligation(self, *, inputs: dict | None = None) -> dict:
        return compile_execution_obligation(
            rule_id="PWV21-K011",
            role="execution_prep",
            subject=self.subject,
            authority_refs=self.authority_refs,
            authority_reader=self.reader,
            prerequisites=["M01-T01 DONE"],
            constraints=["canonical writes are coordinator-owned"],
            acceptance=["typed contract accepted"],
            tests=["contract suite GREEN"],
            evidence_requirements=["durable evidence"],
            determining_inputs=inputs or {"board_revision": 8, "card_id": "M02-T01"},
            mutation_preconditions=[{"path": "board.revision", "equals": 8}],
            mutation_postconditions=[{"path": "board.revision", "equals": 9}],
        )

    def result(self, obligation: dict) -> dict:
        return {
            "kind": "pwv2_execution_result",
            "schema_version": 1,
            "obligation_id": obligation["obligation_id"],
            "freshness_fingerprint": obligation["freshness"]["fingerprint"],
            "status": "success",
            "subject": self.subject,
            "changed_artifacts": [],
            "tests": [
                {"name": "contract suite", "status": "green", "evidence": "evidence/M02.md"}
            ],
            "evidence": ["evidence/M02.md"],
            "readback": [
                {
                    "target": "Task Board",
                    "status": "verified",
                    "observation": "exact postcondition present",
                }
            ],
            "blocker": None,
            "semantic_outcome": "M02 contract complete",
        }

    def test_obligation_is_deterministic_and_matches_golden_json(self) -> None:
        first = self.obligation()
        second = self.obligation()
        self.assertEqual(first, second)
        self.assertEqual(serialize_obligation(first), serialize_obligation(second))
        golden = json.loads(OBLIGATION_GOLDEN.read_text(encoding="utf-8"))
        self.assertEqual(first, golden)
        self.assertEqual(
            serialize_obligation(first),
            (json.dumps(golden, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8"),
        )

    def test_minimal_fingerprint_ignores_unselected_noise_but_tracks_material_input(self) -> None:
        canonical = {
            "board_revision": 8,
            "card_id": "M02-T01",
            "unrelated_file_blob": "1" * 40,
        }

        def selected() -> dict:
            return {
                "board_revision": canonical["board_revision"],
                "card_id": canonical["card_id"],
            }

        first = self.obligation(inputs=selected())
        canonical["unrelated_file_blob"] = "2" * 40
        noise_only = self.obligation(inputs=selected())
        self.assertEqual(first["freshness"]["fingerprint"], noise_only["freshness"]["fingerprint"])
        self.assertEqual(first["obligation_id"], noise_only["obligation_id"])

        canonical["board_revision"] = 9
        material_change = self.obligation(inputs=selected())
        self.assertNotEqual(first["freshness"]["fingerprint"], material_change["freshness"]["fingerprint"])
        self.assertNotEqual(first["obligation_id"], material_change["obligation_id"])

    def test_authority_resolution_requires_exact_refs_and_bundles_only_selected_sources(self) -> None:
        obligation = self.obligation()
        self.assertEqual(len(obligation["authority_bundle"]), 2)
        self.assertEqual(
            {source["path"] for source in obligation["authority_bundle"]},
            {"requirements/R.md", "decisions/A.md"},
        )

        inexact = copy.deepcopy(self.authority_refs)
        inexact[0]["commit"] = "main"
        with self.assertRaisesRegex(ExecutionEnvelopeError, "commit must be exact"):
            compile_execution_obligation(
                rule_id="PWV21-K011",
                role="execution_prep",
                subject=self.subject,
                authority_refs=inexact,
                authority_reader=self.reader,
                prerequisites=[],
                constraints=[],
                acceptance=[],
                tests=[],
                evidence_requirements=[],
                determining_inputs={"card_id": "M02-T01"},
                mutation_preconditions=[],
                mutation_postconditions=[],
            )

        invalid_subject = copy.deepcopy(self.subject)
        invalid_subject["repository"] = "owner/project/extra"
        with self.assertRaisesRegex(ExecutionEnvelopeError, "repository must be owner/name"):
            compile_execution_obligation(
                rule_id="PWV21-K011",
                role="execution_prep",
                subject=invalid_subject,
                authority_refs=self.authority_refs,
                authority_reader=self.reader,
                prerequisites=[],
                constraints=[],
                acceptance=[],
                tests=[],
                evidence_requirements=[],
                determining_inputs={"card_id": "M02-T01"},
                mutation_preconditions=[],
                mutation_postconditions=[],
            )

        wrong_blob = copy.deepcopy(self.authority_refs)
        wrong_blob[0]["blob"] = "d" * 40
        with self.assertRaisesRegex(ExecutionEnvelopeError, "blob mismatch"):
            compile_execution_obligation(
                rule_id="PWV21-K011",
                role="execution_prep",
                subject=self.subject,
                authority_refs=wrong_blob,
                authority_reader=self.reader,
                prerequisites=[],
                constraints=[],
                acceptance=[],
                tests=[],
                evidence_requirements=[],
                determining_inputs={"card_id": "M02-T01"},
                mutation_preconditions=[],
                mutation_postconditions=[],
            )

    def test_versions_and_telemetry_vocabulary_fail_closed(self) -> None:
        obligation = self.obligation()
        changed = copy.deepcopy(obligation)
        changed["schema_version"] = 2
        with self.assertRaisesRegex(ExecutionEnvelopeError, "unsupported schema_version"):
            validate_execution_obligation(changed)

        with self.assertRaisesRegex(ExecutionEnvelopeError, "telemetry key"):
            self.obligation(inputs={"card_id": "M02-T01", "worker_id": "worker-7"})

        result = self.result(obligation)
        result["schema_version"] = 2
        with self.assertRaisesRegex(ExecutionEnvelopeError, "unsupported schema_version"):
            validate_execution_result(result)

        result = self.result(obligation)
        result["session_id"] = "session-7"
        with self.assertRaisesRegex(ExecutionEnvelopeError, "telemetry key"):
            validate_execution_result(result)

    def test_obligation_identity_and_freshness_surface_reject_drift(self) -> None:
        obligation = self.obligation()

        changed = copy.deepcopy(obligation)
        changed["role"] = "review"
        with self.assertRaisesRegex(ExecutionEnvelopeError, "deterministic identity drift"):
            validate_execution_obligation(changed)

        drift_cases = {
            "prerequisites": ["different dependency"],
            "constraints": ["different constraint"],
            "completion": {
                "acceptance": ["different acceptance"],
                "tests": ["contract suite GREEN"],
                "evidence": ["durable evidence"],
            },
            "mutation": {
                "preconditions": [{"path": "board.revision", "equals": 8}],
                "postconditions": [{"path": "board.revision", "equals": 10}],
            },
        }
        for field, replacement in drift_cases.items():
            with self.subTest(field=field):
                changed = copy.deepcopy(obligation)
                changed[field] = replacement
                with self.assertRaisesRegex(ExecutionEnvelopeError, f"{field}/freshness drift"):
                    validate_execution_obligation(changed)

    def test_result_binding_staleness_and_safe_reuse_are_explicit(self) -> None:
        obligation = self.obligation()
        result = self.result(obligation)
        validate_execution_result(result)
        self.assertEqual(
            reconcile_execution_result(
                result,
                obligation,
                current_freshness_material=obligation["freshness"]["material"],
            ),
            "accept",
        )

        stale_material = copy.deepcopy(obligation["freshness"]["material"])
        stale_material["inputs"]["board_revision"] = 9
        self.assertEqual(
            reconcile_execution_result(
                result,
                obligation,
                current_freshness_material=stale_material,
            ),
            "reexecute",
        )
        current = freshness_fingerprint(stale_material)
        for action in ("reuse", "rebase", "reconcile"):
            proof = {
                "prior_fingerprint": obligation["freshness"]["fingerprint"],
                "current_fingerprint": current,
                "action": action,
                "safety_proven": True,
                "basis": "The stale delta was bounded and independently proven safe for this resolution.",
            }
            self.assertEqual(
                reconcile_execution_result(
                    result,
                    obligation,
                    current_freshness_material=stale_material,
                    stale_resolution=proof,
                ),
                action,
            )

        unsafe = {
            "prior_fingerprint": obligation["freshness"]["fingerprint"],
            "current_fingerprint": current,
            "action": "reuse",
            "safety_proven": False,
            "basis": "No positive safety proof.",
        }
        with self.assertRaisesRegex(ExecutionEnvelopeError, "does not establish safety"):
            reconcile_execution_result(
                result,
                obligation,
                current_freshness_material=stale_material,
                stale_resolution=unsafe,
            )

        mismatched_subject = self.result(obligation)
        mismatched_subject["subject"] = {
            "repository": "owner/project",
            "commit": "d" * 40,
            "path": "implementation/cards/OTHER.md",
            "blob": "e" * 40,
        }
        with self.assertRaisesRegex(ExecutionEnvelopeError, "subject binding mismatch"):
            reconcile_execution_result(
                mismatched_subject,
                obligation,
                current_freshness_material=obligation["freshness"]["material"],
            )

        mismatched = self.result(obligation)
        mismatched["obligation_id"] = "sha256:" + ("0" * 64)
        with self.assertRaisesRegex(ExecutionEnvelopeError, "obligation binding mismatch"):
            reconcile_execution_result(
                mismatched,
                obligation,
                current_freshness_material=obligation["freshness"]["material"],
            )

    def test_result_matches_golden_and_is_canonical(self) -> None:
        obligation = self.obligation()
        result = self.result(obligation)
        golden = json.loads(RESULT_GOLDEN.read_text(encoding="utf-8"))
        self.assertEqual(result, golden)
        self.assertEqual(
            serialize_result(result),
            (json.dumps(golden, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8"),
        )

    def test_json_schemas_validate_golden_and_reject_invalid_matrix(self) -> None:
        obligation_schema = json.loads(OBLIGATION_SCHEMA.read_text(encoding="utf-8"))
        result_schema = json.loads(RESULT_SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(obligation_schema)
        Draft202012Validator.check_schema(result_schema)
        obligation_validator = Draft202012Validator(obligation_schema)
        result_validator = Draft202012Validator(result_schema)

        obligation = json.loads(OBLIGATION_GOLDEN.read_text(encoding="utf-8"))
        result = json.loads(RESULT_GOLDEN.read_text(encoding="utf-8"))
        obligation_validator.validate(obligation)
        result_validator.validate(result)

        invalid_obligations: list[tuple[str, dict]] = []

        candidate = copy.deepcopy(obligation)
        candidate["schema_version"] = 2
        invalid_obligations.append(("breaking version", candidate))

        candidate = copy.deepcopy(obligation)
        candidate["subject"]["path"] = "../outside.md"
        invalid_obligations.append(("parent path", candidate))

        candidate = copy.deepcopy(obligation)
        candidate["freshness"]["material"]["inputs"] = {
            "card": {"provider": "must-not-be-canonical"}
        }
        invalid_obligations.append(("nested telemetry input", candidate))

        candidate = copy.deepcopy(obligation)
        candidate["mutation"]["preconditions"][0]["equals"] = {
            "nested": {"session_id": "must-not-be-canonical"}
        }
        candidate["freshness"]["material"]["mutation"] = copy.deepcopy(candidate["mutation"])
        invalid_obligations.append(("nested telemetry mutation", candidate))

        candidate = copy.deepcopy(obligation)
        candidate["role"] = "   "
        invalid_obligations.append(("blank role", candidate))

        for label, candidate in invalid_obligations:
            with self.subTest(obligation_case=label), self.assertRaises(JsonSchemaValidationError):
                obligation_validator.validate(candidate)

        invalid_results: list[tuple[str, dict]] = []

        candidate = copy.deepcopy(result)
        candidate["schema_version"] = 2
        invalid_results.append(("breaking version", candidate))

        candidate = copy.deepcopy(result)
        candidate["subject"]["path"] = "/absolute/result.md"
        invalid_results.append(("absolute path", candidate))

        candidate = copy.deepcopy(result)
        candidate["status"] = "blocked"
        candidate["blocker"] = None
        invalid_results.append(("blocked without blocker", candidate))

        candidate = copy.deepcopy(result)
        candidate["semantic_outcome"] = "   "
        invalid_results.append(("blank semantic outcome", candidate))

        for label, candidate in invalid_results:
            with self.subTest(result_case=label), self.assertRaises(JsonSchemaValidationError):
                result_validator.validate(candidate)

    def test_mutation_is_governed_by_preconditions_postconditions_and_readback(self) -> None:
        obligation = self.obligation()
        self.assertEqual(
            obligation["mutation"],
            {
                "preconditions": [{"path": "board.revision", "equals": 8}],
                "postconditions": [{"path": "board.revision", "equals": 9}],
            },
        )
        self.assertEqual(
            verify_mutation_preconditions(obligation, {"board": {"revision": 8}}),
            "verified",
        )
        self.assertEqual(
            verify_mutation_readback(obligation, {"board": {"revision": 9}}),
            "verified",
        )
        with self.assertRaisesRegex(ExecutionEnvelopeError, "condition failed"):
            verify_mutation_readback(obligation, {"board": {"revision": 8}})

    def test_unknown_external_effect_never_authorizes_blind_retry(self) -> None:
        self.assertEqual(
            external_effect_retry_decision(readback_state="pending", observation="unknown"),
            "readback_exact_target",
        )
        with self.assertRaisesRegex(ExecutionEnvelopeError, "fail closed without retry"):
            external_effect_retry_decision(readback_state="uncertain", observation="unknown")
        self.assertEqual(
            external_effect_retry_decision(readback_state="verified", observation="no_effect"),
            "retry_allowed",
        )
        self.assertEqual(
            external_effect_retry_decision(readback_state="verified", observation="expected_effect"),
            "reconcile_without_retry",
        )

    def test_schemas_are_closed_and_exclude_runtime_telemetry_fields(self) -> None:
        forbidden = {
            "provider", "model", "model_id", "worker", "worker_id", "session", "session_id",
            "retry", "retries", "worktree", "paseo", "runtime", "invocation", "scheduler",
        }

        def property_names(value: object) -> set[str]:
            found: set[str] = set()
            if isinstance(value, dict):
                properties = value.get("properties")
                if isinstance(properties, dict):
                    found.update(properties)
                for child in value.values():
                    found.update(property_names(child))
            elif isinstance(value, list):
                for child in value:
                    found.update(property_names(child))
            return found

        for path in (OBLIGATION_SCHEMA, RESULT_SCHEMA):
            schema = json.loads(path.read_text(encoding="utf-8"))
            self.assertFalse(schema["additionalProperties"])
            self.assertTrue(property_names(schema).isdisjoint(forbidden))

        def object_keys(value: object) -> set[str]:
            found: set[str] = set()
            if isinstance(value, dict):
                found.update(str(key).lower() for key in value)
                for child in value.values():
                    found.update(object_keys(child))
            elif isinstance(value, list):
                for child in value:
                    found.update(object_keys(child))
            return found

        for path in (OBLIGATION_GOLDEN, RESULT_GOLDEN):
            fixture = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(object_keys(fixture).isdisjoint(forbidden))

    def test_policy_kernel_m02_seams_bind_registered_rule_to_typed_contract(self) -> None:
        kernel = PolicyKernel.from_path(REGISTRY)
        obligation = kernel.compile_obligations(
            "PWV21-K011",
            role="execution_prep",
            subject=self.subject,
            authority_refs=self.authority_refs,
            authority_reader=self.reader,
            prerequisites=["M01-T01 DONE"],
            constraints=["canonical writes are coordinator-owned"],
            acceptance=["typed contract accepted"],
            tests=["contract suite GREEN"],
            evidence_requirements=["durable evidence"],
            determining_inputs={"board_revision": 8, "card_id": "M02-T01"},
            mutation_preconditions=[{"path": "board.revision", "equals": 8}],
            mutation_postconditions=[{"path": "board.revision", "equals": 9}],
        )
        result = self.result(obligation)
        kernel.validate_results(result)
        self.assertEqual(
            kernel.reconcile(
                result,
                obligation,
                current_freshness_material=obligation["freshness"]["material"],
            ),
            "accept",
        )
        with self.assertRaisesRegex(Exception, "unknown mechanical rule"):
            kernel.compile_obligations("PWV21-K999", role="execution_prep")


if __name__ == "__main__":
    unittest.main()
