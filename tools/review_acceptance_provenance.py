#!/usr/bin/env python3
"""Explicit migration proof for immutable path-only Card Review acceptance."""

from __future__ import annotations

import re
import subprocess
import tomllib
from collections.abc import Mapping
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
except ModuleNotFoundError:
    from exact_locator import (
        ExactLocatorError,
        normalize_locator_path,
        read_git_blob_bytes,
        resolve_blob_at_commit,
        verify_exact_git_locator,
        verify_worktree_freshness,
    )

SHA40 = re.compile(r"^[0-9a-f]{40}$")
PROOF_KEYS = frozenset({
    "card_id", "attempt_id", "source_repository", "source_commit",
    "source_path", "source_blob", "source_workstream", "source_card",
    "acceptance_path", "acceptance_blob",
})


class ReviewAcceptanceProvenanceError(ValueError):
    def __init__(self, message: str, *, kind: str = "invalid") -> None:
        super().__init__(message)
        self.kind = kind


def _fail(label: str, detail: str, kind: str = "invalid") -> ReviewAcceptanceProvenanceError:
    return ReviewAcceptanceProvenanceError(f"{label}: {detail}", kind=kind)


def _require_ancestry(root: Path, commit: str, label: str) -> None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "merge-base", "--is-ancestor", commit, "HEAD"],
            capture_output=True, check=False, timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise _fail(label, f"HEAD ancestry check failed: {exc}", "git_unavailable") from exc
    if proc.returncode != 0:
        raise _fail(label, f"source commit {commit} is not in selected HEAD ancestry", "stale")


def validate_review_acceptance_migration_shape(
    raw: Any, *, workstream_id: str, card_id: str | None = None,
    label: str = "review acceptance migration",
) -> dict[str, str]:
    if not isinstance(raw, Mapping):
        raise _fail(label, "proof must be a table")
    extra = sorted(set(raw) - PROOF_KEYS)
    missing = sorted(PROOF_KEYS - set(raw))
    if extra or missing:
        raise _fail(label, f"proof keys mismatch; missing={missing}, extra={extra}")
    out = {key: raw[key] for key in PROOF_KEYS}
    if any(not isinstance(value, str) or not value for value in out.values()):
        raise _fail(label, "all proof fields must be non-empty strings")
    if card_id is not None and out["card_id"] != card_id:
        raise _fail(label, "card_id does not match selected Card")
    if out["source_card"] != out["card_id"]:
        raise _fail(label, "source_card does not match card_id")
    if out["source_workstream"] != workstream_id:
        raise _fail(label, "source_workstream does not match selected workstream")
    if SHA40.fullmatch(out["source_commit"]) is None:
        raise _fail(label, "source_commit must be exact 40-hex Git identity")
    if SHA40.fullmatch(out["source_blob"]) is None or SHA40.fullmatch(out["acceptance_blob"]) is None:
        raise _fail(label, "source_blob and acceptance_blob must be exact 40-hex Git identities")
    try:
        source_path = normalize_locator_path(out["source_path"], f"{label}.source_path")
        acceptance_path = normalize_locator_path(out["acceptance_path"], f"{label}.acceptance_path")
    except ExactLocatorError as exc:
        raise _fail(label, str(exc), exc.kind) from exc
    review_prefix = f"implementation/workstreams/{workstream_id}/reviews/"
    card_prefix = f"implementation/workstreams/{workstream_id}/cards/"
    if not source_path.startswith(review_prefix) or not source_path.endswith(".toml"):
        raise _fail(label, "source_path is outside selected workstream reviews")
    if not acceptance_path.startswith(card_prefix) or not acceptance_path.endswith(".md"):
        raise _fail(label, "acceptance_path is outside selected workstream cards")
    expected_card = f"{card_prefix}{out['card_id']}.md"
    if acceptance_path != expected_card:
        raise _fail(label, "acceptance_path does not name the selected Card")
    return out


def migration_for_attempt(
    board: Mapping[str, Any], card_id: str, attempt_id: str
) -> Mapping[str, Any] | None:
    records = board.get("review_acceptance_migrations", []) or []
    found = [
        r for r in records
        if isinstance(r, Mapping)
        and r.get("card_id") == card_id
        and r.get("attempt_id") == attempt_id
    ]
    if len(found) > 1:
        raise _fail("review acceptance migration", f"duplicate proofs for {card_id}/{attempt_id}")
    return found[0] if found else None


def verify_review_acceptance_migration(
    *, project_root: Path | str, project_repository: str, workstream_id: str,
    card: Mapping[str, Any], attempt_ref: Mapping[str, Any],
    attempt: Mapping[str, Any], proof: Mapping[str, Any],
    label: str = "review acceptance migration",
) -> str:
    root = Path(project_root).resolve()
    card_id = card.get("id")
    attempt_id = attempt.get("attempt")
    if not isinstance(card_id, str) or not card_id:
        raise _fail(label, "selected Card has no identity")
    if not isinstance(attempt_id, str) or not attempt_id:
        raise _fail(label, "selected Review attempt has no identity")
    p = validate_review_acceptance_migration_shape(
        proof, workstream_id=workstream_id, card_id=card_id, label=label
    )
    if p["attempt_id"] != attempt_id:
        raise _fail(label, "attempt_id does not match selected Review attempt")
    if p["source_repository"] != project_repository:
        raise _fail(label, "source_repository does not match selected project", "repository")
    if card.get("status") != "done":
        raise _fail(label, "migration is valid only for an already DONE historical Card")
    if attempt.get("verdict") != "green" or not isinstance(attempt.get("review_kind"), str):
        raise _fail(label, "source Review must be terminal explicit GREEN history")
    acceptance = attempt.get("acceptance")
    if not isinstance(acceptance, Mapping):
        raise _fail(label, "source Review has no Task Card acceptance")
    if acceptance.get("class") != "task_card" or acceptance.get("path") != p["acceptance_path"]:
        raise _fail(label, "source Review acceptance does not name the proved Task Card")
    if "commit" in acceptance or "blob" in acceptance:
        raise _fail(label, "only wholly path-only acceptance may use migration proof")
    for field, expected in (
        ("path", p["source_path"]), ("commit", p["source_commit"]), ("blob", p["source_blob"])
    ):
        if attempt_ref.get(field) != expected:
            raise _fail(label, f"source_{field} does not match selected exact Review locator")
    try:
        verified_review = verify_exact_git_locator(
            project_root=root, repository=p["source_repository"],
            expected_repository=project_repository, commit=p["source_commit"],
            path=p["source_path"], blob=p["source_blob"], label=f"{label}.source_review",
        )
        review_bytes = verify_worktree_freshness(
            project_root=root, path=p["source_path"], blob=p["source_blob"],
            label=f"{label}.current_review",
        )
        source_bytes = read_git_blob_bytes(
            project_root=root, blob=p["source_blob"], label=f"{label}.source_review"
        )
        accepted_blob = resolve_blob_at_commit(
            project_root=root, commit=p["source_commit"], path=p["acceptance_path"],
            label=f"{label}.source_acceptance",
        )
        verify_worktree_freshness(
            project_root=root, path=p["acceptance_path"], blob=p["acceptance_blob"],
            label=f"{label}.current_acceptance",
        )
    except ExactLocatorError as exc:
        raise _fail(label, str(exc), exc.kind) from exc
    _require_ancestry(root, p["source_commit"], label)
    if source_bytes != review_bytes:
        raise _fail(label, "current Review bytes differ from immutable source", "stale")
    if accepted_blob != p["acceptance_blob"]:
        raise _fail(label, "proved acceptance_blob does not match Task Card at source Review commit", "stale")
    try:
        source_attempt = tomllib.loads(source_bytes.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise _fail(label, f"source Review is invalid TOML: {exc}", "mismatch") from exc
    if (
        source_attempt.get("workstream_id") != workstream_id
        or source_attempt.get("card_id") != card_id
        or source_attempt.get("attempt") != attempt_id
        or source_attempt.get("verdict") != "green"
        or source_attempt.get("review_kind") != attempt.get("review_kind")
    ):
        raise _fail(label, "immutable source Review identity/status does not match selected attempt", "mismatch")
    source_acceptance = source_attempt.get("acceptance")
    if not isinstance(source_acceptance, Mapping):
        raise _fail(label, "immutable source Review lacks acceptance", "mismatch")
    if (
        source_acceptance.get("class") != "task_card"
        or source_acceptance.get("path") != p["acceptance_path"]
        or "commit" in source_acceptance
        or "blob" in source_acceptance
    ):
        raise _fail(label, "immutable source Review is not the proved path-only acceptance", "mismatch")
    return f"project-git:{verified_review.key}|acceptance:{p['source_commit']}:{p['acceptance_path']}@{p['acceptance_blob']}"
