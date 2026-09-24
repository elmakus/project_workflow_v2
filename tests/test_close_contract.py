from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

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
    verify_final_observation_reconciliation_from_board,
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


def _derived_snapshot(entries: dict[str, str]) -> dict[str, dict[str, str]]:
    return {
        observation_id: {"id": observation_id, "disposition": disposition}
        for observation_id, disposition in entries.items()
    }


def _reviewed_cleanup_work(
    work_id: str = "cleanup-O2",
    covers: tuple[str, ...] = ("O2",),
    **overrides: object,
) -> dict[str, object]:
    work: dict[str, object] = {
        "work_id": work_id,
        "subject": {
            "repository": "owner/repo",
            "commit": "a" * 40,
            "path": "results/cleanup-O2.md",
            "blob": "b" * 40,
        },
        "tests_evidence": ["tests/test_cleanup_o2.py"],
        "covers_observation_ids": list(covers),
        "complete": True,
        "independent_review_green": True,
    }
    work.update(overrides)
    return work


class FinalObservationReconciliationTests(unittest.TestCase):
    def test_pre_final_gate_accepts_only_five_terminal_dispositions(self) -> None:
        observations = [
            {"id": "O1", "disposition": "resolved"},
            {"id": "O2", "disposition": "cleanup_candidate"},
            {"id": "O3", "disposition": "deferred"},
            {"id": "O4", "disposition": "promoted"},
            {"id": "O5", "disposition": "tracked"},
        ]
        derived = _derived_snapshot({
            "O1": "resolved",
            "O2": "cleanup_candidate",
            "O3": "deferred",
            "O4": "promoted",
            "O5": "tracked",
        })
        self.assertEqual(
            verify_final_observation_reconciliation(
                observations=observations,
                derived_state=derived,
                cleanup_works=[_reviewed_cleanup_work()],
            ),
            "final_observation_reconciliation_complete",
        )
        self.assertEqual(
            verify_final_observation_reconciliation(
                observations=[], derived_state={}
            ),
            "final_observation_reconciliation_complete",
        )

    def test_pre_final_gate_blocks_unreconciled_open_observations(self) -> None:
        with self.assertRaisesRegex(CloseContractError, "unreconciled"):
            verify_final_observation_reconciliation(
                observations=[
                    {"id": "O1", "disposition": "resolved"},
                    {"id": "O2", "disposition": "open"},
                ],
                derived_state=_derived_snapshot({"O1": "resolved", "O2": "open"}),
            )
        with self.assertRaisesRegex(CloseContractError, "terminal disposition"):
            verify_final_observation_reconciliation(
                observations=[{"id": "O1", "disposition": "ignored"}],
                derived_state=_derived_snapshot({"O1": "ignored"}),
            )
        with self.assertRaisesRegex(CloseContractError, "explicit disposition"):
            verify_final_observation_reconciliation(
                observations=[{"id": "O1"}],
                derived_state=_derived_snapshot({"O1": "resolved"}),
            )

    def test_pre_final_gate_rejects_omitted_or_fabricated_observations(self) -> None:
        attempts = [{
            "attempt": "R01",
            "verdict": "green",
            "review_kind": "discovery",
            "review_epoch": "E01",
            "material_finding_ids": [],
            "evidence_path": "evidence/review-R01.md",
            "observations": [{
                "id": "O1", "category": "advisory",
                "evidence": "evidence/review-R01.md#O1",
                "disposition": "open", "disposition_basis": "",
            }],
        }]
        with self.assertRaisesRegex(CloseContractError, "omit"):
            verify_final_observation_reconciliation(
                observations=[], review_attempts=attempts
            )
        with self.assertRaisesRegex(CloseContractError, "derived disposition"):
            verify_final_observation_reconciliation(
                observations=[{"id": "O1", "disposition": "resolved"}],
                review_attempts=attempts,
            )
        with self.assertRaisesRegex(CloseContractError, "unknown observation"):
            verify_final_observation_reconciliation(
                observations=[
                    {"id": "O1", "disposition": "resolved"},
                    {"id": "O9", "disposition": "resolved"},
                ],
                derived_state=_derived_snapshot({"O1": "resolved"}),
            )
        with self.assertRaisesRegex(CloseContractError, "completeness"):
            verify_final_observation_reconciliation(observations=[])

    def test_cleanup_candidate_requires_completed_reviewed_covering_work(self) -> None:
        observations = [{"id": "O2", "disposition": "cleanup_candidate"}]
        derived = _derived_snapshot({"O2": "cleanup_candidate"})
        with self.assertRaisesRegex(CloseContractError, "cleanup"):
            verify_final_observation_reconciliation(
                observations=observations, derived_state=derived
            )
        incomplete = _reviewed_cleanup_work()
        incomplete["complete"] = False
        with self.assertRaisesRegex(CloseContractError, "cleanup"):
            verify_final_observation_reconciliation(
                observations=observations,
                derived_state=derived,
                cleanup_works=[incomplete],
            )
        unreviewed = _reviewed_cleanup_work()
        unreviewed["independent_review_green"] = False
        with self.assertRaisesRegex(CloseContractError, "independent review"):
            verify_final_observation_reconciliation(
                observations=observations,
                derived_state=derived,
                cleanup_works=[unreviewed],
            )
        with self.assertRaisesRegex(CloseContractError, "unknown observation"):
            verify_final_observation_reconciliation(
                observations=observations,
                derived_state=derived,
                cleanup_works=[_reviewed_cleanup_work(
                    work_id="cleanup-O9", covers=("O9",)
                )],
            )

    def test_final_gate_rejects_bare_boolean_and_out_of_scope_cleanup(self) -> None:
        observations = [{"id": "O2", "disposition": "cleanup_candidate"}]
        derived = _derived_snapshot({"O2": "cleanup_candidate"})
        bare = {
            "work_id": "cleanup-O2",
            "covers_observation_ids": ["O2"],
            "complete": True,
            "independent_review_green": True,
        }
        with self.assertRaisesRegex(CloseContractError, "exact subject"):
            verify_final_observation_reconciliation(
                observations=observations,
                derived_state=derived,
                cleanup_works=[bare],
            )
        speculative = _reviewed_cleanup_work(speculative_redesign=True)
        with self.assertRaisesRegex(CloseContractError, "speculative"):
            verify_final_observation_reconciliation(
                observations=observations,
                derived_state=derived,
                cleanup_works=[speculative],
            )
        new_scope = _reviewed_cleanup_work(new_product_scope=True)
        with self.assertRaisesRegex(CloseContractError, "product scope"):
            verify_final_observation_reconciliation(
                observations=observations,
                derived_state=derived,
                cleanup_works=[new_scope],
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
        with self.assertRaisesRegex(CloseContractError, "tests/evidence"):
            validate_cleanup_work(
                work_id="cleanup-O2",
                subject=subject,
                tests_evidence="tests/test_cleanup_o2.py",
                independent_review_green=True,
                covers_observation_ids=["O2"],
            )
        with self.assertRaisesRegex(CloseContractError, "grounded"):
            validate_cleanup_work(
                work_id="cleanup-O2",
                subject=subject,
                tests_evidence=["tests/test_cleanup_o2.py"],
                independent_review_green=True,
                covers_observation_ids="O2",
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
                derived_state=_derived_snapshot({"O1": "resolved"}),
                further_advisory_improvement_conceivable=True,
            ),
            "final_observation_reconciliation_complete",
        )


BOARD_WORKSTREAM = "sample-workstream"
BOARD_CARD = "M01-T01"
BOARD_PATH = f"implementation/workstreams/{BOARD_WORKSTREAM}/TASK_BOARD.toml"


def _write_attempt_toml(
    project: Path,
    attempt: str,
    *,
    verdict: str = "green",
    observations: str = "",
    observation_updates: str = "",
) -> str:
    review_path = (
        f"implementation/workstreams/{BOARD_WORKSTREAM}/reviews/{BOARD_CARD}-{attempt}.toml"
    )
    evidence = f"implementation/workstreams/{BOARD_WORKSTREAM}/evidence/review-{attempt}.md"
    path = project / review_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'workstream_id = "{BOARD_WORKSTREAM}"\n'
        f'card_id = "{BOARD_CARD}"\n'
        f'attempt = "{attempt}"\n'
        f'verdict = "{verdict}"\n'
        f'evidence_path = "{evidence}"\n'
        'review_kind = "discovery"\n'
        'source_discovery_attempt = ""\n'
        "discovery_complete = true\n"
        "material_finding_ids = []\n"
        + observations
        + observation_updates
        + "[subject]\n"
        'class = "git_blob"\n'
        'repository = "owner/fixture"\n'
        f'commit = "{"a" * 40}"\n'
        f'path = "implementation/workstreams/{BOARD_WORKSTREAM}/results/{BOARD_CARD}.md"\n'
        f'blob = "{"b" * 40}"\n'
        "[acceptance]\n"
        'class = "authority"\n'
        'path = "requirements/PROJECT_WORKFLOW_V2.md"\n'
        "[independence]\n"
        "materially_produced_or_repaired_subject = false\n"
        'basis = "Fresh semantic reviewer context."\n',
        encoding="utf-8",
    )
    return review_path


def _observation_table(entry_id: str, attempt: str, disposition: str = "open") -> str:
    evidence = f"implementation/workstreams/{BOARD_WORKSTREAM}/evidence/review-{attempt}.md"
    basis = "" if disposition == "open" else "Reconciled with concrete basis."
    return (
        "[[observations]]\n"
        f'id = "{entry_id}"\n'
        'category = "advisory"\n'
        f'evidence = "{evidence}#{entry_id}"\n'
        f'disposition = "{disposition}"\n'
        f'disposition_basis = "{basis}"\n'
    )


def _write_board_toml(project: Path, review_paths: list[str]) -> None:
    locators = ", ".join(
        f'{{ class = "review_attempt", path = "{review_path}" }}'
        for review_path in review_paths
    )
    path = project / BOARD_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'workstream_id = "{BOARD_WORKSTREAM}"\n'
        "revision = 1\n"
        "[execution_ref]\n"
        'branch = "work/pwv21-policy-kernel"\n'
        "[[cards]]\n"
        f'id = "{BOARD_CARD}"\n'
        'status = "in_progress"\n'
        f'contract = {{ class = "task_card", path = "implementation/workstreams/{BOARD_WORKSTREAM}/cards/{BOARD_CARD}.md" }}\n'
        f"review_attempts = [{locators}]\n",
        encoding="utf-8",
    )


class BoardBoundFinalGateTests(unittest.TestCase):
    def test_board_gate_rejects_omitted_known_open_observation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            review = _write_attempt_toml(
                project, "R01", observations=_observation_table("O1", "R01")
            )
            _write_board_toml(project, [review])
            with self.assertRaisesRegex(CloseContractError, "omit.*O1"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[],
                )

    def test_board_gate_reads_full_history_not_just_first_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            first = _write_attempt_toml(
                project, "R01", observations=_observation_table("O1", "R01")
            )
            second = _write_attempt_toml(
                project,
                "R02",
                observations=_observation_table("O2", "R02"),
                observation_updates="[[observation_updates]]\n"
                'id = "O1"\n'
                'disposition = "resolved"\n'
                'basis = "Fixed in R02."\n',
            )
            third = _write_attempt_toml(
                project,
                "R03",
                observation_updates="[[observation_updates]]\n"
                'id = "O2"\n'
                'disposition = "tracked"\n'
                'basis = "Exported as follow-up."\n',
            )
            _write_board_toml(project, [first, second, third])
            with self.assertRaisesRegex(CloseContractError, "omit.*O2"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[{"id": "O1", "disposition": "resolved"}],
                )
            self.assertEqual(
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[
                        {"id": "O1", "disposition": "resolved"},
                        {"id": "O2", "disposition": "tracked"},
                    ],
                ),
                "final_observation_reconciliation_complete",
            )

    def test_board_gate_detects_forged_disposition_against_durable_truth(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            review = _write_attempt_toml(
                project, "R01", observations=_observation_table("O1", "R01")
            )
            _write_board_toml(project, [review])
            with self.assertRaisesRegex(CloseContractError, "derived disposition"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[{"id": "O1", "disposition": "resolved"}],
                )

    def test_board_gate_fails_closed_on_dangling_attempt_locator(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            review = _write_attempt_toml(
                project, "R01", observations=_observation_table("O1", "R01")
            )
            missing = (
                f"implementation/workstreams/{BOARD_WORKSTREAM}/reviews/{BOARD_CARD}-R09.toml"
            )
            _write_board_toml(project, [review, missing])
            with self.assertRaisesRegex(CloseContractError, "review attempt"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[{"id": "O1", "disposition": "resolved"}],
                )

    def test_board_gate_accepts_proven_empty_history_and_reviewed_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _write_board_toml(project, [])
            self.assertEqual(
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[],
                ),
                "final_observation_reconciliation_complete",
            )
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            evidence = f"implementation/workstreams/{BOARD_WORKSTREAM}/evidence/review-R01.md"
            review = _write_attempt_toml(
                project,
                "R01",
                observations="[[observations]]\n"
                'id = "O2"\n'
                'category = "optional_cleanup"\n'
                f'evidence = "{evidence}#O2"\n'
                'disposition = "cleanup_candidate"\n'
                'disposition_basis = "Safe bounded cleanup."\n',
            )
            _write_board_toml(project, [review])
            self.assertEqual(
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[{"id": "O2", "disposition": "cleanup_candidate"}],
                    cleanup_works=[_reviewed_cleanup_work()],
                ),
                "final_observation_reconciliation_complete",
            )


if __name__ == "__main__":
    unittest.main()
