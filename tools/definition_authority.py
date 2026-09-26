#!/usr/bin/env python3
"""RF012 deterministic exact Definition-authority key (H021).

Planning and Plan Review bind one canonical key covering the Definition
revision plus exact requirements/decision Git blob identities. The router
proves the stored key against live Definition plus current worktree bytes;
legacy keyless plans prove freshness by deriving the snapshot key from the
immutable frozen plan subject commit and comparing it with current bytes.
Ambiguity fails closed. Unrelated commits never churn the key because it
binds content blobs, never HEAD or per-file commits.

Key format (single line, no whitespace):
  rf012-v1:repository:<repo>|definition:<rev>|
  requirements:<req_path>@<req_blob>|
  decisions:<dec_path>@<dec_blob>,...

Decisions are sorted lexicographically by path with no duplicates.
Helperless derivation: ``git rev-parse <commit>:<path>`` for snapshot blobs,
``git hash-object <path>`` for worktree blobs, string comparison for equality.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any

try:
    from tools.exact_locator import (
        ExactLocatorError,
        git_blob_sha,
        normalize_locator_path,
        read_confined_worktree_bytes,
        read_git_blob_bytes,
        resolve_blob_at_commit,
    )
except ModuleNotFoundError:  # direct script execution from tools/
    from exact_locator import (
        ExactLocatorError,
        git_blob_sha,
        normalize_locator_path,
        read_confined_worktree_bytes,
        read_git_blob_bytes,
        resolve_blob_at_commit,
    )

KEY_PREFIX = "rf012-v1:repository:"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
AUTHORITY_ROOTS = ("requirements/", "decisions/", "planning/", "workflow/")


class DefinitionAuthorityError(ValueError):
    """A Definition-authority key could not be proved.

    ``kind`` names the failure class: ``shape``, ``mismatch``,
    ``stale``, ``ambiguous``, ``missing`` or an RF007 locator kind
    (``unsafe_path``, ``dangling``, ``not_blob``, ``git_unavailable``,
    ``escape``, ``mutated``).
    """

    def __init__(self, message: str, *, kind: str) -> None:
        super().__init__(message)
        self.kind = kind


def _fail(label: str, detail: str, kind: str) -> DefinitionAuthorityError:
    return DefinitionAuthorityError(f"{label}: {detail}", kind=kind)


def _check_token(value: Any, label: str, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise _fail(label, f"{field} must be a non-empty string", "shape")
    if value != value.strip():
        raise _fail(label, f"{field} must not have surrounding whitespace", "shape")
    if "|" in value or any(char.isspace() for char in value):
        raise _fail(label, f"{field} must not contain pipes or whitespace", "shape")
    return value


def _split_path_blob(entry: str, label: str) -> tuple[str, str]:
    if "@" not in entry:
        raise _fail(label, f"entry {entry!r} must be path@blob", "shape")
    path, blob = entry.rsplit("@", 1)
    try:
        canonical = normalize_locator_path(path, f"{label}.path")
    except ExactLocatorError as exc:
        raise _fail(label, f"unsafe authority path {path!r}: {exc}", "shape") from exc
    if not canonical.startswith(AUTHORITY_ROOTS):
        raise _fail(
            label, f"authority path {canonical!r} is outside accepted roots", "shape"
        )
    if SHA40.fullmatch(blob) is None:
        raise _fail(label, "blob must be exact 40-hex Git identity", "shape")
    return canonical, blob


def parse_definition_authority_key(raw: Any, label: str) -> dict[str, Any]:
    """Parse and validate a canonical key, returning its structured form."""
    if not isinstance(raw, str) or not raw:
        raise _fail(label, "key must be a non-empty string", "shape")
    if raw != raw.strip():
        raise _fail(label, "key must not have surrounding whitespace", "shape")
    parts = raw.split("|")
    if len(parts) != 4:
        raise _fail(label, "key must have exactly four pipe-separated segments", "shape")
    if not parts[0].startswith(KEY_PREFIX):
        raise _fail(label, "key must start with rf012-v1:repository:", "shape")
    repository = _check_token(parts[0][len(KEY_PREFIX):], label, "repository")
    if not parts[1].startswith("definition:"):
        raise _fail(label, "second segment must start with definition:", "shape")
    revision = _check_token(parts[1][len("definition:"):], label, "definition revision")
    if not parts[2].startswith("requirements:"):
        raise _fail(label, "third segment must start with requirements:", "shape")
    req_path, req_blob = _split_path_blob(
        parts[2][len("requirements:"):], f"{label}.requirements"
    )
    if not parts[3].startswith("decisions:"):
        raise _fail(label, "fourth segment must start with decisions:", "shape")
    decisions_raw = parts[3][len("decisions:"):]
    if not decisions_raw:
        raise _fail(label, "decisions must list at least one path@blob", "shape")
    if "||" in raw or ",," in decisions_raw or decisions_raw.startswith(",") or decisions_raw.endswith(","):
        raise _fail(label, "decisions list must not have empty entries", "shape")
    decisions: list[tuple[str, str]] = []
    for entry in decisions_raw.split(","):
        decisions.append(_split_path_blob(entry, f"{label}.decisions"))
    paths = [path for path, _ in decisions]
    if len(set(paths)) != len(paths):
        raise _fail(label, "decisions must not duplicate paths", "shape")
    if paths != sorted(paths):
        raise _fail(label, "decisions must be sorted lexicographically by path", "shape")
    return {
        "repository": repository,
        "definition_revision": revision,
        "requirements_path": req_path,
        "requirements_blob": req_blob,
        "decisions": decisions,
    }


def validate_definition_authority_key_shape(raw: Any, label: str) -> None:
    """Raise unless ``raw`` is a well-formed canonical key."""
    parse_definition_authority_key(raw, label)


def build_definition_authority_key(
    *,
    repository: str,
    definition_revision: str,
    requirements_path: str,
    requirements_blob: str,
    decisions: list[tuple[str, str]],
    label: str = "definition authority key",
) -> str:
    """Build the canonical key string from structured parts (sorted)."""
    repository = _check_token(repository, label, "repository")
    definition_revision = _check_token(definition_revision, label, "definition revision")
    req_path, req_blob = _split_path_blob(
        f"{requirements_path}@{requirements_blob}", f"{label}.requirements"
    )
    normalized: list[tuple[str, str]] = []
    for path, blob in decisions:
        normalized.append(_split_path_blob(f"{path}@{blob}", f"{label}.decisions"))
    if not normalized:
        raise _fail(label, "decisions must list at least one path@blob", "shape")
    paths = [path for path, _ in normalized]
    if len(set(paths)) != len(paths):
        raise _fail(label, "decisions must not duplicate paths", "shape")
    ordered = sorted(normalized, key=lambda item: item[0])
    decisions_part = ",".join(f"{path}@{blob}" for path, blob in ordered)
    key = (
        f"rf012-v1:repository:{repository}|definition:{definition_revision}|"
        f"requirements:{req_path}@{req_blob}|decisions:{decisions_part}"
    )
    parse_definition_authority_key(key, label)
    return key


def parse_entry_subject_revision(entry_subject: Any, label: str) -> str:
    """Extract the Definition revision from a planning entry subject."""
    if not isinstance(entry_subject, str) or not entry_subject:
        raise _fail(label, "entry_subject must be a non-empty string", "ambiguous")
    parts = entry_subject.split("|")
    if len(parts) != 2 or not parts[0].startswith("definition:"):
        raise _fail(
            label,
            "entry_subject must be definition:<rev>|planning-cycle:<N>",
            "ambiguous",
        )
    revision = parts[0][len("definition:"):]
    if not revision or "|" in revision or any(char.isspace() for char in revision):
        raise _fail(label, "entry_subject Definition revision is malformed", "ambiguous")
    cycle_part = parts[1]
    if not cycle_part.startswith("planning-cycle:"):
        raise _fail(
            label,
            "entry_subject must be definition:<rev>|planning-cycle:<N>",
            "ambiguous",
        )
    try:
        cycle = int(cycle_part[len("planning-cycle:"):])
    except ValueError as exc:
        raise _fail(label, "entry_subject planning cycle is malformed", "ambiguous") from exc
    if cycle < 1:
        raise _fail(label, "entry_subject planning cycle is malformed", "ambiguous")
    return revision


def _definition_paths(definition: dict[str, Any], label: str) -> tuple[str, str, list[str]]:
    try:
        revision = definition["revision"]
        requirements = definition["requirements"]
        decisions = definition["decisions"]
    except (KeyError, TypeError) as exc:
        raise _fail(label, f"Definition record is incomplete: {exc}", "ambiguous") from exc
    if not isinstance(revision, str) or not revision:
        raise _fail(label, "Definition revision must be a non-empty string", "ambiguous")
    if not isinstance(requirements, dict):
        raise _fail(label, "Definition requirements must be a table", "ambiguous")
    req_path = requirements.get("path")
    try:
        req_path = normalize_locator_path(req_path, f"{label}.requirements.path")
    except ExactLocatorError as exc:
        raise DefinitionAuthorityError(str(exc), kind=exc.kind) from exc
    if not isinstance(decisions, list):
        raise _fail(label, "Definition decisions must be an array", "ambiguous")
    dec_paths: list[str] = []
    for index, decision in enumerate(decisions):
        if not isinstance(decision, dict):
            raise _fail(label, f"Definition decisions[{index}] must be a table", "ambiguous")
        try:
            dec_paths.append(
                normalize_locator_path(
                    decision.get("path"), f"{label}.decisions[{index}].path"
                )
            )
        except ExactLocatorError as exc:
            raise DefinitionAuthorityError(str(exc), kind=exc.kind) from exc
    return revision, req_path, dec_paths


def derive_current_authority_key(
    *,
    project_root: Path,
    project_repository: str,
    definition: dict[str, Any],
    label: str = "current Definition authority",
) -> str:
    """Build the live key from current Definition plus worktree bytes."""
    _check_token(project_repository, label, "repository")
    revision, req_path, dec_paths = _definition_paths(definition, label)
    _check_token(revision, label, "definition revision")
    try:
        req_bytes = read_confined_worktree_bytes(
            project_root=project_root, path=req_path, label=f"{label}.requirements"
        )
    except ExactLocatorError as exc:
        raise DefinitionAuthorityError(str(exc), kind=exc.kind) from exc
    req_blob = git_blob_sha(req_bytes)
    decisions: list[tuple[str, str]] = []
    for index, dec_path in enumerate(dec_paths):
        try:
            content = read_confined_worktree_bytes(
                project_root=project_root,
                path=dec_path,
                label=f"{label}.decisions[{index}]",
            )
        except ExactLocatorError as exc:
            raise DefinitionAuthorityError(str(exc), kind=exc.kind) from exc
        decisions.append((dec_path, git_blob_sha(content)))
    try:
        return build_definition_authority_key(
            repository=project_repository,
            definition_revision=revision,
            requirements_path=req_path,
            requirements_blob=req_blob,
            decisions=decisions,
            label=label,
        )
    except DefinitionAuthorityError:
        raise
    except ValueError as exc:
        raise _fail(label, f"cannot build current key: {exc}", "ambiguous") from exc


def _read_snapshot_definition(
    *,
    project_root: Path,
    subject_commit: str,
    workstream_id: str,
    label: str,
) -> dict[str, Any]:
    definition_path = f"implementation/workstreams/{workstream_id}/DEFINITION.toml"
    try:
        blob = resolve_blob_at_commit(
            project_root=project_root,
            commit=subject_commit,
            path=definition_path,
            label=f"{label}.definition",
        )
        content = read_git_blob_bytes(
            project_root=project_root, blob=blob, label=f"{label}.definition"
        )
    except ExactLocatorError as exc:
        raise DefinitionAuthorityError(str(exc), kind=exc.kind) from exc
    try:
        parsed = tomllib.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError, ValueError) as exc:
        raise _fail(label, f"snapshot Definition TOML is unreadable: {exc}", "ambiguous") from exc
    if not isinstance(parsed, dict):
        raise _fail(label, "snapshot Definition must be a TOML table", "ambiguous")
    return parsed


def derive_snapshot_authority_key(
    *,
    project_root: Path,
    project_repository: str,
    subject_commit: str,
    workstream_id: str,
    entry_revision: str,
    label: str = "snapshot Definition authority",
) -> str:
    """Build the freeze-time key from the immutable plan subject snapshot."""
    _check_token(project_repository, label, "repository")
    if not isinstance(subject_commit, str) or SHA40.fullmatch(subject_commit) is None:
        raise _fail(label, "plan subject commit must be exact 40-hex", "ambiguous")
    snapshot = _read_snapshot_definition(
        project_root=project_root,
        subject_commit=subject_commit,
        workstream_id=workstream_id,
        label=label,
    )
    if snapshot.get("workstream_id") != workstream_id:
        raise _fail(label, "snapshot Definition workstream binding is ambiguous", "ambiguous")
    snap_revision, snap_req, snap_decs = _definition_paths(snapshot, f"{label}.snapshot")
    if snap_revision != entry_revision:
        raise _fail(
            label,
            f"entry_subject revision {entry_revision!r} does not match "
            f"snapshot Definition revision {snap_revision!r}",
            "ambiguous",
        )
    if snapshot.get("state") != "green":
        raise _fail(label, "snapshot Definition was not GREEN at freeze time", "ambiguous")
    try:
        req_blob = resolve_blob_at_commit(
            project_root=project_root,
            commit=subject_commit,
            path=snap_req,
            label=f"{label}.requirements",
        )
    except ExactLocatorError as exc:
        raise DefinitionAuthorityError(str(exc), kind=exc.kind) from exc
    decisions: list[tuple[str, str]] = []
    for index, dec_path in enumerate(snap_decs):
        try:
            blob = resolve_blob_at_commit(
                project_root=project_root,
                commit=subject_commit,
                path=dec_path,
                label=f"{label}.decisions[{index}]",
            )
        except ExactLocatorError as exc:
            raise DefinitionAuthorityError(str(exc), kind=exc.kind) from exc
        decisions.append((dec_path, blob))
    return build_definition_authority_key(
        repository=project_repository,
        definition_revision=snap_revision,
        requirements_path=snap_req,
        requirements_blob=req_blob,
        decisions=decisions,
        label=label,
    )


def _describe_key_difference(stored: dict[str, Any], current: dict[str, Any]) -> str:
    if stored["repository"] != current["repository"]:
        return (
            f"repository {stored['repository']!r} does not match "
            f"current {current['repository']!r}"
        )
    if stored["definition_revision"] != current["definition_revision"]:
        return (
            f"Definition revision {stored['definition_revision']!r} is stale; "
            f"current is {current['definition_revision']!r}"
        )
    if (
        stored["requirements_path"] != current["requirements_path"]
        or stored["requirements_blob"] != current["requirements_blob"]
    ):
        return (
            f"requirements {stored['requirements_path']}@{stored['requirements_blob']} "
            f"does not match current "
            f"{current['requirements_path']}@{current['requirements_blob']}"
        )
    if stored["decisions"] != current["decisions"]:
        return "decisions Git identities do not match current authority bytes"
    return "keys differ"


def _describe_snapshot_difference(stored: dict[str, Any], snapshot: dict[str, Any]) -> str:
    if stored["repository"] != snapshot["repository"]:
        return (
            f"repository {stored['repository']!r} does not match "
            f"freeze-time {snapshot['repository']!r}"
        )
    if stored["definition_revision"] != snapshot["definition_revision"]:
        return (
            f"stored revision {stored['definition_revision']!r} does not match "
            f"freeze-time revision {snapshot['definition_revision']!r}"
        )
    if (
        stored["requirements_path"] != snapshot["requirements_path"]
        or stored["requirements_blob"] != snapshot["requirements_blob"]
    ):
        return (
            f"stored requirements {stored['requirements_path']}@{stored['requirements_blob']} "
            f"does not match freeze-time "
            f"{snapshot['requirements_path']}@{snapshot['requirements_blob']}"
        )
    if stored["decisions"] != snapshot["decisions"]:
        return "stored decisions Git identities do not match freeze-time snapshot"
    return "stored key differs from freeze-time snapshot"


def verify_planning_authority_freshness(
    *,
    project_root: Path,
    project_repository: str,
    workstream_id: str,
    definition: dict[str, Any],
    planning: dict[str, Any],
    plan_review: dict[str, Any] | None,
) -> list[str]:
    """Prove Planning/Plan Review freshness against current Definition authority.

    Draft plans return without proof because Strategic Planning already owns
    them. Frozen/approved plans with explicit keys must match each other, the
    live key, and the exact freeze-time snapshot derived from the immutable
    frozen subject commit, with the planning entry revision matching that
    snapshot; keyless plans must uniquely derive the snapshot key and match
    current bytes. Any other state raises :class:`DefinitionAuthorityError`
    for the owning Recovery boundary. Returns the worktree read records for
    progressive disclosure on success.
    """
    state = planning.get("state")
    if state == "draft":
        return []
    if state not in {"frozen", "approved"}:
        raise _fail("planning authority", f"unsupported planning state {state!r}", "ambiguous")
    planning_raw = planning.get("definition_authority_key", "")
    if planning_raw is None:
        planning_raw = ""
    if planning_raw != "" and not isinstance(planning_raw, str):
        raise _fail("planning authority", "planning key must be a string", "shape")
    review_raw = ""
    if plan_review is not None:
        review_raw = plan_review.get("definition_authority_key", "")
        if review_raw is None:
            review_raw = ""
        if review_raw != "" and not isinstance(review_raw, str):
            raise _fail("planning authority", "plan review key must be a string", "shape")
    planning_has = isinstance(planning_raw, str) and planning_raw != ""
    review_has = plan_review is not None and isinstance(review_raw, str) and review_raw != ""
    if plan_review is not None and planning_has != review_has:
        raise _fail(
            "planning authority",
            "Planning and Plan Review authority bindings must both be present or both absent",
            "mismatch",
        )
    if planning_has:
        try:
            stored = parse_definition_authority_key(planning_raw, "planning authority")
        except DefinitionAuthorityError as exc:
            raise _fail("planning authority", f"planning key is malformed: {exc}", exc.kind) from exc
        if plan_review is not None:
            try:
                review_parsed = parse_definition_authority_key(
                    review_raw, "plan review authority"
                )
            except DefinitionAuthorityError as exc:
                raise _fail(
                    "planning authority", f"plan review key is malformed: {exc}", exc.kind
                ) from exc
            if planning_raw != review_raw:
                raise _fail(
                    "planning authority",
                    "Planning and Plan Review authority keys do not match",
                    "mismatch",
                )
            _ = review_parsed
        try:
            current_raw = derive_current_authority_key(
                project_root=project_root,
                project_repository=project_repository,
                definition=definition,
            )
            current = parse_definition_authority_key(current_raw, "current authority")
        except DefinitionAuthorityError as exc:
            raise _fail(
                "planning authority",
                f"live Definition authority is not provable: {exc}",
                exc.kind,
            ) from exc
        if planning_raw != current_raw:
            detail = _describe_key_difference(stored, current)
            raise _fail(
                "planning authority",
                f"stored authority key is stale for current Definition authority: {detail}",
                "stale",
            )
        subject = planning.get("subject")
        if not isinstance(subject, dict):
            raise _fail("planning authority", "frozen plan subject is missing", "ambiguous")
        subject_commit = subject.get("commit")
        if subject.get("repository") != project_repository:
            raise _fail(
                "planning authority",
                "frozen plan subject repository does not match selected project",
                "ambiguous",
            )
        try:
            entry_revision = parse_entry_subject_revision(
                planning.get("entry_subject"), "planning authority"
            )
        except DefinitionAuthorityError:
            raise
        try:
            snapshot_raw = derive_snapshot_authority_key(
                project_root=project_root,
                project_repository=project_repository,
                subject_commit=subject_commit,
                workstream_id=workstream_id,
                entry_revision=entry_revision,
            )
            snapshot = parse_definition_authority_key(snapshot_raw, "snapshot authority")
        except DefinitionAuthorityError as exc:
            raise _fail(
                "planning authority",
                f"freeze-time snapshot is not provable: {exc}",
                exc.kind if exc.kind != "shape" else "ambiguous",
            ) from exc
        if planning_raw != snapshot_raw:
            detail = _describe_snapshot_difference(stored, snapshot)
            raise _fail(
                "planning authority",
                "stored authority key does not match freeze-time snapshot and "
                f"cannot authorize the old subject: {detail}",
                "stale",
            )
        _, req_path, dec_paths = _definition_paths(definition, "planning authority")
        return [f"project:{req_path}", *(f"project:{path}" for path in dec_paths)]
    # Legacy keyless path: derive snapshot from the immutable frozen subject.
    subject = planning.get("subject")
    if not isinstance(subject, dict):
        raise _fail("planning authority", "frozen plan subject is missing", "ambiguous")
    subject_commit = subject.get("commit")
    subject_repository = subject.get("repository")
    if subject_repository != project_repository:
        raise _fail(
            "planning authority",
            "frozen plan subject repository does not match selected project",
            "ambiguous",
        )
    try:
        entry_revision = parse_entry_subject_revision(
            planning.get("entry_subject"), "planning authority"
        )
    except DefinitionAuthorityError:
        raise
    try:
        snapshot_raw = derive_snapshot_authority_key(
            project_root=project_root,
            project_repository=project_repository,
            subject_commit=subject_commit,
            workstream_id=workstream_id,
            entry_revision=entry_revision,
        )
        snapshot = parse_definition_authority_key(snapshot_raw, "snapshot authority")
        current_raw = derive_current_authority_key(
            project_root=project_root,
            project_repository=project_repository,
            definition=definition,
        )
        current = parse_definition_authority_key(current_raw, "current authority")
    except DefinitionAuthorityError as exc:
        raise _fail(
            "planning authority",
            f"legacy authority derivation is ambiguous: {exc}",
            exc.kind if exc.kind != "shape" else "ambiguous",
        ) from exc
    if snapshot_raw != current_raw:
        detail = _describe_key_difference(snapshot, current)
        raise _fail(
            "planning authority",
            f"legacy plan authority is stale for current Definition authority: {detail}",
            "stale",
        )
    _, req_path, dec_paths = _definition_paths(definition, "planning authority")
    return [f"project:{req_path}", *(f"project:{path}" for path in dec_paths)]
