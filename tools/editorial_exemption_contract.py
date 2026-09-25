#!/usr/bin/env python3
"""RF008 durable proof contract for Planning editorial-review exemptions.

The exemption is intentionally narrower than ordinary Plan Review.  It may
reuse a prior GREEN-reviewed plan only when an immutable classification record
binds the exact old/new plan subjects, records the inspected semantic diff,
and was produced by a context independent of the changed subject.

This module validates the semantic record and its exact locator shape.  Exact
Git object readback is performed by the router at the serving boundary; a
future generalized locator resolver remains outside RF008.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import PurePosixPath
from typing import Any

SHA40 = re.compile(r"^[0-9a-f]{40}$")
UNCHANGED_DIMENSIONS = (
    "strategy",
    "milestone_topology",
    "requirement_coverage",
    "gates",
    "acceptance_semantics",
)
PLACEHOLDER_EVIDENCE = frozenset({"n/a", "na", "none", "tbd", "todo"})


class EditorialExemptionError(ValueError):
    """Raised when an editorial-exemption proof is missing or inconsistent."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise EditorialExemptionError(message)


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    _require(not missing, f"{label}: missing field(s): {', '.join(missing)}")
    _require(not extra, f"{label}: unknown field(s): {', '.join(extra)}")


def _safe_relative_path(raw: Any, label: str) -> str:
    _require(isinstance(raw, str) and raw.strip(), f"{label}: path must be non-empty string")
    path = PurePosixPath(raw)
    _require(not path.is_absolute(), f"{label}: absolute paths are forbidden")
    _require("." not in path.parts and ".." not in path.parts, f"{label}: path traversal is forbidden")
    return raw


def git_blob_subject_key(
    subject: Any,
    label: str,
    *,
    planning_subject: bool = False,
) -> str:
    _require(isinstance(subject, Mapping), f"{label}: subject must be a table")
    if planning_subject:
        _exact_keys(subject, {"repository", "commit", "path", "blob"}, label)
    else:
        _exact_keys(subject, {"class", "repository", "commit", "path", "blob"}, label)
        _require(subject.get("class") == "git_blob", f"{label}: class must be 'git_blob'")
    repository = subject.get("repository")
    commit = subject.get("commit")
    path = subject.get("path")
    blob = subject.get("blob")
    _require(isinstance(repository, str) and repository.strip(), f"{label}: repository is required")
    _require(isinstance(commit, str) and SHA40.fullmatch(commit) is not None,
             f"{label}: commit must be exact 40-hex")
    _safe_relative_path(path, f"{label}.path")
    _require(isinstance(blob, str) and SHA40.fullmatch(blob) is not None,
             f"{label}: blob must be exact 40-hex")
    return f"{repository}@{commit}:{path}@{blob}"


def validate_editorial_classification_locator(
    ref: Any,
    workstream_id: str,
) -> dict[str, str]:
    """Validate the immutable locator recorded by PLANNING.toml.

    This is deliberately RF008-local.  It does not attempt to provide the
    generalized locator/readback abstraction owned by RF007.
    """
    _require(isinstance(ref, Mapping), "planning.review_exemption_classification: locator must be a table")
    _exact_keys(ref, {"class", "repository", "commit", "path", "blob"},
                "planning.review_exemption_classification")
    key = git_blob_subject_key(ref, "planning.review_exemption_classification")
    path = str(ref["path"])
    prefix = f"implementation/workstreams/{workstream_id}/planning_classifications/"
    _require(path.startswith(prefix) and path.endswith(".toml"),
             "planning.review_exemption_classification: proof must be a workstream-local planning_classifications TOML")
    return {
        "class": "git_blob",
        "repository": str(ref["repository"]),
        "commit": str(ref["commit"]),
        "path": path,
        "blob": str(ref["blob"]),
        "key": key,
    }


def validate_editorial_exemption_classification(
    data: Any,
    *,
    workstream_id: str,
    planning: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate one independently produced immutable RF008 classification."""
    _require(isinstance(data, Mapping), "editorial classification: top-level value must be a table")
    _exact_keys(
        data,
        {
            "workstream_id",
            "planning_cycle",
            "plan_revision",
            "verdict",
            "classification",
            "inspected_diff_evidence",
            "base_subject",
            "changed_subject",
            "unchanged",
            "independence",
        },
        "editorial classification",
    )
    _require(data.get("workstream_id") == workstream_id,
             "editorial classification: wrong workstream_id")
    _require(data.get("planning_cycle") == planning.get("cycle"),
             "editorial classification: wrong planning_cycle")
    _require(data.get("plan_revision") == planning.get("revision"),
             "editorial classification: wrong plan_revision")
    _require(data.get("verdict") == "green",
             "editorial classification: exemption requires exact GREEN classification")
    _require(data.get("classification") == "editorial_only",
             "editorial classification: exemption requires classification='editorial_only'")

    evidence = data.get("inspected_diff_evidence")
    _require(isinstance(evidence, str) and evidence.strip(),
             "editorial classification: inspected_diff_evidence must be non-empty")
    _require(evidence.strip().lower() not in PLACEHOLDER_EVIDENCE,
             "editorial classification: inspected_diff_evidence cannot be a placeholder")

    base_key = git_blob_subject_key(data.get("base_subject"), "editorial classification.base_subject")
    changed_key = git_blob_subject_key(data.get("changed_subject"), "editorial classification.changed_subject")
    expected_base = planning.get("review_exemption_base_subject")
    expected_changed = git_blob_subject_key(
        planning.get("subject"),
        "planning.subject",
        planning_subject=True,
    )
    _require(base_key == expected_base,
             "editorial classification: base subject does not match prior GREEN-reviewed exemption base")
    _require(changed_key == expected_changed,
             "editorial classification: changed subject does not match current planning subject")
    _require(base_key != changed_key,
             "editorial classification: old and changed subjects must differ")

    unchanged = data.get("unchanged")
    _require(isinstance(unchanged, Mapping), "editorial classification.unchanged: table is required")
    _exact_keys(unchanged, set(UNCHANGED_DIMENSIONS), "editorial classification.unchanged")
    for dimension in UNCHANGED_DIMENSIONS:
        _require(unchanged.get(dimension) is True,
                 f"editorial classification: {dimension} must be explicitly unchanged")

    independence = data.get("independence")
    _require(isinstance(independence, Mapping), "editorial classification.independence: table is required")
    _exact_keys(
        independence,
        {"materially_produced_or_repaired_changed_subject", "basis"},
        "editorial classification.independence",
    )
    _require(independence.get("materially_produced_or_repaired_changed_subject") is False,
             "editorial classification: classifier is not independent of the changed subject")
    basis = independence.get("basis")
    _require(isinstance(basis, str) and basis.strip(),
             "editorial classification: independence basis must be durable and non-empty")

    return {
        "verdict": "green",
        "classification": "editorial_only",
        "base_subject": base_key,
        "changed_subject": changed_key,
        "inspected_diff_evidence": evidence,
        "unchanged": {dimension: True for dimension in UNCHANGED_DIMENSIONS},
        "independence_basis": basis,
    }
