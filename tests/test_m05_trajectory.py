from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from tests.test_router import BOARD, MANIFEST, RouterTests
from tools.close_contract import (
    CloseContractError,
    close_continuation,
    external_effect_recovery_action,
)
from tools.continuation_contract import (
    ContinuationContractError,
    ProgressObservation,
    classify_progress,
    classify_route_completion,
    resume_action,
)
from tools.recovery_contract import classify_resolution
from tools.review_contract import review_delivery_policy, select_review_realization
from tools.router import select_route
from tools.user_stop_contract import HANDOFF_NONE, HANDOFF_REQUIRED


class M05TrajectoryConformanceTests(unittest.TestCase):
    def helper(self) -> RouterTests:
        return RouterTests(methodName="test_active_card_routes_to_runtime_neutral_execution")

    def test_01_active_result_reconciliation_review_trajectory(self) -> None:
        h = self.helper()
        temp, project = h.copy_fixture()
        try:
            self.assertEqual(select_route(project, [MANIFEST]).obligation, "execution")
            h.install_reviewable_result(project, "required")
            self.assertEqual(select_route(project, [MANIFEST]).obligation, "review_freeze")
            h.add_review_attempt(project, "pending")
            self.assertEqual(select_route(project, [MANIFEST]).obligation, "review")
        finally:
            temp.cleanup()

    def test_02_green_finalization_then_close_trajectory(self) -> None:
        h = self.helper()
        temp, project = h.copy_fixture()
        try:
            h.install_reviewable_result(project, "required")
            h.add_review_attempt(project, "green")
            self.assertEqual(select_route(project, [MANIFEST]).obligation, "post_review_finalization")
            board = project / BOARD
            board.write_text(board.read_text().replace('status = "in_progress"', 'status = "done"', 1))
            self.assertEqual(select_route(project, [MANIFEST]).obligation, "close")
        finally:
            temp.cleanup()

    def test_03_red_correction_new_subject_requires_new_review(self) -> None:
        h = self.helper()
        temp, project = h.copy_fixture()
        try:
            h.install_reviewable_result(project, "required")
            h.add_review_attempt(project, "red")
            self.assertEqual(select_route(project, [MANIFEST]).obligation, "execution_resolution")
            self.assertEqual(classify_resolution("bounded_correction"), ("execution", False))
            board = project / BOARD
            board.write_text(board.read_text().replace('blob = "' + ("b" * 40) + '"', 'blob = "' + ("c" * 40) + '"'))
            self.assertEqual(select_route(project, [MANIFEST]).obligation, "review_freeze")
        finally:
            temp.cleanup()

    def test_04_repairing_context_cannot_review_repaired_subject(self) -> None:
        self.assertEqual(
            select_review_realization(current_context_produced_subject=True, independent_context_available=False),
            "fresh_context",
        )

    def test_05_internal_independent_reviewer_continues_without_handoff(self) -> None:
        self.assertEqual(
            select_review_realization(current_context_produced_subject=True, independent_context_available=True),
            "internal_independent",
        )
        self.assertEqual(
            review_delivery_policy(current_context_produced_subject=True, independent_context_available=True),
            HANDOFF_NONE,
        )

    def test_06_external_independence_boundary_requires_handoff(self) -> None:
        self.assertEqual(
            review_delivery_policy(current_context_produced_subject=True, independent_context_available=False),
            HANDOFF_REQUIRED,
        )

    def test_07_red_research_return_owner_trajectory(self) -> None:
        h = self.helper()
        temp, project = h.copy_fixture()
        try:
            self.assertEqual(classify_resolution("missing_evidence"), ("research", False))
            h.install_board_research(project, state="active")
            self.assertEqual(select_route(project, [MANIFEST]).obligation, "research")
            (project / "implementation/workstreams/sample-workstream/RESEARCH.toml").write_text(
                (project / "implementation/workstreams/sample-workstream/RESEARCH.toml").read_text()
                .replace('state = "active"', 'state = "complete"')
            )
            self.assertEqual(select_route(project, [MANIFEST]).obligation, "execution_resolution")
        finally:
            temp.cleanup()

    def test_08_red_escalation_routes_and_premium_boundary(self) -> None:
        self.assertEqual(classify_resolution("plan_strategy"), ("planning", False))
        self.assertEqual(classify_resolution("definition_authority"), ("definition", False))
        self.assertTrue(classify_route_completion(disposition="stop", obligation="premium_A").legal_return)

    def test_09_runtime_loss_consumes_durable_result_without_replay(self) -> None:
        h = self.helper()
        temp, project = h.copy_fixture()
        try:
            h.install_reviewable_result(project, "none")
            self.assertEqual(select_route(project, [MANIFEST]).obligation, "result_reconciliation")
            self.assertEqual(
                resume_action(durable_semantic_result=True, external_effect_uncertain=False),
                "reconcile_without_replay",
            )
        finally:
            temp.cleanup()

    def test_10_jit_predecessor_success_then_stale_failure(self) -> None:
        h = self.helper()
        temp, project = h.copy_fixture()
        try:
            path = "implementation/workstreams/sample-workstream/results/M01-T03.md"
            commit, blob = "a" * 40, "b" * 40
            h.install_done_predecessor(project, path=path, commit=commit, blob=blob)
            h.make_ready_card(project, dependencies=f"{path}@{commit}:{blob}")
            self.assertEqual(select_route(project, [MANIFEST]).obligation, "execution_prep")
            board = project / BOARD
            board.write_text(board.read_text().replace(f'commit = "{commit}"', f'commit = "{"c" * 40}"'))
            self.assertEqual(select_route(project, [MANIFEST]).disposition, "recovery")
        finally:
            temp.cleanup()

    def test_11_close_incomplete_continues_complete_ends_once(self) -> None:
        self.assertEqual(
            close_continuation(approved_scope_durably_complete=False, next_authorized_obligation=True, explicit_authorization_gate_due=False),
            "continue_deterministically",
        )
        self.assertEqual(
            close_continuation(approved_scope_durably_complete=True, next_authorized_obligation=False, explicit_authorization_gate_due=False),
            "end_of_scope_stop",
        )
        with self.assertRaises(CloseContractError):
            close_continuation(approved_scope_durably_complete=True, next_authorized_obligation=True, explicit_authorization_gate_due=False)

    def test_12_alignment_and_premium_boundaries_are_real_stops(self) -> None:
        for obligation in ("unresolved_user_or_product_decision", "premium_A", "premium_B", "premium_C"):
            with self.subTest(obligation=obligation):
                self.assertTrue(classify_route_completion(disposition="stop", obligation=obligation).legal_return)

    def test_13_remediable_recovery_continues_nonremediable_blocker_stops(self) -> None:
        self.assertEqual(classify_resolution("bounded_correction"), ("execution", False))
        self.assertEqual(classify_resolution("runtime_access_input"), ("blocker_stop", True))

    def test_14_same_fingerprint_without_progress_fails_closed(self) -> None:
        obs = ProgressObservation("route:execution:M05-T01", "evidence:1")
        with self.assertRaises(ContinuationContractError):
            classify_progress(previous=obs, current=obs)

    def test_15_semantic_cycle_without_new_evidence_fails_closed(self) -> None:
        previous = ProgressObservation("route:review:M05-T01", "evidence:1")
        current = ProgressObservation("route:execution:M05-T01", "evidence:1")
        with self.assertRaises(ContinuationContractError):
            classify_progress(previous=previous, current=current, seen=frozenset({(current.fingerprint, current.evidence_epoch)}))

    def test_16_uncertain_external_effect_is_readback_first(self) -> None:
        self.assertEqual(
            resume_action(durable_semantic_result=False, external_effect_uncertain=True),
            "readback_external_effect_before_retry",
        )
        self.assertEqual(
            external_effect_recovery_action(readback_state="pending", observation="unknown"),
            "readback_exact_target",
        )

    def test_17_runtime_model_session_noise_does_not_change_route(self) -> None:
        h = self.helper()
        temp, project = h.copy_fixture()
        try:
            semantics = []
            for noise in (
                {"RUNTIME": "chatgpt", "MODEL_ID": "one", "SESSION_ID": "a"},
                {"RUNTIME": "codex", "MODEL_ID": "two", "SESSION_ID": "b"},
            ):
                with patch.dict(os.environ, noise, clear=False):
                    r = select_route(project, [MANIFEST])
                semantics.append((r.disposition, r.obligation, r.subject, r.owner_module))
            self.assertEqual(semantics[0], semantics[1])
        finally:
            temp.cleanup()

    def test_18_explicit_user_stop_returns_immediately(self) -> None:
        decision = classify_route_completion(disposition="stop", obligation="explicit_user_stop")
        self.assertEqual(decision.action, "return")
        self.assertTrue(decision.legal_return)

    def test_19_non_boundary_transitions_have_no_synthetic_handoff(self) -> None:
        for obligation in ("post_review_finalization", "execution", "research", "close"):
            with self.subTest(obligation=obligation):
                decision = classify_route_completion(disposition="route", obligation=obligation)
                self.assertEqual(decision.action, "continue")
                self.assertFalse(decision.legal_return)
        self.assertEqual(
            review_delivery_policy(current_context_produced_subject=False, independent_context_available=False),
            HANDOFF_NONE,
        )


if __name__ == "__main__":
    unittest.main()
