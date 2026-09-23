from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.policy_kernel import (
    DEFAULT_PREDICATES,
    DeferredKernelCapabilityError,
    KernelContractError,
    MechanicalDecision,
    PolicyKernel,
)
from tools.router import Reads, policy_result

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "policy" / "mechanical_policy.json"
PROJECTION = ROOT / "workflow" / "POLICY_KERNEL.md"
SCHEMA = ROOT / "schemas" / "POLICY_REGISTRY.schema.json"


class PolicyKernelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel = PolicyKernel.from_path(REGISTRY)
        self.payload = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_registry_version_vocabulary_and_rule_order_are_valid(self) -> None:
        self.kernel.validate()
        self.assertEqual(self.payload["registry_version"], 1)
        self.assertEqual(self.payload["schema_version"], 1)
        self.assertEqual(len(self.kernel.rule_ids), 12)
        self.assertEqual(self.kernel.rule_ids[0], "PWV21-K001")
        self.assertEqual(self.kernel.rule_ids[-1], "PWV21-K012")
        self.assertEqual(
            {rule["predicate"] for rule in self.payload["rules"]},
            set(DEFAULT_PREDICATES),
        )

    def test_unsupported_versions_and_arbitrary_expression_fail_closed(self) -> None:
        candidate = copy.deepcopy(self.payload)
        candidate["registry_version"] = 2
        with self.assertRaisesRegex(KernelContractError, "unsupported registry_version"):
            PolicyKernel.from_mapping(candidate)

        candidate = copy.deepcopy(self.payload)
        candidate["schema_version"] = 2
        with self.assertRaisesRegex(KernelContractError, "unsupported schema_version"):
            PolicyKernel.from_mapping(candidate)

        candidate = copy.deepcopy(self.payload)
        candidate["rules"][0]["expression"] = "tracker.state == 'ambiguous'"
        with self.assertRaisesRegex(KernelContractError, "keys mismatch"):
            PolicyKernel.from_mapping(candidate)

        candidate = copy.deepcopy(self.payload)
        candidate["rules"][0]["predicate"] = "eval_expression"
        with self.assertRaisesRegex(KernelContractError, "unknown predicate"):
            PolicyKernel.from_mapping(candidate)

    def test_registry_and_implementation_vocabulary_drift_fails_closed(self) -> None:
        implementations = dict(DEFAULT_PREDICATES)
        implementations["unregistered_predicate"] = lambda inputs: True
        with self.assertRaisesRegex(KernelContractError, "vocabulary mismatch"):
            PolicyKernel.from_mapping(self.payload, implementations=implementations)

    def test_every_registered_rule_is_wired_into_the_production_router(self) -> None:
        router = (ROOT / "tools" / "router.py").read_text(encoding="utf-8")
        positions = []
        for rule_id in self.kernel.rule_ids:
            needle = f'kernel.route("{rule_id}"'
            self.assertEqual(router.count(needle), 1)
            positions.append(router.index(needle))
        self.assertEqual(positions, sorted(positions))

    def test_policy_result_consumes_registered_outcome_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            reads = Reads(Path(temp), Path(temp))
            routed = policy_result(
                reads,
                MechanicalDecision(
                    rule_id="PWV21-K999",
                    disposition="route",
                    obligation="registry_owned_obligation",
                    owner_module="workflow/REGISTRY_OWNER.md",
                ),
                "registered outcome adapter probe",
                subject="subject-1",
            )
        self.assertEqual(routed.disposition, "route")
        self.assertEqual(routed.obligation, "registry_owned_obligation")
        self.assertEqual(routed.owner_module, "workflow/REGISTRY_OWNER.md")
        self.assertEqual(routed.subject, "subject-1")

    def test_projection_is_exact_registry_derived_contract(self) -> None:
        self.kernel.verify_projection(PROJECTION)
        rendered = self.kernel.render_projection()
        self.assertEqual(rendered, PROJECTION.read_text(encoding="utf-8"))
        for rule_id in self.kernel.rule_ids:
            self.assertIn(f"## {rule_id} —", rendered)

        with tempfile.TemporaryDirectory() as temp:
            drifted = Path(temp) / "POLICY_KERNEL.md"
            drifted.write_text(rendered.replace("premium_A", "premium_X", 1), encoding="utf-8")
            with self.assertRaisesRegex(KernelContractError, "projection drift"):
                self.kernel.verify_projection(drifted)

    def test_schema_is_closed_and_has_no_expression_language(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertFalse(schema["additionalProperties"])
        rule_schema = schema["properties"]["rules"]["items"]
        self.assertFalse(rule_schema["additionalProperties"])
        self.assertNotIn("expression", rule_schema["properties"])
        self.assertNotIn("script", rule_schema["properties"])
        self.assertNotIn("when", rule_schema["properties"])

    def test_route_uses_only_declared_inputs_and_returns_registered_outcome(self) -> None:
        state = {
            "planning": {"state": "approved", "premium_c": "due", "unrelated": "ignored"},
            "runtime": {"provider": "must-not-be-read"},
        }
        first = self.kernel.route("PWV21-K008", state)
        second = self.kernel.route("PWV21-K008", state)
        self.assertEqual(first, second)
        self.assertEqual(
            first,
            MechanicalDecision(
                rule_id="PWV21-K008",
                disposition="stop",
                obligation="premium_C",
                owner_module="workflow/PLANNING.md",
            ),
        )
        self.assertIsNone(
            self.kernel.route(
                "PWV21-K008",
                {"planning": {"state": "approved", "premium_c": "satisfied"}},
            )
        )
        with self.assertRaisesRegex(KernelContractError, "missing canonical input"):
            self.kernel.route("PWV21-K008", {"planning": {"state": "approved"}})

    def test_board_predicates_are_mechanical_and_deterministic(self) -> None:
        self.assertTrue(
            self.kernel.matches("PWV21-K011", {"board": {"cards": [{"status": "ready"}]}})
        )
        self.assertTrue(
            self.kernel.matches(
                "PWV21-K012",
                {"board": {"cards": [{"status": "done"}, {"status": "done"}]}},
            )
        )
        self.assertFalse(self.kernel.matches("PWV21-K012", {"board": {"cards": []}}))
        with self.assertRaisesRegex(KernelContractError, "string status"):
            self.kernel.matches("PWV21-K011", {"board": {"cards": [{}]}})

    def test_kernel_is_read_only_over_registry_and_projection(self) -> None:
        registry_before = REGISTRY.read_bytes()
        projection_before = PROJECTION.read_bytes()
        for _ in range(3):
            self.kernel.matches("PWV21-K002", {"definition": {"premium_a": "due"}})
            self.kernel.matches("PWV21-K010", {"brainstorm": {"state": "active"}})
        self.assertEqual(REGISTRY.read_bytes(), registry_before)
        self.assertEqual(PROJECTION.read_bytes(), projection_before)

    def test_m02_owned_seams_are_declared_but_not_implemented_early(self) -> None:
        for method in (
            self.kernel.compile_obligations,
            self.kernel.validate_results,
            self.kernel.reconcile,
        ):
            with self.subTest(method=method.__name__), self.assertRaises(DeferredKernelCapabilityError):
                method({})


if __name__ == "__main__":
    unittest.main()
