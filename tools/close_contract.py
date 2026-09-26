#!/usr/bin/env python3
"""Deterministic Project Workflow V2 Close/integration refresh contract."""

from __future__ import annotations

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
        read_project,
        validate_locator,
        validate_project,
        validate_review_history,
    )
    from tools.exact_locator import ExactLocatorError, normalize_locator_path
    from tools.review_attempt_provenance import (
        ReviewAttemptProvenanceError,
        verify_legacy_migration,
        verify_review_attempt_locator,
        verify_terminal_append_only_from_git,
    )
except ModuleNotFoundError:  # direct script execution from tools/
    from review_contract import (
        OBSERVATION_DISPOSITIONS,
        ReviewContractError,
        derive_observation_state,
    )
    from state_contract import (
        ValidationError,
        read_project,
        validate_locator,
        validate_project,
        validate_review_history,
    )
    from exact_locator import ExactLocatorError, normalize_locator_path
    from review_attempt_provenance import (
        ReviewAttemptProvenanceError,
        verify_legacy_migration,
        verify_review_attempt_locator,
        verify_terminal_append_only_from_git,
    )


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
