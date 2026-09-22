#!/usr/bin/env python3
"""Trigger-only downstream fork release lineage helpers for Project Workflow V2."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable


class ForkReleaseContractError(ValueError):
    pass


UPSTREAM_RE = re.compile(r"^v(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)$")
PRIVATE_RE = re.compile(
    r"^v(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)-private\\.([1-9]\\d*)$"
)
FORK_RELEASE_OPERATION = "downstream_fork_release"
FORK_RELEASE_MODULE = "workflow/FORK_RELEASE_VERSIONING.md"


@dataclass(frozen=True)
class UpstreamLineage:
    repository: str
    tag: str
    commit: str

    def __post_init__(self) -> None:
        if not self.repository.strip() or not self.commit.strip():
            raise ForkReleaseContractError("upstream repository/tag/SHA lineage must be complete")
        if parse_upstream_tag(self.tag) is None:
            raise ForkReleaseContractError("accepted upstream tag must be exact vX.Y.Z")


def parse_upstream_tag(tag: str) -> tuple[int, int, int] | None:
    match = UPSTREAM_RE.fullmatch(tag)
    if match is None:
        return None
    return tuple(int(value) for value in match.groups())


def parse_private_tag(tag: str) -> tuple[int, int, int, int] | None:
    match = PRIVATE_RE.fullmatch(tag)
    if match is None:
        return None
    return tuple(int(value) for value in match.groups())


def module_for_operation(
    operation_kind: str | None,
    *,
    lineage: UpstreamLineage | None = None,
) -> str | None:
    """Return the optional module only for the exact durable fork-release trigger."""

    if operation_kind != FORK_RELEASE_OPERATION:
        return None
    if lineage is None:
        raise ForkReleaseContractError(
            "declared downstream fork release requires accepted upstream repo/tag/SHA"
        )
    return FORK_RELEASE_MODULE


def next_private_tag(lineage: UpstreamLineage, existing_tags: Iterable[str]) -> str:
    baseline = parse_upstream_tag(lineage.tag)
    assert baseline is not None
    revisions = []
    for tag in existing_tags:
        parsed = parse_private_tag(tag)
        if parsed is not None and parsed[:3] == baseline:
            revisions.append(parsed[3])
    return f"{lineage.tag}-private.{max(revisions, default=0) + 1}"


def canonical_order_key(tag: str) -> tuple[int, int, int, int]:
    parsed = parse_private_tag(tag)
    if parsed is None:
        raise ForkReleaseContractError(f"not a canonical private release tag: {tag!r}")
    return parsed


def select_latest_canonical(tags: Iterable[str]) -> str:
    canonical = [(canonical_order_key(tag), tag) for tag in tags if parse_private_tag(tag)]
    if not canonical:
        raise ForkReleaseContractError("no canonical private releases available")
    return max(canonical)[1]


def verify_history_immutable(before: Iterable[str], after: Iterable[str]) -> str:
    missing = set(before) - set(after)
    if missing:
        raise ForkReleaseContractError(
            "published release history is immutable; missing: " + ", ".join(sorted(missing))
        )
    return "history_immutable"


def validate_latest_alias(
    *,
    alias_kind: str | None,
    canonical_artifact_identity: str,
    alias_artifact_identity: str | None = None,
) -> str:
    if not canonical_artifact_identity.strip():
        raise ForkReleaseContractError("canonical artifact identity must be non-empty")

    if alias_kind is None:
        if alias_artifact_identity not in {None, ""}:
            raise ForkReleaseContractError("alias identity supplied without an alias")
        return "no_latest_alias"

    if alias_kind == "vlatest":
        raise ForkReleaseContractError("synthetic vlatest tag/version is forbidden")
    if alias_kind != "native_latest":
        raise ForkReleaseContractError(f"unsupported latest alias kind: {alias_kind!r}")
    if alias_artifact_identity != canonical_artifact_identity:
        raise ForkReleaseContractError(
            "native latest alias must point to the exact accepted canonical artifact"
        )
    return "native_latest_same_artifact"
