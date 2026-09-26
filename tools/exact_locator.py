#!/usr/bin/env python3
"""RF007 reusable exact locator/readback foundation (H010/H020/H029).

A locator may serve as workflow proof only after this resolver establishes,
against the actual target, the declared semantic path, the exact Git
commit/path/blob identity and — where the serving route relies on current
worktree bytes — that those bytes still match the declared blob. Path
traversal, POSIX/Windows separator aliases and symlink escapes fail closed.

This module is runtime-neutral and dependency-free (stdlib only). Serving
boundaries in ``tools/router.py`` and shape validators across the contracts
reuse it; each caller maps :class:`ExactLocatorError` onto its own owning
Recovery/validation boundary without changing that boundary's semantics.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

SHA40 = re.compile(r"^[0-9a-f]{40}$")
_DRIVE_PREFIX = re.compile(r"^[A-Za-z]:")
_GIT_TIMEOUT_SECONDS = 5


class ExactLocatorError(ValueError):
    """A locator could not be proved against its actual target.

    ``kind`` names the failure class so owning boundaries can map it onto
    their established Recovery/validation reasons: ``unsafe_path``,
    ``repository``, ``identity``, ``dangling``, ``blob_mismatch``,
    ``not_blob``, ``git_unavailable``, ``missing`` or ``mutated``,
    ``escape``.
    """

    def __init__(self, message: str, *, kind: str) -> None:
        super().__init__(message)
        self.kind = kind


def _fail(label: str, detail: str, kind: str) -> ExactLocatorError:
    return ExactLocatorError(f"{label}: {detail}", kind=kind)


def normalize_locator_path(raw: Any, label: str) -> str:
    """Return the canonical repo-relative POSIX spelling of a locator path.

    Rejects empty/non-string values, surrounding whitespace, NUL bytes,
    backslash separators, Windows drive qualifications, absolute paths,
    ``.``/``..`` segments and duplicate/leading/trailing separators, so one
    spelling names one target on every platform.
    """
    if not isinstance(raw, str) or not raw.strip():
        raise _fail(label, f"path must be a non-empty string, got {raw!r}", "unsafe_path")
    if raw != raw.strip():
        raise _fail(label, f"leading/trailing whitespace is forbidden in {raw!r}", "unsafe_path")
    if "\x00" in raw:
        raise _fail(label, "NUL byte is forbidden in locator paths", "unsafe_path")
    if "\\" in raw:
        raise _fail(
            label,
            f"backslash separators are forbidden in {raw!r}; use canonical POSIX spelling",
            "unsafe_path",
        )
    if _DRIVE_PREFIX.match(raw):
        raise _fail(
            label, f"drive-qualified paths are forbidden in {raw!r}", "unsafe_path"
        )
    if any(char in raw for char in ("\n", "\r", "\t")):
        raise _fail(label, "control characters are forbidden in locator paths", "unsafe_path")
    path = PurePosixPath(raw)
    if path.is_absolute():
        raise _fail(label, f"absolute paths are forbidden in {raw!r}", "unsafe_path")
    if ".." in path.parts:
        raise _fail(label, f"path traversal is forbidden in {raw!r}", "unsafe_path")
    if raw != path.as_posix() or raw in {".", ".."}:
        raise _fail(
            label,
            f"path must use canonical repo-relative POSIX spelling, got {raw!r}",
            "unsafe_path",
        )
    return raw


def git_blob_sha(content: bytes) -> str:
    """Return the Git blob object id for exact content bytes."""
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def _run_git(project_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", "-C", str(project_root), *args],
            capture_output=True,
            text=True,
            check=False,
            timeout=_GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise _fail("git", f"Git readback failed: {exc}", "git_unavailable") from exc


@dataclass(frozen=True)
class VerifiedLocator:
    """An existence- and identity-proved exact locator."""

    repository: str
    commit: str
    path: str
    blob: str
    key: str


def resolve_blob_at_commit(
    *,
    project_root: Path,
    commit: Any,
    path: Any,
    label: str,
) -> str:
    """Return the exact blob identity for ``<commit>:<path>`` in Git.

    RF012 legacy derivation uses this to discover the Definition authority
    snapshot bound to an immutable frozen plan subject commit. Path
    normalization, Git timeout handling and blob-type proof match
    :func:`verify_exact_git_locator` exactly.
    """
    locator_path = normalize_locator_path(path, f"{label}.path")
    if not isinstance(commit, str) or SHA40.fullmatch(commit) is None:
        raise _fail(label, "commit must be exact 40-hex Git identity", "identity")
    resolved = _run_git(project_root, "rev-parse", "--verify", f"{commit}:{locator_path}")
    if resolved.returncode != 0:
        raise _fail(
            label,
            f"exact Git subject {commit}:{locator_path} does not resolve",
            "dangling",
        )
    actual_blob = resolved.stdout.strip()
    if SHA40.fullmatch(actual_blob) is None:
        raise _fail(
            label,
            f"exact Git subject {commit}:{locator_path} does not resolve to a blob identity",
            "dangling",
        )
    kind = _run_git(project_root, "cat-file", "-t", actual_blob)
    if kind.returncode != 0 or kind.stdout.strip() != "blob":
        raise _fail(
            label,
            f"exact locator {locator_path!r} does not resolve to a Git blob",
            "not_blob",
        )
    return actual_blob


def read_confined_worktree_bytes(
    *,
    project_root: Path,
    path: Any,
    label: str,
) -> bytes:
    """Return current worktree bytes at ``path`` after rooted confinement proof.

    RF012 current-authority derivation uses this to hash live authority bytes
    without a declared blob. Confinement, missing-file and unsafe-path
    behavior match :func:`verify_worktree_freshness` exactly.
    """
    locator_path = normalize_locator_path(path, f"{label}.path")
    root = project_root.resolve()
    candidate = (root / Path(*PurePosixPath(locator_path).parts)).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise _fail(
            label, f"path escapes the declared root: {locator_path!r}", "escape"
        ) from exc
    try:
        return candidate.read_bytes()
    except OSError as exc:
        raise _fail(
            label, f"declared target {locator_path!r} cannot be read back: {exc}", "missing"
        ) from exc


def read_git_blob_bytes(
    *,
    project_root: Path,
    blob: Any,
    label: str,
) -> bytes:
    """Return the exact content bytes for a Git blob identity.

    RF012 legacy derivation uses this to read the snapshot Definition record
    bound to an immutable frozen plan subject commit.
    """
    if not isinstance(blob, str) or SHA40.fullmatch(blob) is None:
        raise _fail(label, "blob must be exact 40-hex Git identity", "identity")
    try:
        completed = subprocess.run(
            ["git", "-C", str(project_root), "cat-file", "-p", blob],
            capture_output=True,
            check=False,
            timeout=_GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise _fail("git", f"Git readback failed: {exc}", "git_unavailable") from exc
    if completed.returncode != 0:
        raise _fail(label, f"exact Git blob {blob} does not resolve", "dangling")
    return bytes(completed.stdout)


def verify_exact_git_locator(
    *,
    project_root: Path,
    repository: Any,
    expected_repository: str | None,
    commit: Any,
    path: Any,
    blob: Any,
    label: str,
) -> VerifiedLocator:
    """Prove that ``(repository, commit, path)`` resolves to ``blob`` in Git.

    Establishes target existence and exact Git object identity. Git
    ``<commit>:<path>`` lookup never traverses committed symlinks, so the
    resolved blob is inherently confined to the repository; worktree
    confinement is enforced separately by :func:`verify_worktree_freshness`
    and the serving boundary's rooted reads.
    """
    locator_path = normalize_locator_path(path, f"{label}.path")
    if expected_repository is not None and repository != expected_repository:
        raise _fail(
            label,
            f"repository {repository!r} does not match {expected_repository!r}",
            "repository",
        )
    if not isinstance(repository, str) or not repository.strip():
        raise _fail(label, "repository must be a non-empty string", "identity")
    if not isinstance(commit, str) or SHA40.fullmatch(commit) is None:
        raise _fail(label, "commit must be exact 40-hex Git identity", "identity")
    if not isinstance(blob, str) or SHA40.fullmatch(blob) is None:
        raise _fail(label, "blob must be exact 40-hex Git identity", "identity")
    resolved = _run_git(project_root, "rev-parse", "--verify", f"{commit}:{locator_path}")
    if resolved.returncode != 0:
        raise _fail(
            label,
            f"exact Git subject {commit}:{locator_path} does not resolve",
            "dangling",
        )
    actual_blob = resolved.stdout.strip()
    if actual_blob != blob:
        raise _fail(
            label,
            f"declared blob {blob} does not match exact Git identity {actual_blob}",
            "blob_mismatch",
        )
    kind = _run_git(project_root, "cat-file", "-t", actual_blob)
    if kind.returncode != 0 or kind.stdout.strip() != "blob":
        raise _fail(
            label,
            f"exact locator {locator_path!r} does not resolve to a Git blob",
            "not_blob",
        )
    return VerifiedLocator(
        repository=repository,
        commit=commit,
        path=locator_path,
        blob=blob,
        key=f"{repository}@{commit}:{locator_path}@{blob}",
    )


def verify_worktree_freshness(
    *,
    project_root: Path,
    path: Any,
    blob: Any,
    label: str,
) -> bytes:
    """Prove current worktree bytes at ``path`` still match declared ``blob``.

    Resolves the path against ``project_root`` (symlink escapes fail closed)
    and compares the single-read content's Git blob id to the declared
    identity, so a same-path mutation cannot pass as the declared subject.
    Returns the verified content bytes so callers never re-read past the
    proof.
    """
    locator_path = normalize_locator_path(path, f"{label}.path")
    if not isinstance(blob, str) or SHA40.fullmatch(blob) is None:
        raise _fail(label, "blob must be exact 40-hex Git identity", "identity")
    root = project_root.resolve()
    candidate = (root / Path(*PurePosixPath(locator_path).parts)).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise _fail(
            label, f"path escapes the declared root: {locator_path!r}", "escape"
        ) from exc
    try:
        content = candidate.read_bytes()
    except OSError as exc:
        raise _fail(
            label, f"declared target {locator_path!r} cannot be read back: {exc}", "missing"
        ) from exc
    if git_blob_sha(content) != blob:
        raise _fail(
            label,
            f"worktree bytes at {locator_path!r} do not match declared blob {blob}",
            "mutated",
        )
    return content
