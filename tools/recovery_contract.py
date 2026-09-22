#!/usr/bin/env python3
"""Runtime-neutral M03 recovery/corrective classification."""

from __future__ import annotations


class RecoveryContractError(ValueError):
    pass


RESOLUTION_ROUTES = {
    "bounded_correction": ("execution", False),
    "plan_strategy": ("planning", False),
    "definition_authority": ("definition", False),
    "missing_evidence": ("research", False),
    "human_authority": ("user_stop", True),
    "runtime_access_input": ("blocker_stop", True),
}


def classify_resolution(kind: str) -> tuple[str, bool]:
    if kind not in RESOLUTION_ROUTES:
        raise RecoveryContractError(f"unknown resolution class {kind!r}")
    return RESOLUTION_ROUTES[kind]


def exact_result_subject(repository: str, result_ref: dict) -> str:
    for key in ("path", "commit", "blob"):
        if not isinstance(result_ref.get(key), str) or not result_ref[key]:
            raise RecoveryContractError(f"result ref missing exact {key}")
    return f"{repository}@{result_ref['commit']}:{result_ref['path']}@{result_ref['blob']}"


def review_subject(review: dict) -> str:
    subject = review.get("subject")
    if not isinstance(subject, dict):
        raise RecoveryContractError("review subject missing")
    try:
        return f"{subject['repository']}@{subject['commit']}:{subject['path']}@{subject['blob']}"
    except KeyError as exc:
        raise RecoveryContractError("review subject incomplete") from exc
