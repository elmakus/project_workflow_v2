#!/usr/bin/env python3
"""Explicit compatibility proof for immutable legacy Card Results."""

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
    from tools.execution_contract import ExecutionContractError, parse_card_result
except ModuleNotFoundError:  # direct script execution from tools/
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from tools.exact_locator import (
        ExactLocatorError,
        normalize_locator_path,
        read_git_blob_bytes,
        resolve_blob_at_commit,
        verify_exact_git_locator,
        verify_worktree_freshness,
    )
    from tools.execution_contract import ExecutionContractError, parse_card_result

SHA40 = re.compile(r"^[0-9a-f]{40}$")
PROOF_KEYS = frozenset({
    "card_id", "source_repository", "source_commit", "source_path",
    "source_blob", "source_workstream", "source_card",
})


class LegacyResultProvenanceError(ValueError):
    def __init__(self, message: str, *, kind: str = "invalid") -> None:
        super().__init__(message)
        self.kind = kind


def _fail(label: str, detail: str, kind: str = "invalid") -> LegacyResultProvenanceError:
    return LegacyResultProvenanceError(f"{label}: {detail}", kind=kind)


def validate_legacy_result_migration_shape(
    raw: Any, *, workstream_id: str, card_id: str | None = None,
    label: str = "legacy result migration",
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
        raise _fail(label, "card_id does not match the selected Card")
    if out["source_card"] != out["card_id"]:
        raise _fail(label, "source_card does not match card_id")
    if out["source_workstream"] != workstream_id:
        raise _fail(label, "source_workstream does not match selected workstream")
    if SHA40.fullmatch(out["source_commit"]) is None or SHA40.fullmatch(out["source_blob"]) is None:
        raise _fail(label, "source_commit and source_blob must be exact 40-hex Git identities")
    try:
        path = normalize_locator_path(out["source_path"], f"{label}.source_path")
    except ExactLocatorError as exc:
        raise _fail(label, str(exc), exc.kind) from exc
    prefix = f"implementation/workstreams/{workstream_id}/results/"
    if not path.startswith(prefix) or not path.endswith(".md"):
        raise _fail(label, "source_path is outside the selected workstream results directory")
    return out


def migration_for_card(board: Mapping[str, Any], card_id: str) -> Mapping[str, Any] | None:
    records = board.get("legacy_result_migrations", []) or []
    found = [r for r in records if isinstance(r, Mapping) and r.get("card_id") == card_id]
    if len(found) > 1:
        raise _fail("legacy result migration", f"duplicate proofs for Card {card_id!r}")
    return found[0] if found else None


def _git_show(project_root: Path, spec: str, label: str) -> bytes:
    try:
        proc = subprocess.run(
            ["git", "-C", str(project_root), "show", spec],
            capture_output=True, check=False, timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise _fail(label, f"Git readback failed: {exc}", "git_unavailable") from exc
    if proc.returncode != 0:
        raise _fail(label, f"Git subject {spec!r} does not resolve", "dangling")
    return bytes(proc.stdout)


def _require_ancestry(project_root: Path, commit: str, label: str) -> None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(project_root), "merge-base", "--is-ancestor", commit, "HEAD"],
            capture_output=True, check=False, timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise _fail(label, f"HEAD ancestry check failed: {exc}", "git_unavailable") from exc
    if proc.returncode != 0:
        raise _fail(label, f"source commit {commit} is not in selected HEAD ancestry", "stale")


def _require_prior_durability(project_root: Path, commit: str, path: str, blob: str, label: str) -> None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(project_root), "rev-parse", "--verify", f"{commit}^"],
            capture_output=True, text=True, check=False, timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise _fail(label, f"source history readback failed: {exc}", "git_unavailable") from exc
    if proc.returncode != 0 or SHA40.fullmatch(proc.stdout.strip()) is None:
        raise _fail(label, "source commit lacks usable parent history", "ambiguous")
    try:
        parent_blob = resolve_blob_at_commit(
            project_root=project_root, commit=proc.stdout.strip(), path=path,
            label=f"{label}.source_parent",
        )
    except ExactLocatorError as exc:
        raise _fail(label, "source Result was not durable before the migration snapshot", "ambiguous") from exc
    if parent_blob != blob:
        raise _fail(label, "source Result bytes changed in the migration snapshot", "ambiguous")


def _normalise_legacy_evidence(parsed: Mapping[str, Any], workstream_id: str, label: str) -> list[str]:
    items: list[str] = []
    for raw in parsed.get("evidence_refs", []):
        for part in str(raw).split(";"):
            value = part.strip()
            if not value:
                continue
            path = normalize_locator_path(value, f"{label}.evidence")
            prefix = f"implementation/workstreams/{workstream_id}/evidence/"
            if not path.startswith(prefix) or not path.endswith(".md"):
                raise _fail(label, f"legacy evidence ref {path!r} is outside workstream evidence")
            items.append(path)
    if not items:
        raise _fail(label, "legacy Result has no evidence refs")
    return items


def verify_legacy_result_migration(
    *, project_root: Path | str, project_repository: str, workstream_id: str,
    card: Mapping[str, Any], proof: Mapping[str, Any],
    label: str = "legacy result migration",
) -> tuple[dict[str, Any], list[str]]:
    root = Path(project_root).resolve()
    card_id = card.get("id")
    if not isinstance(card_id, str) or not card_id:
        raise _fail(label, "selected Card has no identity")
    p = validate_legacy_result_migration_shape(
        proof, workstream_id=workstream_id, card_id=card_id, label=label
    )
    if p["source_repository"] != project_repository:
        raise _fail(label, "source_repository does not match selected project", "repository")
    result_ref = card.get("result")
    if not isinstance(result_ref, Mapping):
        raise _fail(label, "selected Card has no Result locator")
    if result_ref.get("class") != "result" or result_ref.get("path") != p["source_path"]:
        raise _fail(label, "current Result path does not match proved legacy source")
    current_commit, current_blob = result_ref.get("commit"), result_ref.get("blob")
    if not isinstance(current_commit, str) or not isinstance(current_blob, str):
        raise _fail(label, "current Result must have exact commit+blob identity")
    try:
        current = verify_exact_git_locator(
            project_root=root, repository=project_repository,
            expected_repository=project_repository, commit=current_commit,
            path=result_ref["path"], blob=current_blob, label=f"{label}.current_result",
        )
        verify_worktree_freshness(
            project_root=root, path=result_ref["path"], blob=current_blob,
            label=f"{label}.current_result",
        )
        source = verify_exact_git_locator(
            project_root=root, repository=p["source_repository"],
            expected_repository=project_repository, commit=p["source_commit"],
            path=p["source_path"], blob=p["source_blob"], label=f"{label}.source_result",
        )
        source_bytes = read_git_blob_bytes(
            project_root=root, blob=p["source_blob"], label=f"{label}.source_result"
        )
    except ExactLocatorError as exc:
        raise _fail(label, str(exc), exc.kind) from exc
    _require_ancestry(root, p["source_commit"], label)
    if current_blob != p["source_blob"]:
        raise _fail(label, "current Result blob differs from immutable legacy source", "stale")
    current_bytes = (root / result_ref["path"]).read_bytes()
    if current_bytes != source_bytes:
        raise _fail(label, "current Result bytes differ from immutable legacy source", "stale")
    try:
        parsed = parse_card_result(source_bytes.decode("utf-8"), card_id, workstream_id)
    except (UnicodeDecodeError, ExecutionContractError) as exc:
        raise _fail(label, f"legacy source Result is invalid: {exc}", "mismatch") from exc
    if parsed.get("result_status") is not None:
        raise _fail(label, "source Result is not statusless legacy serialization", "mismatch")
    if str(parsed.get("tests_summary", "")).strip().upper().startswith("FAILED:"):
        raise _fail(label, "legacy Result carries normative FAILED summary", "mismatch")
    board_path = f"implementation/workstreams/{workstream_id}/TASK_BOARD.toml"
    try:
        source_board = tomllib.loads(_git_show(root, f"{p['source_commit']}:{board_path}", label).decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise _fail(label, f"source Board is invalid: {exc}", "mismatch") from exc
    source_card = next(
        (x for x in source_board.get("cards", []) if isinstance(x, Mapping) and x.get("id") == card_id),
        None,
    )
    if source_card is None or source_card.get("status") != "done":
        raise _fail(label, "source Board does not prove the Card already DONE", "ambiguous")
    source_ref = source_card.get("result")
    if not isinstance(source_ref, Mapping) or source_ref.get("path") != p["source_path"]:
        raise _fail(label, "source Board does not list the proved Result path", "ambiguous")
    source_result_commit = source_ref.get("commit")
    if (
        source_ref.get("blob") != p["source_blob"]
        or not isinstance(source_result_commit, str)
        or SHA40.fullmatch(source_result_commit) is None
    ):
        raise _fail(label, "source Board does not carry exact matching Result identity", "ambiguous")
    try:
        verify_exact_git_locator(
            project_root=root,
            repository=p["source_repository"],
            expected_repository=project_repository,
            commit=source_result_commit,
            path=p["source_path"],
            blob=p["source_blob"],
            label=f"{label}.source_board_result",
        )
    except ExactLocatorError as exc:
        raise _fail(label, f"source Board Result identity failed: {exc}", exc.kind) from exc
    try:
        ancestry = subprocess.run(
            [
                "git", "-C", str(root), "merge-base", "--is-ancestor",
                source_result_commit, p["source_commit"],
            ],
            capture_output=True, check=False, timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise _fail(
            label,
            f"source Board Result ancestry check failed: {exc}",
            "git_unavailable",
        ) from exc
    if ancestry.returncode != 0:
        raise _fail(
            label,
            "source Board Result commit is not an ancestor of the source Board snapshot",
            "stale",
        )
    _require_prior_durability(root, p["source_commit"], p["source_path"], p["source_blob"], label)
    adapted = dict(parsed)
    adapted["evidence_refs"] = _normalise_legacy_evidence(parsed, workstream_id, label)
    reads = [f"project-git:{source.key}", f"project-git:{current.key}"]
    return adapted, reads


def derive_path_only_review_acceptance(
    *, project_root: Path | str, project_repository: str,
    attempt_ref: Mapping[str, Any], acceptance: Mapping[str, Any],
    current_card_path: str, label: str = "legacy review acceptance",
) -> str:
    """Derive exact Card acceptance only inside a proved legacy-Result path."""
    if acceptance.get("class") != "task_card" or acceptance.get("path") != current_card_path:
        raise _fail(label, "path-only acceptance does not name the selected Task Card")
    if "commit" in acceptance or "blob" in acceptance:
        raise _fail(label, "partially exact acceptance cannot use legacy derivation")
    commit = attempt_ref.get("commit")
    if not isinstance(commit, str) or SHA40.fullmatch(commit) is None:
        raise _fail(label, "review attempt lacks exact commit identity")
    _require_ancestry(Path(project_root).resolve(), commit, label)
    try:
        blob = resolve_blob_at_commit(
            project_root=Path(project_root).resolve(), commit=commit,
            path=current_card_path, label=label,
        )
        verify_worktree_freshness(
            project_root=Path(project_root).resolve(), path=current_card_path,
            blob=blob, label=label,
        )
    except ExactLocatorError as exc:
        raise _fail(label, str(exc), exc.kind) from exc
    return f"project-git:{project_repository}@{commit}:{current_card_path}@{blob}"