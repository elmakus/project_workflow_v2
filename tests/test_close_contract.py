from __future__ import annotations

import unittest

from tools.close_contract import (
    CloseContractError,
    RefreshSnapshot,
    classify_review_coverage,
    cleanup_branch_action,
    close_continuation,
    external_effect_recovery_action,
    reconcile_issue_readback,
    stacked_integration_path,
    tracker_pr_linkage,
    validate_cleanup_work,
    verify_final_observation_reconciliation,
    verify_pre_mutation_target,
    verify_target_side_recovery,
    verify_terminal_unmerged_closure,
)


def snap(
    target: str,
    *,
    content: str = "content-A",
    behavior: str = "behavior-A",
    acceptance: frozenset[str] = frozenset({"A08", "A09"}),
) -> RefreshSnapshot:
    return RefreshSnapshot(target, content, behavior, acceptance)


class CloseRefreshTests(unittest.TestCase):
    def test_target_sha_movement_alone_reuses_green_review(self) -> None:
        self.assertEqual(
            classify_review_coverage(
                snap("target-old"),
                snap("target-new"),
                affected_compatibility_green=True,
            ),
            "reuse_green_review",
        )

    def test_stronger_review_coverage_may_be_reused(self) -> None:
        reviewed = snap(
            "target-old",
            acceptance=frozenset({"A08", "A09", "extra-check"}),
        )
        current = snap("target-new", acceptance=frozenset({"A08", "A09"}))
        self.assertEqual(
            classify_review_coverage(
                reviewed, current, affected_compatibility_green=True
            ),
            "reuse_green_review",
        )

    def test_new_required_acceptance_creates_new_subject(self) -> None:
        reviewed = snap("target-old")
        current = snap(
            "target-new",
            acceptance=frozenset({"A08", "A09", "new-required-check"}),
        )
        self.assertEqual(
            classify_review_coverage(
                reviewed, current, affected_compatibility_green=True
            ),
            "new_review_subject",
        )

    def test_changed_content_creates_new_subject_even_when_merge_can_be_clean(self) -> None:
        self.assertEqual(
            classify_review_coverage(
                snap("target-old"),
                snap("target-new", content="content-B"),
                affected_compatibility_green=True,
            ),
            "new_review_subject",
        )

    def test_changed_behavior_creates_new_subject(self) -> None:
        self.assertEqual(
            classify_review_coverage(
                snap("target-old"),
                snap("target-new", behavior="behavior-B"),
                affected_compatibility_green=True,
            ),
            "new_review_subject",
        )

    def test_unchanged_surface_without_green_compatibility_fails_closed(self) -> None:
        with self.assertRaises(CloseContractError):
            classify_review_coverage(
                snap("target-old"),
                snap("target-new"),
                affected_compatibility_green=False,
            )

    def test_target_race_requires_refresh_repeat(self) -> None:
        with self.assertRaises(CloseContractError):
            verify_pre_mutation_target("refreshed-target", "moved-target")
        verify_pre_mutation_target("same-target", "same-target")

    def test_stacked_paths_do_not_require_parent_branch_survival(self) -> None:
        self.assertEqual(
            stacked_integration_path(
                genuine_parent_only_dependency=True,
                dependency_accepted_in_target=False,
            ),
            "fold_child_into_parent",
        )
        self.assertEqual(
            stacked_integration_path(
                genuine_parent_only_dependency=True,
                dependency_accepted_in_target=True,
            ),
            "integrate_child_independently",
        )
        self.assertEqual(
            stacked_integration_path(
                genuine_parent_only_dependency=False,
                dependency_accepted_in_target=False,
            ),
            "integrate_child_independently",
        )


    def test_external_effect_recovery_requires_readback_before_retry(self) -> None:
        self.assertEqual(
            external_effect_recovery_action(
                readback_state="pending", observation="unknown"
            ),
            "readback_exact_target",
        )
        with self.assertRaisesRegex(CloseContractError, "fail closed without retry"):
            external_effect_recovery_action(
                readback_state="uncertain", observation="unknown"
            )

    def test_verified_external_effect_selects_idempotent_continuation(self) -> None:
        self.assertEqual(
            external_effect_recovery_action(
                readback_state="verified", observation="no_effect"
            ),
            "retry_allowed",
        )
        self.assertEqual(
            external_effect_recovery_action(
                readback_state="verified", observation="expected_effect"
            ),
            "reconcile_without_retry",
        )
        self.assertEqual(
            external_effect_recovery_action(
                readback_state="verified", observation="unexpected_effect"
            ),
            "reconcile_unexpected_effect",
        )

    def test_tracker_closing_linkage_is_final_default_branch_only(self) -> None:
        self.assertEqual(
            tracker_pr_linkage(
                tracker_linked=True,
                final_scope_completing=False,
                target_is_default_branch=True,
            ),
            "reference_only",
        )
        self.assertEqual(
            tracker_pr_linkage(
                tracker_linked=True,
                final_scope_completing=True,
                target_is_default_branch=False,
            ),
            "reference_only",
        )
        self.assertEqual(
            tracker_pr_linkage(
                tracker_linked=True,
                final_scope_completing=True,
                target_is_default_branch=True,
            ),
            "closing_linkage",
        )

    def test_issue_readback_never_turns_early_close_into_approval(self) -> None:
        self.assertEqual(
            reconcile_issue_readback(
                accepted_scope_durably_complete=False,
                observed_issue_state="closed",
                automatic_close_available=True,
            ),
            "reconcile_unexpected_early_close",
        )
        self.assertEqual(
            reconcile_issue_readback(
                accepted_scope_durably_complete=False,
                observed_issue_state="open",
                automatic_close_available=True,
            ),
            "keep_open",
        )

    def test_issue_fallback_close_requires_accepted_completion(self) -> None:
        self.assertEqual(
            reconcile_issue_readback(
                accepted_scope_durably_complete=True,
                observed_issue_state="closed",
                automatic_close_available=True,
            ),
            "verified_closed",
        )
        self.assertEqual(
            reconcile_issue_readback(
                accepted_scope_durably_complete=True,
                observed_issue_state="open",
                automatic_close_available=False,
            ),
            "explicit_close_allowed",
        )
        self.assertEqual(
            reconcile_issue_readback(
                accepted_scope_durably_complete=True,
                observed_issue_state="open",
                automatic_close_available=True,
            ),
            "reconcile_missing_automatic_close",
        )


    def test_target_side_recovery_does_not_require_live_source_ref(self) -> None:
        self.assertEqual(
            verify_target_side_recovery(
                source_branch="feat/example",
                source_head="source-head",
                merged_source_head="source-head",
                target_package_subject_head="source-head",
                immutable_merge_evidence=True,
                required_artifacts=frozenset({"manifest", "board", "evidence"}),
                present_artifacts=frozenset({"manifest", "board", "evidence", "card"}),
            ),
            "source_ref_independent_recovery",
        )

    def test_target_side_recovery_fails_when_unique_artifact_is_missing(self) -> None:
        with self.assertRaisesRegex(CloseContractError, "missing unique recovery artifacts"):
            verify_target_side_recovery(
                source_branch="feat/example",
                source_head="source-head",
                merged_source_head="source-head",
                target_package_subject_head="source-head",
                immutable_merge_evidence=True,
                required_artifacts=frozenset({"manifest", "board", "evidence"}),
                present_artifacts=frozenset({"manifest", "board"}),
            )

    def test_cleanup_treats_auto_deleted_source_as_normal_success(self) -> None:
        self.assertEqual(
            cleanup_branch_action(
                terminal_package_independent=True,
                source_ref_exists=False,
                current_head="",
                cleanup_state="none",
                verified_head="",
            ),
            "automatic_cleanup_complete",
        )

    def test_safe_to_delete_revalidates_exact_head_before_delete(self) -> None:
        self.assertEqual(
            cleanup_branch_action(
                terminal_package_independent=True,
                source_ref_exists=True,
                current_head="same-head",
                cleanup_state="safe_to_delete",
                verified_head="same-head",
            ),
            "delete_exact_ref",
        )
        with self.assertRaisesRegex(CloseContractError, "head is stale"):
            cleanup_branch_action(
                terminal_package_independent=True,
                source_ref_exists=True,
                current_head="moved-head",
                cleanup_state="safe_to_delete",
                verified_head="old-head",
            )

    def test_absence_readback_is_required_before_deleted_state(self) -> None:
        self.assertEqual(
            cleanup_branch_action(
                terminal_package_independent=True,
                source_ref_exists=False,
                current_head="",
                cleanup_state="safe_to_delete",
                verified_head="old-head",
            ),
            "record_deleted_after_absence_readback",
        )
        with self.assertRaisesRegex(CloseContractError, "contradicts surviving source ref"):
            cleanup_branch_action(
                terminal_package_independent=True,
                source_ref_exists=True,
                current_head="old-head",
                cleanup_state="deleted",
                verified_head="old-head",
            )

    def test_terminal_unmerged_closure_preserves_history_without_code(self) -> None:
        self.assertEqual(
            verify_terminal_unmerged_closure(
                closure_package_present=True,
                history_artifacts_complete=True,
                implementation_content_in_target=False,
            ),
            "unmerged_history_preserved",
        )
        with self.assertRaisesRegex(CloseContractError, "must not import rejected implementation"):
            verify_terminal_unmerged_closure(
                closure_package_present=True,
                history_artifacts_complete=True,
                implementation_content_in_target=True,
            )

    def test_end_of_scope_requires_durable_completion(self) -> None:
        self.assertEqual(
            close_continuation(
                approved_scope_durably_complete=True,
                next_authorized_obligation=False,
                explicit_authorization_gate_due=False,
            ),
            "end_of_scope_stop",
        )
        self.assertEqual(
            close_continuation(
                approved_scope_durably_complete=False,
                next_authorized_obligation=True,
                explicit_authorization_gate_due=False,
            ),
            "continue_deterministically",
        )
        self.assertEqual(
            close_continuation(
                approved_scope_durably_complete=False,
                next_authorized_obligation=False,
                explicit_authorization_gate_due=False,
            ),
            "continue_close_reconciliation",
        )

    def test_live_write_alone_does_not_create_stop_but_explicit_gate_does(self) -> None:
        self.assertEqual(
            close_continuation(
                approved_scope_durably_complete=False,
                next_authorized_obligation=True,
                explicit_authorization_gate_due=False,
                deployment_or_live_write=True,
            ),
            "continue_deterministically",
        )
        self.assertEqual(
            close_continuation(
                approved_scope_durably_complete=False,
                next_authorized_obligation=True,
                explicit_authorization_gate_due=True,
                deployment_or_live_write=True,
            ),
            "authorization_stop",
        )

    def test_terminal_scope_cannot_claim_an_authorized_remaining_obligation(self) -> None:
        with self.assertRaisesRegex(CloseContractError, "cannot be terminal"):
            close_continuation(
                approved_scope_durably_complete=True,
                next_authorized_obligation=True,
                explicit_authorization_gate_due=False,
            )


class FinalObservationReconciliationTests(unittest.TestCase):
    def test_pre_final_gate_accepts_only_five_terminal_dispositions(self) -> None:
        observations = [
            {"id": "O1", "disposition": "resolved"},
            {"id": "O2", "disposition": "cleanup_candidate"},
            {"id": "O3", "disposition": "deferred"},
            {"id": "O4", "disposition": "promoted"},
            {"id": "O5", "disposition": "tracked"},
        ]
        self.assertEqual(
            verify_final_observation_reconciliation(
                observations=observations,
                cleanup_works=[{
                    "work_id": "cleanup-O2",
                    "covers_observation_ids": ["O2"],
                    "complete": True,
                    "independent_review_green": True,
                }],
            ),
            "final_observation_reconciliation_complete",
        )
        self.assertEqual(
            verify_final_observation_reconciliation(observations=[]),
            "final_observation_reconciliation_complete",
        )

    def test_pre_final_gate_blocks_unreconciled_open_observations(self) -> None:
        with self.assertRaisesRegex(CloseContractError, "unreconciled"):
            verify_final_observation_reconciliation(
                observations=[
                    {"id": "O1", "disposition": "resolved"},
                    {"id": "O2", "disposition": "open"},
                ]
            )
        with self.assertRaisesRegex(CloseContractError, "terminal disposition"):
            verify_final_observation_reconciliation(
                observations=[{"id": "O1", "disposition": "ignored"}]
            )
        with self.assertRaisesRegex(CloseContractError, "explicit disposition"):
            verify_final_observation_reconciliation(observations=[{"id": "O1"}])

    def test_cleanup_candidate_requires_completed_reviewed_covering_work(self) -> None:
        observations = [{"id": "O2", "disposition": "cleanup_candidate"}]
        with self.assertRaisesRegex(CloseContractError, "cleanup"):
            verify_final_observation_reconciliation(observations=observations)
        with self.assertRaisesRegex(CloseContractError, "cleanup"):
            verify_final_observation_reconciliation(
                observations=observations,
                cleanup_works=[{
                    "work_id": "cleanup-O2",
                    "covers_observation_ids": ["O2"],
                    "complete": False,
                    "independent_review_green": True,
                }],
            )
        with self.assertRaisesRegex(CloseContractError, "independent review"):
            verify_final_observation_reconciliation(
                observations=observations,
                cleanup_works=[{
                    "work_id": "cleanup-O2",
                    "covers_observation_ids": ["O2"],
                    "complete": True,
                    "independent_review_green": False,
                }],
            )
        with self.assertRaisesRegex(CloseContractError, "unknown observation"):
            verify_final_observation_reconciliation(
                observations=observations,
                cleanup_works=[{
                    "work_id": "cleanup-O9",
                    "covers_observation_ids": ["O9"],
                    "complete": True,
                    "independent_review_green": True,
                }],
            )

    def test_cleanup_work_requires_exact_subject_tests_and_independent_review(self) -> None:
        subject = {
            "repository": "owner/repo",
            "commit": "a" * 40,
            "path": "results/cleanup-O2.md",
            "blob": "b" * 40,
        }
        self.assertEqual(
            validate_cleanup_work(
                work_id="cleanup-O2",
                subject=subject,
                tests_evidence=["tests/test_cleanup_o2.py"],
                independent_review_green=True,
                covers_observation_ids=["O2"],
            ),
            "cleanup_work_complete",
        )
        with self.assertRaisesRegex(CloseContractError, "exact subject"):
            validate_cleanup_work(
                work_id="cleanup-O2",
                subject={"repository": "owner/repo", "path": "results/cleanup-O2.md"},
                tests_evidence=["tests/test_cleanup_o2.py"],
                independent_review_green=True,
                covers_observation_ids=["O2"],
            )
        with self.assertRaisesRegex(CloseContractError, "tests/evidence"):
            validate_cleanup_work(
                work_id="cleanup-O2",
                subject=subject,
                tests_evidence=[],
                independent_review_green=True,
                covers_observation_ids=["O2"],
            )
        with self.assertRaisesRegex(CloseContractError, "independent review"):
            validate_cleanup_work(
                work_id="cleanup-O2",
                subject=subject,
                tests_evidence=["tests/test_cleanup_o2.py"],
                independent_review_green=False,
                covers_observation_ids=["O2"],
            )
        with self.assertRaisesRegex(CloseContractError, "grounded"):
            validate_cleanup_work(
                work_id="cleanup-O2",
                subject=subject,
                tests_evidence=["tests/test_cleanup_o2.py"],
                independent_review_green=True,
                covers_observation_ids=[],
            )

    def test_cleanup_rejects_speculative_redesign_and_new_product_scope(self) -> None:
        subject = {
            "repository": "owner/repo",
            "commit": "a" * 40,
            "path": "results/cleanup-O2.md",
            "blob": "b" * 40,
        }
        with self.assertRaisesRegex(CloseContractError, "speculative"):
            validate_cleanup_work(
                work_id="cleanup-O2",
                subject=subject,
                tests_evidence=["tests/test_cleanup_o2.py"],
                independent_review_green=True,
                covers_observation_ids=["O2"],
                speculative_redesign=True,
            )
        with self.assertRaisesRegex(CloseContractError, "product scope"):
            validate_cleanup_work(
                work_id="cleanup-O2",
                subject=subject,
                tests_evidence=["tests/test_cleanup_o2.py"],
                independent_review_green=True,
                covers_observation_ids=["O2"],
                new_product_scope=True,
            )

    def test_final_reconciliation_terminates_despite_conceivable_further_advisories(self) -> None:
        self.assertEqual(
            verify_final_observation_reconciliation(
                observations=[{"id": "O1", "disposition": "resolved"}],
                further_advisory_improvement_conceivable=True,
            ),
            "final_observation_reconciliation_complete",
        )


if __name__ == "__main__":
    unittest.main()
