from __future__ import annotations

import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from tools.close_contract import (
    CloseContractError,
    H017RecoveryProof,
    _h017_compute_package_digest,
    RefreshSnapshot,
    _select_cleanup_readback_action,
    classify_review_coverage,
    cleanup_branch_action,
    close_continuation,
    derive_recovery_package_from_board,
    external_effect_recovery_action,
    reconcile_issue_readback,
    stacked_integration_path,
    tracker_pr_linkage,
    validate_cleanup_work,
    verify_final_observation_reconciliation,
    verify_final_observation_reconciliation_from_board,
    verify_pre_mutation_target,
    verify_target_side_recovery,
    verify_target_side_recovery_from_board,
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


    def test_target_side_recovery_rejects_caller_attested_sets(self) -> None:
        # H017 retired the bypass this case used to encode: even textually
        # complete caller-supplied sets can never yield independence.
        with self.assertRaisesRegex(CloseContractError, "caller-attested"):
            verify_target_side_recovery(
                source_branch="feat/example",
                source_head="source-head",
                merged_source_head="source-head",
                target_package_subject_head="source-head",
                immutable_merge_evidence=True,
                required_artifacts=frozenset({"manifest", "board", "evidence"}),
                present_artifacts=frozenset({"manifest", "board", "evidence", "card"}),
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
            _select_cleanup_readback_action(
                package_independent=True,
                source_ref_exists=False,
                current_head="",
                cleanup_state="none",
                verified_head="",
            ),
            "automatic_cleanup_complete",
        )

    def test_safe_to_delete_revalidates_exact_head_before_delete(self) -> None:
        self.assertEqual(
            _select_cleanup_readback_action(
                package_independent=True,
                source_ref_exists=True,
                current_head="same-head",
                cleanup_state="safe_to_delete",
                verified_head="same-head",
            ),
            "delete_exact_ref",
        )
        with self.assertRaisesRegex(CloseContractError, "head is stale"):
            _select_cleanup_readback_action(
                package_independent=True,
                source_ref_exists=True,
                current_head="moved-head",
                cleanup_state="safe_to_delete",
                verified_head="old-head",
            )

    def test_absence_readback_is_required_before_deleted_state(self) -> None:
        self.assertEqual(
            _select_cleanup_readback_action(
                package_independent=True,
                source_ref_exists=False,
                current_head="",
                cleanup_state="safe_to_delete",
                verified_head="old-head",
            ),
            "record_deleted_after_absence_readback",
        )
        with self.assertRaisesRegex(CloseContractError, "contradicts surviving source ref"):
            _select_cleanup_readback_action(
                package_independent=True,
                source_ref_exists=True,
                current_head="old-head",
                cleanup_state="deleted",
                verified_head="old-head",
            )

    def test_public_cleanup_rejects_caller_attested_independence(self) -> None:
        # The old terminal_package_independent=True bypass is gone: the
        # parameter no longer exists and booleans fail proof integrity.
        with self.assertRaises(TypeError):
            cleanup_branch_action(  # type: ignore[call-arg]
                terminal_package_independent=True,
                source_ref_exists=True,
                current_head="same-head",
                cleanup_state="safe_to_delete",
                verified_head="same-head",
            )
        for bogus in (True, None, "proof", 1):
            with self.assertRaisesRegex(CloseContractError, "fresh durable Board"):
                cleanup_branch_action(
                    recovery_proof=bogus,  # type: ignore[arg-type]
                    source_ref_exists=True,
                    current_head="same-head",
                    cleanup_state="safe_to_delete",
                    verified_head="same-head",
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
        'class = "task_card"\n'
        f'path = "implementation/workstreams/{BOARD_WORKSTREAM}/cards/{BOARD_CARD}.md"\n'
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
            commit, blob = _git_identity_for(project, review)
            _write_board_toml_exact(project, [(review, commit, blob)])
            with self.assertRaisesRegex(CloseContractError, "omit.*O1"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[],
                    project_repository="owner/fixture",
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
            first_commit, first_blob = _git_identity_for(project, first)
            second_commit, second_blob = _git_identity_for(project, second)
            third_commit, third_blob = _git_identity_for(project, third)
            _write_board_toml_exact(project, [
                (first, first_commit, first_blob),
                (second, second_commit, second_blob),
                (third, third_commit, third_blob),
            ])
            with self.assertRaisesRegex(CloseContractError, "omit.*O2"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[{"id": "O1", "disposition": "resolved"}],
                    project_repository="owner/fixture",
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
                    project_repository="owner/fixture",
                ),
                "final_observation_reconciliation_complete",
            )

    def test_board_gate_detects_forged_disposition_against_durable_truth(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            review = _write_attempt_toml(
                project, "R01", observations=_observation_table("O1", "R01")
            )
            commit, blob = _git_identity_for(project, review)
            _write_board_toml_exact(project, [(review, commit, blob)])
            with self.assertRaisesRegex(CloseContractError, "derived disposition"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[{"id": "O1", "disposition": "resolved"}],
                    project_repository="owner/fixture",
                )

    def test_board_gate_fails_closed_on_dangling_attempt_locator(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            review = _write_attempt_toml(
                project, "R01", observations=_observation_table("O1", "R01")
            )
            commit, blob = _git_identity_for(project, review)
            missing = (
                f"implementation/workstreams/{BOARD_WORKSTREAM}/reviews/{BOARD_CARD}-R09.toml"
            )
            _write_board_toml_exact(project, [
                (review, commit, blob),
                (missing, commit, "f" * 40),
            ])
            with self.assertRaisesRegex(CloseContractError, "review attempt"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[{"id": "O1", "disposition": "resolved"}],
                    project_repository="owner/fixture",
                )

    def test_board_gate_accepts_proven_empty_history_and_reviewed_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _write_board_toml(project, [])
            _git_identity_for(project, BOARD_PATH)
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
            commit, blob = _git_identity_for(project, review)
            _write_board_toml_exact(project, [(review, commit, blob)])
            self.assertEqual(
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[{"id": "O2", "disposition": "cleanup_candidate"}],
                    cleanup_works=[_reviewed_cleanup_work()],
                    project_repository="owner/fixture",
                ),
                "final_observation_reconciliation_complete",
            )


def _write_board_toml_exact(
    project: Path, entries: list[tuple[str, str, str]]
) -> None:
    locators = ", ".join(
        f'{{ class = "review_attempt", path = "{path}", '
        f'commit = "{commit}", blob = "{blob}" }}'
        for path, commit, blob in entries
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


def _git_identity_for(project: Path, relpath: str) -> tuple[str, str]:
    if not (project / ".git").exists():
        subprocess.run(["git", "init", "-q", str(project)], check=True)
        subprocess.run(
            ["git", "-C", str(project), "config", "user.email", "fixture@example.invalid"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(project), "config", "user.name", "Fixture"],
            check=True,
        )
    subprocess.run(["git", "-C", str(project), "add", relpath], check=True)
    subprocess.run(
        ["git", "-C", str(project), "commit", "-q", "-m", f"fixture {relpath}"],
        check=True,
    )
    commit = subprocess.run(
        ["git", "-C", str(project), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    blob = subprocess.run(
        ["git", "-C", str(project), "rev-parse", f"HEAD:{relpath}"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return commit, blob


class H018CompleteHistoryTests(unittest.TestCase):
    def test_truncated_board_with_durable_attempt_fails(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            review = _write_attempt_toml(
                project, "R01", observations=_observation_table("O1", "R01")
            )
            _git_identity_for(project, review)
            _write_board_toml(project, [])
            with self.assertRaisesRegex(CloseContractError, "omits durable"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[],
                )

    def test_listed_board_cannot_omit_known_observation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            review = _write_attempt_toml(
                project, "R01", observations=_observation_table("O1", "R01")
            )
            commit, blob = _git_identity_for(project, review)
            _write_board_toml_exact(project, [(review, commit, blob)])
            with self.assertRaisesRegex(CloseContractError, "omit.*O1"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[],
                    project_repository="owner/fixture",
                )

    def test_orphan_durable_attempt_fails(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            first = _write_attempt_toml(
                project, "R01", observations=_observation_table("O1", "R01")
            )
            second = _write_attempt_toml(
                project, "R02", observations=_observation_table("O2", "R02")
            )
            first_commit, first_blob = _git_identity_for(project, first)
            _git_identity_for(project, second)
            _write_board_toml_exact(project, [(first, first_commit, first_blob)])
            with self.assertRaisesRegex(CloseContractError, "omits durable.*R02"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[],
                    project_repository="owner/fixture",
                )

    def test_duplicate_board_locator_fails(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            review = _write_attempt_toml(
                project, "R01", observations=_observation_table("O1", "R01")
            )
            commit, blob = _git_identity_for(project, review)
            _write_board_toml_exact(project, [
                (review, commit, blob),
                (review, commit, blob),
            ])
            with self.assertRaisesRegex(CloseContractError, "duplicate.*locator"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[{"id": "O1", "disposition": "resolved"}],
                    project_repository="owner/fixture",
                )

    def test_sibling_filename_attempt_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            review_path = (
                f"implementation/workstreams/{BOARD_WORKSTREAM}/reviews/{BOARD_CARD}-R01.toml"
            )
            path = project / review_path
            path.parent.mkdir(parents=True, exist_ok=True)
            evidence = f"implementation/workstreams/{BOARD_WORKSTREAM}/evidence/review-R02.md"
            path.write_text(
                f'workstream_id = "{BOARD_WORKSTREAM}"\n'
                f'card_id = "{BOARD_CARD}"\n'
                'attempt = "R02"\n'
                'verdict = "green"\n'
                f'evidence_path = "{evidence}"\n'
                'review_kind = "discovery"\n'
                'source_discovery_attempt = ""\n'
                "discovery_complete = true\n"
                "material_finding_ids = []\n"
                "[subject]\n"
                'class = "git_blob"\n'
                'repository = "owner/fixture"\n'
                f'commit = "{"a" * 40}"\n'
                f'path = "implementation/workstreams/{BOARD_WORKSTREAM}/results/{BOARD_CARD}.md"\n'
                f'blob = "{"b" * 40}"\n'
                "[acceptance]\n"
                'class = "task_card"\n'
                f'path = "implementation/workstreams/{BOARD_WORKSTREAM}/cards/{BOARD_CARD}.md"\n'
                "[independence]\n"
                "materially_produced_or_repaired_subject = false\n"
                'basis = "Fresh semantic reviewer context."\n',
                encoding="utf-8",
            )
            commit, blob = _git_identity_for(project, review_path)
            _write_board_toml_exact(project, [(review_path, commit, blob)])
            with self.assertRaisesRegex(CloseContractError, "identity"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[],
                    project_repository="owner/fixture",
                )

    def test_genuinely_empty_inventory_completes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _write_board_toml(project, [])
            reviews_dir = project / f"implementation/workstreams/{BOARD_WORKSTREAM}/reviews"
            reviews_dir.mkdir(parents=True, exist_ok=True)
            _git_identity_for(project, BOARD_PATH)
            self.assertEqual(
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[],
                ),
                "final_observation_reconciliation_complete",
            )

    def test_git_unavailable_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _write_board_toml(project, [])
            with self.assertRaisesRegex(CloseContractError, "cannot read durable Git"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[],
                )

    def test_path_only_explicit_attempt_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            review = _write_attempt_toml(
                project, "R01", observations=_observation_table("O1", "R01")
            )
            _git_identity_for(project, review)
            _write_board_toml(project, [review])
            with self.assertRaisesRegex(CloseContractError, "identity|path-only|commit"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[],
                    project_repository="owner/fixture",
                )

    def test_fully_reconciled_positive_continues(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            first = _write_attempt_toml(
                project, "R01", observations=_observation_table("O1", "R01")
            )
            second = _write_attempt_toml(
                project,
                "R02",
                observation_updates="[[observation_updates]]\n"
                'id = "O1"\n'
                'disposition = "resolved"\n'
                'basis = "Fixed in R02."\n',
            )
            first_commit, first_blob = _git_identity_for(project, first)
            second_commit, second_blob = _git_identity_for(project, second)
            _write_board_toml_exact(project, [
                (first, first_commit, first_blob),
                (second, second_commit, second_blob),
            ])
            self.assertEqual(
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[{"id": "O1", "disposition": "resolved"}],
                    project_repository="owner/fixture",
                ),
                "final_observation_reconciliation_complete",
            )

    def test_git_head_inventory_catches_worktree_deleted_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            review = _write_attempt_toml(
                project, "R01", observations=_observation_table("O1", "R01")
            )
            _git_identity_for(project, review)
            (project / review).unlink()
            _write_board_toml(project, [])
            with self.assertRaisesRegex(CloseContractError, "omits durable.*R01"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[],
                )

    def test_git_exact_locator_positive_continues(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            review = _write_attempt_toml(
                project,
                "R01",
                observations=_observation_table("O1", "R01", disposition="resolved"),
            )
            commit, blob = _git_identity_for(project, review)
            _write_board_toml_exact(project, [(review, commit, blob)])
            self.assertEqual(
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[{"id": "O1", "disposition": "resolved"}],
                    project_repository="owner/fixture",
                ),
                "final_observation_reconciliation_complete",
            )

    def test_git_stale_locator_fails(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            review = _write_attempt_toml(
                project,
                "R01",
                observations=_observation_table("O1", "R01", disposition="resolved"),
            )
            commit, blob = _git_identity_for(project, review)
            (project / review).write_text(
                (project / review).read_text(encoding="utf-8") + "\n# stale mutation\n",
                encoding="utf-8",
            )
            _write_board_toml_exact(project, [(review, commit, blob)])
            with self.assertRaisesRegex(CloseContractError, "identity|mutated|stale"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[{"id": "O1", "disposition": "resolved"}],
                    project_repository="owner/fixture",
                )

    def test_git_history_inventory_catches_deleted_committed_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            review = _write_attempt_toml(
                project, "R01", observations=_observation_table("O1", "R01")
            )
            _git_identity_for(project, review)
            (project / review).unlink()
            subprocess.run(
                ["git", "-C", str(project), "add", "-u", review], check=True
            )
            subprocess.run(
                ["git", "-C", str(project), "commit", "-q", "-m", "delete attempt"],
                check=True,
            )
            _write_board_toml(project, [])
            with self.assertRaisesRegex(CloseContractError, "omits durable.*R01"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[],
                )

    def test_git_terminal_rewrite_with_rebound_locator_fails(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            review = _write_attempt_toml(
                project, "R01", observations=_observation_table("O1", "R01")
            )
            _git_identity_for(project, review)
            _write_attempt_toml(
                project,
                "R01",
                observations=_observation_table("O1", "R01", disposition="resolved"),
            )
            commit, blob = _git_identity_for(project, review)
            _write_board_toml_exact(project, [(review, commit, blob)])
            with self.assertRaisesRegex(CloseContractError, "append-only|rewritten"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[{"id": "O1", "disposition": "resolved"}],
                    project_repository="owner/fixture",
                )

    def test_git_merge_side_branch_addition_cannot_disappear(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _write_board_toml(project, [])
            _git_identity_for(project, BOARD_PATH)
            subprocess.run(
                ["git", "-C", str(project), "branch", "-M", "main"], check=True
            )
            subprocess.run(
                ["git", "-C", str(project), "checkout", "-qb", "side"], check=True
            )
            review = _write_attempt_toml(
                project, "R09", observations=_observation_table("O9", "R09")
            )
            subprocess.run(["git", "-C", str(project), "add", review], check=True)
            subprocess.run(
                ["git", "-C", str(project), "commit", "-q", "-m", "side add R09"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(project), "checkout", "-q", "main"], check=True
            )
            other = project / "other.txt"
            other.write_text("main advance\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(project), "add", "other.txt"], check=True)
            subprocess.run(
                ["git", "-C", str(project), "commit", "-q", "-m", "main advance"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(project), "merge", "--no-commit", "side"],
                check=True,
            )
            (project / review).unlink()
            subprocess.run(["git", "-C", str(project), "add", "-A"], check=True)
            subprocess.run(
                ["git", "-C", str(project), "commit", "-q", "-m", "merge dropping R09"],
                check=True,
            )
            with self.assertRaisesRegex(CloseContractError, "omits durable.*R09"):
                verify_final_observation_reconciliation_from_board(
                    project_root=project,
                    board_path=BOARD_PATH,
                    card_id=BOARD_CARD,
                    observations=[],
                )


class H017LegacyEmptyPackageTests(unittest.TestCase):
    def test_legacy_empty_required_present_cannot_yield_independent_recovery(self) -> None:
        with self.assertRaisesRegex(CloseContractError, "empty|completeness|genuinely"):
            verify_target_side_recovery(
                source_branch="feat/example",
                source_head="source-head",
                merged_source_head="source-head",
                target_package_subject_head="source-head",
                immutable_merge_evidence=True,
                required_artifacts=frozenset(),
                present_artifacts=frozenset(),
            )


H017_WORKSTREAM_PATH = (
    f"implementation/workstreams/{BOARD_WORKSTREAM}/WORKSTREAM.toml"
)
H017_CARD_PATH = (
    f"implementation/workstreams/{BOARD_WORKSTREAM}/cards/{BOARD_CARD}.md"
)
H017_RESULT_PATH = (
    f"implementation/workstreams/{BOARD_WORKSTREAM}/results/{BOARD_CARD}.md"
)
H017_EVIDENCE_PATH = (
    f"implementation/workstreams/{BOARD_WORKSTREAM}/evidence/{BOARD_CARD}-evidence.md"
)
H017_REVIEW_EVIDENCE_PATH = (
    f"implementation/workstreams/{BOARD_WORKSTREAM}/evidence/review-R01.md"
)


def _h017_write_workstream(project: Path, branch: str = "work/h017-fixture") -> None:
    path = project / H017_WORKSTREAM_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'workstream_id = "{BOARD_WORKSTREAM}"\n'
        'kind = "feature"\n'
        f'branch = "{branch}"\n'
        f'created_from = "{"a" * 40}"\n'
        'integration_target = "main"\n'
        'authority = [{ class = "authority", path = "workflow/CLOSE.md" }]\n'
        "\n[task_board]\n"
        'class = "task_board"\n'
        f'path = "{BOARD_PATH}"\n',
        encoding="utf-8",
    )


def _h017_write_card(project: Path) -> None:
    path = project / H017_CARD_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# Task Card — {BOARD_CARD}\n\n"
        f"- Card ID: {BOARD_CARD}\n"
        "- Included scope: H017 derived recovery package fixture.\n"
        "- Excluded scope: H019 cleanup semantic proof.\n"
        "- Authority refs: workflow/CLOSE.md\n"
        "- Dependencies: none\n"
        "- Acceptance: Derived package proves every required class.\n"
        "- Required tests/readback: H017 fixtures.\n"
        "- Review requirement: required\n"
        "- Technical contract: none\n",
        encoding="utf-8",
    )


def _h017_write_result(project: Path, evidence_refs: list[str]) -> None:
    path = project / H017_RESULT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    refs = ", ".join(evidence_refs)
    path.write_text(
        "# Card Result\n\n"
        f"- Card ID: {BOARD_CARD}\n"
        "- Implementation subject: h017-fixture-subject\n"
        f"- Evidence refs: {refs}\n"
        "- Tests/readback summary: GREEN; H017 fixture.\n"
        "- Result status: success\n",
        encoding="utf-8",
    )


def _h017_write_evidence(project: Path, relpath: str) -> None:
    path = project / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# evidence\n\nH017 fixture evidence.\n", encoding="utf-8")


def _h017_commit_all(project: Path, message: str) -> str:
    if not (project / ".git").exists():
        subprocess.run(["git", "init", "-q", str(project)], check=True)
        subprocess.run(
            ["git", "-C", str(project), "config", "user.email", "fixture@example.invalid"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(project), "config", "user.name", "Fixture"],
            check=True,
        )
    subprocess.run(["git", "-C", str(project), "add", "-A"], check=True)
    subprocess.run(
        ["git", "-C", str(project), "commit", "-q", "-m", message], check=True
    )
    return subprocess.run(
        ["git", "-C", str(project), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def _h017_blob_for(project: Path, relpath: str, commit: str = "HEAD") -> str:
    return subprocess.run(
        ["git", "-C", str(project), "rev-parse", f"{commit}:{relpath}"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def _h017_write_board_package(
    project: Path,
    *,
    branch: str = "work/h017-fixture",
    cards: list[dict] | None = None,
) -> None:
    if cards is None:
        cards = []
    path = project / BOARD_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f'workstream_id = "{BOARD_WORKSTREAM}"',
        "revision = 1",
    ]
    if not cards:
        lines.append("cards = []")
    lines.extend([
        "",
        "[execution_ref]",
        f'branch = "{branch}"',
        "",
    ])
    for card in cards:
        lines.append("[[cards]]")
        lines.append(f'id = "{card["id"]}"')
        lines.append(f'status = "{card.get("status", "done")}"')
        if card.get("result") is not None:
            result = card["result"]
            lines.append("")
            lines.append("[cards.result]")
            lines.append('class = "result"')
            lines.append(f'path = "{result["path"]}"')
            if "commit" in result and "blob" in result:
                lines.append(f'commit = "{result["commit"]}"')
                lines.append(f'blob = "{result["blob"]}"')
        lines.append("")
        lines.append("[cards.contract]")
        lines.append('class = "task_card"')
        contract_path = card.get("contract_path", H017_CARD_PATH)
        lines.append(f'path = "{contract_path}"')
        for review in card.get("reviews", []):
            lines.append("")
            lines.append("[[cards.review_attempts]]")
            lines.append('class = "review_attempt"')
            lines.append(f'path = "{review["path"]}"')
            if "commit" in review and "blob" in review:
                lines.append(f'commit = "{review["commit"]}"')
                lines.append(f'blob = "{review["blob"]}"')
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _h017_complete_fixture(project: Path) -> tuple[str, str, str]:
    _h017_write_workstream(project)
    _h017_write_card(project)
    _h017_write_evidence(project, H017_EVIDENCE_PATH)
    _h017_write_evidence(project, H017_REVIEW_EVIDENCE_PATH)
    _h017_write_result(project, [H017_EVIDENCE_PATH])
    review = _write_attempt_toml(project, "R01")
    head1 = _h017_commit_all(project, "h017 package files")
    result_blob = _h017_blob_for(project, H017_RESULT_PATH, head1)
    review_blob = _h017_blob_for(project, review, head1)
    _h017_write_board_package(project, cards=[{
        "id": BOARD_CARD,
        "status": "done",
        "result": {"path": H017_RESULT_PATH, "commit": head1, "blob": result_blob},
        "reviews": [{"path": review, "commit": head1, "blob": review_blob}],
    }])
    head2 = _h017_commit_all(project, "h017 board")
    return head1, head2, review


class H017DerivedRecoveryPackageTests(unittest.TestCase):
    def test_complete_exact_package_continues_deterministically(self) -> None:
        from tools.close_contract import verify_target_side_recovery_from_board

        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _, head2, _ = _h017_complete_fixture(project)
            self.assertEqual(
                verify_target_side_recovery_from_board(
                    project_root=project,
                    workstream_path=H017_WORKSTREAM_PATH,
                    board_path=BOARD_PATH,
                    source_branch="work/h017-fixture",
                    source_head=head2,
                    merge_commit=head2,
                    project_repository="owner/fixture",
                ),
                "source_ref_independent_recovery",
            )

    def test_genuinely_empty_no_history_recovers_vacuously(self) -> None:
        from tools.close_contract import verify_target_side_recovery_from_board

        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _h017_write_workstream(project)
            _h017_write_board_package(project, cards=[])
            head = _h017_commit_all(project, "h017 empty workstream")
            self.assertEqual(
                verify_target_side_recovery_from_board(
                    project_root=project,
                    workstream_path=H017_WORKSTREAM_PATH,
                    board_path=BOARD_PATH,
                    source_branch="work/h017-fixture",
                    source_head=head,
                    merge_commit=head,
                    project_repository="owner/fixture",
                ),
                "source_ref_independent_recovery",
            )

    def test_empty_board_with_durable_history_cannot_recover(self) -> None:
        from tools.close_contract import verify_target_side_recovery_from_board

        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _h017_write_workstream(project)
            _h017_write_card(project)
            _h017_write_evidence(project, H017_EVIDENCE_PATH)
            _h017_write_result(project, [H017_EVIDENCE_PATH])
            review = _write_attempt_toml(project, "R01")
            _h017_commit_all(project, "h017 durable history")
            _h017_write_board_package(project, cards=[])
            head = _h017_commit_all(project, "h017 empty board over history")
            with self.assertRaisesRegex(CloseContractError, "empty|history|omits|durable"):
                verify_target_side_recovery_from_board(
                    project_root=project,
                    workstream_path=H017_WORKSTREAM_PATH,
                    board_path=BOARD_PATH,
                    source_branch="work/h017-fixture",
                    source_head=head,
                    merge_commit=head,
                    project_repository="owner/fixture",
                )
            _ = review

    def test_omitted_result_class_fails_closed(self) -> None:
        from tools.close_contract import verify_target_side_recovery_from_board

        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _h017_write_workstream(project)
            _h017_write_card(project)
            _h017_write_evidence(project, H017_EVIDENCE_PATH)
            _h017_write_evidence(project, H017_REVIEW_EVIDENCE_PATH)
            review = _write_attempt_toml(project, "R01")
            head1 = _h017_commit_all(project, "h017 files without result")
            review_blob = _h017_blob_for(project, review, head1)
            _h017_write_board_package(project, cards=[{
                "id": BOARD_CARD,
                "status": "done",
                "reviews": [{"path": review, "commit": head1, "blob": review_blob}],
            }])
            head2 = _h017_commit_all(project, "h017 board omits result")
            with self.assertRaisesRegex(CloseContractError, "omits|result|required|completeness"):
                verify_target_side_recovery_from_board(
                    project_root=project,
                    workstream_path=H017_WORKSTREAM_PATH,
                    board_path=BOARD_PATH,
                    source_branch="work/h017-fixture",
                    source_head=head2,
                    merge_commit=head2,
                    project_repository="owner/fixture",
                )

    def test_dangling_result_locator_fails_closed(self) -> None:
        from tools.close_contract import verify_target_side_recovery_from_board

        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _h017_write_workstream(project)
            _h017_write_card(project)
            _h017_write_evidence(project, H017_EVIDENCE_PATH)
            _h017_write_evidence(project, H017_REVIEW_EVIDENCE_PATH)
            _h017_write_result(project, [H017_EVIDENCE_PATH])
            review = _write_attempt_toml(project, "R01")
            head1 = _h017_commit_all(project, "h017 files")
            review_blob = _h017_blob_for(project, review, head1)
            missing = (
                f"implementation/workstreams/{BOARD_WORKSTREAM}/results/{BOARD_CARD}-MISSING.md"
            )
            _h017_write_board_package(project, cards=[{
                "id": BOARD_CARD,
                "status": "done",
                "result": {"path": missing, "commit": head1, "blob": "f" * 40},
                "reviews": [{"path": review, "commit": head1, "blob": review_blob}],
            }])
            head2 = _h017_commit_all(project, "h017 board dangling result")
            with self.assertRaisesRegex(CloseContractError, "dangling|resolve|missing|recovery package"):
                verify_target_side_recovery_from_board(
                    project_root=project,
                    workstream_path=H017_WORKSTREAM_PATH,
                    board_path=BOARD_PATH,
                    source_branch="work/h017-fixture",
                    source_head=head2,
                    merge_commit=head2,
                    project_repository="owner/fixture",
                )

    def test_stale_result_locator_fails_closed(self) -> None:
        from tools.close_contract import verify_target_side_recovery_from_board

        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _, head2, _ = _h017_complete_fixture(project)
            (project / H017_RESULT_PATH).write_text(
                (project / H017_RESULT_PATH).read_text(encoding="utf-8")
                + "\n# stale mutation\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(CloseContractError, "stale|mutated|mismatch|recovery package"):
                verify_target_side_recovery_from_board(
                    project_root=project,
                    workstream_path=H017_WORKSTREAM_PATH,
                    board_path=BOARD_PATH,
                    source_branch="work/h017-fixture",
                    source_head=head2,
                    merge_commit=head2,
                    project_repository="owner/fixture",
                )

    def test_sibling_contract_locator_fails_closed(self) -> None:
        from tools.close_contract import verify_target_side_recovery_from_board

        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _h017_write_workstream(project)
            _h017_write_card(project)
            _h017_write_evidence(project, H017_EVIDENCE_PATH)
            _h017_write_evidence(project, H017_REVIEW_EVIDENCE_PATH)
            _h017_write_result(project, [H017_EVIDENCE_PATH])
            review = _write_attempt_toml(project, "R01")
            head1 = _h017_commit_all(project, "h017 files")
            result_blob = _h017_blob_for(project, H017_RESULT_PATH, head1)
            review_blob = _h017_blob_for(project, review, head1)
            sibling = (
                f"implementation/workstreams/{BOARD_WORKSTREAM}/cards/M01-T02.md"
            )
            _h017_write_board_package(project, cards=[{
                "id": BOARD_CARD,
                "status": "done",
                "contract_path": sibling,
                "result": {"path": H017_RESULT_PATH, "commit": head1, "blob": result_blob},
                "reviews": [{"path": review, "commit": head1, "blob": review_blob}],
            }])
            head2 = _h017_commit_all(project, "h017 board sibling contract")
            with self.assertRaisesRegex(CloseContractError, "sibling|another|does not match|exact Card"):
                verify_target_side_recovery_from_board(
                    project_root=project,
                    workstream_path=H017_WORKSTREAM_PATH,
                    board_path=BOARD_PATH,
                    source_branch="work/h017-fixture",
                    source_head=head2,
                    merge_commit=head2,
                    project_repository="owner/fixture",
                )

    def test_duplicate_review_locator_fails_closed(self) -> None:
        from tools.close_contract import verify_target_side_recovery_from_board

        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _h017_write_workstream(project)
            _h017_write_card(project)
            _h017_write_evidence(project, H017_EVIDENCE_PATH)
            _h017_write_evidence(project, H017_REVIEW_EVIDENCE_PATH)
            _h017_write_result(project, [H017_EVIDENCE_PATH])
            review = _write_attempt_toml(project, "R01")
            head1 = _h017_commit_all(project, "h017 files")
            result_blob = _h017_blob_for(project, H017_RESULT_PATH, head1)
            review_blob = _h017_blob_for(project, review, head1)
            entry = {"path": review, "commit": head1, "blob": review_blob}
            _h017_write_board_package(project, cards=[{
                "id": BOARD_CARD,
                "status": "done",
                "result": {"path": H017_RESULT_PATH, "commit": head1, "blob": result_blob},
                "reviews": [entry, dict(entry)],
            }])
            head2 = _h017_commit_all(project, "h017 board duplicate review")
            with self.assertRaisesRegex(CloseContractError, "duplicate"):
                verify_target_side_recovery_from_board(
                    project_root=project,
                    workstream_path=H017_WORKSTREAM_PATH,
                    board_path=BOARD_PATH,
                    source_branch="work/h017-fixture",
                    source_head=head2,
                    merge_commit=head2,
                    project_repository="owner/fixture",
                )

    def test_board_bound_cleanup_blocks_empty_with_history_and_allows_complete(self) -> None:
        from tools.close_contract import cleanup_branch_action_from_board

        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _h017_write_workstream(project)
            _h017_write_card(project)
            _h017_write_evidence(project, H017_EVIDENCE_PATH)
            _h017_write_result(project, [H017_EVIDENCE_PATH])
            _write_attempt_toml(project, "R01")
            _h017_commit_all(project, "h017 durable history")
            _h017_write_board_package(project, cards=[])
            head = _h017_commit_all(project, "h017 empty board over history")
            with self.assertRaisesRegex(CloseContractError, "empty|history|omits|durable|recovery"):
                cleanup_branch_action_from_board(
                    project_root=project,
                    workstream_path=H017_WORKSTREAM_PATH,
                    board_path=BOARD_PATH,
                    source_branch="work/h017-fixture",
                    source_head=head,
                    merge_commit=head,
                    project_repository="owner/fixture",
                    source_ref_exists=True,
                    current_head=head,
                    cleanup_state="safe_to_delete",
                    verified_head=head,
                )
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _, head2, _ = _h017_complete_fixture(project)
            self.assertEqual(
                cleanup_branch_action_from_board(
                    project_root=project,
                    workstream_path=H017_WORKSTREAM_PATH,
                    board_path=BOARD_PATH,
                    source_branch="work/h017-fixture",
                    source_head=head2,
                    merge_commit=head2,
                    project_repository="owner/fixture",
                    source_ref_exists=True,
                    current_head=head2,
                    cleanup_state="safe_to_delete",
                    verified_head=head2,
                ),
                "delete_exact_ref",
            )


H017_FINDING_ID = "LF-001"
H017_FINDING_EVIDENCE = (
    f"implementation/workstreams/{BOARD_WORKSTREAM}/evidence/LF-001.md"
)
H017_FINDING_RECORD = (
    f"implementation/workstreams/{BOARD_WORKSTREAM}/findings/LF-001.toml"
)
H017_TRIGGER_ID = "after-M01-T01"
H017_READINESS_RECORD = (
    f"implementation/workstreams/{BOARD_WORKSTREAM}/readiness/after-M01-T01.toml"
)
H017_HANDOFF_PATH = (
    f"implementation/workstreams/{BOARD_WORKSTREAM}/handoffs/note.md"
)


def _h017_append_live_finding(project: Path) -> None:
    path = project / BOARD_PATH
    text = path.read_text(encoding="utf-8")
    text += (
        "\n[[live_findings]]\n"
        f'id = "{H017_FINDING_ID}"\n'
        'finding_class = "implementation_defect"\n'
        'observed = "Live execution showed the retry helper succeeding without writing."\n'
        f'evidence_refs = ["{H017_FINDING_EVIDENCE}"]\n'
        'owner_stage = "execution"\n'
        'authorization = "owning_stage_accepted"\n'
        "\n[live_findings.acceptance]\n"
        'stage = "execution"\n'
        "\n[live_findings.acceptance.record]\n"
        'class = "finding_acceptance"\n'
        f'path = "{H017_FINDING_RECORD}"\n'
    )
    path.write_text(text, encoding="utf-8")


def _h017_write_finding_record(project: Path) -> None:
    path = project / H017_FINDING_RECORD
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'finding_id = "{H017_FINDING_ID}"\n'
        'finding_class = "implementation_defect"\n'
        'accepting_stage = "execution"\n'
        'decision = "accepted"\n',
        encoding="utf-8",
    )


def _h017_append_admitted_trigger(project: Path) -> None:
    path = project / BOARD_PATH
    text = path.read_text(encoding="utf-8")
    text += (
        "\n[[jit_triggers]]\n"
        f'id = "{H017_TRIGGER_ID}"\n'
        f'after_card = "{BOARD_CARD}"\n'
        'state = "satisfied"\n'
        'condition = "Downstream live-consumer test depends on the predecessor result."\n'
        "\n[jit_triggers.live_consumer]\n"
        "intended = true\n"
        'readiness = "admitted"\n'
        "\n[jit_triggers.live_consumer.authority]\n"
        'repository = "owner/fixture"\n'
        f'commit = "{"e" * 40}"\n'
        'path = "planning/PLAN.md"\n'
        f'blob = "{"f" * 40}"\n'
        "\n[jit_triggers.live_consumer.admission]\n"
        'stage = "execution_prep"\n'
        "\n[jit_triggers.live_consumer.admission.record]\n"
        'class = "live_consumer_admission"\n'
        f'path = "{H017_READINESS_RECORD}"\n'
    )
    path.write_text(text, encoding="utf-8")


def _h017_write_readiness_record(project: Path) -> None:
    path = project / H017_READINESS_RECORD
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'trigger_id = "{H017_TRIGGER_ID}"\n'
        'decision = "admitted"\n',
        encoding="utf-8",
    )


def _h017_complete_fixture_with_records(
    project: Path,
    *,
    with_finding_record: bool = False,
    with_readiness_record: bool = False,
    cite_finding: bool = False,
    cite_readiness: bool = False,
) -> tuple[str, str]:
    _h017_write_workstream(project)
    _h017_write_card(project)
    _h017_write_evidence(project, H017_EVIDENCE_PATH)
    _h017_write_evidence(project, H017_REVIEW_EVIDENCE_PATH)
    _h017_write_evidence(project, H017_FINDING_EVIDENCE)
    if with_finding_record:
        _h017_write_finding_record(project)
    if with_readiness_record:
        _h017_write_readiness_record(project)
    _h017_write_result(project, [H017_EVIDENCE_PATH])
    review = _write_attempt_toml(project, "R01")
    head1 = _h017_commit_all(project, "h017 package files")
    result_blob = _h017_blob_for(project, H017_RESULT_PATH, head1)
    review_blob = _h017_blob_for(project, review, head1)
    _h017_write_board_package(project, cards=[{
        "id": BOARD_CARD,
        "status": "done",
        "result": {"path": H017_RESULT_PATH, "commit": head1, "blob": result_blob},
        "reviews": [{"path": review, "commit": head1, "blob": review_blob}],
    }])
    if cite_finding:
        _h017_append_live_finding(project)
    if cite_readiness:
        _h017_append_admitted_trigger(project)
    head2 = _h017_commit_all(project, "h017 board")
    return head1, head2


class H017MergeEvidenceTests(unittest.TestCase):
    def test_old_ancestor_is_not_exact_merged_source_head(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _, source_head, _ = _h017_complete_fixture(project)
            (project / "later-target-only.txt").write_text("later target\n", encoding="utf-8")
            later = _h017_commit_all(project, "target advances after source")
            with self.assertRaisesRegex(CloseContractError, "exact merged source parent"):
                verify_target_side_recovery_from_board(
                    project_root=project,
                    workstream_path=H017_WORKSTREAM_PATH,
                    board_path=BOARD_PATH,
                    source_branch="work/h017-fixture",
                    source_head=source_head,
                    merge_commit=later,
                    project_repository="owner/fixture",
                )

    def test_malformed_merge_commit_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _, head2, _ = _h017_complete_fixture(project)
            with self.assertRaisesRegex(CloseContractError, "40-hex|merge-commit identity"):
                verify_target_side_recovery_from_board(
                    project_root=project,
                    workstream_path=H017_WORKSTREAM_PATH,
                    board_path=BOARD_PATH,
                    source_branch="work/h017-fixture",
                    source_head=head2,
                    merge_commit="not-a-commit",
                    project_repository="owner/fixture",
                )

    def test_unknown_merge_commit_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _, head2, _ = _h017_complete_fixture(project)
            with self.assertRaisesRegex(CloseContractError, "does not resolve"):
                verify_target_side_recovery_from_board(
                    project_root=project,
                    workstream_path=H017_WORKSTREAM_PATH,
                    board_path=BOARD_PATH,
                    source_branch="work/h017-fixture",
                    source_head=head2,
                    merge_commit="0" * 40,
                    project_repository="owner/fixture",
                )

    def test_source_head_outside_merge_history_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            head1, head2, _ = _h017_complete_fixture(project)
            with self.assertRaisesRegex(CloseContractError, "not contained|stale|sibling"):
                verify_target_side_recovery_from_board(
                    project_root=project,
                    workstream_path=H017_WORKSTREAM_PATH,
                    board_path=BOARD_PATH,
                    source_branch="work/h017-fixture",
                    source_head=head2,
                    merge_commit=head1,
                    project_repository="owner/fixture",
                )

    def test_merge_target_missing_package_file_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            head1, _, _ = _h017_complete_fixture(project)
            # head1 predates the Board commit: the merge target tree lacks
            # the selected Board, so containment must fail.
            with self.assertRaisesRegex(
                CloseContractError, "does not match the exact merged source head"
            ):
                verify_target_side_recovery_from_board(
                    project_root=project,
                    workstream_path=H017_WORKSTREAM_PATH,
                    board_path=BOARD_PATH,
                    source_branch="work/h017-fixture",
                    source_head=head1,
                    merge_commit=head1,
                    project_repository="owner/fixture",
                )


class H017ProofIntegrityTests(unittest.TestCase):
    def test_derive_binds_exact_locator_classes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _h017_complete_fixture(project)
            proof = derive_recovery_package_from_board(
                project_root=project,
                workstream_path=H017_WORKSTREAM_PATH,
                board_path=BOARD_PATH,
                source_branch="work/h017-fixture",
                project_repository="owner/fixture",
            )
            self.assertFalse(proof.genuinely_empty)
            classes = sorted(item.locator_class for item in proof.locators)
            self.assertEqual(
                classes,
                ["evidence", "evidence", "result", "review_attempt", "task_card"],
            )
            self.assertTrue(proof.package_digest.startswith("sha256:"))
            # Even a derived digest cannot replace a fresh Board/merge readback.
            with self.assertRaisesRegex(CloseContractError, "fresh durable Board"):
                cleanup_branch_action(
                    recovery_proof=proof,
                    source_ref_exists=True,
                    current_head="same-head",
                    cleanup_state="safe_to_delete",
                    verified_head="same-head",
                )

    def test_tampered_proof_cannot_authorize_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _h017_complete_fixture(project)
            proof = derive_recovery_package_from_board(
                project_root=project,
                workstream_path=H017_WORKSTREAM_PATH,
                board_path=BOARD_PATH,
                source_branch="work/h017-fixture",
                project_repository="owner/fixture",
            )
            tampered = H017RecoveryProof(
                workstream_id=proof.workstream_id,
                workstream_path=proof.workstream_path,
                workstream_commit=proof.workstream_commit,
                workstream_blob=proof.workstream_blob,
                board_path=proof.board_path,
                board_commit=proof.board_commit,
                board_blob=proof.board_blob,
                locators=(),
                genuinely_empty=proof.genuinely_empty,
                package_digest=proof.package_digest,
            )
            with self.assertRaisesRegex(CloseContractError, "fresh durable Board"):
                cleanup_branch_action(
                    recovery_proof=tampered,
                    source_ref_exists=True,
                    current_head="same-head",
                    cleanup_state="safe_to_delete",
                    verified_head="same-head",
                )

    def test_recomputed_digest_cannot_forge_cleanup_authority(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _h017_complete_fixture(project)
            proof = derive_recovery_package_from_board(
                project_root=project,
                workstream_path=H017_WORKSTREAM_PATH,
                board_path=BOARD_PATH,
                source_branch="work/h017-fixture",
                project_repository="owner/fixture",
            )
            forged = replace(proof, locators=(), genuinely_empty=True)
            forged = replace(forged, package_digest=_h017_compute_package_digest(forged))
            with self.assertRaisesRegex(CloseContractError, "fresh durable Board"):
                cleanup_branch_action(
                    recovery_proof=forged,
                    source_ref_exists=True,
                    current_head="same-head",
                    cleanup_state="safe_to_delete",
                    verified_head="same-head",
                )

    def test_empty_derive_marks_genuine_emptiness(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _h017_write_workstream(project)
            _h017_write_board_package(project, cards=[])
            _h017_commit_all(project, "h017 empty workstream")
            proof = derive_recovery_package_from_board(
                project_root=project,
                workstream_path=H017_WORKSTREAM_PATH,
                board_path=BOARD_PATH,
                source_branch="work/h017-fixture",
                project_repository="owner/fixture",
            )
            self.assertTrue(proof.genuinely_empty)
            self.assertEqual(proof.locators, ())


class H017RecordClosureTests(unittest.TestCase):
    def test_cited_finding_record_joins_package(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _h017_complete_fixture_with_records(
                project, with_finding_record=True, cite_finding=True
            )
            proof = derive_recovery_package_from_board(
                project_root=project,
                workstream_path=H017_WORKSTREAM_PATH,
                board_path=BOARD_PATH,
                source_branch="work/h017-fixture",
                project_repository="owner/fixture",
            )
            self.assertIn(
                H017_FINDING_RECORD, [item.path for item in proof.locators]
            )

    def test_missing_cited_finding_record_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _h017_complete_fixture_with_records(project, cite_finding=True)
            with self.assertRaisesRegex(CloseContractError, "finding_record|dangling"):
                derive_recovery_package_from_board(
                    project_root=project,
                    workstream_path=H017_WORKSTREAM_PATH,
                    board_path=BOARD_PATH,
                    source_branch="work/h017-fixture",
                    project_repository="owner/fixture",
                )

    def test_cited_readiness_record_joins_package(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _h017_complete_fixture_with_records(
                project, with_readiness_record=True, cite_readiness=True
            )
            proof = derive_recovery_package_from_board(
                project_root=project,
                workstream_path=H017_WORKSTREAM_PATH,
                board_path=BOARD_PATH,
                source_branch="work/h017-fixture",
                project_repository="owner/fixture",
            )
            self.assertIn(
                H017_READINESS_RECORD, [item.path for item in proof.locators]
            )

    def test_missing_cited_readiness_record_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _h017_complete_fixture_with_records(project, cite_readiness=True)
            with self.assertRaisesRegex(CloseContractError, "readiness_record|dangling"):
                derive_recovery_package_from_board(
                    project_root=project,
                    workstream_path=H017_WORKSTREAM_PATH,
                    board_path=BOARD_PATH,
                    source_branch="work/h017-fixture",
                    project_repository="owner/fixture",
                )


class H017HandoffTests(unittest.TestCase):
    def test_head_handoff_joins_package_and_deleted_handoff_is_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            _h017_complete_fixture(project)
            handoff = project / H017_HANDOFF_PATH
            handoff.parent.mkdir(parents=True, exist_ok=True)
            handoff.write_text("# handoff\n", encoding="utf-8")
            _h017_commit_all(project, "h017 add handoff")
            proof = derive_recovery_package_from_board(
                project_root=project,
                workstream_path=H017_WORKSTREAM_PATH,
                board_path=BOARD_PATH,
                source_branch="work/h017-fixture",
                project_repository="owner/fixture",
            )
            self.assertIn(H017_HANDOFF_PATH, [item.path for item in proof.locators])
            handoff.unlink()
            _h017_commit_all(project, "h017 discard handoff")
            proof = derive_recovery_package_from_board(
                project_root=project,
                workstream_path=H017_WORKSTREAM_PATH,
                board_path=BOARD_PATH,
                source_branch="work/h017-fixture",
                project_repository="owner/fixture",
            )
            self.assertNotIn(H017_HANDOFF_PATH, [item.path for item in proof.locators])


if __name__ == "__main__":
    unittest.main()
