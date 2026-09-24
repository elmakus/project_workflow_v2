from __future__ import annotations

import copy
import unittest
from pathlib import Path

from tools.state_contract import (
    ValidationError,
    read_toml,
    read_project,
    parse_task_card,
    reject_prohibited_keys,
    validate_board,
    validate_brainstorm,
    validate_bundle,
    validate_definition,
    validate_external_effect,
    validate_intake,
    validate_plan_review,
    validate_planning,
    validate_project,
    validate_research,
    validate_review,
    validate_review_history,
    validate_tracker,
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

    def test_task_card_parser_requires_complete_stable_launch_contract(self) -> None:
        text = (
            "# Task Card\n"
            "- Card ID: M03-T01\n"
            "- Included scope: runtime-neutral readiness\n"
            "- Excluded scope: runtime adapters\n"
            "- Authority refs: requirements/PROJECT_WORKFLOW_V2.md, decisions/ADR-004.md\n"
            "- Dependencies: none\n"
            "- Acceptance: READY is independent of worker availability\n"
            "- Required tests/readback: production parser and router tests\n"
            "- Review requirement: none\n"
            "- Technical contract: none\n"
        )
        parsed = parse_task_card(text, "M03-T01", "sample-workstream")
        self.assertEqual(parsed["dependencies"], [])
        self.assertIsNone(parsed["technical_contract"])

        unresolved = text.replace(
            "- Required tests/readback: production parser and router tests",
            "- Required tests/readback: <checks>",
        )
        with self.assertRaisesRegex(ValidationError, "unresolved"):
            parse_task_card(unresolved, "M03-T01", "sample-workstream")

        wrong_id = text.replace("M03-T01", "M03-T99", 1)
        with self.assertRaisesRegex(ValidationError, "Card ID"):
            parse_task_card(wrong_id, "M03-T01", "sample-workstream")

        exact_dependency = (
            "implementation/workstreams/sample-workstream/results/M03-T00.md@"
            + ("a" * 40) + ":" + ("b" * 40)
        )
        with_dependency = text.replace("- Dependencies: none", f"- Dependencies: {exact_dependency}")
        parsed_dependency = parse_task_card(with_dependency, "M03-T01", "sample-workstream")
        self.assertEqual(
            parsed_dependency["dependencies"],
            [{
                "path": "implementation/workstreams/sample-workstream/results/M03-T00.md",
                "commit": "a" * 40,
                "blob": "b" * 40,
            }],
        )

        path_only = text.replace(
            "- Dependencies: none",
            "- Dependencies: implementation/workstreams/sample-workstream/results/M03-T00.md",
        )
        with self.assertRaisesRegex(ValidationError, "path@commit:blob"):
            parse_task_card(path_only, "M03-T01", "sample-workstream")

    def test_jit_trigger_preserves_predecessor_boundary_without_placeholder_card(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["jit_triggers"] = [{
            "id": "after-M01-T01",
            "after_card": "M01-T01",
            "state": "waiting",
            "condition": "Predecessor result determines exact downstream Card boundary.",
        }]
        validate_board(board, self.workstream)

        board["jit_triggers"][0]["state"] = "satisfied"
        validate_board(board, self.workstream)

        stale = copy.deepcopy(board)
        stale["jit_triggers"][0]["after_card"] = "M01-T02"
        with self.assertRaisesRegex(ValidationError, "DONE predecessor result"):
            validate_board(stale, self.workstream)

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


    def test_review_terminal_evidence_and_append_only_history(self) -> None:
        base = read_toml(VALID / "REVIEW_ATTEMPT.toml")
        validate_review(base)

        pending = copy.deepcopy(base)
        pending["attempt"] = "R02"
        pending["verdict"] = "pending"
        pending["evidence_path"] = ""
        pending["review_kind"] = "discovery"
        pending["source_discovery_attempt"] = ""
        pending["discovery_complete"] = False
        pending["material_finding_ids"] = []
        pending["review_scope"] = "card"
        pending["review_epoch"] = "E01"
        pending["epoch_reset_basis"] = ""
        pending["material_defect_class_ids"] = []
        pending["post_convergence_validation"] = False
        pending["convergence_basis"] = ""
        pending["subject"]["blob"] = "4" * 40
        validate_review_history([base, pending])

        bad_order = [pending, base]
        with self.assertRaisesRegex(ValidationError, "latest attempt"):
            validate_review_history(bad_order)

        terminal_without_evidence = copy.deepcopy(base)
        terminal_without_evidence["evidence_path"] = ""
        with self.assertRaisesRegex(ValidationError, "terminal verdict"):
            validate_review(terminal_without_evidence)

    def test_pw21_discovery_and_closure_history_is_explicit_and_bounded(self) -> None:
        base = read_toml(VALID / "REVIEW_ATTEMPT.toml")
        base.update({
            "review_kind": "discovery",
            "source_discovery_attempt": "",
            "discovery_complete": True,
            "material_finding_ids": ["F1", "F2"],
            "review_scope": "card",
            "review_epoch": "E01",
            "epoch_reset_basis": "",
            "material_defect_class_ids": ["class-a", "class-b"],
            "post_convergence_validation": False,
            "convergence_basis": "",
            "verdict": "red",
        })
        validate_review(base)

        closure = copy.deepcopy(base)
        closure.update({
            "attempt": "R02",
            "review_kind": "closure_verification",
            "source_discovery_attempt": "R01",
            "discovery_complete": False,
            "material_finding_ids": ["F1"],
            "material_defect_class_ids": ["class-a"],
            "verdict": "green",
        })
        closure["subject"]["blob"] = "4" * 40
        validate_review_history([base, closure])

        premature_discovery = copy.deepcopy(base)
        premature_discovery.update({
            "attempt": "R03",
            "review_kind": "discovery",
            "source_discovery_attempt": "",
            "discovery_complete": False,
            "material_finding_ids": [],
            "material_defect_class_ids": [],
            "verdict": "pending",
            "evidence_path": "",
        })
        premature_discovery["subject"]["blob"] = "4" * 40
        with self.assertRaisesRegex(ValidationError, "before all known material findings"):
            validate_review_history([base, closure, premature_discovery])

        closure_two = copy.deepcopy(closure)
        closure_two.update({
            "attempt": "R03",
            "material_finding_ids": ["F2"],
            "material_defect_class_ids": ["class-b"],
        })
        validate_review_history([base, closure, closure_two])

        next_discovery = copy.deepcopy(premature_discovery)
        next_discovery["attempt"] = "R04"
        validate_review_history([base, closure, closure_two, next_discovery])

        unknown_source = copy.deepcopy(closure)
        unknown_source["source_discovery_attempt"] = "R99"
        with self.assertRaisesRegex(ValidationError, "earlier attempt"):
            validate_review_history([base, unknown_source])

        foreign_finding = copy.deepcopy(closure)
        foreign_finding["material_finding_ids"] = ["F3"]
        with self.assertRaisesRegex(ValidationError, "only findings frozen"):
            validate_review_history([base, foreign_finding])

        incomplete_discovery = copy.deepcopy(base)
        incomplete_discovery["discovery_complete"] = False
        with self.assertRaisesRegex(ValidationError, "complete acceptance-surface"):
            validate_review(incomplete_discovery)

        green_with_blocker = copy.deepcopy(base)
        green_with_blocker["verdict"] = "green"
        with self.assertRaisesRegex(ValidationError, "cannot retain material blocking"):
            validate_review(green_with_blocker)

        legacy_active = read_toml(VALID / "REVIEW_ATTEMPT.toml")
        legacy_active["verdict"] = "pending"
        legacy_active["evidence_path"] = ""
        with self.assertRaisesRegex(ValidationError, "explicit review_kind"):
            validate_review_history([legacy_active])

        historical = read_toml(VALID / "REVIEW_ATTEMPT.toml")
        explicit_after_history = copy.deepcopy(historical)
        explicit_after_history.update({
            "attempt": "R02",
            "review_kind": "discovery",
            "source_discovery_attempt": "",
            "discovery_complete": False,
            "material_finding_ids": [],
            "review_scope": "card",
            "review_epoch": "E01",
            "epoch_reset_basis": "",
            "material_defect_class_ids": [],
            "post_convergence_validation": False,
            "convergence_basis": "",
            "verdict": "pending",
            "evidence_path": "",
        })
        validate_review_history([historical, explicit_after_history])

        legacy_after_explicit = copy.deepcopy(historical)
        legacy_after_explicit["attempt"] = "R03"
        explicit_terminal = copy.deepcopy(explicit_after_history)
        explicit_terminal.update({
            "verdict": "green",
            "discovery_complete": True,
            "evidence_path": historical["evidence_path"],
        })
        with self.assertRaisesRegex(ValidationError, "initial historical prefix"):
            validate_review_history([historical, explicit_terminal, legacy_after_explicit])

    def test_review_epoch_reset_requires_material_accepted_redesign_basis(self) -> None:
        base = read_toml(VALID / "REVIEW_ATTEMPT.toml")
        base.update({
            "review_kind": "discovery",
            "source_discovery_attempt": "",
            "discovery_complete": True,
            "material_finding_ids": ["F1"],
            "review_scope": "card",
            "review_epoch": "E01",
            "epoch_reset_basis": "",
            "material_defect_class_ids": ["class-a"],
            "post_convergence_validation": False,
            "convergence_basis": "",
            "verdict": "red",
        })

        reset = copy.deepcopy(base)
        reset.update({
            "attempt": "R02",
            "review_epoch": "E02",
            "material_finding_ids": [],
            "material_defect_class_ids": [],
            "discovery_complete": False,
            "verdict": "pending",
            "evidence_path": "",
        })
        reset["subject"]["blob"] = "4" * 40
        with self.assertRaisesRegex(ValidationError, "changed review_epoch requires"):
            validate_review_history([base, reset])

        reset["epoch_reset_basis"] = "repair convenience is not a redesign"
        reset["epoch_reset_subject"] = {
            "class": "accepted_redesign",
            "repository": "owner/fixture-project",
            "commit": "4" * 40,
            "path": "implementation/workstreams/sample-workstream/results/M03-T03.md",
            "blob": "5" * 40,
        }
        with self.assertRaisesRegex(ValidationError, "accepted authority or acceptance redesign"):
            validate_review_history([base, reset])

        reset["epoch_reset_basis"] = (
            "Accepted authority/acceptance redesign revision R4 replaces the prior epoch."
        )
        reset["epoch_reset_subject"]["path"] = reset["acceptance"]["path"]
        validate_review_history([base, reset])

        same_epoch_claim = copy.deepcopy(base)
        same_epoch_claim.update({
            "attempt": "R02",
            "epoch_reset_basis": "repair convenience is not a redesign",
            "epoch_reset_subject": copy.deepcopy(reset["epoch_reset_subject"]),
            "material_finding_ids": [],
            "material_defect_class_ids": [],
            "discovery_complete": False,
            "verdict": "pending",
            "evidence_path": "",
        })
        same_epoch_claim["subject"]["blob"] = "4" * 40
        with self.assertRaisesRegex(ValidationError, "unchanged review_epoch"):
            validate_review_history([base, same_epoch_claim])

    def test_post_convergence_validation_requires_threshold_and_is_single(self) -> None:
        attempts = []
        for index in range(5):
            discovery = read_toml(VALID / "REVIEW_ATTEMPT.toml")
            discovery.update({
                "attempt": f"R{index * 2 + 1:02d}",
                "review_kind": "discovery",
                "source_discovery_attempt": "",
                "discovery_complete": True,
                "material_finding_ids": [f"F{index}"],
                "review_scope": "card",
                "review_epoch": "E01",
                "epoch_reset_basis": "",
                "material_defect_class_ids": [f"class-{index}"],
                "post_convergence_validation": False,
                "convergence_basis": "",
                "verdict": "red",
            })
            discovery["subject"]["blob"] = chr(ord("4") + index) * 40
            attempts.append(discovery)
            closure = copy.deepcopy(discovery)
            closure.update({
                "attempt": f"R{index * 2 + 2:02d}",
                "review_kind": "closure_verification",
                "source_discovery_attempt": discovery["attempt"],
                "discovery_complete": False,
                "verdict": "green",
            })
            attempts.append(closure)

        post = copy.deepcopy(attempts[-1])
        post.update({
            "attempt": "R11",
            "review_kind": "discovery",
            "source_discovery_attempt": "",
            "discovery_complete": False,
            "material_finding_ids": [],
            "material_defect_class_ids": [],
            "post_convergence_validation": True,
            "convergence_basis": "Main convergence/root-cause analysis C01",
            "verdict": "pending",
            "evidence_path": "",
        })
        validate_review_history(attempts + [post])

        terminal_post = copy.deepcopy(post)
        terminal_post.update({
            "verdict": "green",
            "discovery_complete": True,
            "evidence_path": attempts[0]["evidence_path"],
        })
        second = copy.deepcopy(post)
        second["attempt"] = "R12"
        with self.assertRaisesRegex(ValidationError, "terminal post-convergence|only one post-convergence"):
            validate_review_history(attempts + [terminal_post, second])

    def test_convergence_aware_closure_can_adapt_open_t01_discovery(self) -> None:
        source = read_toml(VALID / "REVIEW_ATTEMPT.toml")
        source.update({
            "review_kind": "discovery",
            "source_discovery_attempt": "",
            "discovery_complete": True,
            "material_finding_ids": ["F1"],
            "verdict": "red",
        })
        closure = copy.deepcopy(source)
        closure.update({
            "attempt": "R02",
            "review_kind": "closure_verification",
            "source_discovery_attempt": "R01",
            "discovery_complete": False,
            "material_finding_ids": ["F1"],
            "review_scope": "card",
            "review_epoch": "E01",
            "epoch_reset_basis": "",
            "material_defect_class_ids": ["class-a"],
            "post_convergence_validation": False,
            "convergence_basis": "",
            "verdict": "green",
        })
        closure["subject"]["blob"] = "4" * 40
        validate_review_history([source, closure])

    def test_terminal_post_convergence_red_forbids_same_epoch_review_continuation(self) -> None:
        attempts = []
        for index in range(5):
            discovery = read_toml(VALID / "REVIEW_ATTEMPT.toml")
            discovery.update({
                "attempt": f"R{index * 2 + 1:02d}",
                "review_kind": "discovery",
                "source_discovery_attempt": "",
                "discovery_complete": True,
                "material_finding_ids": [f"F{index}"],
                "review_scope": "card",
                "review_epoch": "E01",
                "epoch_reset_basis": "",
                "material_defect_class_ids": [f"class-{index}"],
                "post_convergence_validation": False,
                "convergence_basis": "",
                "verdict": "red",
            })
            discovery["subject"]["blob"] = chr(ord("4") + index) * 40
            attempts.append(discovery)
            closure = copy.deepcopy(discovery)
            closure.update({
                "attempt": f"R{index * 2 + 2:02d}",
                "review_kind": "closure_verification",
                "source_discovery_attempt": discovery["attempt"],
                "discovery_complete": False,
                "verdict": "green",
            })
            attempts.append(closure)

        post_red = copy.deepcopy(attempts[-1])
        post_red.update({
            "attempt": "R11",
            "review_kind": "discovery",
            "source_discovery_attempt": "",
            "discovery_complete": True,
            "material_finding_ids": ["F-post"],
            "material_defect_class_ids": ["class-post"],
            "post_convergence_validation": True,
            "convergence_basis": "Main convergence/root-cause analysis C01",
            "verdict": "red",
        })
        attempts.append(post_red)
        validate_review_history(attempts)

        forbidden = copy.deepcopy(post_red)
        forbidden.update({
            "attempt": "R12",
            "review_kind": "closure_verification",
            "source_discovery_attempt": "R11",
            "discovery_complete": False,
            "post_convergence_validation": False,
            "convergence_basis": "",
            "verdict": "green",
        })
        with self.assertRaisesRegex(ValidationError, "terminal post-convergence"):
            validate_review_history(attempts + [forbidden])

        new_epoch = copy.deepcopy(post_red)
        new_epoch.update({
            "attempt": "R12",
            "review_kind": "discovery",
            "source_discovery_attempt": "",
            "discovery_complete": False,
            "material_finding_ids": [],
            "review_epoch": "E02",
            "epoch_reset_basis": "Accepted structural redesign R5 establishes a new acceptance epoch.",
            "epoch_reset_subject": {
                "class": "accepted_redesign",
                "repository": "owner/fixture-project",
                "commit": "8" * 40,
                "path": post_red["acceptance"]["path"],
                "blob": "9" * 40,
            },
            "material_defect_class_ids": [],
            "post_convergence_validation": False,
            "convergence_basis": "",
            "verdict": "pending",
            "evidence_path": "",
        })
        validate_review_history(attempts + [new_epoch])

    def test_review_epoch_identity_cannot_be_reused_after_reset(self) -> None:
        first = read_toml(VALID / "REVIEW_ATTEMPT.toml")
        first.update({
            "review_kind": "discovery",
            "source_discovery_attempt": "",
            "discovery_complete": True,
            "material_finding_ids": [],
            "review_scope": "card",
            "review_epoch": "E01",
            "epoch_reset_basis": "",
            "material_defect_class_ids": [],
            "post_convergence_validation": False,
            "convergence_basis": "",
            "verdict": "green",
        })
        second = copy.deepcopy(first)
        second.update({
            "attempt": "R02",
            "review_epoch": "E02",
            "epoch_reset_basis": "Accepted redesign R2",
            "epoch_reset_subject": {
                "class": "accepted_redesign",
                "repository": "owner/fixture-project",
                "commit": "6" * 40,
                "path": first["acceptance"]["path"],
                "blob": "7" * 40,
            },
        })
        third = copy.deepcopy(first)
        third.update({
            "attempt": "R03",
            "epoch_reset_basis": "Accepted redesign R3",
            "epoch_reset_subject": {
                "class": "accepted_redesign",
                "repository": "owner/fixture-project",
                "commit": "8" * 40,
                "path": first["acceptance"]["path"],
                "blob": "9" * 40,
            },
        })
        with self.assertRaisesRegex(ValidationError, "cannot be reused"):
            validate_review_history([first, second, third])

    def test_task_card_review_acceptance_is_exact_and_semantic(self) -> None:
        review = {
            "workstream_id": "sample-workstream",
            "card_id": "M03-T03",
            "attempt": "R01",
            "verdict": "pending",
            "evidence_path": "",
            "review_kind": "discovery",
            "source_discovery_attempt": "",
            "discovery_complete": False,
            "material_finding_ids": [],
            "review_scope": "card",
            "review_epoch": "E01",
            "epoch_reset_basis": "",
            "material_defect_class_ids": [],
            "post_convergence_validation": False,
            "convergence_basis": "",
            "subject": {
                "class": "git_blob",
                "repository": "owner/repo",
                "commit": "a" * 40,
                "path": "workflow/STATE.md",
                "blob": "b" * 40,
            },
            "acceptance": {
                "class": "task_card",
                "path": "implementation/workstreams/sample-workstream/cards/M03-T03.md",
            },
            "independence": {
                "materially_produced_or_repaired_subject": False,
                "basis": "Reviewer did not materially produce or repair the exact subject.",
            },
        }
        validate_review(review)
        validate_review_history(
            [review],
            expected_card_id="M03-T03",
            workstream_id="sample-workstream",
        )

        self_review = copy.deepcopy(review)
        self_review["independence"]["materially_produced_or_repaired_subject"] = True
        with self.assertRaisesRegex(ValidationError, "not semantically independent"):
            validate_review(self_review)

    def test_issue_intake_alignment_is_exact_and_stale_subject_fails(self) -> None:
        intake = read_toml(VALID / "INTAKE.toml")
        validate_intake(intake, "sample-workstream")

        stale = copy.deepcopy(intake)
        stale["repair_subject"] = "repair:sample:v3"
        with self.assertRaisesRegex(ValidationError, "stale"):
            validate_intake(stale, "sample-workstream")

        missing_prior_art = copy.deepcopy(intake)
        missing_prior_art["diagnosis_prior_art_subject"] = ""
        missing_prior_art["diagnosis_prior_art_result"] = ""
        with self.assertRaisesRegex(ValidationError, "diagnosis prior-art"):
            validate_intake(missing_prior_art, "sample-workstream")

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
            "diagnosis_prior_art_subject": "",
            "diagnosis_prior_art_result": "",
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
            "conflicts": "No material conflicts observed across checked source classes.",
            "sources": sources,
        }
        validate_research(data, "sample-workstream")

        no_conflicts = copy.deepcopy(data)
        no_conflicts["conflicts"] = ""
        with self.assertRaisesRegex(ValidationError, "conflict accounting"):
            validate_research(no_conflicts, "sample-workstream")

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


    def planning_record(self, state: str = "draft") -> dict:
        subject = {"repository": "", "commit": "", "path": "", "blob": ""}
        data = {
            "workstream_id": "sample-workstream",
            "cycle": 1,
            "entry_subject": "definition:R1|planning-cycle:1",
            "revision": "P1",
            "state": state,
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
            "subject": subject,
        }
        if state in {"frozen", "approved"}:
            data["planner_audit"] = "green"
            data["subject"] = {
                "repository": "owner/repo",
                "commit": "a" * 40,
                "path": "planning/MASTER_PLAN.md",
                "blob": "b" * 40,
            }
            key = f"owner/repo@{'a' * 40}:planning/MASTER_PLAN.md@{'b' * 40}"
            data["premium_b"] = "due" if state == "frozen" else "satisfied"
            data["premium_b_subject"] = key
            if state == "approved":
                data["premium_c"] = "due"
                data["premium_c_subject"] = key
        return data

    def test_planning_cycle_rejects_stale_premium_a_and_orders_b_c(self) -> None:
        draft = self.planning_record()
        validate_planning(draft, "sample-workstream")

        stale = copy.deepcopy(draft)
        stale["cycle"] = 2
        stale["entry_subject"] = "definition:R1|planning-cycle:2"
        with self.assertRaisesRegex(ValidationError, "premium A"):
            validate_planning(stale, "sample-workstream")

        reentry = copy.deepcopy(draft)
        reentry["cycle"] = 2
        reentry["entry_subject"] = "definition:R1|planning-cycle:2"
        reentry["revision"] = "P2"
        reentry["premium_a"] = "due"
        reentry["premium_a_subject"] = reentry["entry_subject"]
        validate_planning(reentry, "sample-workstream")
        reentry["premium_a"] = "satisfied"
        validate_planning(reentry, "sample-workstream")

        frozen = self.planning_record("frozen")
        validate_planning(frozen, "sample-workstream")
        bad_c = copy.deepcopy(frozen)
        bad_c["premium_c"] = "due"
        bad_c["premium_c_subject"] = frozen["premium_b_subject"]
        with self.assertRaisesRegex(ValidationError, "premium C cannot"):
            validate_planning(bad_c, "sample-workstream")

        approved = self.planning_record("approved")
        validate_planning(approved, "sample-workstream")

    def test_plan_review_must_match_frozen_subject_and_terminal_evidence(self) -> None:
        planning = self.planning_record("frozen")
        planning["premium_b"] = "satisfied"
        subject = {
            "class": "git_blob",
            "repository": "owner/repo",
            "commit": "a" * 40,
            "path": "planning/MASTER_PLAN.md",
            "blob": "b" * 40,
        }
        review = {
            "workstream_id": "sample-workstream",
            "plan_revision": "P1",
            "planning_cycle": 1,
            "attempt": "R01",
            "verdict": "pending",
            "evidence_path": "",
            "subject": subject,
            "acceptance": {"class": "authority", "path": "requirements/REQUIREMENTS.md"},
            "independence": {
                "materially_produced_or_repaired_subject": False,
                "basis": "Fresh semantic review context.",
            },
        }
        validate_plan_review(review, "sample-workstream", planning)

        mismatch = copy.deepcopy(review)
        mismatch["subject"]["blob"] = "c" * 40
        with self.assertRaisesRegex(ValidationError, "does not match"):
            validate_plan_review(mismatch, "sample-workstream", planning)

        green = copy.deepcopy(review)
        green["verdict"] = "green"
        with self.assertRaisesRegex(ValidationError, "evidence_path"):
            validate_plan_review(green, "sample-workstream", planning)
        green["evidence_path"] = "evidence/plan-review-R01.md"
        validate_plan_review(green, "sample-workstream", planning)

    def test_editorial_plan_exemption_preserves_prior_green_subject(self) -> None:
        planning = self.planning_record("approved")
        prior = planning["premium_b_subject"]
        planning["subject"]["blob"] = "c" * 40
        planning["review_mode"] = "editorial_exempt"
        planning["review_exemption_basis"] = "Wording only; no strategy, milestones, coverage or gates changed."
        planning["review_exemption_base_subject"] = prior
        planning["premium_c"] = "satisfied"
        planning["premium_b_subject"] = prior
        planning["premium_c_subject"] = prior
        validate_planning(planning, "sample-workstream")

        review = {
            "workstream_id": "sample-workstream",
            "plan_revision": "P1",
            "planning_cycle": 1,
            "attempt": "R01",
            "verdict": "green",
            "evidence_path": "evidence/plan-review-R01.md",
            "subject": {
                "class": "git_blob",
                "repository": "owner/repo",
                "commit": "a" * 40,
                "path": "planning/MASTER_PLAN.md",
                "blob": "b" * 40,
            },
            "acceptance": {"class": "authority", "path": "requirements/REQUIREMENTS.md"},
            "independence": {
                "materially_produced_or_repaired_subject": False,
                "basis": "Fresh semantic review context.",
            },
        }
        validate_plan_review(review, "sample-workstream", planning)

        bad = copy.deepcopy(planning)
        bad["review_exemption_basis"] = ""
        with self.assertRaisesRegex(ValidationError, "bounded semantic basis"):
            validate_planning(bad, "sample-workstream")

    def test_planning_and_plan_review_locators_are_exact(self) -> None:
        workstream = copy.deepcopy(self.workstream)
        for key, klass, filename in (
            ("planning", "planning", "PLANNING.toml"),
            ("plan_review", "plan_review", "PLAN_REVIEW.toml"),
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


    def test_tracker_correlation_states_and_authority_boundary(self) -> None:
        base = {
            "workstream_id": "sample-workstream",
            "provider": "github",
            "repository": "owner/repo",
            "dedup_key": "project-workflow:sample-workstream",
            "state": "discovery",
            "issue_number": 0,
            "candidate_issue_numbers": [],
            "readback_state": "pending",
            "final_pr": 0,
        }
        validate_tracker(base, "sample-workstream")

        pending = copy.deepcopy(base)
        pending.update({"state": "create_pending_readback", "readback_state": "uncertain"})
        validate_tracker(pending, "sample-workstream")

        linked = copy.deepcopy(base)
        linked.update({"state": "linked", "issue_number": 7, "readback_state": "verified"})
        validate_tracker(linked, "sample-workstream")
        linked["final_pr"] = 9
        validate_tracker(linked, "sample-workstream")

        ambiguous = copy.deepcopy(base)
        ambiguous.update({
            "state": "ambiguous",
            "candidate_issue_numbers": [7, 8],
            "readback_state": "uncertain",
        })
        validate_tracker(ambiguous, "sample-workstream")

        unavailable = copy.deepcopy(base)
        unavailable.update({"state": "unavailable", "readback_state": "not_applicable"})
        validate_tracker(unavailable, "sample-workstream")

        forbidden = copy.deepcopy(linked)
        forbidden["repair_authorized"] = True
        with self.assertRaisesRegex(ValidationError, "must not carry workflow authorization"):
            validate_tracker(forbidden, "sample-workstream")

    def test_tracker_locator_is_exact_and_workstream_bound(self) -> None:
        workstream = copy.deepcopy(self.workstream)
        workstream["tracker"] = {
            "class": "tracker",
            "path": "implementation/workstreams/sample-workstream/TRACKER.toml",
        }
        validate_workstream(workstream)
        workstream["tracker"]["path"] = "implementation/workstreams/other/TRACKER.toml"
        with self.assertRaises(ValidationError):
            validate_workstream(workstream)

    def test_external_effect_observation_matches_readback_state(self) -> None:
        effect = read_toml(VALID / "EXTERNAL_EFFECT.toml")
        validate_external_effect(effect, "sample-workstream")

        pending = copy.deepcopy(effect)
        pending.update({"readback_state": "pending", "observation": "unknown"})
        validate_external_effect(pending, "sample-workstream")

        uncertain = copy.deepcopy(effect)
        uncertain.update({"readback_state": "uncertain", "observation": "unknown"})
        validate_external_effect(uncertain, "sample-workstream")

        bad_pending = copy.deepcopy(effect)
        bad_pending.update({"readback_state": "pending", "observation": "expected_effect"})
        with self.assertRaisesRegex(ValidationError, "cannot claim an observation"):
            validate_external_effect(bad_pending, "sample-workstream")

        bad_verified = copy.deepcopy(effect)
        bad_verified.update({"readback_state": "verified", "observation": "unknown"})
        with self.assertRaisesRegex(ValidationError, "requires a concrete observation"):
            validate_external_effect(bad_verified, "sample-workstream")

    def test_project_contract_is_common_v2_only(self) -> None:
        project = read_project(VALID / "PROJECT.md")
        validate_project(project)
        reject_prohibited_keys(project)


if __name__ == "__main__":
    unittest.main()
