#!/usr/bin/env python3
"""RF009 exact Research-provenance bindings (H014/H016).

A complete Research record routes to its declared return target only when
the exact origin-to-return binding is proved from a real owning subject:
the declared return target must be the owning boundary of the verified
origin, and the origin subject must equal that owner's exact current
subject. Mismatched or nonexistent origins fail closed to Recovery; a
declared target alone is never proof.

Intake prior-art bindings prove exact consumed-Research result provenance
through an RF007 exact locator to the immutable consumed ``RESEARCH.toml``
Git blob. The binding's subject/result must equal the blob's
origin_subject/return_result exactly, and the blob must be a consumed
intake-origin record with applied reconciliation. Forged bindings, missing
Research and mismatched results cannot present stable issue alignment.
No worktree-freshness check applies to the proof blob: the single live
Research slot may legitimately be reused after Intake persists its durable
binding, and the immutable blob remains the proof.

Helperless derivation: ``git rev-parse <commit>:<path>`` plus ``git cat-file``
for blob identity/content, string comparison for the binding.
"""

from __future__ import annotations

import re
import tomllib
from collections.abc import Callable
from pathlib import Path
from typing import Any

try:
    from tools.exact_locator import (
        ExactLocatorError,
        normalize_locator_path,
        read_git_blob_bytes,
        verify_exact_git_locator,
    )
except ModuleNotFoundError:  # direct script execution from tools/
    from exact_locator import (
        ExactLocatorError,
        normalize_locator_path,
        read_git_blob_bytes,
        verify_exact_git_locator,
    )

SHA40 = re.compile(r"^[0-9a-f]{40}$")
WORKSTREAM_ORIGIN_ROLES = ("intake", "brainstorming", "definition")
EXECUTION_ORIGIN_ROLES = ("execution_prep", "execution", "execution_resolution")
PROOF_KEYS = {"class", "repository", "commit", "path", "blob"}
BINDING_LABEL = "research origin/return binding"
PROOF_LABEL = "intake diagnosis prior-art proof"


class ResearchProvenanceError(ValueError):
    """An exact Research-provenance binding could not be proved.

    ``kind`` names the failure class: ``shape``, ``mismatch``,
    ``stale``, ``missing`` or an RF007 locator kind (``repository``,
    ``identity``, ``dangling``, ``blob_mismatch``, ``not_blob``,
    ``git_unavailable``, ``unsafe_path``, ``escape``).
    """

    def __init__(self, message: str, *, kind: str) -> None:
        super().__init__(message)
        self.kind = kind


def _fail(label: str, detail: str, kind: str) -> ResearchProvenanceError:
    return ResearchProvenanceError(f"{label}: {detail}", kind=kind)


def validate_prior_art_proof_shape(
    ref: Any,
    workstream_id: str,
    *,
    label: str = PROOF_LABEL,
) -> dict[str, str]:
    """Validate the Intake proof locator shape, returning its canonical form.

    The proof binds the exact workstream-local ``RESEARCH.toml`` path plus
    the immutable ``(repository, commit, blob)`` identity of the consumed
    record. Git existence/identity is proved by the serving boundary through
    the shared RF007 resolver, never here.
    """
    if not isinstance(ref, dict):
        raise _fail(label, "proof locator must be a table", "shape")
    missing = sorted(PROOF_KEYS - set(ref))
    extra = sorted(set(ref) - PROOF_KEYS)
    if missing:
        raise _fail(label, f"missing field(s): {', '.join(missing)}", "shape")
    if extra:
        raise _fail(label, f"unknown field(s): {', '.join(extra)}", "shape")
    if ref.get("class") != "research":
        raise _fail(label, "proof class must be 'research'", "shape")
    repository = ref.get("repository")
    if not isinstance(repository, str) or not repository.strip():
        raise _fail(label, "proof repository must be a non-empty string", "shape")
    commit = ref.get("commit")
    if not isinstance(commit, str) or SHA40.fullmatch(commit) is None:
        raise _fail(label, "proof commit must be exact 40-hex Git identity", "shape")
    blob = ref.get("blob")
    if not isinstance(blob, str) or SHA40.fullmatch(blob) is None:
        raise _fail(label, "proof blob must be exact 40-hex Git identity", "shape")
    try:
        path = normalize_locator_path(ref.get("path"), f"{label}.path")
    except ExactLocatorError as exc:
        raise _fail(label, f"proof path is unsafe: {exc}", "shape") from exc
    expected = f"implementation/workstreams/{workstream_id}/RESEARCH.toml"
    if path != expected:
        raise _fail(
            label,
            f"proof must bind the exact workstream RESEARCH.toml path {expected!r}",
            "shape",
        )
    return {
        "class": "research",
        "repository": repository,
        "commit": commit,
        "path": path,
        "blob": blob,
    }


def expected_origin_subject(
    *,
    origin_role: str,
    owner: dict[str, Any],
    label: str = BINDING_LABEL,
) -> str:
    """Derive the exact current subject of the Research origin owner."""
    if origin_role == "intake":
        if owner.get("kind") != "issue":
            raise _fail(
                label, "intake-origin Research requires an issue Intake owner", "mismatch"
            )
        repair = owner.get("repair_subject")
        if not isinstance(repair, str) or not repair:
            raise _fail(
                label,
                "intake-origin Research requires an exact current repair subject",
                "missing",
            )
        return repair
    if origin_role == "brainstorming":
        scope_id = owner.get("scope_id")
        revision = owner.get("revision")
        if (
            not isinstance(scope_id, str)
            or not scope_id
            or not isinstance(revision, int)
            or isinstance(revision, bool)
        ):
            raise _fail(
                label, "brainstorming owner has no exact scope subject", "missing"
            )
        return f"{scope_id}@{revision}"
    if origin_role == "definition":
        revision = owner.get("revision")
        if not isinstance(revision, str) or not revision:
            raise _fail(
                label, "definition owner has no exact revision subject", "missing"
            )
        return revision
    raise _fail(label, f"unknown origin_role {origin_role!r}", "mismatch")


def verify_complete_workstream_return(
    *,
    research: dict[str, Any],
    workstream: dict[str, Any],
    read_owner: Callable[[str], dict[str, Any] | None],
    label: str = BINDING_LABEL,
) -> str:
    """Return the verified return obligation for complete workstream Research.

    ``read_owner`` returns the owning record for an origin role after that
    owner passes its owning validator, or None when the workstream binds no
    such owner. The declared return target must be the owning boundary of
    the verified origin, and the origin subject must equal that owner's
    exact current subject.
    """
    origin_role = research.get("origin_role")
    if origin_role not in WORKSTREAM_ORIGIN_ROLES:
        raise _fail(
            label,
            f"origin_role {origin_role!r} is not workstream-owned; "
            "execution Research is Board-owned",
            "mismatch",
        )
    return_target = research.get("return_target")
    if return_target != origin_role:
        raise _fail(
            label,
            f"return_target {return_target!r} does not match "
            f"origin_role {origin_role!r}; Research never selects a different target",
            "mismatch",
        )
    owner = read_owner(origin_role)
    if owner is None:
        raise _fail(
            label,
            f"origin_role {origin_role!r} names no owning record in this workstream",
            "missing",
        )
    expected = expected_origin_subject(
        origin_role=origin_role, owner=owner, label=label
    )
    if research.get("origin_subject") != expected:
        raise _fail(
            label,
            f"origin_subject {research.get('origin_subject')!r} does not match "
            f"the exact current {origin_role} subject {expected!r}",
            "stale",
        )
    return origin_role


def verify_complete_board_return(
    *,
    research: dict[str, Any],
    board: dict[str, Any],
    label: str = BINDING_LABEL,
) -> str:
    """Return the verified execution obligation for complete Board Research.

    The declared return target must be exactly ``<origin_role>:<origin>``
    and the origin subject must name an exact current Task Board Card.
    """
    origin_role = research.get("origin_role")
    if origin_role not in EXECUTION_ORIGIN_ROLES:
        raise _fail(
            label,
            "Task Board Research pointer must own implementation/recovery Research",
            "mismatch",
        )
    origin_subject = research.get("origin_subject")
    expected = f"{origin_role}:{origin_subject}"
    if research.get("return_target") != expected:
        raise _fail(
            label,
            f"return_target {research.get('return_target')!r} does not match "
            f"the exact origin binding {expected!r}",
            "mismatch",
        )
    cards = board.get("cards", [])
    card_ids = {
        card.get("id") for card in cards if isinstance(card, dict)
    }
    if origin_subject not in card_ids:
        raise _fail(
            label,
            f"origin_subject {origin_subject!r} names no exact current Task Board Card",
            "missing",
        )
    obligations = {
        "execution_resolution": "execution_resolution",
        "execution_prep": "execution_prep",
        "execution": "execution",
    }
    return obligations[origin_role]


def verify_consumed_prior_art_proof(
    *,
    project_root: Path,
    project_repository: str,
    workstream_id: str,
    intake: dict[str, Any],
    label: str = PROOF_LABEL,
) -> tuple[dict[str, Any], str]:
    """Prove the Intake binding against the exact consumed-Research Git blob.

    Returns the parsed consumed record plus the progressive-disclosure read
    record. The caller runs full shape validation on the parsed record; this
    verifier establishes locator proof plus exact field binding only.
    """
    proof = intake.get("diagnosis_prior_art_proof")
    if not isinstance(proof, dict):
        raise _fail(
            label,
            "a persisted prior-art binding requires its exact consumed-Research "
            "proof locator",
            "missing",
        )
    locator = validate_prior_art_proof_shape(
        proof, workstream_id, label=label
    )
    if locator["repository"] != project_repository:
        raise _fail(
            label,
            f"repository {locator['repository']!r} does not match "
            f"the selected project {project_repository!r}",
            "repository",
        )
    try:
        verified = verify_exact_git_locator(
            project_root=project_root,
            repository=locator["repository"],
            expected_repository=project_repository,
            commit=locator["commit"],
            path=locator["path"],
            blob=locator["blob"],
            label=label,
        )
        content = read_git_blob_bytes(
            project_root=project_root, blob=locator["blob"], label=label
        )
    except ExactLocatorError as exc:
        raise ResearchProvenanceError(str(exc), kind=exc.kind) from exc
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _fail(
            label, f"consumed Research blob is not UTF-8 text: {exc}", "mismatch"
        ) from exc
    try:
        parsed = tomllib.loads(text)
    except (tomllib.TOMLDecodeError, ValueError) as exc:
        raise _fail(
            label, f"consumed Research blob TOML is malformed: {exc}", "mismatch"
        ) from exc
    if not isinstance(parsed, dict):
        raise _fail(label, "consumed Research blob must be a TOML table", "mismatch")
    if parsed.get("workstream_id") != workstream_id:
        raise _fail(
            label, "consumed Research proof belongs to another workstream", "mismatch"
        )
    if parsed.get("state") != "consumed":
        raise _fail(
            label, "proof must bind a consumed Research record", "mismatch"
        )
    if parsed.get("origin_role") != "intake" or parsed.get("return_target") != "intake":
        raise _fail(
            label, "proof must bind intake-origin Research returned to Intake", "mismatch"
        )
    repair_subject = intake.get("repair_subject")
    if parsed.get("origin_subject") != repair_subject:
        raise _fail(
            label,
            f"proof origin_subject {parsed.get('origin_subject')!r} does not match "
            f"the exact current repair subject {repair_subject!r}",
            "mismatch",
        )
    if parsed.get("return_reconciliation") != "applied":
        raise _fail(
            label, "proof must bind an applied Research return", "mismatch"
        )
    bound_result = intake.get("diagnosis_prior_art_result")
    if parsed.get("return_result") != bound_result:
        raise _fail(
            label,
            "proof return_result does not match the exact persisted prior-art binding",
            "mismatch",
        )
    return parsed, f"project-git:{verified.key}"
