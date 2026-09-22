from __future__ import annotations

import copy
import unittest
from pathlib import Path

from tools.state_contract import (
    ValidationError,
    read_toml,
    read_project,
    reject_prohibited_keys,
    validate_board,
    validate_brainstorm,
    validate_bundle,
    validate_definition,
    validate_intake,
    validate_project,
    validate_research,
    validate_review,
    validate_workstream,
)

ROOT = Path(__file__).resolve().parents[1]
VALID = ROOT / "tests" / "fixtures" / "state" / "valid"
INVALID = ROOT / "tests" / "fixtures" / "state" / "invalid"


class StateEnvelopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workstream = read_toml(VALID / "WORKSTREAM.toml")

    def test_valid_bundle_and_expected_revision(self) -> None:
        validate_bundle(
            VALID / "PROJECT.md",
            VALID / "WORKSTREAM.toml",
            VALID / "TASK_BOARD.toml",
            VALID / "REVIEW_ATTEMPT.toml",
            VALID / "EXTERNAL_EFFECT.toml",
            expected_revision=7,
        )

    def test_stale_revision_fails_closed(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        with self.assertRaisesRegex(ValidationError, "stale expected revision"):
            validate_board(board, self.workstream, expected_revision=6)

    def test_wrong_workstream_and_branch_fail_closed(self) -> None:
        for name in ("wrong-workstream-board.toml", "wrong-branch-board.toml"):
            with self.subTest(name=name), self.assertRaises(ValidationError):
                validate_board(read_toml(INVALID / name), self.workstream)

    def test_one_card_in_progress_is_enforced(self) -> None:
        with self.assertRaisesRegex(ValidationError, "more than one"):
            validate_board(read_toml(INVALID / "two-active-board.toml"), self.workstream)

    def test_prohibited_policy_runtime_scheduler_keys_fail(self) -> None:
        with self.assertRaisesRegex(ValidationError, "execution_policy"):
            validate_board(read_toml(INVALID / "prohibited-policy-board.toml"), self.workstream)
        value = read_toml(VALID / "TASK_BOARD.toml")
        for key in ("runtime", "runtime_id", "model_id", "session_id", "worker", "worker_id", "active_execution", "lane", "lane_id", "context_health"):
            candidate = copy.deepcopy(value)
            candidate[key] = "forbidden"
            with self.subTest(key=key), self.assertRaises(ValidationError):
                validate_board(candidate, self.workstream)

    def test_locator_class_missing_and_cross_workstream_path_fail(self) -> None:
        for name in ("wrong-class-workstream.toml", "missing-locator-workstream.toml", "cross-workstream-path.toml"):
            with self.subTest(name=name), self.assertRaises(ValidationError):
                validate_workstream(read_toml(INVALID / name))

    def test_review_is_exact_subject_and_semantic_only(self) -> None:
        validate_review(read_toml(VALID / "REVIEW_ATTEMPT.toml"))
        with self.assertRaisesRegex(ValidationError, "session"):
            validate_review(read_toml(INVALID / "review-runtime-identity.toml"))
        with self.assertRaisesRegex(ValidationError, "not semantically independent"):
            validate_review(read_toml(INVALID / "review-not-independent.toml"))


    def test_issue_intake_alignment_is_exact_and_stale_subject_fails(self) -> None:
        intake = read_toml(VALID / "INTAKE.toml")
        validate_intake(intake, "sample-workstream")

        stale = copy.deepcopy(intake)
        stale["repair_subject"] = "repair:sample:v3"
        with self.assertRaisesRegex(ValidationError, "stale"):
            validate_intake(stale, "sample-workstream")

    def test_issue_question_is_response_but_not_authorization(self) -> None:
        intake = read_toml(VALID / "INTAKE.toml")
        intake.update({
            "state": "active",
            "response_kind": "question",
            "response_observed": True,
            "alignment_state": "pending",
            "alignment_subject": "",
            "micro_fix_candidate": False,
        })
        validate_intake(intake, "sample-workstream")

        intake["micro_fix_candidate"] = True
        with self.assertRaisesRegex(ValidationError, "micro-fix candidate"):
            validate_intake(intake, "sample-workstream")

    def test_feature_discovery_does_not_manufacture_issue_alignment(self) -> None:
        intake = read_toml(VALID / "INTAKE.toml")
        intake.update({
            "kind": "feature",
            "state": "active",
            "repair_subject": "",
            "response_kind": "none",
            "response_observed": False,
            "alignment_state": "not_required",
            "alignment_subject": "",
            "micro_fix_candidate": False,
        })
        validate_intake(intake, "sample-workstream")
        intake["alignment_state"] = "authorized"
        with self.assertRaisesRegex(ValidationError, "must not manufacture"):
            validate_intake(intake, "sample-workstream")


    def test_pre_execution_workstream_may_have_intake_without_task_board(self) -> None:
        workstream = copy.deepcopy(self.workstream)
        workstream.pop("task_board")
        workstream["intake"] = {
            "class": "intake",
            "path": "implementation/workstreams/sample-workstream/INTAKE.toml",
        }
        validate_workstream(workstream)
        workstream.pop("intake")
        with self.assertRaisesRegex(ValidationError, "workstream-local state locator"):
            validate_workstream(workstream)

    def test_intake_locator_is_workstream_bound(self) -> None:
        workstream = copy.deepcopy(self.workstream)
        workstream["intake"] = {
            "class": "intake",
            "path": "implementation/workstreams/sample-workstream/INTAKE.toml",
        }
        validate_workstream(workstream)
        workstream["intake"]["path"] = "implementation/workstreams/other/INTAKE.toml"
        with self.assertRaises(ValidationError):
            validate_workstream(workstream)


    def test_brainstorm_promotion_binds_exact_revision(self) -> None:
        data = {
            "workstream_id": "sample-workstream",
            "scope_id": "scope-a",
            "revision": 2,
            "state": "ready_for_definition",
            "challenge_audit": "green",
            "explicit_user_stop": False,
            "promotion_state": "pending",
            "promotion_subject": "",
        }
        validate_brainstorm(data, "sample-workstream")

        data["promotion_state"] = "authorized"
        data["promotion_subject"] = "scope-a@2"
        validate_brainstorm(data, "sample-workstream")

        stale = copy.deepcopy(data)
        stale["revision"] = 3
        with self.assertRaisesRegex(ValidationError, "stale"):
            validate_brainstorm(stale, "sample-workstream")

    def test_research_requires_all_source_classes_and_once_only_return_state(self) -> None:
        sources = [
            {"class": "official_upstream", "status": "checked", "weight": "primary"},
            {"class": "project_runtime", "status": "checked", "weight": "direct"},
            {"class": "tracker_discussion", "status": "not_relevant", "weight": "supporting"},
            {"class": "practitioner_community", "status": "unavailable", "weight": "supporting"},
        ]
        data = {
            "workstream_id": "sample-workstream",
            "state": "complete",
            "origin_role": "brainstorming",
            "origin_subject": "scope-a@2",
            "return_target": "brainstorming",
            "return_reconciliation": "pending",
            "return_result": "",
            "finding": "No conflicting prior art.",
            "limitations": "Community source unavailable.",
            "sources": sources,
        }
        validate_research(data, "sample-workstream")

        missing = copy.deepcopy(data)
        missing["sources"] = missing["sources"][:-1]
        with self.assertRaisesRegex(ValidationError, "all proportional"):
            validate_research(missing, "sample-workstream")

        applied = copy.deepcopy(data)
        applied["return_reconciliation"] = "applied"
        with self.assertRaisesRegex(ValidationError, "return_result"):
            validate_research(applied, "sample-workstream")

        applied["return_result"] = "brainstorm:scope-a@2:reconciled"
        validate_research(applied, "sample-workstream")
        applied["state"] = "consumed"
        validate_research(applied, "sample-workstream")

    def test_definition_green_requires_authority_and_premium_a(self) -> None:
        active = {
            "workstream_id": "sample-workstream",
            "source_scope_subject": "scope-a@2",
            "revision": "R1",
            "state": "active",
            "completeness_audit": "pending",
            "premium_a": "not_due",
            "requirements": {"class": "authority", "path": "requirements/REQUIREMENTS.md"},
            "decisions": [],
        }
        validate_definition(active, "sample-workstream")

        green = copy.deepcopy(active)
        green.update({
            "state": "green",
            "completeness_audit": "green",
            "premium_a": "due",
            "decisions": [{"class": "authority", "path": "decisions/ADR-001.md"}],
        })
        validate_definition(green, "sample-workstream")

        bad = copy.deepcopy(green)
        bad["premium_a"] = "not_due"
        with self.assertRaisesRegex(ValidationError, "premium stop A"):
            validate_definition(bad, "sample-workstream")

    def test_exploration_locators_are_exact_and_workstream_bound(self) -> None:
        workstream = copy.deepcopy(self.workstream)
        for key, klass, filename in (
            ("brainstorm", "brainstorm", "BRAINSTORM.toml"),
            ("research", "research", "RESEARCH.toml"),
            ("definition", "definition", "DEFINITION.toml"),
        ):
            candidate = copy.deepcopy(workstream)
            candidate[key] = {
                "class": klass,
                "path": f"implementation/workstreams/sample-workstream/{filename}",
            }
            validate_workstream(candidate)
            candidate[key]["path"] = f"implementation/workstreams/other/{filename}"
            with self.subTest(key=key), self.assertRaises(ValidationError):
                validate_workstream(candidate)

    def test_project_contract_is_common_v2_only(self) -> None:
        project = read_project(VALID / "PROJECT.md")
        validate_project(project)
        reject_prohibited_keys(project)


if __name__ == "__main__":
    unittest.main()
