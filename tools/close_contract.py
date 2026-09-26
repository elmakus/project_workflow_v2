#!/usr/bin/env python3
"""Deterministic Project Workflow V2 Close/integration refresh contract."""

from __future__ import annotations

import hashlib
import re
import subprocess
import tomllib
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

try:
    from tools.review_contract import (
        OBSERVATION_DISPOSITIONS,
        ReviewContractError,
        derive_observation_state,
    )
    from tools.state_contract import (
        ValidationError,
        parse_task_card,
        read_project,
        validate_blocker,
        validate_board,
        validate_locator,
        validate_project,
        validate_review_history,
        validate_workstream,
    )
    from tools.exact_locator import (
        ExactLocatorError,
        normalize_locator_path,
        resolve_blob_at_commit,
        verify_exact_git_locator,
        verify_worktree_freshness,
    )
    from tools.review_attempt_provenance import (
        ReviewAttemptProvenanceError,
        verify_legacy_migration,
        verify_review_attempt_locator,
        verify_terminal_append_only_from_git,
    )
    from tools.execution_contract import ExecutionContractError, parse_card_result
except ModuleNotFoundError:  # direct script execution from tools/
    from review_contract import (
        OBSERVATION_DISPOSITIONS,
        ReviewContractError,
        derive_observation_state,
    )
    from state_contract import (
        ValidationError,
        parse_task_card,
        read_project,
        validate_blocker,
        validate_board,
        validate_locator,
        validate_project,
        validate_review_history,
        validate_workstream,
    )
    from exact_locator import (
        ExactLocatorError,
        normalize_locator_path,
        resolve_blob_at_commit,
        verify_exact_git_locator,
        verify_worktree_freshness,
    )
    from review_attempt_provenance import (
        ReviewAttemptProvenanceError,
        verify_legacy_migration,
        verify_review_attempt_locator,
        verify_terminal_append_only_from_git,
    )
    from execution_contract import ExecutionContractError, parse_card_result


class CloseContractError(ValueError):
    pass


@dataclass(frozen=True)
class H017RecoveryPackageLocator:
    """One identity-proved locator in the H017 recovery package."""

    locator_class: str
    path: str
    commit: str
    blob: str


@dataclass(frozen=True)
class H017RecoveryProof:
    """Snapshot of a derived package with an accidental-mutation digest.

    The digest is not an authority seal. A caller can construct this class
    and recompute its digest, so cleanup must rederive from durable Board
    state and verify target Git evidence before selecting an action.
    """

    workstream_id: str
    workstream_path: str
    workstream_commit: str
    workstream_blob: str
    board_path: str
    board_commit: str
    board_blob: str
    locators: tuple[H017RecoveryPackageLocator, ...]
    genuinely_empty: bool
    package_digest: str


def _h017_canonical_digest_input(proof: H017RecoveryProof) -> bytes:
    entries = [
        ("task_board", proof.board_path, proof.board_commit, proof.board_blob),
        (
            "workstream",
            proof.workstream_path,
            proof.workstream_commit,
            proof.workstream_blob,
        ),
    ]
    entries.extend(
        (item.locator_class, item.path, item.commit, item.blob)
        for item in proof.locators
    )
    canonical = "\n".join(
        "\0".join(entry) for entry in sorted(entries)
    )
    return f"{proof.workstream_id}\n{canonical}\n{int(proof.genuinely_empty)}\n".encode(
        "utf-8"
    )


def _h017_compute_package_digest(proof: H017RecoveryProof) -> str:
    return "sha256:" + hashlib.sha256(_h017_canonical_digest_input(proof)).hexdigest()


def _h017_check_proof_integrity(proof: H017RecoveryProof) -> None:
    if not isinstance(proof, H017RecoveryProof):
        raise CloseContractError(
            "cleanup requires an H017 recovery proof derived from durable "
            "Board state via derive_recovery_package_from_board; a "
            f"caller-attested {type(proof).__name__} can never authorize deletion"
        )
    if not proof.workstream_id.strip():
        raise CloseContractError("H017 recovery proof lacks workstream identity")
    for label, value in (
        ("workstream commit", proof.workstream_commit),
        ("workstream blob", proof.workstream_blob),
        ("board commit", proof.board_commit),
        ("board blob", proof.board_blob),
    ):
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{40}", value) is None:
            raise CloseContractError(
                f"H017 recovery proof {label} must be exact 40-hex Git identity"
            )
    if not isinstance(proof.locators, tuple) or any(
        not isinstance(item, H017RecoveryPackageLocator) for item in proof.locators
    ):
        raise CloseContractError("H017 recovery proof locators are malformed")
    for item in proof.locators:
        if not item.locator_class.strip() or not item.path.strip():
            raise CloseContractError("H017 recovery proof locator lacks class/path")
        for label, value in (("commit", item.commit), ("blob", item.blob)):
            if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{40}", value) is None:
                raise CloseContractError(
                    "H017 recovery proof locator "
                    f"{item.path!r} {label} must be exact 40-hex Git identity"
                )
    if proof.genuinely_empty is not True and proof.genuinely_empty is not False:
        raise CloseContractError("H017 recovery proof genuinely_empty must be boolean")
    if proof.locators and proof.genuinely_empty:
        raise CloseContractError(
            "H017 recovery proof is contradictory: a genuinely empty package "
            "carries no card/result/review/evidence locators"
        )
    if _h017_compute_package_digest(proof) != proof.package_digest:
        raise CloseContractError(
            "H017 recovery proof digest does not bind its locator set; only "
            "derive_recovery_package_from_board produces valid proofs"
        )


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
    """Fail closed: caller-attested sets can never prove recovery.

    H017 removed the production bypass this signature used to provide.
    Required/present artifact sets supplied by the caller cannot establish
    package completeness, so this entry point never returns
    ``source_ref_independent_recovery``: an empty claim fails as an empty
    package, a gapped claim fails with the missing names, and even a
    textually complete claim fails because attestation is not derivation.
    The only production entry point is
    :func:`verify_target_side_recovery_from_board`, which derives the
    mandatory package from durable workstream/Board state and verifies
    postmerge evidence against immutable Git identities.
    """

    if not source_branch.strip() or not source_head.strip():
        raise CloseContractError("original source provenance must be preserved")
    if not required_artifacts:
        raise CloseContractError(
            "target package is empty; caller-attested empty package cannot "
            "prove source-ref-independent recovery (package completeness "
            "must be derived from durable workstream/Board state; a "
            "genuinely empty/no-history workstream requires Git-verified "
            "empty inventory via verify_target_side_recovery_from_board)"
        )
    if not immutable_merge_evidence:
        raise CloseContractError("target-side recovery requires immutable merge evidence")
    if merged_source_head != source_head or target_package_subject_head != source_head:
        raise CloseContractError("target package does not match the exact merged source head")
    missing = required_artifacts - present_artifacts
    if missing:
        raise CloseContractError(
            "target package is missing unique recovery artifacts: " + ", ".join(sorted(missing))
        )
    raise CloseContractError(
        "caller-attested artifact sets cannot prove source-ref-independent "
        "recovery even when textually complete; package completeness must be "
        "derived from durable workstream/Board state via "
        "verify_target_side_recovery_from_board"
    )


def _select_cleanup_readback_action(
    *,
    package_independent: bool,
    source_ref_exists: bool,
    current_head: str,
    cleanup_state: str,
    verified_head: str,
) -> str:
    """Relative readback/state engine shared by the cleanup gates.

    This helper is deliberately private: ``package_independent`` is trusted
    as given and proves nothing about package completeness. Production
    callers must use :func:`cleanup_branch_action` with a digest-bound
    :class:`H017RecoveryProof` (or :func:`cleanup_branch_action_from_board`
    end to end). Direct use is reserved for unit tests of the readback
    state machine.
    """

    if not package_independent:
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


def cleanup_branch_action(
    *,
    recovery_proof: H017RecoveryProof,
    source_ref_exists: bool,
    current_head: str,
    cleanup_state: str,
    verified_head: str,
) -> str:
    """Fail closed without a fresh board and target-Git readback.

    A digest checks accidental mutation, but a caller can recompute it for
    an invented package. Only cleanup_branch_action_from_board may select a
    cleanup action after deriving the package and checking merge evidence.
    """

    raise CloseContractError(
        "cleanup requires fresh durable Board and target Git proof via "
        "cleanup_branch_action_from_board; a caller-supplied recovery proof "
        "cannot authorize deletion"
    )


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
    if isinstance(tests_evidence, str) or not isinstance(tests_evidence, Iterable):
        raise CloseContractError(
            f"cleanup work {work_id!r} requires non-empty tests/evidence"
        )
    evidence = [item for item in tests_evidence if isinstance(item, str) and item.strip()]
    if not evidence:
        raise CloseContractError(
            f"cleanup work {work_id!r} requires non-empty tests/evidence"
        )
    if isinstance(covers_observation_ids, str) or not isinstance(covers_observation_ids, Iterable):
        raise CloseContractError(
            f"cleanup work {work_id!r} must be grounded in non-empty unique cleanup-candidate observation ids"
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


def _canonical_final_dispositions(
    *,
    review_attempts: Iterable[Mapping[str, object]] | None,
    derived_state: Mapping[str, object] | None,
) -> dict[str, str]:
    """Return canonical dispositions from history or a completeness-bound snapshot."""
    if (review_attempts is None) == (derived_state is None):
        raise CloseContractError(
            "Final reconciliation requires canonical review_attempts or a "
            "completeness-bound derived_state snapshot, exactly one, as its "
            "completeness proof"
        )
    if review_attempts is not None:
        try:
            canonical = derive_observation_state(review_attempts)
        except ReviewContractError as exc:
            raise CloseContractError(
                f"Final reconciliation history invalid: {exc}"
            ) from exc
        return {
            observation_id: entry["disposition"]
            for observation_id, entry in canonical.items()
        }
    assert derived_state is not None
    if not isinstance(derived_state, Mapping):
        raise CloseContractError("Final reconciliation derived_state snapshot must be a table")
    canonical: dict[str, str] = {}
    for observation_id, entry in derived_state.items():
        if (
            not isinstance(observation_id, str)
            or not observation_id.strip()
            or not isinstance(entry, Mapping)
            or entry.get("id") != observation_id
        ):
            raise CloseContractError(
                "Final reconciliation snapshot entries must be derived-state tables keyed by observation id"
            )
        disposition = entry.get("disposition")
        if not isinstance(disposition, str) or not disposition.strip():
            raise CloseContractError(
                f"snapshot observation {observation_id!r} lacks an explicit disposition"
            )
        canonical[observation_id] = disposition
    return canonical


def verify_final_observation_reconciliation(
    *,
    observations: Iterable[Mapping[str, object]],
    review_attempts: Iterable[Mapping[str, object]] | None = None,
    derived_state: Mapping[str, object] | None = None,
    cleanup_works: Iterable[Mapping[str, object]] = (),
    further_advisory_improvement_conceivable: bool = False,
) -> str:
    """Check a proposed Final set against supplied canonical dispositions.

    This is the relative-consistency engine: the proposal must exactly match
    the given review_attempts derivation or derived_state snapshot, every
    entry must carry a terminal disposition, and every cleanup candidate must
    be covered by a fully validated completed cleanup work. It proves nothing
    about the completeness of its own inputs; truncation-proof completeness
    against durable state is provided only by
    verify_final_observation_reconciliation_from_board.
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

    canonical = _canonical_final_dispositions(
        review_attempts=review_attempts, derived_state=derived_state
    )
    omitted = set(canonical) - set(dispositions)
    if omitted:
        raise CloseContractError(
            "Final reconciliation omits known observations from canonical history: "
            + ", ".join(sorted(omitted))
        )
    fabricated = set(dispositions) - set(canonical)
    if fabricated:
        raise CloseContractError(
            "Final reconciliation proposes unknown observations absent from canonical history: "
            + ", ".join(sorted(fabricated))
        )
    for observation_id, disposition in dispositions.items():
        if disposition != canonical[observation_id]:
            raise CloseContractError(
                f"observation {observation_id!r} proposed disposition {disposition!r} "
                "does not match canonical derived disposition "
                f"{canonical[observation_id]!r}"
            )

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
            validate_cleanup_work(
                work_id=work.get("work_id", ""),
                subject=work.get("subject", {}),
                tests_evidence=work.get("tests_evidence", []),
                independent_review_green=work.get("independent_review_green", False),
                covers_observation_ids=covers,
                speculative_redesign=work.get("speculative_redesign", False),
                new_product_scope=work.get("new_product_scope", False),
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


def _read_project_toml(root: Path, raw_path: str, label: str) -> dict:
    """Read a worktree TOML file, failing closed on escape, absence or corruption."""
    try:
        rel = normalize_locator_path(raw_path, label)
    except ExactLocatorError as exc:
        raise CloseContractError(
            f"{label} path escapes the project worktree: {raw_path!r}: {exc}"
        ) from exc
    path = (root / Path(*PurePosixPath(rel).parts)).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise CloseContractError(
            f"{label} path escapes the project worktree: {raw_path!r}"
        ) from exc
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except OSError as exc:
        raise CloseContractError(f"{label} {raw_path!r} is unreadable: {exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise CloseContractError(f"{label} {raw_path!r} is not valid TOML: {exc}") from exc
    if not isinstance(data, dict):
        raise CloseContractError(f"{label} {raw_path!r} must be a TOML table")
    return data


_GIT_TIMEOUT_SECONDS = 5


def _derive_durable_review_inventory(
    root: Path, workstream_id: str, card_id: str
) -> list[str]:
    """Derive the complete durable review-attempt inventory for one Card.

    Unions the worktree reviews directory with required Git HEAD and
    HEAD-history listings for the Card prefix, so a Board that omits a
    durable attempt cannot reconcile vacuously. Both Git reads must
    succeed; an unavailable repository, missing HEAD, command failure or
    timeout fails closed. A verifiably empty inventory needs actual Git
    evidence, never worktree absence alone.
    """
    for label, value in (("workstream", workstream_id), ("card", card_id)):
        if (
            not isinstance(value, str)
            or not value.strip()
            or value != value.strip()
            or "/" in value
            or "\\" in value
            or ".." in value
            or value in {".", ".."}
            or "\x00" in value
            or "\n" in value
            or "\r" in value
        ):
            raise CloseContractError(f"Final gate {label} id is unsafe: {value!r}")
    reviews_dir_rel = f"implementation/workstreams/{workstream_id}/reviews"
    prefix = f"{reviews_dir_rel}/{card_id}-"
    inventory: set[str] = set()

    reviews_dir = root / "implementation" / "workstreams" / workstream_id / "reviews"
    try:
        resolved_dir = reviews_dir.resolve()
        resolved_dir.relative_to(root)
    except ValueError as exc:
        raise CloseContractError(
            "Final gate reviews directory escapes the project worktree"
        ) from exc
    if resolved_dir.is_dir():
        try:
            entries = list(resolved_dir.iterdir())
        except OSError as exc:
            raise CloseContractError(
                f"Final gate cannot enumerate durable review inventory: {exc}"
            ) from exc
        for entry in entries:
            name = entry.name
            if not (name.startswith(f"{card_id}-") and name.endswith(".toml")):
                continue
            try:
                is_candidate = entry.is_symlink() or entry.is_file()
            except OSError:
                is_candidate = True
            if is_candidate:
                inventory.add(f"{reviews_dir_rel}/{name}")

    git_sources = (
        ("HEAD", ["ls-tree", "-r", "--name-only", "HEAD", "--", reviews_dir_rel]),
        (
            "history",
            [
                "log",
                "--full-history",
                "--format=",
                "--name-only",
                "--diff-filter=ACMR",
                "HEAD",
                "--",
                reviews_dir_rel,
            ],
        ),
    )
    for source, args in git_sources:
        try:
            completed = subprocess.run(
                ["git", "-C", str(root), *args],
                capture_output=True,
                text=True,
                check=False,
                timeout=_GIT_TIMEOUT_SECONDS,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise CloseContractError(
                f"Final gate cannot read durable Git {source} inventory: {exc}"
            ) from exc
        if completed.returncode != 0:
            detail = (completed.stderr or "").strip().splitlines()
            reason = detail[0][:200] if detail and detail[0] else f"exit {completed.returncode}"
            raise CloseContractError(
                f"Final gate cannot read durable Git {source} inventory: {reason}"
            )
        for line in completed.stdout.splitlines():
            candidate = line.strip()
            if candidate.startswith(prefix) and candidate.endswith(".toml"):
                inventory.add(candidate)
    return sorted(inventory)


def _resolve_project_repository(
    root: Path, explicit: str | None
) -> str | None:
    if explicit is not None:
        if not isinstance(explicit, str) or not explicit.strip():
            raise CloseContractError("Final gate project repository must be non-empty")
        return explicit
    candidate = root / "PROJECT.md"
    if not candidate.is_file():
        return None
    try:
        project = read_project(candidate)
        validate_project(project)
    except (OSError, ValidationError):
        return None
    repository = project.get("repository")
    if not isinstance(repository, str) or not repository.strip():
        return None
    return repository


def verify_final_observation_reconciliation_from_board(
    *,
    project_root: Path | str,
    board_path: str,
    card_id: str,
    observations: Iterable[Mapping[str, object]],
    cleanup_works: Iterable[Mapping[str, object]] = (),
    accepted_authority_paths: set[str] | None = None,
    exact_blob_reader: Callable[[str, str, str], str | None] | None = None,
    expected_review_scope: str | None = None,
    project_repository: str | None = None,
    further_advisory_improvement_conceivable: bool = False,
) -> str:
    """Authoritatively gate Final Integration on complete durable review history.

    This is the truncation-proof entry point: it derives the complete
    review-attempt inventory from durable Git/workstream state (worktree
    reviews directory plus required HEAD and history reads), requires
    the Board to list every durable attempt, proves every listed
    locator through exact RF007/T11 Git identity and legacy provenance,
    validates the full history, freezes terminal bytes against Git
    history, and derives the canonical observation set itself. A
    missing Git inventory, a path-only relied-upon locator, an omitted
    durable attempt, an omitted known observation, or a forged
    disposition fails against durable truth. Only a workstream with a
    Git-verified empty durable inventory may reconcile vacuously.
    Callers must not substitute in-memory caller-supplied histories
    when durable state is available.
    """
    root = Path(project_root).resolve()
    try:
        board = _read_project_toml(root, board_path, "task board")
    except CloseContractError as exc:
        raise CloseContractError(f"Final gate cannot read durable Task Board: {exc}") from exc
    workstream_id = board.get("workstream_id")
    if not isinstance(workstream_id, str) or not workstream_id.strip():
        raise CloseContractError("Final gate Task Board lacks workstream_id")
    try:
        validate_locator(
            {"class": "task_board", "path": board_path},
            "task_board",
            "final gate board",
            workstream_id,
        )
    except ValidationError as exc:
        raise CloseContractError(f"Final gate Task Board locator invalid: {exc}") from exc

    cards = board.get("cards")
    if not isinstance(cards, list):
        raise CloseContractError("Final gate Task Board has no card array")
    card = next(
        (entry for entry in cards if isinstance(entry, dict) and entry.get("id") == card_id),
        None,
    )
    if card is None:
        raise CloseContractError(f"Final gate Task Board has no Card {card_id!r}")
    refs = card.get("review_attempts", [])
    if not isinstance(refs, list):
        raise CloseContractError(f"Final gate Card {card_id!r} has no review_attempts array")

    listed_paths: list[str] = []
    for index, ref in enumerate(refs):
        label = f"final gate review_attempts[{index}]"
        try:
            listed_paths.append(
                validate_locator(ref, "review_attempt", label, workstream_id)
            )
        except ValidationError as exc:
            raise CloseContractError(
                f"Final gate review attempt locator invalid: {exc}"
            ) from exc
    if len(set(listed_paths)) != len(listed_paths):
        dupes = sorted({path for path in listed_paths if listed_paths.count(path) > 1})
        raise CloseContractError(
            "Final gate Board lists duplicate review attempt locator(s): "
            + ", ".join(dupes)
        )

    durable = _derive_durable_review_inventory(root, workstream_id, card_id)
    omitted = sorted(set(durable) - set(listed_paths))
    if omitted:
        raise CloseContractError(
            "Final gate Board omits durable review attempt(s): "
            + ", ".join(omitted)
            + "; review history is append-only and Board locators must cover "
            "the complete durable inventory derived from worktree and Git state"
        )

    repository: str | None = None
    if refs:
        repository = _resolve_project_repository(root, project_repository)
        if repository is None:
            raise CloseContractError(
                "Final gate exact review attempt identity requires project "
                "repository; pass project_repository or provide a valid PROJECT.md"
            )

    attempts: list[dict] = []
    for index, ref in enumerate(refs):
        label = f"final gate review_attempts[{index}]"
        assert repository is not None
        try:
            attempt, _, _ = verify_review_attempt_locator(
                project_root=root,
                project_repository=repository,
                workstream_id=workstream_id,
                card_id=card_id,
                ref=ref,
                label=label,
            )
        except ReviewAttemptProvenanceError as exc:
            raise CloseContractError(
                f"Final gate review attempt identity failed: {exc}"
            ) from exc
        if "review_kind" not in attempt and attempt.get("verdict") in {
            "green",
            "red",
        }:
            try:
                verify_legacy_migration(
                    project_root=root,
                    project_repository=repository,
                    workstream_id=workstream_id,
                    card_id=card_id,
                    attempt=attempt,
                    label=label,
                )
            except ReviewAttemptProvenanceError as exc:
                raise CloseContractError(
                    f"Final gate legacy review attempt provenance failed: {exc}"
                ) from exc
        attempts.append(attempt)

    if attempts:
        try:
            validate_review_history(
                attempts,
                expected_card_id=card_id,
                workstream_id=workstream_id,
                accepted_authority_paths=accepted_authority_paths,
                exact_blob_reader=exact_blob_reader,
                expected_review_scope=expected_review_scope,
            )
        except ValidationError as exc:
            raise CloseContractError(
                f"Final gate durable review history invalid: {exc}"
            ) from exc
        try:
            verify_terminal_append_only_from_git(
                project_root=root,
                workstream_id=workstream_id,
                card_id=card_id,
                attempts=attempts,
                label="final gate review history",
            )
        except ReviewAttemptProvenanceError as exc:
            raise CloseContractError(
                f"Final gate durable review history is not append-only: {exc}"
            ) from exc

    return verify_final_observation_reconciliation(
        observations=observations,
        review_attempts=attempts,
        cleanup_works=cleanup_works,
        further_advisory_improvement_conceivable=further_advisory_improvement_conceivable,
    )


def _h017_head_commit(root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            timeout=_GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise CloseContractError(
            f"recovery package cannot read durable Git HEAD inventory: {exc}"
        ) from exc
    if completed.returncode != 0:
        detail = (completed.stderr or "").strip().splitlines()
        reason = detail[0][:200] if detail and detail[0] else f"exit {completed.returncode}"
        raise CloseContractError(
            f"recovery package cannot read durable Git HEAD inventory: {reason}"
        )
    head = completed.stdout.strip()
    if re.fullmatch(r"[0-9a-f]{40}", head) is None:
        raise CloseContractError("recovery package Git HEAD identity is malformed")
    return head


def _h017_inventory_for_subdir(
    root: Path, workstream_id: str, subdir: str, suffix: str
) -> list[str]:
    rel_dir = f"implementation/workstreams/{workstream_id}/{subdir}"
    inventory: set[str] = set()
    work_dir = root / "implementation" / "workstreams" / workstream_id / subdir
    try:
        resolved = work_dir.resolve()
        resolved.relative_to(root)
    except ValueError as exc:
        raise CloseContractError(
            f"recovery package {subdir} directory escapes the project worktree"
        ) from exc
    if resolved.is_dir():
        try:
            entries = list(resolved.iterdir())
        except OSError as exc:
            raise CloseContractError(
                f"recovery package cannot enumerate durable {subdir} inventory: {exc}"
            ) from exc
        for entry in entries:
            name = entry.name
            if not name.endswith(suffix):
                continue
            try:
                is_candidate = entry.is_symlink() or entry.is_file()
            except OSError:
                is_candidate = True
            if is_candidate:
                inventory.add(f"{rel_dir}/{name}")
    git_sources = (
        ("HEAD", ["ls-tree", "-r", "--name-only", "HEAD", "--", rel_dir]),
        (
            "history",
            [
                "log",
                "--full-history",
                "--format=",
                "--name-only",
                "--diff-filter=ACMR",
                "HEAD",
                "--",
                rel_dir,
            ],
        ),
    )
    for source, args in git_sources:
        try:
            completed = subprocess.run(
                ["git", "-C", str(root), *args],
                capture_output=True,
                text=True,
                check=False,
                timeout=_GIT_TIMEOUT_SECONDS,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise CloseContractError(
                f"recovery package cannot read durable Git {source} inventory: {exc}"
            ) from exc
        if completed.returncode != 0:
            detail = (completed.stderr or "").strip().splitlines()
            reason = detail[0][:200] if detail and detail[0] else f"exit {completed.returncode}"
            raise CloseContractError(
                f"recovery package cannot read durable Git {source} inventory: {reason}"
            )
        for line in completed.stdout.splitlines():
            candidate = line.strip()
            if candidate.startswith(rel_dir + "/") and candidate.endswith(suffix):
                inventory.add(candidate)
    return sorted(inventory)


def _h017_durable_package_inventory(root: Path, workstream_id: str) -> dict[str, list[str]]:
    """Union worktree, HEAD and full-history inventory for genuine-emptiness.

    History is deliberately included here: a workstream that ever carried
    cards, results, reviews, evidence, handoffs, blockers or reconciliation
    records has accepted history and is not genuinely empty, even if its
    Board was later truncated to zero cards.
    """

    return {
        "cards": _h017_inventory_for_subdir(root, workstream_id, "cards", ".md"),
        "results": _h017_inventory_for_subdir(root, workstream_id, "results", ".md"),
        "reviews": _h017_inventory_for_subdir(root, workstream_id, "reviews", ".toml"),
        "evidence": _h017_inventory_for_subdir(root, workstream_id, "evidence", ".md"),
        "handoffs": _h017_inventory_for_subdir(root, workstream_id, "handoffs", ".md"),
        "blockers": _h017_inventory_for_subdir(root, workstream_id, "blockers", ".toml"),
        "findings": _h017_inventory_for_subdir(root, workstream_id, "findings", ".toml"),
        "readiness": _h017_inventory_for_subdir(root, workstream_id, "readiness", ".toml"),
    }


def _h017_head_present_files(
    root: Path, workstream_id: str, subdir: str, suffix: str
) -> list[str]:
    """List subdir files present in the worktree or at HEAD (no history).

    Used for proving standalone artifacts such as handoffs: a handoff
    removed before HEAD is discarded and correctly excluded from the
    package, while proving it at HEAD would falsely report it dangling.
    (Review attempts are the opposite case — append-only history — and
    keep the history-inclusive inventory with Board-coverage enforcement.)
    """

    rel_dir = f"implementation/workstreams/{workstream_id}/{subdir}"
    inventory: set[str] = set()
    work_dir = root / "implementation" / "workstreams" / workstream_id / subdir
    try:
        resolved = work_dir.resolve()
        resolved.relative_to(root)
    except ValueError as exc:
        raise CloseContractError(
            f"recovery package {subdir} directory escapes the project worktree"
        ) from exc
    if resolved.is_dir():
        try:
            entries = list(resolved.iterdir())
        except OSError as exc:
            raise CloseContractError(
                f"recovery package cannot enumerate durable {subdir} inventory: {exc}"
            ) from exc
        for entry in entries:
            name = entry.name
            if not name.endswith(suffix):
                continue
            try:
                is_candidate = entry.is_symlink() or entry.is_file()
            except OSError:
                is_candidate = True
            if is_candidate:
                inventory.add(f"{rel_dir}/{name}")
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "ls-tree", "-r", "--name-only", "HEAD", "--", rel_dir],
            capture_output=True,
            text=True,
            check=False,
            timeout=_GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise CloseContractError(
            f"recovery package cannot read durable Git HEAD inventory: {exc}"
        ) from exc
    if completed.returncode != 0:
        detail = (completed.stderr or "").strip().splitlines()
        reason = detail[0][:200] if detail and detail[0] else f"exit {completed.returncode}"
        raise CloseContractError(
            f"recovery package cannot read durable Git HEAD inventory: {reason}"
        )
    for line in completed.stdout.splitlines():
        candidate = line.strip()
        if candidate.startswith(rel_dir + "/") and candidate.endswith(suffix):
            inventory.add(candidate)
    return sorted(inventory)


def _h017_prove_file_via_head(
    root: Path, relpath: str, label: str
) -> tuple[str, str, bytes]:
    try:
        rel = normalize_locator_path(relpath, f"{label}.path")
    except ExactLocatorError as exc:
        raise CloseContractError(
            f"recovery package {label} path is unsafe: {exc}"
        ) from exc
    try:
        head = _h017_head_commit(root)
    except CloseContractError as exc:
        raise CloseContractError(
            f"recovery package {label} {rel!r} cannot prove Git identity: {exc}"
        ) from exc
    try:
        blob = resolve_blob_at_commit(
            project_root=root, commit=head, path=rel, label=label
        )
    except ExactLocatorError as exc:
        if exc.kind == "dangling":
            raise CloseContractError(
                f"recovery package {label} {rel!r} is dangling: exact Git "
                f"subject {head}:{rel} does not resolve"
            ) from exc
        raise CloseContractError(
            f"recovery package {label} {rel!r} Git identity failed: {exc}"
        ) from exc
    try:
        content = verify_worktree_freshness(
            project_root=root, path=rel, blob=blob, label=label
        )
    except ExactLocatorError as exc:
        if exc.kind in {"mutated", "missing", "escape"}:
            detail = "stale: worktree bytes do not match the exact Git blob"
            if exc.kind == "missing":
                detail = "dangling: worktree target cannot be read back"
            elif exc.kind == "escape":
                detail = "sibling: path escapes the project worktree"
            raise CloseContractError(
                f"recovery package {label} {rel!r} is {detail} "
                f"(blob mismatch; {exc})"
            ) from exc
        raise CloseContractError(
            f"recovery package {label} {rel!r} freshness failed: {exc}"
        ) from exc
    return head, blob, content


def _h017_read_proved_toml(root: Path, relpath: str, label: str) -> tuple[dict, str, str]:
    _, blob, content = _h017_prove_file_via_head(root, relpath, label)
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CloseContractError(
            f"recovery package {label} {relpath!r} is not UTF-8 text: {exc}"
        ) from exc
    try:
        data = tomllib.loads(text)
    except (tomllib.TOMLDecodeError, ValueError) as exc:
        raise CloseContractError(
            f"recovery package {label} {relpath!r} is not valid TOML: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise CloseContractError(
            f"recovery package {label} {relpath!r} must be a TOML table"
        )
    head = _h017_head_commit(root)
    return data, head, blob


def _h017_read_proved_text(root: Path, relpath: str, label: str) -> tuple[str, str, str]:
    _, blob, content = _h017_prove_file_via_head(root, relpath, label)
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CloseContractError(
            f"recovery package {label} {relpath!r} is not UTF-8 text: {exc}"
        ) from exc
    head = _h017_head_commit(root)
    return text, head, blob


def _h017_prove_board_locator(
    *,
    root: Path,
    repository: str | None,
    ref: object,
    expected_class: str,
    workstream_id: str,
    label: str,
) -> tuple[str, str, str, bytes]:
    if not isinstance(ref, dict):
        raise CloseContractError(
            f"recovery package {label} locator must be a table"
        )
    try:
        path = validate_locator(ref, expected_class, label, workstream_id)
    except ValidationError as exc:
        message = str(exc)
        if "does not match exact" in message or "wrong" in message or "another" in message:
            raise CloseContractError(
                f"recovery package {label} is sibling: {exc} "
                f"(belongs to another Card/workstream)"
            ) from exc
        raise CloseContractError(
            f"recovery package {label} locator invalid: {exc}"
        ) from exc
    has_commit = "commit" in ref
    has_blob = "blob" in ref
    if has_commit or has_blob:
        if repository is None:
            raise CloseContractError(
                f"recovery package {label} exact Git identity requires project "
                "repository; pass project_repository or provide a valid PROJECT.md"
            )
        commit = ref.get("commit")
        blob = ref.get("blob")
        if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
            raise CloseContractError(
                f"recovery package {label} commit must be exact 40-hex Git identity"
            )
        if not isinstance(blob, str) or re.fullmatch(r"[0-9a-f]{40}", blob) is None:
            raise CloseContractError(
                f"recovery package {label} blob must be exact 40-hex Git identity"
            )
        try:
            verify_exact_git_locator(
                project_root=root,
                repository=repository,
                expected_repository=repository,
                commit=commit,
                path=path,
                blob=blob,
                label=label,
            )
        except ExactLocatorError as exc:
            if exc.kind == "dangling":
                raise CloseContractError(
                    f"recovery package {label} {path!r} is dangling: exact Git "
                    f"subject {commit}:{path} does not resolve"
                ) from exc
            if exc.kind == "blob_mismatch":
                raise CloseContractError(
                    f"recovery package {label} {path!r} is stale: declared blob "
                    f"{blob} does not match exact Git identity (blob mismatch)"
                ) from exc
            raise CloseContractError(
                f"recovery package {label} {path!r} Git identity failed: {exc}"
            ) from exc
        try:
            content = verify_worktree_freshness(
                project_root=root, path=path, blob=blob, label=label
            )
        except ExactLocatorError as exc:
            if exc.kind == "mutated":
                raise CloseContractError(
                    f"recovery package {label} {path!r} is stale: worktree bytes "
                    f"do not match declared blob {blob} (blob mismatch; worktree mutated)"
                ) from exc
            if exc.kind == "missing":
                raise CloseContractError(
                    f"recovery package {label} {path!r} is dangling: worktree "
                    f"target cannot be read back: {exc}"
                ) from exc
            raise CloseContractError(
                f"recovery package {label} {path!r} freshness failed: {exc}"
            ) from exc
        return path, commit, blob, content
    head, blob, content = _h017_prove_file_via_head(root, path, label)
    return path, head, blob, content


def _h017_finalize_proof(
    *,
    workstream_id: str,
    work_rel: str,
    work_commit: str,
    work_blob: str,
    board_rel: str,
    board_commit: str,
    board_blob: str,
    locators: list[H017RecoveryPackageLocator],
    genuinely_empty: bool,
) -> H017RecoveryProof:
    draft = H017RecoveryProof(
        workstream_id=workstream_id,
        workstream_path=work_rel,
        workstream_commit=work_commit,
        workstream_blob=work_blob,
        board_path=board_rel,
        board_commit=board_commit,
        board_blob=board_blob,
        locators=tuple(sorted(
            locators, key=lambda item: (item.locator_class, item.path)
        )),
        genuinely_empty=genuinely_empty,
        package_digest="",
    )
    return H017RecoveryProof(
        workstream_id=draft.workstream_id,
        workstream_path=draft.workstream_path,
        workstream_commit=draft.workstream_commit,
        workstream_blob=draft.workstream_blob,
        board_path=draft.board_path,
        board_commit=draft.board_commit,
        board_blob=draft.board_blob,
        locators=draft.locators,
        genuinely_empty=draft.genuinely_empty,
        package_digest=_h017_compute_package_digest(draft),
    )


def derive_recovery_package_from_board(
    *,
    project_root: Path | str,
    workstream_path: str,
    board_path: str,
    source_branch: str,
    project_repository: str | None = None,
) -> H017RecoveryProof:
    """Derive the mandatory premerge H017 recovery package from durable state.

    This is the truncation-proof premerge derivation: it computes the
    transitive closure of recovery-critical canonical locators rooted at
    the durable workstream identity/provenance and selected Task Board and
    proves every locator to exact Git identity through the DONE/GREEN RF007
    resolver with the RF006 attempt-identity/history foundations. Covered
    classes are the workstream record, the selected Board, stable
    non-discarded Card contracts, required Results, all review attempts
    needed for terminal state (Board coverage of the complete durable
    inventory, proved and append-only), referenced evidence (results,
    reviews, blockers, live findings, late-oversize preserved refs),
    cited findings/reconciliation and live-consumer admission records,
    HEAD-present handoffs, and the observation state derived from the
    proved review history. Checkpoints live under ``evidence/`` and enter
    through reference; discarded files removed before HEAD are excluded
    except append-only review history, which can never be discarded. An
    empty locator set is valid only for a Git-verified genuinely
    empty/no-history workstream; it can never authorize recovery of a
    workstream with accepted history. Omitted, dangling, stale, sibling or
    duplicate locators fail closed with an exact completeness reason.

    Scope boundaries (deliberate, not gaps): observation-disposition
    terminality and cleanup-work semantic proof belong to H019 — H017
    proves the reconciliation inputs (attempts plus referenced records),
    and review-history validation already derives the observation state;
    pre-execution pointers (research obligation) and authority-target
    contents belong to their owning RF domains, not the Close package.
    Postmerge merge-dependent fields are NOT decided here; see
    :func:`verify_target_side_recovery_from_board`.
    """
    root = Path(project_root).resolve()
    if not source_branch.strip():
        raise CloseContractError("original source provenance must be preserved")
    try:
        work_rel = normalize_locator_path(workstream_path, "recovery workstream path")
        board_rel = normalize_locator_path(board_path, "recovery board path")
    except ExactLocatorError as exc:
        raise CloseContractError(
            f"recovery package workstream/board path is unsafe: {exc}"
        ) from exc
    try:
        workstream, work_commit, work_blob = _h017_read_proved_toml(
            root, work_rel, "workstream"
        )
    except CloseContractError as exc:
        raise CloseContractError(
            f"recovery package cannot read durable workstream identity/provenance: {exc}"
        ) from exc
    workstream_id = workstream.get("workstream_id")
    if not isinstance(workstream_id, str) or not workstream_id.strip():
        raise CloseContractError("recovery package workstream lacks workstream_id")
    expected_work = f"implementation/workstreams/{workstream_id}/WORKSTREAM.toml"
    if work_rel != expected_work:
        raise CloseContractError(
            f"recovery package workstream locator is sibling: path {work_rel!r} "
            f"does not match the exact workstream path {expected_work!r} "
            "(belongs to another workstream)"
        )
    try:
        validate_workstream(workstream)
    except ValidationError as exc:
        raise CloseContractError(
            f"recovery package workstream identity/provenance invalid: {exc}"
        ) from exc
    try:
        board, board_commit, board_blob = _h017_read_proved_toml(
            root, board_rel, "task board"
        )
    except CloseContractError as exc:
        raise CloseContractError(
            f"recovery package cannot read durable Task Board: {exc}"
        ) from exc
    board_workstream = board.get("workstream_id")
    if board_workstream != workstream_id:
        raise CloseContractError(
            f"recovery package Task Board is sibling: workstream_id "
            f"{board_workstream!r} does not match selected workstream "
            f"{workstream_id!r} (belongs to another workstream)"
        )
    expected_board = f"implementation/workstreams/{workstream_id}/TASK_BOARD.toml"
    if board_rel != expected_board:
        raise CloseContractError(
            f"recovery package Task Board locator is sibling: path {board_rel!r} "
            f"does not match the exact Board path {expected_board!r}"
        )
    try:
        validate_board(board, workstream)
    except ValidationError as exc:
        raise CloseContractError(
            f"recovery package selected Board invalid (premerge knowable "
            f"package completeness): {exc}"
        ) from exc
    if source_branch != workstream.get("branch") or source_branch != board.get("execution_ref", {}).get("branch"):
        raise CloseContractError(
            "recovery package original source provenance does not match durable "
            f"workstream/Board branch: {source_branch!r} is sibling to the "
            f"selected {workstream.get('branch')!r}"
        )
    cards = board.get("cards", [])
    if not isinstance(cards, list):
        raise CloseContractError("recovery package Task Board has no card array")
    repository = _resolve_project_repository(root, project_repository)
    if cards and repository is None:
        has_exact = False
        for card in cards:
            if not isinstance(card, dict):
                continue
            for key in ("result",):
                ref = card.get(key)
                if isinstance(ref, dict) and ("commit" in ref or "blob" in ref):
                    has_exact = True
            for ref in card.get("review_attempts", []) or []:
                if isinstance(ref, dict) and ("commit" in ref or "blob" in ref):
                    has_exact = True
        if has_exact:
            raise CloseContractError(
                "recovery package exact Git identity requires project "
                "repository; pass project_repository or provide a valid PROJECT.md"
            )
        repository = "unknown/repository"
    if repository is None:
        repository = "unknown/repository"
    if not cards:
        inventory = _h017_durable_package_inventory(root, workstream_id)
        durable_hits = sorted(
            path for paths in inventory.values() for path in paths
        )
        if durable_hits:
            raise CloseContractError(
                "recovery package is empty but workstream has accepted durable "
                "history: Board omits durable recovery artifact(s): "
                + ", ".join(durable_hits[:10])
                + ("; ..." if len(durable_hits) > 10 else "")
                + "; genuinely empty/no-history workstream requires Git-verified "
                "empty inventory"
            )
        return _h017_finalize_proof(
            workstream_id=workstream_id,
            work_rel=work_rel,
            work_commit=work_commit,
            work_blob=work_blob,
            board_rel=board_rel,
            board_commit=board_commit,
            board_blob=board_blob,
            locators=[],
            genuinely_empty=True,
        )
    proven: list[H017RecoveryPackageLocator] = []
    evidence_closure: list[str] = []
    for index, card in enumerate(cards):
        if not isinstance(card, dict):
            raise CloseContractError(
                f"recovery package task_board.cards[{index}] must be a table"
            )
        card_id = card.get("id")
        if not isinstance(card_id, str) or not card_id.strip():
            raise CloseContractError(
                f"recovery package task_board.cards[{index}] lacks Card id"
            )
        status = card.get("status")
        contract_ref = card.get("contract")
        if contract_ref is None:
            raise CloseContractError(
                f"recovery package omits required card contract class: Card "
                f"{card_id!r} has no contract locator (premerge knowable "
                "package completeness)"
            )
        try:
            contract_path = validate_locator(
                contract_ref, "task_card",
                f"recovery package cards[{card_id}].contract", workstream_id
            )
        except ValidationError as exc:
            raise CloseContractError(
                f"recovery package Card {card_id!r} contract is sibling: {exc}"
            ) from exc
        expected_contract = (
            f"implementation/workstreams/{workstream_id}/cards/{card_id}.md"
        )
        if contract_path != expected_contract:
            raise CloseContractError(
                f"recovery package Card {card_id!r} contract is sibling: path "
                f"{contract_path!r} does not match the exact Card path "
                f"{expected_contract!r} (belongs to another Card)"
            )
        contract_locator = _h017_prove_board_locator(
            root=root,
            repository=repository,
            ref=contract_ref,
            expected_class="task_card",
            workstream_id=workstream_id,
            label=f"cards[{card_id}].contract",
        )
        proven.append(
            H017RecoveryPackageLocator(
                "task_card", contract_locator[0], contract_locator[1], contract_locator[2]
            )
        )
        contract_bytes = contract_locator[3]
        try:
            contract_text = contract_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CloseContractError(
                f"recovery package Card {card_id!r} contract is not UTF-8 text: {exc}"
            ) from exc
        try:
            parsed_card = parse_task_card(contract_text, card_id, workstream_id)
        except ValidationError as exc:
            raise CloseContractError(
                f"recovery package Card {card_id!r} stable contract invalid: {exc}"
            ) from exc
        result_ref = card.get("result")
        if status == "done" and result_ref is None:
            raise CloseContractError(
                f"recovery package omits required result class: done Card "
                f"{card_id!r} requires an exact result locator (premerge "
                "knowable package completeness)"
            )
        if result_ref is not None:
            result_locator = _h017_prove_board_locator(
                root=root,
                repository=repository,
                ref=result_ref,
                expected_class="result",
                workstream_id=workstream_id,
                label=f"cards[{card_id}].result",
            )
            proven.append(
                H017RecoveryPackageLocator(
                    "result", result_locator[0], result_locator[1], result_locator[2]
                )
            )
            result_bytes = result_locator[3]
            try:
                result_text = result_bytes.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise CloseContractError(
                    f"recovery package Card {card_id!r} result is not UTF-8 text: {exc}"
                ) from exc
            try:
                parsed_result = parse_card_result(result_text, card_id, workstream_id)
            except ExecutionContractError as exc:
                raise CloseContractError(
                    f"recovery package Card {card_id!r} result invalid: {exc}"
                ) from exc
            refs = parsed_result.get("evidence_refs", [])
            if len(set(refs)) != len(refs):
                dupes = sorted({item for item in refs if refs.count(item) > 1})
                raise CloseContractError(
                    f"recovery package Card {card_id!r} lists duplicate evidence "
                    f"locator(s): " + ", ".join(dupes)
                )
            evidence_closure.extend(refs)
        refs = card.get("review_attempts", [])
        if not isinstance(refs, list):
            raise CloseContractError(
                f"recovery package Card {card_id!r} has no review_attempts array"
            )
        listed: list[str] = []
        for attempt_index, ref in enumerate(refs):
            label = f"recovery package cards[{card_id}].review_attempts[{attempt_index}]"
            try:
                listed.append(
                    validate_locator(ref, "review_attempt", label, workstream_id)
                )
            except ValidationError as exc:
                raise CloseContractError(
                    f"recovery package Card {card_id!r} review attempt locator "
                    f"invalid: {exc}"
                ) from exc
        if len(set(listed)) != len(listed):
            dupes = sorted({item for item in listed if listed.count(item) > 1})
            raise CloseContractError(
                "recovery package Board lists duplicate review attempt "
                f"locator(s): " + ", ".join(dupes)
            )
        durable = _derive_durable_review_inventory(root, workstream_id, card_id)
        omitted = sorted(set(durable) - set(listed))
        if omitted:
            raise CloseContractError(
                "recovery package omits durable review attempt(s): "
                + ", ".join(omitted)
                + "; review history is append-only and Board locators must cover "
                "the complete durable inventory derived from worktree and Git state"
            )
        if status == "done" and parsed_card.get("review_requirement") == "required":
            if not refs and not durable:
                raise CloseContractError(
                    f"recovery package omits required review class: done Card "
                    f"{card_id!r} with required review needs at least one review "
                    "attempt to justify terminal state (premerge knowable "
                    "package completeness)"
                )
        attempts: list[dict] = []
        for attempt_index, ref in enumerate(refs):
            label = f"recovery package cards[{card_id}].review_attempts[{attempt_index}]"
            try:
                attempt, _, _ = verify_review_attempt_locator(
                    project_root=root,
                    project_repository=repository,
                    workstream_id=workstream_id,
                    card_id=card_id,
                    ref=ref,
                    label=label,
                )
            except ReviewAttemptProvenanceError as exc:
                kind = getattr(exc, "kind", "")
                if kind == "dangling":
                    raise CloseContractError(
                        f"recovery package Card {card_id!r} review attempt is "
                        f"dangling: {exc}"
                    ) from exc
                if kind in {"mutated", "blob_mismatch", "mismatch", "stale"}:
                    raise CloseContractError(
                        f"recovery package Card {card_id!r} review attempt is "
                        f"stale: {exc} (blob mismatch)"
                    ) from exc
                if kind in {"repository"} or "another" in str(exc):
                    raise CloseContractError(
                        f"recovery package Card {card_id!r} review attempt is "
                        f"sibling: {exc}"
                    ) from exc
                raise CloseContractError(
                    f"recovery package Card {card_id!r} review attempt identity "
                    f"failed: {exc}"
                ) from exc
            if "review_kind" not in attempt and attempt.get("verdict") in {"green", "red"}:
                try:
                    verify_legacy_migration(
                        project_root=root,
                        project_repository=repository,
                        workstream_id=workstream_id,
                        card_id=card_id,
                        attempt=attempt,
                        label=label,
                    )
                except ReviewAttemptProvenanceError as exc:
                    raise CloseContractError(
                        f"recovery package Card {card_id!r} legacy review attempt "
                        f"provenance failed: {exc}"
                    ) from exc
            attempts.append(attempt)
            # RF006 proved this locator carries exact commit+blob identity.
            proven.append(
                H017RecoveryPackageLocator(
                    "review_attempt",
                    listed[attempt_index],
                    str(ref.get("commit")),
                    str(ref.get("blob")),
                )
            )
            evidence_path = attempt.get("evidence_path", "")
            if isinstance(evidence_path, str) and evidence_path.strip():
                evidence_closure.append(evidence_path.strip())
        if attempts:
            try:
                validate_review_history(
                    attempts,
                    expected_card_id=card_id,
                    workstream_id=workstream_id,
                )
            except ValidationError as exc:
                raise CloseContractError(
                    f"recovery package Card {card_id!r} durable review history "
                    f"invalid: {exc}"
                ) from exc
            try:
                verify_terminal_append_only_from_git(
                    project_root=root,
                    workstream_id=workstream_id,
                    card_id=card_id,
                    attempts=attempts,
                    label="recovery package review history",
                )
            except ReviewAttemptProvenanceError as exc:
                raise CloseContractError(
                    f"recovery package Card {card_id!r} durable review history "
                    f"is not append-only: {exc}"
                ) from exc
        blocker_ref = card.get("blocker")
        if blocker_ref is not None:
            blocker_locator = _h017_prove_board_locator(
                root=root,
                repository=repository,
                ref=blocker_ref,
                expected_class="blocker",
                workstream_id=workstream_id,
                label=f"cards[{card_id}].blocker",
            )
            proven.append(
                H017RecoveryPackageLocator(
                    "blocker", blocker_locator[0], blocker_locator[1], blocker_locator[2]
                )
            )
            blocker_bytes = blocker_locator[3]
            try:
                blocker_text = blocker_bytes.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise CloseContractError(
                    f"recovery package Card {card_id!r} blocker is not UTF-8 text: {exc}"
                ) from exc
            try:
                blocker_data = tomllib.loads(blocker_text)
            except (tomllib.TOMLDecodeError, ValueError) as exc:
                raise CloseContractError(
                    f"recovery package Card {card_id!r} blocker is not valid TOML: {exc}"
                ) from exc
            try:
                validate_blocker(blocker_data, workstream_id, card_id)
            except ValidationError as exc:
                raise CloseContractError(
                    f"recovery package Card {card_id!r} blocker invalid: {exc}"
                ) from exc
            evidence_path = blocker_data.get("evidence_path", "")
            if isinstance(evidence_path, str) and evidence_path.strip():
                evidence_closure.append(evidence_path.strip())
    cited_records: list[tuple[str, str, str]] = []
    for finding in board.get("live_findings", []) or []:
        if not isinstance(finding, dict):
            continue
        for ref in finding.get("evidence_refs", []) or []:
            if isinstance(ref, str) and ref.strip():
                evidence_closure.append(ref.strip())
        acceptance = finding.get("acceptance")
        if isinstance(acceptance, dict):
            cited = acceptance.get("record")
            if isinstance(cited, dict) and isinstance(cited.get("path"), str):
                cited_records.append((
                    "finding_record",
                    str(cited.get("class", "finding_acceptance")),
                    cited["path"],
                ))
        downstream = finding.get("downstream", {})
        if isinstance(downstream, dict):
            for ref in downstream.get("material_evidence_refs", []) or []:
                if isinstance(ref, str) and ref.strip():
                    evidence_closure.append(ref.strip())
            downstream_acceptance = downstream.get("acceptance")
            if isinstance(downstream_acceptance, dict):
                cited = downstream_acceptance.get("record")
                if isinstance(cited, dict) and isinstance(cited.get("path"), str):
                    cited_records.append((
                        "finding_record",
                        str(cited.get("class", "finding_reconciliation")),
                        cited["path"],
                    ))
    for record in board.get("late_oversize_returns", []) or []:
        if not isinstance(record, dict):
            continue
        for ref in record.get("preserved_refs", []) or []:
            if isinstance(ref, str) and ref.strip():
                evidence_closure.append(ref.strip())
    for trigger in board.get("jit_triggers", []) or []:
        if not isinstance(trigger, dict):
            continue
        live_consumer = trigger.get("live_consumer")
        if not isinstance(live_consumer, dict):
            continue
        admission = live_consumer.get("admission")
        if not isinstance(admission, dict):
            continue
        cited = admission.get("record")
        if isinstance(cited, dict) and isinstance(cited.get("path"), str):
            cited_records.append((
                "readiness_record",
                str(cited.get("class", "live_consumer_admission")),
                cited["path"],
            ))
    seen_evidence: set[str] = set()
    for raw in evidence_closure:
        try:
            rel = normalize_locator_path(raw, "recovery package evidence")
        except ExactLocatorError as exc:
            raise CloseContractError(
                f"recovery package evidence locator {raw!r} is unsafe: {exc}"
            ) from exc
        prefix = f"implementation/workstreams/{workstream_id}/evidence/"
        if not (rel.startswith(prefix) and rel.endswith(".md")):
            raise CloseContractError(
                f"recovery package evidence locator {rel!r} is sibling: expected "
                f"workstream-local {prefix}*.md (belongs to another workstream)"
            )
        if rel in seen_evidence:
            continue
        seen_evidence.add(rel)
        try:
            evidence_commit, evidence_blob, _ = _h017_prove_file_via_head(
                root, rel, "evidence"
            )
        except CloseContractError as exc:
            raise CloseContractError(str(exc)) from exc
        proven.append(
            H017RecoveryPackageLocator("evidence", rel, evidence_commit, evidence_blob)
        )
    seen_records: set[tuple[str, str]] = set()
    for locator_class, record_class, raw in cited_records:
        try:
            rel = normalize_locator_path(raw, f"recovery package {locator_class}")
        except ExactLocatorError as exc:
            raise CloseContractError(
                f"recovery package {locator_class} locator {raw!r} is unsafe: {exc}"
            ) from exc
        subdir = "findings" if locator_class == "finding_record" else "readiness"
        prefix = f"implementation/workstreams/{workstream_id}/{subdir}/"
        if not (rel.startswith(prefix) and rel.endswith(".toml")):
            raise CloseContractError(
                f"recovery package {locator_class} locator {rel!r} is sibling: "
                f"expected workstream-local {prefix}*.toml "
                "(belongs to another workstream)"
            )
        expected_classes = (
            {"finding_acceptance", "finding_reconciliation"}
            if locator_class == "finding_record"
            else {"live_consumer_admission"}
        )
        if record_class not in expected_classes:
            raise CloseContractError(
                f"recovery package {locator_class} locator {rel!r} carries "
                f"unexpected record class {record_class!r}"
            )
        if (locator_class, rel) in seen_records:
            continue
        seen_records.add((locator_class, rel))
        try:
            record_commit, record_blob, _ = _h017_prove_file_via_head(
                root, rel, locator_class
            )
        except CloseContractError as exc:
            raise CloseContractError(str(exc)) from exc
        proven.append(
            H017RecoveryPackageLocator(locator_class, rel, record_commit, record_blob)
        )
    for rel in _h017_head_present_files(root, workstream_id, "handoffs", ".md"):
        try:
            handoff_commit, handoff_blob, _ = _h017_prove_file_via_head(
                root, rel, "handoff"
            )
        except CloseContractError as exc:
            raise CloseContractError(str(exc)) from exc
        proven.append(
            H017RecoveryPackageLocator("handoff", rel, handoff_commit, handoff_blob)
        )
    return _h017_finalize_proof(
        workstream_id=workstream_id,
        work_rel=work_rel,
        work_commit=work_commit,
        work_blob=work_blob,
        board_rel=board_rel,
        board_commit=board_commit,
        board_blob=board_blob,
        locators=proven,
        genuinely_empty=False,
    )


def _verify_postmerge_evidence(
    *,
    target_root: Path,
    source_head: str,
    merge_commit: str,
    proof: H017RecoveryProof,
) -> None:
    """Verify merge-dependent fields against immutable target Git identities.

    The merge commit itself is the immutable evidence: it must resolve to a
    commit in the target repository, identify the source head as the exact
    second (or later) merge parent or equal it for a fast-forward, and carry
    every package locator blob identically. Unknown or malformed identities,
    an older ancestor, and a target tree that drops or rewrites a package
    file fail closed. There is no boolean attestation input.
    """

    if re.fullmatch(r"[0-9a-f]{40}", merge_commit) is None:
        raise CloseContractError(
            "target-side recovery requires immutable merge evidence carrying "
            "exact 40-hex merge-commit identity"
        )
    if re.fullmatch(r"[0-9a-f]{40}", source_head) is None:
        raise CloseContractError(
            "target-side recovery requires the exact 40-hex source head to "
            "bind it into merge history"
        )
    try:
        kind = subprocess.run(
            ["git", "-C", str(target_root), "cat-file", "-t", merge_commit],
            capture_output=True,
            text=True,
            check=False,
            timeout=_GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise CloseContractError(
            f"target-side merge evidence readback failed: {exc}"
        ) from exc
    if kind.returncode != 0 or kind.stdout.strip() != "commit":
        raise CloseContractError(
            f"immutable merge evidence {merge_commit} does not resolve to an "
            "immutable commit in the target repository"
        )
    try:
        source_kind = subprocess.run(
            ["git", "-C", str(target_root), "cat-file", "-t", source_head],
            capture_output=True,
            text=True,
            check=False,
            timeout=_GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise CloseContractError(
            f"target-side source head readback failed: {exc}"
        ) from exc
    if source_kind.returncode != 0 or source_kind.stdout.strip() != "commit":
        raise CloseContractError(
            f"source head {source_head} does not resolve to an immutable "
            "commit in the target repository"
        )
    try:
        contained = subprocess.run(
            [
                "git", "-C", str(target_root), "merge-base", "--is-ancestor",
                source_head, merge_commit,
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=_GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise CloseContractError(
            f"target-side merge ancestry readback failed: {exc}"
        ) from exc
    if contained.returncode != 0:
        raise CloseContractError(
            f"source head {source_head} is not contained in merge target "
            f"history at {merge_commit}; a stale or sibling merge cannot "
            "prove target-side recovery"
        )
    try:
        parent_readback = subprocess.run(
            ["git", "-C", str(target_root), "rev-list", "--parents", "-n", "1", merge_commit],
            capture_output=True,
            text=True,
            check=False,
            timeout=_GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise CloseContractError(
            f"target-side merge parent readback failed: {exc}"
        ) from exc
    parents = parent_readback.stdout.strip().split()
    if parent_readback.returncode != 0 or not parents or parents[0] != merge_commit:
        raise CloseContractError("target-side merge parent identity is unavailable")
    if source_head != merge_commit and source_head not in parents[2:]:
        raise CloseContractError(
            f"source head {source_head} is only an ancestor of {merge_commit}, "
            "not its exact merged source parent; immutable merge evidence "
            "must bind the precise source head"
        )
    entries = [
        ("workstream", proof.workstream_path, proof.workstream_blob),
        ("task_board", proof.board_path, proof.board_blob),
    ]
    entries.extend(
        (item.locator_class, item.path, item.blob) for item in proof.locators
    )
    mismatched: list[str] = []
    for locator_class, path, blob in entries:
        try:
            at_merge = resolve_blob_at_commit(
                project_root=target_root,
                commit=merge_commit,
                path=path,
                label=f"merge evidence {locator_class}",
            )
        except ExactLocatorError:
            mismatched.append(f"{path} (absent from merge target)")
            continue
        if at_merge != blob:
            mismatched.append(f"{path} (target blob {at_merge} != package blob {blob})")
    if mismatched:
        raise CloseContractError(
            "target package does not match the exact merged source head: "
            + "; ".join(sorted(mismatched)[:10])
            + ("; ..." if len(mismatched) > 10 else "")
        )


def verify_target_side_recovery_from_board(
    *,
    project_root: Path | str,
    workstream_path: str,
    board_path: str,
    source_branch: str,
    source_head: str,
    merge_commit: str,
    target_root: Path | str | None = None,
    project_repository: str | None = None,
) -> str:
    """Prove target-side recovery from the derived package plus merge evidence.

    Authoritative postmerge gate: derives the mandatory premerge package
    via :func:`derive_recovery_package_from_board` (failing closed on any
    omitted, dangling, stale, sibling or duplicate locator, and on any
    empty package over accepted history), then verifies the
    merge-dependent fields against immutable target Git identities — the
    merge commit must resolve, contain the exact source head, and carry
    every package blob identically. ``target_root`` selects the repository
    holding the merge (default: the project root itself); cross-checkout
    merges pass the target checkout explicitly. Fails closed wherever
    immutable evidence is unavailable. Returns
    ``source_ref_independent_recovery`` only when both halves hold.
    """

    proof = derive_recovery_package_from_board(
        project_root=project_root,
        workstream_path=workstream_path,
        board_path=board_path,
        source_branch=source_branch,
        project_repository=project_repository,
    )
    _verify_postmerge_evidence(
        target_root=Path(target_root).resolve() if target_root is not None else Path(project_root).resolve(),
        source_head=source_head,
        merge_commit=merge_commit,
        proof=proof,
    )
    return "source_ref_independent_recovery"


def cleanup_branch_action_from_board(
    *,
    project_root: Path | str,
    workstream_path: str,
    board_path: str,
    source_branch: str,
    source_head: str,
    merge_commit: str,
    target_root: Path | str | None = None,
    project_repository: str | None = None,
    source_ref_exists: bool,
    current_head: str,
    cleanup_state: str,
    verified_head: str,
) -> str:
    """Select cleanup action only after the derived H017 package is independent.

    Derives the mandatory source-ref-independent recovery package from
    durable workstream/Board state, verifies the merge-dependent fields
    against immutable target Git identities, and only then selects the
    exact-head/absence readback action. An
    empty package over accepted history, an omitted class, a
    dangling/stale/sibling/duplicate locator, or unavailable merge
    evidence fails here and can never reach delete_exact_ref.
    """
    proof = derive_recovery_package_from_board(
        project_root=project_root,
        workstream_path=workstream_path,
        board_path=board_path,
        source_branch=source_branch,
        project_repository=project_repository,
    )
    _verify_postmerge_evidence(
        target_root=Path(target_root).resolve() if target_root is not None else Path(project_root).resolve(),
        source_head=source_head,
        merge_commit=merge_commit,
        proof=proof,
    )
    return _select_cleanup_readback_action(
        package_independent=True,
        source_ref_exists=source_ref_exists,
        current_head=current_head,
        cleanup_state=cleanup_state,
        verified_head=verified_head,
    )


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
