#!/usr/bin/env python3
"""RF006 review-attempt identity and legacy migration provenance (H008/H009).

New/current review attempts have immutable exact Git blob identity and
append-only attempt history: the same Card/attempt ID cannot silently change
bytes or verdict, and an attempt locator must resolve exact
repository/commit/path/blob before any route or review status relies on it.

A genuinely legacy-shaped attempt is recognized only by explicit migration
provenance bound to the exact immutable source attempt and exact source
Git/workstream state. Migration fields may be added only when uniquely
derivable; ambiguous or newly authored legacy-looking attempts fail closed.

Helperless derivation: ``git rev-parse <commit>:<path>`` plus ``git cat-file``
for blob identity/content, string comparison for bindings, TOML parse for
source Board listing proof.
"""

from __future__ import annotations

import re
import subprocess
import tomllib
from pathlib import Path
from typing import Any

try:
    from tools.exact_locator import (
        ExactLocatorError,
        normalize_locator_path,
        read_git_blob_bytes,
        resolve_blob_at_commit,
        verify_exact_git_locator,
        verify_worktree_freshness,
    )
except ModuleNotFoundError:  # direct script execution from tools/
    from exact_locator import (
        ExactLocatorError,
        normalize_locator_path,
        read_git_blob_bytes,
        resolve_blob_at_commit,
        verify_exact_git_locator,
        verify_worktree_freshness,
    )

SHA40 = re.compile(r"^[0-9a-f]{40}$")
PROVENANCE_KEYS = frozenset({
    "source_repository",
    "source_commit",
    "source_path",
    "source_blob",
    "source_workstream",
    "source_card",
    "source_attempt",
})
LOCATOR_KEYS = frozenset({"class", "path", "commit", "blob"})


class ReviewAttemptProvenanceError(ValueError):
    """A review-attempt identity or legacy provenance binding could not be proved.

    ``kind`` names the failure class: ``shape``, ``mismatch``, ``stale``,
    ``missing``, ``ambiguous``, ``ancestry`` or an RF007 locator kind
    (``repository``, ``identity``, ``dangling``, ``blob_mismatch``,
    ``not_blob``, ``git_unavailable``, ``unsafe_path``, ``escape``,
    ``mutated``).
    """

    def __init__(self, message: str, *, kind: str) -> None:
        super().__init__(message)
        self.kind = kind


def _fail(label: str, detail: str, kind: str) -> ReviewAttemptProvenanceError:
    return ReviewAttemptProvenanceError(f"{label}: {detail}", kind=kind)


def validate_review_attempt_locator_shape(
    ref: Any,
    workstream_id: str,
    label: str,
) -> dict[str, str | None]:
    """Validate a Board review_attempt locator shape, returning its canonical form.

    Path must be the exact workstream-local reviews TOML. ``commit``/``blob``
    are optional at shape level so correctly terminal history stays
    shape-valid, but when either is present both must be exact 40-hex Git
    identity. Unknown keys fail closed so bogus locators cannot be ignored.
    Git existence/identity is proved by the serving boundary through the
    shared RF007 resolver, never here.
    """
    if not isinstance(ref, dict):
        raise _fail(label, "locator must be a table", "shape")
    unknown = sorted(set(ref) - LOCATOR_KEYS)
    if unknown:
        raise _fail(label, f"unknown field(s): {', '.join(unknown)}", "shape")
    if ref.get("class") != "review_attempt":
        raise _fail(label, "expected class 'review_attempt'", "shape")
    try:
        path = normalize_locator_path(ref.get("path"), f"{label}.path")
    except ExactLocatorError as exc:
        raise _fail(label, f"path is unsafe: {exc}", "shape") from exc
    prefix = f"implementation/workstreams/{workstream_id}/reviews/"
    if not (path.startswith(prefix) and path.endswith(".toml")):
        raise _fail(label, "wrong review_attempt class/path", "shape")
    has_commit = "commit" in ref
    has_blob = "blob" in ref
    if has_commit != has_blob:
        raise _fail(
            label,
            "exact review_attempt identity requires commit + blob together",
            "shape",
        )
    commit = ref.get("commit")
    blob = ref.get("blob")
    if has_commit:
        if not isinstance(commit, str) or SHA40.fullmatch(commit) is None:
            raise _fail(label, "commit must be exact 40-hex Git identity", "shape")
        if not isinstance(blob, str) or SHA40.fullmatch(blob) is None:
            raise _fail(label, "blob must be exact 40-hex Git identity", "shape")
        return {"class": "review_attempt", "path": path, "commit": commit, "blob": blob}
    return {"class": "review_attempt", "path": path, "commit": None, "blob": None}


def validate_legacy_migration_shape(
    provenance: Any,
    *,
    workstream_id: str,
    card_id: str,
    attempt_id: str,
    label: str = "legacy migration provenance",
) -> dict[str, str]:
    """Validate explicit legacy migration provenance shape, returning canonical form.

    The provenance binds the exact immutable source attempt
    (repository/commit/path/blob) plus the exact source Git/workstream state
    (source commit plus source workstream/card/attempt). Git proof is owned by
    the serving boundary; this validator establishes exact keys, canonical
    path spelling, 40-hex identities and workstream-local binding only.
    """
    if not isinstance(provenance, dict):
        raise _fail(label, "provenance must be a table", "shape")
    missing = sorted(PROVENANCE_KEYS - set(provenance))
    extra = sorted(set(provenance) - PROVENANCE_KEYS)
    if missing:
        raise _fail(label, f"missing field(s): {', '.join(missing)}", "shape")
    if extra:
        raise _fail(label, f"unknown field(s): {', '.join(extra)}", "shape")
    repository = provenance.get("source_repository")
    if not isinstance(repository, str) or not repository.strip():
        raise _fail(label, "source_repository must be a non-empty string", "shape")
    commit = provenance.get("source_commit")
    if not isinstance(commit, str) or SHA40.fullmatch(commit) is None:
        raise _fail(label, "source_commit must be exact 40-hex Git identity", "shape")
    blob = provenance.get("source_blob")
    if not isinstance(blob, str) or SHA40.fullmatch(blob) is None:
        raise _fail(label, "source_blob must be exact 40-hex Git identity", "shape")
    try:
        path = normalize_locator_path(provenance.get("source_path"), f"{label}.source_path")
    except ExactLocatorError as exc:
        raise _fail(label, f"source_path is unsafe: {exc}", "shape") from exc
    prefix = f"implementation/workstreams/{workstream_id}/reviews/"
    if not (path.startswith(prefix) and path.endswith(".toml")):
        raise _fail(label, "source_path must be the exact workstream-local reviews TOML", "shape")
    expected_path = f"implementation/workstreams/{workstream_id}/reviews/{card_id}-{attempt_id}.toml"
    if path != expected_path:
        raise _fail(
            label,
            f"source_path {path!r} does not match the exact current attempt path {expected_path!r}",
            "shape",
        )
    for field, expected in (
        ("source_workstream", workstream_id),
        ("source_card", card_id),
        ("source_attempt", attempt_id),
    ):
        value = provenance.get(field)
        if not isinstance(value, str) or not value:
            raise _fail(label, f"{field} must be a non-empty string", "shape")
        if value != expected:
            raise _fail(
                label,
                f"{field} {value!r} does not match the exact current {expected!r}",
                "shape",
            )
    return {
        "source_repository": repository,
        "source_commit": commit,
        "source_path": path,
        "source_blob": blob,
        "source_workstream": workstream_id,
        "source_card": card_id,
        "source_attempt": attempt_id,
    }


def _parse_toml_bytes(content: bytes, label: str) -> dict[str, Any]:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _fail(label, f"source blob is not UTF-8 text: {exc}", "mismatch") from exc
    try:
        parsed = tomllib.loads(text)
    except (tomllib.TOMLDecodeError, ValueError) as exc:
        raise _fail(label, f"source blob TOML is malformed: {exc}", "mismatch") from exc
    if not isinstance(parsed, dict):
        raise _fail(label, "source blob must be a TOML table", "mismatch")
    return parsed


def _strip_provenance(attempt: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in attempt.items() if key != "legacy_migration"}


def verify_legacy_migration(
    *,
    project_root: Path,
    project_repository: str,
    workstream_id: str,
    card_id: str,
    attempt: dict[str, Any],
    label: str = "legacy migration provenance",
) -> str:
    """Prove explicit legacy provenance against exact immutable source state.

    The source (repository/commit/path/blob) must resolve in Git, the source
    blob must be a legacy-shaped terminal attempt without its own provenance
    whose remaining fields exactly equal the current attempt's fields, and the
    source Task Board at the source commit must already list the attempt path
    for the Card. Any other state — missing source, rewritten verdict/bytes,
    sibling/workstream mismatch, or a source Board that never listed the path
    — fails closed as ambiguous/mismatched. Returns the progressive-disclosure
    read record on success.
    """
    attempt_id = attempt.get("attempt")
    if not isinstance(attempt_id, str) or not attempt_id:
        raise _fail(label, "current attempt has no exact attempt identity", "missing")
    provenance_raw = attempt.get("legacy_migration")
    if not isinstance(provenance_raw, dict):
        raise _fail(
            label,
            "legacy-shaped attempt requires explicit migration provenance; "
            "file shape alone never proves historical status",
            "missing",
        )
    provenance = validate_legacy_migration_shape(
        provenance_raw,
        workstream_id=workstream_id,
        card_id=card_id,
        attempt_id=attempt_id,
        label=label,
    )
    if provenance["source_repository"] != project_repository:
        raise _fail(
            label,
            f"source repository {provenance['source_repository']!r} does not match "
            f"the selected project {project_repository!r}",
            "repository",
        )
    try:
        verified = verify_exact_git_locator(
            project_root=project_root,
            repository=provenance["source_repository"],
            expected_repository=project_repository,
            commit=provenance["source_commit"],
            path=provenance["source_path"],
            blob=provenance["source_blob"],
            label=label,
        )
        source_bytes = read_git_blob_bytes(
            project_root=project_root, blob=provenance["source_blob"], label=label
        )
    except ExactLocatorError as exc:
        raise ReviewAttemptProvenanceError(str(exc), kind=exc.kind) from exc
    source = _parse_toml_bytes(source_bytes, label)
    if "legacy_migration" in source:
        raise _fail(
            label,
            "source attempt must be the exact immutable pre-migration record; "
            "a provenance-bearing source is ambiguous",
            "ambiguous",
        )
    if "review_kind" in source:
        raise _fail(
            label,
            "source attempt must be legacy-shaped; an explicit source cannot "
            "prove legacy status",
            "mismatch",
        )
    current_stripped = _strip_provenance(attempt)
    if source != current_stripped:
        # Fail closed on any silent rewrite: verdict, subject, evidence,
        # acceptance, independence or any other durable field differs.
        raise _fail(
            label,
            "source attempt content does not exactly match the current "
            "legacy-shaped attempt; the same attempt ID cannot silently "
            "change bytes or verdict",
            "mismatch",
        )
    if source.get("workstream_id") != workstream_id:
        raise _fail(label, "source attempt belongs to another workstream", "mismatch")
    if source.get("card_id") != card_id:
        raise _fail(label, "source attempt belongs to another Card", "mismatch")
    if source.get("attempt") != attempt_id:
        raise _fail(label, "source attempt identity does not match current attempt", "mismatch")
    if source.get("verdict") not in {"green", "red"}:
        raise _fail(label, "source legacy attempt must be terminal green/red", "mismatch")
    # The source Board at the source commit must already list this attempt
    # path for the Card. A newly authored file committed now was never listed
    # in any prior Board, so no valid source commit exists for it.
    board_path = f"implementation/workstreams/{workstream_id}/TASK_BOARD.toml"
    board_bytes = _read_board_at_commit(
        project_root=project_root,
        commit=provenance["source_commit"],
        path=board_path,
        label=label,
    )
    board = _parse_toml_bytes(board_bytes, f"{label}.source_board")
    cards = board.get("cards", [])
    if not isinstance(cards, list):
        raise _fail(label, "source Board has no card array; provenance is ambiguous", "ambiguous")
    card = next(
        (entry for entry in cards if isinstance(entry, dict) and entry.get("id") == card_id),
        None,
    )
    if card is None:
        raise _fail(
            label,
            f"source Board at {provenance['source_commit']} has no Card {card_id!r}; "
            "newly authored attempts were never historically listed",
            "ambiguous",
        )
    refs = card.get("review_attempts", [])
    if not isinstance(refs, list):
        raise _fail(label, "source Card has no review_attempts array", "ambiguous")
    listed = {
        item.get("path") for item in refs if isinstance(item, dict)
    }
    if provenance["source_path"] not in listed:
        raise _fail(
            label,
            f"source Board at {provenance['source_commit']} never listed "
            f"{provenance['source_path']!r}; migration is uniquely derivable "
            "only from a historically listed source",
            "ambiguous",
        )
    # The source bytes must already be durable at the source commit's parent:
    # a legacy file introduced (or rewritten) by the source commit itself was
    # never historically listed, so a same-commit file+Board addition cannot
    # self-certify historical status.
    _require_source_predates_listing(
        project_root=project_root,
        commit=provenance["source_commit"],
        path=provenance["source_path"],
        blob=provenance["source_blob"],
        label=label,
    )
    return f"project-git:{verified.key}"


def _require_source_predates_listing(
    *, project_root: Path, commit: str, path: str, blob: str, label: str
) -> None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(project_root), "rev-parse", "--verify", f"{commit}^"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ReviewAttemptProvenanceError(
            f"{label}: source history readback failed: {exc}", kind="git_unavailable"
        ) from exc
    if completed.returncode != 0:
        raise _fail(
            label,
            "source commit has no parent history; a file introduced together "
            "with its Board listing cannot prove prior durability",
            "ambiguous",
        )
    parent = completed.stdout.strip()
    if SHA40.fullmatch(parent) is None:
        raise _fail(label, "source parent commit identity is malformed", "git_unavailable")
    try:
        parent_blob = resolve_blob_at_commit(
            project_root=project_root, commit=parent, path=path, label=f"{label}.source_parent"
        )
    except ExactLocatorError as exc:
        raise _fail(
            label,
            "source attempt was added in the same source commit as its Board "
            "listing; a same-commit addition cannot self-certify historical status",
            "ambiguous",
        ) from exc
    if parent_blob != blob:
        raise _fail(
            label,
            "source commit rewrote the source attempt bytes; the listing cannot "
            "certify bytes with no prior durability",
            "ambiguous",
        )


def _read_board_at_commit(
    *, project_root: Path, commit: str, path: str, label: str
) -> bytes:
    try:
        blob = resolve_blob_at_commit(
            project_root=project_root, commit=commit, path=path, label=f"{label}.source_board"
        )
        return read_git_blob_bytes(project_root=project_root, blob=blob, label=f"{label}.source_board")
    except ExactLocatorError as exc:
        raise ReviewAttemptProvenanceError(
            f"{label}: source Board {commit}:{path} is unreadable; provenance is ambiguous",
            kind="ambiguous",
        ) from exc


def _require_commit_in_head_ancestry(
    *, project_root: Path, commit: str, label: str
) -> None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(project_root), "merge-base", "--is-ancestor", commit, "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ReviewAttemptProvenanceError(
            f"{label}: HEAD ancestry readback failed: {exc}", kind="git_unavailable"
        ) from exc
    if completed.returncode != 0:
        raise _fail(
            label,
            f"locator commit {commit} is outside HEAD ancestry; relied-upon "
            "review history must be anchored on the selected HEAD line",
            "ancestry",
        )


def verify_review_attempt_locator(
    *,
    project_root: Path,
    project_repository: str,
    workstream_id: str,
    card_id: str,
    ref: dict[str, Any],
    label: str,
) -> tuple[dict[str, Any], bytes, str]:
    """Prove one Board review_attempt locator and return its verified attempt.

    The locator must carry exact (commit, blob) Git identity, resolve in Git,
    sit within HEAD ancestry, and match current worktree bytes. Returns the
    parsed attempt, the verified content bytes and the progressive-disclosure
    read record. Callers must never re-read past this proof.
    """
    try:
        shape = validate_review_attempt_locator_shape(ref, workstream_id, label)
    except ReviewAttemptProvenanceError as exc:
        raise ReviewAttemptProvenanceError(str(exc), kind=exc.kind) from exc
    if shape["commit"] is None or shape["blob"] is None:
        raise _fail(
            label,
            "exact review_attempt identity requires commit + blob 40-hex; "
            "path-only locators cannot prove immutable history",
            "missing",
        )
    try:
        verified = verify_exact_git_locator(
            project_root=project_root,
            repository=project_repository,
            expected_repository=project_repository,
            commit=shape["commit"],
            path=shape["path"],
            blob=shape["blob"],
            label=label,
        )
        content = verify_worktree_freshness(
            project_root=project_root,
            path=shape["path"],
            blob=shape["blob"],
            label=label,
        )
    except ExactLocatorError as exc:
        raise ReviewAttemptProvenanceError(str(exc), kind=exc.kind) from exc
    # Relied-upon history must be anchored on the selected HEAD line: the
    # terminal freeze walks HEAD ancestry, so an off-HEAD locator commit
    # would hide its own prior terminal state from that walk.
    _require_commit_in_head_ancestry(
        project_root=project_root,
        commit=shape["commit"],
        label=label,
    )
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _fail(label, f"review attempt {shape['path']!r} is not UTF-8 text", "mismatch") from exc
    try:
        parsed = tomllib.loads(text)
    except (tomllib.TOMLDecodeError, ValueError) as exc:
        raise _fail(
            label, f"review attempt {shape['path']!r} has malformed TOML: {exc}", "mismatch"
        ) from exc
    if not isinstance(parsed, dict):
        raise _fail(label, "review attempt must be a TOML table", "mismatch")
    if parsed.get("workstream_id") != workstream_id:
        raise _fail(label, "review attempt belongs to another workstream", "mismatch")
    if parsed.get("card_id") != card_id:
        raise _fail(label, "review attempt belongs to another Card", "mismatch")
    attempt_id = parsed.get("attempt")
    if not isinstance(attempt_id, str) or not attempt_id:
        raise _fail(label, "review attempt has no exact attempt identity", "mismatch")
    expected_path = f"implementation/workstreams/{workstream_id}/reviews/{card_id}-{attempt_id}.toml"
    if shape["path"] != expected_path:
        raise _fail(
            label,
            f"locator path {shape['path']!r} does not match the exact attempt "
            f"identity path {expected_path!r}",
            "mismatch",
        )
    return parsed, content, f"project-git:{verified.key}"


def verify_history_append_only(
    prior: list[dict[str, Any]] | None,
    current: list[dict[str, Any]],
    *,
    label: str = "review history",
) -> None:
    """Require current history to extend prior without silent rewrite.

    Every prior attempt ID must still be present with byte-identical durable
    content (attempt, verdict, subject, acceptance, evidence and, for explicit
    attempts, review-kind/convergence fields; legacy provenance itself is
    excluded because migration only adds it). A same-ID RED-to-GREEN flip or
    any other silent mutation fails closed. ``None`` prior means no earlier
    history is claimed and only current-list append-only rules apply.
    """
    if prior is None:
        return
    if not isinstance(prior, list) or not isinstance(current, list):
        raise _fail(label, "histories must be arrays", "shape")
    prior_by_id = {}
    for entry in prior:
        if not isinstance(entry, dict):
            raise _fail(label, "prior history entries must be tables", "shape")
        attempt_id = entry.get("attempt")
        if not isinstance(attempt_id, str) or not attempt_id:
            raise _fail(label, "prior history entry lacks attempt identity", "shape")
        if attempt_id in prior_by_id:
            raise _fail(label, f"duplicate prior attempt {attempt_id!r}", "shape")
        prior_by_id[attempt_id] = entry
    current_by_id = {}
    for entry in current:
        if not isinstance(entry, dict):
            raise _fail(label, "current history entries must be tables", "shape")
        attempt_id = entry.get("attempt")
        if not isinstance(attempt_id, str) or not attempt_id:
            raise _fail(label, "current history entry lacks attempt identity", "shape")
        if attempt_id in current_by_id:
            raise _fail(label, f"duplicate current attempt {attempt_id!r}", "shape")
        current_by_id[attempt_id] = entry
    for attempt_id, prior_entry in prior_by_id.items():
        current_entry = current_by_id.get(attempt_id)
        if current_entry is None:
            raise _fail(
                label,
                f"prior attempt {attempt_id!r} is missing from current history; "
                "review history is append-only",
                "mismatch",
            )
        if _strip_provenance(prior_entry) != _strip_provenance(current_entry):
            raise _fail(
                label,
                f"prior attempt {attempt_id!r} was silently rewritten; the same "
                "attempt ID cannot change bytes or verdict",
                "mismatch",
            )


def _history_commits_for_path(
    *, project_root: Path, path: str, label: str
) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "-C", str(project_root), "log", "--full-history", "--format=%H", "HEAD", "--", path],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ReviewAttemptProvenanceError(
            f"{label}: Git history readback failed: {exc}", kind="git_unavailable"
        ) from exc
    if completed.returncode != 0:
        raise ReviewAttemptProvenanceError(
            f"{label}: Git history for {path!r} is unreadable", kind="git_unavailable"
        )
    commits = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    for commit in commits:
        if SHA40.fullmatch(commit) is None:
            raise _fail(
                label,
                f"Git history for {path!r} returned a malformed commit identity",
                "git_unavailable",
            )
    return commits


def verify_terminal_append_only_from_git(
    *,
    project_root: Path,
    workstream_id: str,
    card_id: str,
    attempts: list[dict[str, Any]],
    label: str = "review history",
) -> list[str]:
    """Freeze terminal attempt bytes against actual durable Git history.

    For every current attempt, walk the attempt path's ``HEAD`` history with
    full history (merged side-branch versions included) and require each
    historical terminal (green/red) version to match the current attempt's
    durable content (legacy provenance itself excluded, because migration
    only adds it). A same-ID RED-to-GREEN flip — or any other silent
    terminal mutation — fails closed even when the Board locator was rebound
    to the rewritten commit/blob. Historical pending/in_progress versions
    impose no constraint, so the legitimate pending/in_progress-to-terminal
    lifecycle still routes. Returns progressive-disclosure read records.
    """
    reads: list[str] = []
    for attempt in attempts:
        attempt_id = attempt.get("attempt")
        if not isinstance(attempt_id, str) or not attempt_id:
            raise _fail(label, "current history entry lacks attempt identity", "shape")
        path = (
            f"implementation/workstreams/{workstream_id}/reviews/"
            f"{card_id}-{attempt_id}.toml"
        )
        current_stripped = _strip_provenance(attempt)
        commits = _history_commits_for_path(
            project_root=project_root, path=path, label=label
        )
        for commit in commits:
            try:
                blob = resolve_blob_at_commit(
                    project_root=project_root, commit=commit, path=path, label=label
                )
            except ExactLocatorError as exc:
                if exc.kind == "dangling":
                    # Path absent at that commit (e.g. deletion); nothing to compare.
                    continue
                raise ReviewAttemptProvenanceError(str(exc), kind=exc.kind) from exc
            try:
                content = read_git_blob_bytes(
                    project_root=project_root, blob=blob, label=label
                )
            except ExactLocatorError as exc:
                raise ReviewAttemptProvenanceError(str(exc), kind=exc.kind) from exc
            try:
                historical = _parse_toml_bytes(content, label)
            except ReviewAttemptProvenanceError:
                # Never a valid attempt; current validation governs current bytes.
                continue
            if (historical.get("workstream_id"), historical.get("card_id"),
                    historical.get("attempt")) != (workstream_id, card_id, attempt_id):
                raise _fail(
                    label,
                    f"attempt path {path!r} carries another attempt identity in "
                    "Git history; the same path cannot change identity",
                    "mismatch",
                )
            if historical.get("verdict") not in {"green", "red"}:
                continue
            if _strip_provenance(historical) != current_stripped:
                raise _fail(
                    label,
                    f"prior terminal attempt {attempt_id!r} was silently rewritten; "
                    "the same attempt ID cannot change bytes or verdict",
                    "mismatch",
                )
        reads.append(f"project-git-log:{path}")
    return reads
