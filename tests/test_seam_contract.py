from __future__ import annotations

import copy
import shutil
import tempfile
import tomllib
import unittest
from pathlib import Path

from tools.router import classify_jit_refinement, select_route
from tools.seam_contract import (
    QUALIFYING_RATIONALE_CLASSES,
    SeamContractError,
    classify_seam_jit_decision,
    validate_preferred_deviation_rationale,
    validate_seam_decisions,
    validate_seam_declarations,
)
from tools.state_contract import (
    ValidationError,
    read_toml,
    validate_board,
    validate_planning,
)
from tools.topology_contract import compute_proposal_digest

ROOT = Path(__file__).resolve().parents[1]
VALID = ROOT / "tests" / "fixtures" / "state" / "valid"
ROUTER_FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
ROUTER_MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
ROUTER_BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
ROUTER_PLANNING = "implementation/workstreams/sample-workstream/PLANNING.toml"


def _seams() -> list[dict[str, str]]:
    return [
        {"id": "BOOT-A", "class": "required_seam",
         "intent": "Review discovery/convergence/observation closure stays a standalone outcome."},
        {"id": "helper-less-derivation", "class": "preferred_seam",
         "intent": "Helper-less derivation is its own outcome unless coupling evidence says otherwise."},
        {"id": "example-split", "class": "illustrative",
         "intent": "Non-binding example of how Cards could split; JIT may ignore it."},
    ]


def _planning_record() -> dict:
    return {
        "workstream_id": "sample-workstream",
        "cycle": 1,
        "entry_subject": "definition:R1|planning-cycle:1",
        "revision": "P1",
        "state": "draft",
        "planner_audit": "pending",
        "plan_path": "planning/MASTER_PLAN.md",
        "review_mode": "independent",
        "review_exemption_basis": "",
        "review_exemption_base_subject": "",
        "premium_a": "satisfied",
        "premium_a_subject": "definition:R1|planning-cycle:1",
        "premium_b": "not_due",
        "premium_b_subject": "",
        "premium_c": "not_due",
        "premium_c_subject": "",
        "subject": {"repository": "", "commit": "", "path": "", "blob": ""},
    }


class SeamIntentTests(unittest.TestCase):
    def test_all_three_classes_are_expressible_without_card_ids(self) -> None:
        records = validate_seam_declarations(_seams())
        self.assertEqual([record["class"] for record in records],
                         ["required_seam", "preferred_seam", "illustrative"])
        for record in records:
            self.assertNotIn("card_id", record)
            self.assertNotIn("card_ids", record)

        planning = _planning_record()
        planning["seams"] = _seams()
        validate_planning(planning, "sample-workstream")

    def test_seam_declarations_reject_unknown_class_and_empty_intent(self) -> None:
        bad_class = [{"id": "S1", "class": "suggested_seam", "intent": "vague boundary"}]
        with self.assertRaisesRegex(SeamContractError, "unknown seam class"):
            validate_seam_declarations(bad_class)

        empty_intent = [{"id": "S1", "class": "required_seam", "intent": "  "}]
        with self.assertRaisesRegex(SeamContractError, "durable non-empty"):
            validate_seam_declarations(empty_intent)

        empty_id = [{"id": "", "class": "required_seam", "intent": "boundary"}]
        with self.assertRaisesRegex(SeamContractError, "non-empty string"):
            validate_seam_declarations(empty_id)

        duplicate = [
            {"id": "S1", "class": "required_seam", "intent": "first"},
            {"id": "S1", "class": "preferred_seam", "intent": "second"},
        ]
        with self.assertRaisesRegex(SeamContractError, "duplicate seam id"):
            validate_seam_declarations(duplicate)

        with self.assertRaisesRegex(SeamContractError, "must be an array"):
            validate_seam_declarations({"id": "S1"})  # type: ignore[arg-type]

    def test_planning_without_seams_remains_valid_history(self) -> None:
        validate_planning(_planning_record(), "sample-workstream")

        planning = _planning_record()
        planning["seams"] = [{"id": "S1", "class": "typo_seam", "intent": "boundary"}]
        with self.assertRaisesRegex(ValidationError, "unknown seam class"):
            validate_planning(planning, "sample-workstream")


class RequiredSeamTests(unittest.TestCase):
    def test_required_seam_merge_is_rejected_and_routed_to_planning(self) -> None:
        with self.assertRaisesRegex(SeamContractError, "must not merge a required_seam"):
            classify_seam_jit_decision(
                seam_id="BOOT-A", seam_class="required_seam", decision="merged",
            )
        with self.assertRaisesRegex(SeamContractError, "Strategic Planning"):
            validate_seam_decisions(
                [{"seam_id": "BOOT-A", "decision": "merged",
                  "rationale_class": "coupling", "rationale": "Shared helper."}],
                _seams(),
            )
        owner, _ = classify_jit_refinement("required_seam_challenge")
        self.assertEqual(owner, "planning")

    def test_required_seam_preserved_and_split_within_stay_in_execution_prep(self) -> None:
        for decision in ("preserved", "split"):
            with self.subTest(decision=decision):
                owner = classify_seam_jit_decision(
                    seam_id="BOOT-A", seam_class="required_seam", decision=decision,
                )
                self.assertEqual(owner, "execution_prep")
        owners = validate_seam_decisions(
            [
                {"seam_id": "BOOT-A", "decision": "split"},
                {"seam_id": "helper-less-derivation", "decision": "preserved"},
                {"seam_id": "example-split", "decision": "preserved"},
            ],
            _seams(),
        )
        self.assertEqual(
            owners,
            {
                "BOOT-A": "execution_prep",
                "helper-less-derivation": "execution_prep",
                "example-split": "execution_prep",
            },
        )

    def test_illustrative_merge_needs_no_rationale(self) -> None:
        owner = classify_seam_jit_decision(
            seam_id="example-split", seam_class="illustrative", decision="merged",
        )
        self.assertEqual(owner, "execution_prep")


class PreferredSeamTests(unittest.TestCase):
    def test_preferred_seam_survives_jit_by_default(self) -> None:
        owner = classify_seam_jit_decision(
            seam_id="helper-less-derivation", seam_class="preferred_seam",
            decision="preserved",
        )
        self.assertEqual(owner, "execution_prep")
        owners = validate_seam_decisions(
            [
                {"seam_id": "BOOT-A", "decision": "preserved"},
                {"seam_id": "helper-less-derivation", "decision": "preserved"},
                {"seam_id": "example-split", "decision": "preserved"},
            ],
            _seams(),
        )
        self.assertEqual(
            owners,
            {
                "BOOT-A": "execution_prep",
                "helper-less-derivation": "execution_prep",
                "example-split": "execution_prep",
            },
        )

    def test_preferred_deviation_accepts_each_qualifying_class(self) -> None:
        self.assertEqual(
            QUALIFYING_RATIONALE_CLASSES,
            {"coupling", "atomicity", "invalid_intermediate_state",
             "non_separable_acceptance", "new_predecessor_evidence"},
        )
        for rationale_class in sorted(QUALIFYING_RATIONALE_CLASSES):
            for decision in ("merged", "split"):
                with self.subTest(rationale_class=rationale_class, decision=decision):
                    owner = classify_seam_jit_decision(
                        seam_id="helper-less-derivation", seam_class="preferred_seam",
                        decision=decision, rationale_class=rationale_class,
                        rationale=f"Concrete {rationale_class} evidence in predecessor result.",
                    )
                    self.assertEqual(owner, "execution_prep")
        owner, _ = classify_jit_refinement("preferred_seam_deviation")
        self.assertEqual(owner, "execution_prep")

    def test_preferred_deviation_rejects_generic_and_empty_rationale(self) -> None:
        for rejected in ("convenience", "same_milestone", "same-milestone",
                         "fewer_cards", "fewer-cards"):
            with self.subTest(rationale_class=rejected):
                with self.assertRaisesRegex(SeamContractError, "insufficient"):
                    validate_preferred_deviation_rationale(
                        rationale_class=rejected,
                        rationale="Same milestone, so merge for convenience.",
                        label="seam 'helper-less-derivation'",
                    )
                with self.assertRaisesRegex(SeamContractError, "insufficient"):
                    classify_seam_jit_decision(
                        seam_id="helper-less-derivation", seam_class="preferred_seam",
                        decision="merged", rationale_class=rejected,
                        rationale="Same milestone, so merge for convenience.",
                    )

        with self.assertRaisesRegex(SeamContractError, "unknown rationale class"):
            classify_seam_jit_decision(
                seam_id="helper-less-derivation", seam_class="preferred_seam",
                decision="merged", rationale_class="faster_reviews",
                rationale="Merging would speed up reviews.",
            )

        with self.assertRaisesRegex(SeamContractError, "durable non-empty rationale"):
            classify_seam_jit_decision(
                seam_id="helper-less-derivation", seam_class="preferred_seam",
                decision="split", rationale_class="coupling", rationale="   ",
            )

        with self.assertRaisesRegex(SeamContractError, "unknown rationale class"):
            classify_seam_jit_decision(
                seam_id="helper-less-derivation", seam_class="preferred_seam",
                decision="merged",
            )

    def test_non_deviation_decisions_must_not_claim_rationale(self) -> None:
        with self.assertRaisesRegex(SeamContractError, "must not claim deviation rationale"):
            classify_seam_jit_decision(
                seam_id="helper-less-derivation", seam_class="preferred_seam",
                decision="preserved", rationale_class="coupling",
                rationale="Preserved because of coupling.",
            )


class SeamBoardBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workstream = read_toml(VALID / "WORKSTREAM.toml")

    def test_board_seam_fidelity_binds_declared_planning_seams(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        validate_board(board, self.workstream)

        preserved = copy.deepcopy(board)
        preserved["seam_decisions"] = [
            {"seam_id": "BOOT-A", "decision": "preserved"},
            {"seam_id": "helper-less-derivation", "decision": "merged",
             "rationale_class": "atomicity",
             "rationale": "Single atomic migration cannot land across two Cards."},
            {"seam_id": "example-split", "decision": "split"},
        ]
        preserved["topology_audits"] = [{
            "card_id": "M01-T02",
            "risk": "risky",
            "triggers": ["preferred_seam_merge"],
            "risk_basis": "Merges preferred seam helper-less-derivation with atomicity rationale.",
            "review_scope": "card_local",
            "atomicity_rationale_class": "",
            "atomicity_rationale": "",
            "challenge": {
                "verdict": "green",
                "evaluated": ["boundary_fidelity", "falsifiability", "review_separation"],
                "scope_statement": "Merged preferred seam boundary checked for fidelity, falsifiability and review split.",
                "independent": True,
                "independence_basis": "Challenger did not author the Execution Prep topology proposal.",
                "fresh": True,
                "challenge_basis": "Fresh review of the merged boundary against seam intent and sizing outcomes.",
                "proposal_digest": "sha256:" + "0" * 64,
                "card_contract_digest": "sha256:" + "1" * 64,
            },
        }]
        sizing = next(audit for audit in preserved["sizing_audits"] if audit["card_id"] == "M01-T02")
        preserved["topology_audits"][0]["challenge"]["proposal_digest"] = compute_proposal_digest(
            card_id="M01-T02",
            sizing_audit=sizing,
            topology_audit=preserved["topology_audits"][0],
            seam_decisions=preserved["seam_decisions"],
            planning_seams=_seams(),
        )
        validate_board(preserved, self.workstream, planning_seams=_seams())

        merged_required = copy.deepcopy(board)
        merged_required["seam_decisions"] = [
            {"seam_id": "BOOT-A", "decision": "merged",
             "rationale_class": "coupling", "rationale": "Shared helper module."},
        ]
        with self.assertRaisesRegex(ValidationError, "must not merge a required_seam"):
            validate_board(merged_required, self.workstream, planning_seams=_seams())

        convenience = copy.deepcopy(board)
        convenience["seam_decisions"] = [
            {"seam_id": "helper-less-derivation", "decision": "merged",
             "rationale_class": "convenience", "rationale": "Easier to review one Card."},
        ]
        with self.assertRaisesRegex(ValidationError, "insufficient"):
            validate_board(convenience, self.workstream, planning_seams=_seams())

    def test_board_seam_decisions_fail_closed_without_declared_seams(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["seam_decisions"] = [{"seam_id": "BOOT-A", "decision": "preserved"}]
        with self.assertRaisesRegex(ValidationError, "require accepted Planning seams"):
            validate_board(board, self.workstream)

        unknown = copy.deepcopy(board)
        with self.assertRaisesRegex(ValidationError, "unknown seam_id"):
            validate_board(unknown, self.workstream, planning_seams=[
                {"id": "other", "class": "required_seam", "intent": "Another boundary."},
            ])

        duplicate = read_toml(VALID / "TASK_BOARD.toml")
        duplicate["seam_decisions"] = [
            {"seam_id": "BOOT-A", "decision": "preserved"},
            {"seam_id": "BOOT-A", "decision": "split"},
        ]
        with self.assertRaisesRegex(ValidationError, "duplicate decision"):
            validate_board(duplicate, self.workstream, planning_seams=_seams())

    def test_board_missing_declared_seam_decision_is_a_bypass(self) -> None:
        partial = read_toml(VALID / "TASK_BOARD.toml")
        partial["seam_decisions"] = [
            {"seam_id": "helper-less-derivation", "decision": "preserved"},
            {"seam_id": "example-split", "decision": "preserved"},
        ]
        with self.assertRaisesRegex(
            ValidationError, "missing durable JIT decision for declared seam 'BOOT-A'"
        ):
            validate_board(partial, self.workstream, planning_seams=_seams())

        omitted = read_toml(VALID / "TASK_BOARD.toml")
        with self.assertRaisesRegex(
            ValidationError, "require durable per-seam JIT decisions"
        ):
            validate_board(omitted, self.workstream, planning_seams=_seams())


class SeamRouterPathTests(unittest.TestCase):
    def copy_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(ROUTER_FIXTURE, project)
        return temp, project

    def install_planning(self, project: Path, *, seams: str = "") -> None:
        manifest = project / ROUTER_MANIFEST
        manifest.write_text(
            manifest.read_text()
            + '\n[planning]\nclass = "planning"\n'
            f'path = "{ROUTER_PLANNING}"\n'
        )
        (project / ROUTER_PLANNING).write_text(
            'workstream_id = "sample-workstream"\n'
            'cycle = 1\n'
            'entry_subject = "definition:R1|planning-cycle:1"\n'
            'revision = "P1"\n'
            'state = "draft"\n'
            'planner_audit = "pending"\n'
            'plan_path = "planning/MASTER_PLAN.md"\n'
            'review_mode = "independent"\n'
            'review_exemption_basis = ""\n'
            'review_exemption_base_subject = ""\n'
            'premium_a = "satisfied"\n'
            'premium_a_subject = "definition:R1|planning-cycle:1"\n'
            'premium_b = "not_due"\n'
            'premium_b_subject = ""\n'
            'premium_c = "not_due"\n'
            'premium_c_subject = ""\n'
            '[subject]\n'
            'repository = ""\n'
            'commit = ""\n'
            'path = ""\n'
            'blob = ""\n'
            f"{seams}"
        )

    def planning_seams(self) -> str:
        return (
            '[[seams]]\n'
            'id = "BOOT-A"\n'
            'class = "required_seam"\n'
            'intent = "Review discovery/convergence/observation closure stays standalone."\n'
            '[[seams]]\n'
            'id = "helper-less-derivation"\n'
            'class = "preferred_seam"\n'
            'intent = "Helper-less derivation is its own outcome unless coupling evidence says otherwise."\n'
            '[[seams]]\n'
            'id = "example-split"\n'
            'class = "illustrative"\n'
            'intent = "Non-binding example split; JIT may ignore it."\n'
        )

    def install_decisions(self, project: Path, decisions: str) -> None:
        board = project / ROUTER_BOARD
        board.write_text(board.read_text() + decisions)

    def test_router_rejects_required_seam_merge_then_routes_challenge_to_planning(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_planning(project, seams=self.planning_seams())
            self.install_decisions(project, (
                '[[seam_decisions]]\n'
                'seam_id = "BOOT-A"\n'
                'decision = "merged"\n'
                'rationale_class = "coupling"\n'
                'rationale = "Shared helper module."\n'
                '[[seam_decisions]]\n'
                'seam_id = "helper-less-derivation"\n'
                'decision = "preserved"\n'
                '[[seam_decisions]]\n'
                'seam_id = "example-split"\n'
                'decision = "preserved"\n'
            ))
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation), ("recovery", "recovery_boundary")
            )
            self.assertIn("must not merge a required_seam", routed.reason)
            self.assertIn(f"project:{ROUTER_PLANNING}", routed.read_set)

            owner, reason = classify_jit_refinement("required_seam_challenge")
            self.assertEqual(owner, "planning")
            self.assertIn("Strategic Planning", reason)
        finally:
            temp.cleanup()

    def test_router_applies_preferred_deviation_rules_on_real_board(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_planning(project, seams=self.planning_seams())
            board = project / ROUTER_BOARD
            base = board.read_text()
            board.write_text(base + (
                '[[seam_decisions]]\n'
                'seam_id = "BOOT-A"\n'
                'decision = "preserved"\n'
                '[[seam_decisions]]\n'
                'seam_id = "helper-less-derivation"\n'
                'decision = "merged"\n'
                'rationale_class = "convenience"\n'
                'rationale = "Easier to review one Card."\n'
                '[[seam_decisions]]\n'
                'seam_id = "example-split"\n'
                'decision = "preserved"\n'
            ))
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation), ("recovery", "recovery_boundary")
            )
            self.assertIn("insufficient", routed.reason)

            risky_base = base.replace(
                '# topology audit for M01-T04: simple single-outcome scope needs no fresh challenge.\n'
                '[[topology_audits]]\n'
                'card_id = "M01-T04"\n'
                'risk = "simple"\n'
                'triggers = []\n'
                'risk_basis = "Single coherent outcome in one invariant family with no seam merge, milestone absorption or material deviation."\n'
                'review_scope = "card_local"\n'
                'atomicity_rationale_class = ""\n'
                'atomicity_rationale = ""\n',
                '# topology audit for M01-T04: preferred merge challenged before launch.\n'
                '[[topology_audits]]\n'
                'card_id = "M01-T04"\n'
                'risk = "risky"\n'
                'triggers = ["preferred_seam_merge"]\n'
                'risk_basis = "Merges preferred seam helper-less-derivation with atomicity rationale."\n'
                'review_scope = "card_local"\n'
                'atomicity_rationale_class = ""\n'
                'atomicity_rationale = ""\n'
                '[topology_audits.challenge]\n'
                'verdict = "green"\n'
                'evaluated = ["boundary_fidelity", "falsifiability", "review_separation"]\n'
                'scope_statement = "Merged preferred seam boundary checked for fidelity, falsifiability and review split."\n'
                'independent = true\n'
                'independence_basis = "Challenger did not author the Execution Prep topology proposal."\n'
                'fresh = true\n'
                'challenge_basis = "Fresh review of the merged boundary against seam intent and sizing outcomes."\n'
                'proposal_digest = "sha256:' + "0" * 64 + '"\n'
                'card_contract_digest = "sha256:' + "1" * 64 + '"\n',
            )
            self.assertNotEqual(risky_base, base)
            board.write_text(risky_base + (
                '[[seam_decisions]]\n'
                'seam_id = "BOOT-A"\n'
                'decision = "preserved"\n'
                '[[seam_decisions]]\n'
                'seam_id = "helper-less-derivation"\n'
                'decision = "merged"\n'
                'rationale_class = "atomicity"\n'
                'rationale = "Single atomic migration cannot land across two Cards."\n'
                '[[seam_decisions]]\n'
                'seam_id = "example-split"\n'
                'decision = "split"\n'
            ))
            data = tomllib.loads(board.read_text())
            planning = tomllib.loads((project / ROUTER_PLANNING).read_text())
            sizing = next(audit for audit in data["sizing_audits"] if audit["card_id"] == "M01-T04")
            audit = next(audit for audit in data["topology_audits"] if audit["card_id"] == "M01-T04")
            board.write_text(board.read_text().replace(
                "sha256:" + "0" * 64,
                compute_proposal_digest(
                    card_id="M01-T04",
                    sizing_audit=sizing,
                    topology_audit=audit,
                    seam_decisions=data.get("seam_decisions"),
                    planning_seams=planning.get("seams"),
                ),
            ))
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution", "M01-T04"),
            )
        finally:
            temp.cleanup()

    def test_router_rejects_missing_decision_bypass(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_planning(project, seams=self.planning_seams())
            self.install_decisions(project, (
                '[[seam_decisions]]\n'
                'seam_id = "helper-less-derivation"\n'
                'decision = "preserved"\n'
                '[[seam_decisions]]\n'
                'seam_id = "example-split"\n'
                'decision = "preserved"\n'
            ))
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation), ("recovery", "recovery_boundary")
            )
            self.assertIn(
                "missing durable JIT decision for declared seam 'BOOT-A'", routed.reason
            )
        finally:
            temp.cleanup()

        temp, project = self.copy_fixture()
        try:
            self.install_planning(project, seams=self.planning_seams())
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation), ("recovery", "recovery_boundary")
            )
            self.assertIn("require durable per-seam JIT decisions", routed.reason)
        finally:
            temp.cleanup()

    def test_router_preserves_legacy_plan_without_seams(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_planning(project)
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution", "M01-T04"),
            )
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
