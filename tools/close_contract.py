#!/usr/bin/env python3
"""Deterministic Project Workflow V2 Close/integration refresh contract."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

try:
    from tools.review_contract import OBSERVATION_DISPOSITIONS
except ModuleNotFoundError:  # direct script execution from tools/
    from review_contract import OBSERVATION_DISPOSITIONS


class CloseContractError(ValueError):
    pass


@dataclass(frozen=True)
class RefreshSnapshot:
    target_commit: str
    content_fingerprint: str
    behavior_fingerprint: str
    acceptance: frozenset[str]

    def __post_init__(self) -> None:
        fields = (
            self.target_commit,
            self.content_fingerprint,
            self.behavior_fingerprint,
        )
        if any(not value.strip() for value in fields):
            raise CloseContractError("refresh snapshot identities must be non-empty")
        if not self.acceptance or any(not item.strip() for item in self.acceptance):
            raise CloseContractError("refresh snapshot acceptance must be non-empty")


def classify_review_coverage(
    reviewed: RefreshSnapshot,
    current: RefreshSnapshot,
    *,
    affected_compatibility_green: bool,
) -> str:
    """Return reuse_green_review or new_review_subject, failing closed on unverified reuse."""

    materially_changed = (
        reviewed.content_fingerprint != current.content_fingerprint
        or reviewed.behavior_fingerprint != current.behavior_fingerprint
        or not current.acceptance.issubset(reviewed.acceptance)
    )
    if materially_changed:
        return "new_review_subject"
    if not affected_compatibility_green:
        raise CloseContractError(
            "review coverage cannot be reused until affected compatibility verification is GREEN"
        )
    return "reuse_green_review"


def verify_pre_mutation_target(refreshed_target_commit: str, reread_target_commit: str) -> None:
    if not refreshed_target_commit.strip() or not reread_target_commit.strip():
        raise CloseContractError("target identities must be non-empty")
    if refreshed_target_commit != reread_target_commit:
        raise CloseContractError(
            "integration target moved after refresh; rerun refresh before mutation"
        )


def stacked_integration_path(
    *,
    genuine_parent_only_dependency: bool,
    dependency_accepted_in_target: bool,
) -> str:
    """Select the semantic stacked path without depending on parent branch survival."""

    if not genuine_parent_only_dependency:
        return "integrate_child_independently"
    if dependency_accepted_in_target:
        return "integrate_child_independently"
    return "fold_child_into_parent"


EXTERNAL_READBACK_STATES = {"pending", "verified", "uncertain"}
EXTERNAL_OBSERVATIONS = {
    "unknown",
    "expected_effect",
    "no_effect",
    "unexpected_effect",
}


def external_effect_recovery_action(*, readback_state: str, observation: str) -> str:
    """Select the only safe continuation after an external mutation attempt."""

    if readback_state not in EXTERNAL_READBACK_STATES:
        raise CloseContractError(f"invalid external readback state: {readback_state!r}")
    if observation not in EXTERNAL_OBSERVATIONS:
        raise CloseContractError(f"invalid external observation: {observation!r}")

    if readback_state == "pending":
        if observation != "unknown":
            raise CloseContractError("pending readback cannot claim an observed effect")
        return "readback_exact_target"

    if readback_state == "uncertain":
        if observation != "unknown":
            raise CloseContractError("uncertain readback cannot claim a verified observation")
        raise CloseContractError(
            "external effect occurrence remains uncertain; fail closed without retry"
        )

    if observation == "unknown":
        raise CloseContractError("verified readback requires a concrete observation")
    if observation == "no_effect":
        return "retry_allowed"
    if observation == "expected_effect":
        return "reconcile_without_retry"
    return "reconcile_unexpected_effect"

def tracker_pr_linkage(
    *,
    tracker_linked: bool,
    final_scope_completing: bool,
    target_is_default_branch: bool,
) -> str:
    """Choose non-closing reference vs closing linkage for a GitHub tracker."""

    if not tracker_linked:
        return "no_linkage"
    if final_scope_completing and target_is_default_branch:
        return "closing_linkage"
    return "reference_only"


def reconcile_issue_readback(
    *,
    accepted_scope_durably_complete: bool,
    observed_issue_state: str,
    automatic_close_available: bool,
) -> str:
    """Classify post-integration Issue state without granting workflow authority."""

    if observed_issue_state not in {"open", "closed"}:
        raise CloseContractError("Issue state must be exact readback: open or closed")

    if observed_issue_state == "closed":
        if accepted_scope_durably_complete:
            return "verified_closed"
        return "reconcile_unexpected_early_close"

    if not accepted_scope_durably_complete:
        return "keep_open"
    if automatic_close_available:
        return "reconcile_missing_automatic_close"
    return "explicit_close_allowed"


def verify_target_side_recovery(
    *,
    source_branch: str,
    source_head: str,
    merged_source_head: str,
    target_package_subject_head: str,
    immutable_merge_evidence: bool,
    required_artifacts: frozenset[str],
    present_artifacts: frozenset[str],
) -> str:
    """Prove closure can recover from target truth without a live source ref."""

    if not source_branch.strip() or not source_head.strip():
        raise CloseContractError("original source provenance must be preserved")
    if not immutable_merge_evidence:
        raise CloseContractError("target-side recovery requires immutable merge evidence")
    if merged_source_head != source_head or target_package_subject_head != source_head:
        raise CloseContractError("target package does not match the exact merged source head")
    missing = required_artifacts - present_artifacts
    if missing:
        raise CloseContractError(
            "target package is missing unique recovery artifacts: " + ", ".join(sorted(missing))
        )
    return "source_ref_independent_recovery"

def cleanup_branch_action(
    *,
    terminal_package_independent: bool,
    source_ref_exists: bool,
    current_head: str,
    cleanup_state: str,
    verified_head: str,
) -> str:
    """Select source-branch cleanup action with exact-head and absence readback."""

    if not terminal_package_independent:
        raise CloseContractError("cleanup requires recovery truth independent of the source ref")
    if cleanup_state not in {"none", "safe_to_delete", "deleted"}:
        raise CloseContractError("invalid cleanup state")

    if not source_ref_exists:
        if cleanup_state == "none":
            return "automatic_cleanup_complete"
        if cleanup_state == "safe_to_delete":
            return "record_deleted_after_absence_readback"
        return "deleted_verified_absent"

    if not current_head.strip():
        raise CloseContractError("existing source ref requires exact current head")
    if cleanup_state == "deleted":
        raise CloseContractError("deleted cleanup state contradicts surviving source ref")
    if cleanup_state == "none":
        return "mark_safe_to_delete"
    if not verified_head.strip() or current_head != verified_head:
        raise CloseContractError("safe_to_delete head is stale; deletion is forbidden")
    return "delete_exact_ref"

def verify_terminal_unmerged_closure(
    *,
    closure_package_present: bool,
    history_artifacts_complete: bool,
    implementation_content_in_target: bool,
) -> str:
    """Preserve terminal-unmerged history without accepting rejected implementation."""

    if not closure_package_present or not history_artifacts_complete:
        raise CloseContractError("terminal-unmerged recovery package is incomplete")
    if implementation_content_in_target:
        raise CloseContractError("terminal-unmerged closure must not import rejected implementation")
    return "unmerged_history_preserved"


def validate_cleanup_work(
    *,
    work_id: str,
    subject: Mapping[str, object],
    tests_evidence: Iterable[str],
    independent_review_green: bool,
    covers_observation_ids: Iterable[str],
    speculative_redesign: bool = False,
    new_product_scope: bool = False,
) -> str:
    """Validate one completed bounded cleanup work before Final Integration evaluates it.

    Cleanup groups concrete cleanup-candidate observations into the smallest
    meaningful work with its own exact subject, tests/evidence and independent
    review. It is never a loophole for speculative redesign or new product scope.
    """
    if not isinstance(work_id, str) or not work_id.strip():
        raise CloseContractError("cleanup work requires a non-empty work_id")
    if not isinstance(subject, Mapping):
        raise CloseContractError(f"cleanup work {work_id!r} requires an exact subject table")
    repository = subject.get("repository")
    path = subject.get("path")
    commit = subject.get("commit")
    blob = subject.get("blob")
    if not isinstance(repository, str) or not repository.strip():
        raise CloseContractError(f"cleanup work {work_id!r} requires an exact subject repository")
    if not isinstance(path, str) or not path.strip():
        raise CloseContractError(f"cleanup work {work_id!r} requires an exact subject path")
    for label, value in (("commit", commit), ("blob", blob)):
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{40}", value) is None:
            raise CloseContractError(
                f"cleanup work {work_id!r} requires an exact subject {label} (40-hex)"
            )
    evidence = [item for item in tests_evidence if isinstance(item, str) and item.strip()]
    if not evidence:
        raise CloseContractError(
            f"cleanup work {work_id!r} requires non-empty tests/evidence"
        )
    covers = list(covers_observation_ids)
    if (
        not covers
        or not all(isinstance(item, str) and item.strip() for item in covers)
        or len(set(covers)) != len(covers)
    ):
        raise CloseContractError(
            f"cleanup work {work_id!r} must be grounded in non-empty unique cleanup-candidate observation ids"
        )
    if speculative_redesign:
        raise CloseContractError(
            f"cleanup work {work_id!r} must not become speculative redesign"
        )
    if new_product_scope:
        raise CloseContractError(
            f"cleanup work {work_id!r} must not introduce new product scope"
        )
    if independent_review_green is not True:
        raise CloseContractError(
            f"cleanup work {work_id!r} requires GREEN independent review before Final Integration"
        )
    return "cleanup_work_complete"


def verify_final_observation_reconciliation(
    *,
    observations: Iterable[Mapping[str, object]],
    cleanup_works: Iterable[Mapping[str, object]] = (),
    further_advisory_improvement_conceivable: bool = False,
) -> str:
    """Gate Final Integration on reconciled observations and completed cleanup.

    Every still-open observation must reconcile to exactly one of the five
    terminal dispositions, and every cleanup candidate must be covered by a
    completed independently reviewed cleanup work.
    """

    # Deliberately do not branch on further_advisory_improvement_conceivable.
    # Conceivable future improvement alone never keeps cleanup recursively open.
    _ = further_advisory_improvement_conceivable

    dispositions: dict[str, str] = {}
    for entry in observations:
        if not isinstance(entry, Mapping):
            raise CloseContractError("observation entries must be tables")
        observation_id = entry.get("id")
        disposition = entry.get("disposition")
        if not isinstance(observation_id, str) or not observation_id.strip():
            raise CloseContractError("observation entries require a non-empty id")
        if observation_id in dispositions:
            raise CloseContractError(
                f"duplicate observation {observation_id!r} in Final reconciliation"
            )
        if disposition is None or (isinstance(disposition, str) and not disposition.strip()):
            raise CloseContractError(
                f"observation {observation_id!r} lacks an explicit disposition"
            )
        if disposition == "open":
            raise CloseContractError(
                f"Final Integration cannot complete with unreconciled open observation {observation_id!r}"
            )
        if disposition not in OBSERVATION_DISPOSITIONS:
            raise CloseContractError(
                f"observation {observation_id!r} has no terminal disposition, "
                f"got {disposition!r}"
            )
        dispositions[observation_id] = str(disposition)

    covered: set[str] = set()
    for work in cleanup_works:
        if not isinstance(work, Mapping):
            raise CloseContractError("cleanup work entries must be tables")
        work_id = work.get("work_id", "cleanup")
        covers = work.get("covers_observation_ids", [])
        if not isinstance(covers, list) or not all(
            isinstance(item, str) and item.strip() for item in covers
        ):
            raise CloseContractError(
                f"cleanup work {work_id!r} must cover non-empty observation ids"
            )
        for observation_id in covers:
            if observation_id not in dispositions:
                raise CloseContractError(
                    f"cleanup work {work_id!r} covers unknown observation {observation_id!r}"
                )
            if dispositions[observation_id] != "cleanup_candidate":
                raise CloseContractError(
                    f"cleanup work {work_id!r} covers observation {observation_id!r} "
                    f"which is reconciled as {dispositions[observation_id]!r}, "
                    "not cleanup_candidate"
                )
        if work.get("complete") is True:
            if work.get("independent_review_green") is not True:
                raise CloseContractError(
                    f"cleanup work {work_id!r} requires GREEN independent review before Final Integration"
                )
            covered.update(covers)

    pending_cleanup = {
        observation_id
        for observation_id, disposition in dispositions.items()
        if disposition == "cleanup_candidate" and observation_id not in covered
    }
    if pending_cleanup:
        raise CloseContractError(
            "Final Integration cannot complete with cleanup candidates lacking "
            "completed independently reviewed cleanup work: "
            + ", ".join(sorted(pending_cleanup))
        )
    return "final_observation_reconciliation_complete"


def close_continuation(
    *,
    approved_scope_durably_complete: bool,
    next_authorized_obligation: bool,
    explicit_authorization_gate_due: bool,
    deployment_or_live_write: bool = False,
) -> str:
    """Choose continuation/stop semantics without treating role or live-write status as a gate."""

    # Deliberately do not branch on deployment_or_live_write. Its presence alone
    # is not human authority and therefore cannot manufacture a stop.
    _ = deployment_or_live_write

    if explicit_authorization_gate_due:
        return "authorization_stop"

    if approved_scope_durably_complete:
        if next_authorized_obligation:
            raise CloseContractError(
                "approved scope cannot be terminal while an authorized in-scope obligation remains"
            )
        return "end_of_scope_stop"

    if next_authorized_obligation:
        return "continue_deterministically"

    return "continue_close_reconciliation"
