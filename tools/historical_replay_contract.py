#!/usr/bin/env python3
"""Exact-source immutable M02 regression replay corpus (BOOT-C, REQ-125/126).

Correctly terminal historical M02 state must never be reopened or rewritten
merely because later workflow rules improve (REQ-125), while material M02
failure classes are replayed as immutable regression fixtures against the
corrected semantics (REQ-126).

This module is the single provenance-owned corpus. Every entry binds the real
terminal M02 source evidence in ``elmakus/chatgpt-codex-project-workflow`` at
the pinned consumer commit: repository, path, git blob id, byte length and
full-file sha256, plus verbatim excerpts with their own digests. Replay inputs
for the sizing, topology and review contracts are derived from these entries,
so a substituted anecdote fails either its digest or its pinned identity.

Covered historical classes, all derived from the cited sources:

- oversized mega-Card topology: M02-T01 combined the whole M02 milestone
  (REQ-018..033) in one Card although accepted P2 explicitly permitted a
  four-surface split (schema, derivation/resolution, acceptance/
  reconciliation, mutation-handoff).
- incomplete discovery: R02 and R06 issued GREEN on subjects for which a
  later independent review established a material defect; early passes did
  not consistently continue across the full acceptance surface after a
  blocking finding.
- literal-only class repair: early repairs were finding-complete but
  class-local, so sibling variants resurfaced; R09+ repaired whole
  defect classes with sibling coverage.
- convergence misuse: the R07-R11 finding-set contraction demonstrates
  process/defect-set convergence, not a GREEN verdict; no ordinary R12 was
  permitted before Main/root-cause convergence analysis.

Terminal preservation pins the exact DONE Card, result, R12 GREEN Card
review and Milestone R02 GREEN review. Earlier RED attempts (Card R01,
Milestone R01) are recorded as non-terminal and must never be treated as
currently active authority.

Prospective use only: tests replay these fixtures through the corrected
contracts without mutating any historical record. Out of scope here: BOOT-D
Worker discipline, M03 and any authority change. The REQ-127 intentional
live-consumer prerequisite lives in ``tools/live_consumer_contract.py``.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from typing import Any


class HistoricalReplayError(ValueError):
    """Raised when replay provenance, corpus shape or terminal state is invalid."""


SOURCE_REPOSITORY = "elmakus/chatgpt-codex-project-workflow"
SOURCE_COMMIT = "03099ca30d2589184ecb35e8d33a1368e989067d"

_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")

_WS = "implementation/workstreams/change-pwv21-policy-kernel-brainstorming"

# Pinned full-file identities, read at SOURCE_COMMIT. Verify with:
#   git -C <consumer> show SOURCE_COMMIT:<path> | sha256sum
#   git -C <consumer> rev-parse SOURCE_COMMIT:<path>
SOURCES: dict[str, dict[str, Any]] = {
    "m02-card": {
        "path": f"{_WS}/cards/M02-T01.md",
        "blob": "3e56fec00abd68fb51d464843983879aa0f4ffb4",
        "bytes": 3087,
        "sha256": "991f417096a35788ceef92182ba99fdf3136f475afabd7633db5621fab2be218",
    },
    "m02-result": {
        "path": f"{_WS}/results/M02-T01.md",
        "blob": "46ce3ec63f7c0ae82fa5c0c13c90f6428d6e9800",
        "bytes": 1890,
        "sha256": "bcfa3e33f982658fd6a9ffd44f0a17d9e314a645d66d3d49e212cecff9e3c98d",
    },
    "m02-card-r01": {
        "path": f"{_WS}/reviews/M02-T01-R01.toml",
        "blob": "f06fb8a5b81c3464973c52f49115d52e7ecbd592",
        "bytes": 881,
        "sha256": "8111302fb0f638c8d44cb60fb825163447326cff2859fe0fa838de131ca7d50a",
    },
    "m02-card-r12": {
        "path": f"{_WS}/reviews/M02-T01-R12.toml",
        "blob": "553964d4c2f391fc4c595db013d09530182da67b",
        "bytes": 1223,
        "sha256": "1dfdf0e625bee25054ab9c8f5e9374144a7285c80ae287331fe0d7d62c26d207",
    },
    "m02-milestone-r01": {
        "path": f"{_WS}/reviews/M02-MILESTONE-R01.toml",
        "blob": "20497ac31795b52bd0587e189f615ade190ad372",
        "bytes": 973,
        "sha256": "ff84fa138adeff59e1958b1755c0c026ce8b3caa0fbda336638cb3d2f1a35529",
    },
    "m02-milestone-r02": {
        "path": f"{_WS}/reviews/M02-MILESTONE-R02.toml",
        "blob": "015850c09fd0d563d1e7875d3875cc859b92fbbd",
        "bytes": 1048,
        "sha256": "5f3ceb9fa75770b0e9a00a47671d1ceaf65e19704c63b4cc767b620a06c58727",
    },
    "m02-convergence": {
        "path": f"{_WS}/evidence/M02-T01_CONVERGENCE_ANALYSIS_2026-09-24.md",
        "blob": "89f5942565de4a3da06dfca9ce0fd46ca5ed1957",
        "bytes": 16013,
        "sha256": "847c0c69936a1d1e824a7c4603c79cd6a439ed44ddcee3f990cf0f49f748bba6",
    },
    "m02-r02-evidence": {
        "path": f"{_WS}/evidence/M02-T01_REVIEW_R02_2026-09-24.md",
        "blob": "da744a58f7525b1b63177afb545c2b574af256dd",
        "bytes": 3029,
        "sha256": "e05a89e4246089c45d0444d5aab4e3b632eb98a376b1c9f29c3809044ce4ff31",
    },
    "m02-r06-evidence": {
        "path": f"{_WS}/evidence/M02-T01_REVIEW_R06_2026-09-24.md",
        "blob": "eb1fdbc89215e74e4f54ccc24e470bdead679438",
        "bytes": 3203,
        "sha256": "750f73581e6979de9ab608d7310f9b9990734a7b5a185c208dabf5f6cdaf67b3",
    },
    "m02-r09-evidence": {
        "path": f"{_WS}/evidence/M02-T01_REVIEW_R09_2026-09-24.md",
        "blob": "27b84f370dcbd382d2a9125908f87f4774dcf2c6",
        "bytes": 5593,
        "sha256": "82888959640a4ce1f4badadddaefc3e03f363a05aa4c2d098f5b84fd55841af1",
    },
    "m02-r10-evidence": {
        "path": f"{_WS}/evidence/M02-T01_R10_REVIEW_2026-09-24.md",
        "blob": "4c18cb1a0c08e06a033efacbb4c7319e7e865cbc",
        "bytes": 5035,
        "sha256": "58142ae00114300adc70d1909d927835cbb708d0aa29f7dfe87cd9a7df465667",
    },
    "m02-r11-evidence": {
        "path": f"{_WS}/evidence/M02-T01_R11_REVIEW_2026-09-24.md",
        "blob": "daee7e118082868475731de76f965be6ecd29da4",
        "bytes": 4901,
        "sha256": "716eeb482ecb6b5a93ec1225fa25dda041692521b711fd01fc63f00e9a11d456",
    },
    "p2-plan": {
        "path": "planning/PWV21_POLICY_KERNEL_MASTER_PLAN_P2.md",
        "blob": "79ee0b6588be32767ba283b9f20a48a192999001",
        "bytes": 64774,
        "sha256": "87a691dc8d67092355df7eb6d0a2ab467bb8a5d91ba8c2ea74c863d35cb57fab",
    },
}

_SOURCE_BY_PATH = {record["path"]: key for key, record in SOURCES.items()}


def _excerpt_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# Verbatim excerpts; each is a byte-exact substring of its pinned source file.
EXCERPTS: dict[str, dict[str, str]] = {
    "p2-m02-seams": {
        "source": "p2-plan",
        "text": (
            "Execution Prep may split M02 into schema, derivation/resolution, acceptance/\n"
            "reconciliation, and mutation-handoff Cards."
        ),
        "sha256": "8172c777d90daa3b33faf895d74e53f7f4acd6df3193f6b30af76bf94867163e",
    },
    "card-m02-scope": {
        "source": "m02-card",
        "text": (
            "Implement the complete M02 Typed Execution Obligation and Result contracts "
            "milestone from approved P2"
        ),
        "sha256": "c7d4c40d0749038bbd6c01fa557549db907b4356a2a3d891b5308623f077cb31",
    },
    "conv-rc5": {
        "source": "m02-convergence",
        "text": "M02-T01 was too broad for efficient falsification",
        "sha256": "d5a27b9061d8f49ccc39a3e02ee9220e6eb22b69a0704a78abf983daa1cb81bd",
    },
    "conv-r02-r06-green": {
        "source": "m02-convergence",
        "text": (
            "R02 and R06 both issued GREEN on subjects for which a later independent "
            "review established a material defect"
        ),
        "sha256": "3141acf710474af95c686e8829cd8def0200e6872fc8c387bb8499c82bdc6dcb",
    },
    "conv-r09-inflection": {
        "source": "m02-convergence",
        "text": (
            "R09 is the inflection point: it explicitly continued the full acceptance "
            "pass after the first defect and produced four independent classes in one attempt."
        ),
        "sha256": "08798fcc55bedc5dc4ab8513ddd79705ab23fd11e063ea30333da8f00cb11f67",
    },
    "conv-contraction": {
        "source": "m02-convergence",
        "text": (
            "the finding set contracted from four classes (R09), to two (R10), "
            "to one narrow class (R11)."
        ),
        "sha256": "31e6e37783fa792a2c36aa1cc1aa6aaa26f038a4304cc69a4386248e2a98a4de",
    },
    "conv-class-local": {
        "source": "m02-convergence",
        "text": (
            "early repairs were mostly finding-complete but class-local; later repairs "
            "became root-cause/class-level."
        ),
        "sha256": "e942e8e91a30357866fe8f0591f042ad80a81afc8c4d59b2aeff35f440dcf5ad",
    },
    "conv-convergence-limit": {
        "source": "m02-convergence",
        "text": (
            "it demonstrates **process and defect-set convergence**, not an independent "
            "GREEN verdict."
        ),
        "sha256": "1e60753957725b05730580fecbe9b7b973bf2950ae3db2faeb3c323ea755eac4",
    },
    "r11-no-ordinary-r12": {
        "source": "m02-r11-evidence",
        "text": (
            "no ordinary R12 full review may be created or executed before subsequent "
            "Main/root-cause convergence analysis."
        ),
        "sha256": "e341063617aecc557935bd901fb9d96d363fd1f23abf61c5bb13e84dadf00cec",
    },
    "r09-full-pass": {
        "source": "m02-r09-evidence",
        "text": (
            "The review continued across the complete acceptance surface after the "
            "first blocking defect."
        ),
        "sha256": "75c9c7a3c1bd2ebc8ad81e5abb8987075f742168e30266960abb4c50c288f8df",
    },
    "r02-green": {
        "source": "m02-r02-evidence",
        "text": "No blocking acceptance defect remains on the exact repaired subject.",
        "sha256": "6c7642f1949de2b9b486efd641a97b88a3c1f415448cf8774b693e18b0889151",
    },
    "r06-green": {
        "source": "m02-r06-evidence",
        "text": (
            "GREEN. The exact M02 Result subject satisfies the stable Card acceptance "
            "surface and the accepted M02 authority."
        ),
        "sha256": "c215f77a1125e729dfe01a2a33390721d071e779a4d694386b45c600658d8872",
    },
    "result-terminal-subject": {
        "source": "m02-result",
        "text": (
            "Implementation subject: "
            "elmakus/project_workflow_v2@e7a939e0a37f3cfcb7e39e04d5654b94101a5090"
        ),
        "sha256": "f5624d47a0fdc003535b20b8bf7e50c871f410c99a06d1609b3235f9c38c558d",
    },
    "r12-terminal": {
        "source": "m02-card-r12",
        "text": 'attempt = "M02-T01-R12"\nverdict = "green"',
        "sha256": "f529caa4d030a5eccb4f2802396aa9e390f61dca35aaac6c93ac318e193152d3",
    },
    "milestone-r02-terminal": {
        "source": "m02-milestone-r02",
        "text": 'attempt = "M02-MILESTONE-R02"\nverdict = "green"',
        "sha256": "aa72e7a9f47d5ef503f29bde051994b5e811c7f6edfd3bb63f13649e58f65697",
    },
}

FAILURE_CLASSES = frozenset({
    "oversized-card-topology",
    "incomplete-discovery",
    "literal-only-repair",
    "convergence-misuse",
    "terminal-preservation",
})

# The complete material finding set of the R09/R10/R11 contraction, taken from
# the exact finding headings of the pinned review evidence.
M02_DEFECT_CLASSES: tuple[dict[str, str], ...] = (
    {
        "id": "r09-f01-caller-projection-derivation",
        "finding": "R09-F01",
        "source": "m02-r09-evidence",
        "finding_title": (
            "production obligation derivation is not bound to the registered "
            "rule's actual canonical determining inputs"
        ),
    },
    {
        "id": "r09-f02-representable-direct-mutation",
        "finding": "R09-F02",
        "source": "m02-r09-evidence",
        "finding_title": (
            "the no-direct-canonical-mutation boundary is not enforced by the "
            "representable Result contract"
        ),
    },
    {
        "id": "r09-f03-readback-acceptance-decoupling",
        "finding": "R09-F03",
        "source": "m02-r09-evidence",
        "finding_title": (
            "mandatory governed readback is not coupled to final fresh-result acceptance"
        ),
    },
    {
        "id": "r09-f04-noncanonical-path-alias",
        "finding": "R09-F04",
        "source": "m02-r09-evidence",
        "finding_title": "exact-ref path validation admits non-canonical path aliases",
    },
    {
        "id": "r10-f01-semantic-result-acceptance",
        "finding": "R10-F01",
        "source": "m02-r10-evidence",
        "finding_title": "semantic Result acceptance is not gated before freshness acceptance",
    },
    {
        "id": "r10-f02-rule-content-binding",
        "finding": "R10-F02",
        "source": "m02-r10-evidence",
        "finding_title": (
            "Obligation identity/freshness is not bound to the registered rule "
            "content that determined the obligation"
        ),
    },
    {
        "id": "r11-f1-collection-minimality",
        "finding": "R11-F1",
        "source": "m02-r11-evidence",
        "finding_title": (
            "freshness fingerprints are not minimal for collection-valued "
            "mechanical inputs"
        ),
    },
)

M02_DEFECT_CLASS_IDS = frozenset(record["id"] for record in M02_DEFECT_CLASSES)

# The four P2-permitted M02 surfaces, from excerpt ``p2-m02-seams``.
M02_MEGA_OUTCOME_IDS = (
    "m02-schema-surface",
    "m02-derivation-resolution-surface",
    "m02-acceptance-reconciliation-surface",
    "m02-mutation-handoff-surface",
)

# M02 acceptance surface from the stable Card: PWV21-REQ-018..033 (16 requirements).
M02_ACCEPTANCE_REQS = tuple(f"PWV21-REQ-{number:03d}" for number in range(18, 34))

# Historical review ceiling replay: the user-defined R07-R11 experiment ran
# five fresh full-scope Card reviews before convergence analysis, matching the
# corrected card-scope discovery ceiling of 5.
M02_CONVERGENCE_REPLAY = {
    "review_scope": "card",
    "discovery_ceiling": 5,
    "fresh_epochs": ("R07", "R08", "R09", "R10", "R11"),
    "contraction": (("R09", 4), ("R10", 2), ("R11", 1)),
    "post_convergence_attempt": "R12",
}

# Correctly terminal historical M02 state. Pinned from the exact terminal
# result and review records; any deviation is a reopening or rewrite.
TERMINAL_M02 = {
    "card_id": "M02-T01",
    "card_status": "done",
    "result_commit": "eb17e9a9fd95195544426d7fc8dba5ae48f30cf0",
    "result_blob": "46ce3ec63f7c0ae82fa5c0c13c90f6428d6e9800",
    "card_review_attempt": "M02-T01-R12",
    "card_review_verdict": "green",
    "card_review_blob": "553964d4c2f391fc4c595db013d09530182da67b",
    "milestone_review_attempt": "M02-MILESTONE-R02",
    "milestone_review_verdict": "green",
    "milestone_review_blob": "015850c09fd0d563d1e7875d3875cc859b92fbbd",
}

# Earlier RED attempts are history, never currently active authority.
NON_TERMINAL_M02_ATTEMPTS = (
    {"attempt": "R01", "verdict": "red", "source": "m02-card-r01"},
    {"attempt": "M02-MILESTONE-R01", "verdict": "red", "source": "m02-milestone-r01"},
)

def _excerpt_ref(excerpt_id: str) -> dict[str, str]:
    return {"id": excerpt_id, "text": EXCERPTS[excerpt_id]["text"]}


CORPUS: tuple[dict[str, Any], ...] = (
    {
        "id": "m02-mega-topology",
        "failure_class": "oversized-card-topology",
        "summary": (
            "M02-T01 carried the complete M02 milestone in one Card while P2 "
            "explicitly permitted a four-surface split."
        ),
        "sources": ("m02-card", "p2-plan", "m02-convergence"),
        "excerpts": (
            _excerpt_ref("card-m02-scope"),
            _excerpt_ref("p2-m02-seams"),
            _excerpt_ref("conv-rc5"),
        ),
        "replay": {"sizing_outcome_ids": M02_MEGA_OUTCOME_IDS},
    },
    {
        "id": "m02-incomplete-discovery",
        "failure_class": "incomplete-discovery",
        "summary": (
            "R02/R06 GREEN verdicts on defective subjects and early passes "
            "without exhaustive continuation; R09 continued the full pass."
        ),
        "sources": ("m02-convergence", "m02-r02-evidence", "m02-r06-evidence", "m02-r09-evidence"),
        "excerpts": (
            _excerpt_ref("conv-r02-r06-green"),
            _excerpt_ref("r02-green"),
            _excerpt_ref("r06-green"),
            _excerpt_ref("r09-full-pass"),
        ),
        "replay": {
            "acceptance": "PWV21-REQ-018..033",
            "partial_attempts": ("R02", "R06"),
            "exhaustive_attempt": "R09",
        },
    },
    {
        "id": "m02-literal-class-repair",
        "failure_class": "literal-only-repair",
        "summary": (
            "Early repairs fixed the recorded finding but not its defect "
            "class; R09+ repaired whole classes with sibling coverage and "
            "the finding set contracted 4-2-1."
        ),
        "sources": ("m02-convergence", "m02-r09-evidence", "m02-r10-evidence", "m02-r11-evidence"),
        "excerpts": (
            _excerpt_ref("conv-class-local"),
            _excerpt_ref("conv-contraction"),
            _excerpt_ref("conv-r09-inflection"),
        ),
        "replay": {"defect_classes": tuple(record["id"] for record in M02_DEFECT_CLASSES)},
    },
    {
        "id": "m02-convergence-misuse",
        "failure_class": "convergence-misuse",
        "summary": (
            "The R07-R11 contraction is process/defect-set convergence, not a "
            "GREEN verdict; no ordinary R12 was allowed before convergence analysis."
        ),
        "sources": ("m02-convergence", "m02-r11-evidence"),
        "excerpts": (
            _excerpt_ref("conv-convergence-limit"),
            _excerpt_ref("r11-no-ordinary-r12"),
            _excerpt_ref("conv-r09-inflection"),
        ),
        "replay": {
            "review_scope": M02_CONVERGENCE_REPLAY["review_scope"],
            "discovery_ceiling": M02_CONVERGENCE_REPLAY["discovery_ceiling"],
            "post_convergence_attempt": M02_CONVERGENCE_REPLAY["post_convergence_attempt"],
        },
    },
    {
        "id": "m02-terminal-preservation",
        "failure_class": "terminal-preservation",
        "summary": (
            "Terminal M02 Card/result/R12/Milestone-R02 state stays immutable "
            "and routable; earlier RED attempts stay non-terminal history."
        ),
        "sources": ("m02-result", "m02-card-r12", "m02-milestone-r02"),
        "excerpts": (
            _excerpt_ref("result-terminal-subject"),
            _excerpt_ref("r12-terminal"),
            _excerpt_ref("milestone-r02-terminal"),
        ),
        "replay": {"terminal_card_id": TERMINAL_M02["card_id"]},
    },
)


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise HistoricalReplayError(f"{label} must be a table")
    return value


def provenance_record(source_key: str) -> dict[str, Any]:
    """Return the full pinned provenance record for a known corpus source."""
    if source_key not in SOURCES:
        raise HistoricalReplayError(f"unknown corpus source {source_key!r}")
    pinned = SOURCES[source_key]
    return {
        "repository": SOURCE_REPOSITORY,
        "commit": SOURCE_COMMIT,
        "path": pinned["path"],
        "blob": pinned["blob"],
        "bytes": pinned["bytes"],
        "sha256": pinned["sha256"],
    }


def validate_source_provenance(record: Any, label: str) -> dict[str, Any]:
    """Validate one exact-source provenance record against its pinned identity.

    The repository, commit, path, blob, byte length and full-file sha256 must
    all match the pinned source. Anything else — including a well-formed but
    substituted source — is rejected so invented anecdotes cannot stand in
    for the real terminal M02 evidence.
    """
    data = _require_mapping(record, label)
    repository = data.get("repository")
    commit = data.get("commit")
    path = data.get("path")
    blob = data.get("blob")
    size = data.get("bytes")
    digest = data.get("sha256")
    if repository != SOURCE_REPOSITORY:
        raise HistoricalReplayError(
            f"{label}: provenance repository must be {SOURCE_REPOSITORY!r}"
        )
    if not isinstance(commit, str) or _SHA40.fullmatch(commit) is None:
        raise HistoricalReplayError(f"{label}: provenance commit must be exact 40-hex")
    if commit != SOURCE_COMMIT:
        raise HistoricalReplayError(
            f"{label}: provenance commit {commit!r} does not match pinned source commit"
        )
    if not isinstance(path, str) or path not in _SOURCE_BY_PATH:
        raise HistoricalReplayError(f"{label}: unknown corpus source path {path!r}")
    if not isinstance(blob, str) or _SHA40.fullmatch(blob) is None:
        raise HistoricalReplayError(f"{label}: provenance blob must be exact 40-hex")
    pinned = SOURCES[_SOURCE_BY_PATH[path]]
    if blob != pinned["blob"]:
        raise HistoricalReplayError(
            f"{label}: provenance blob does not match pinned identity for {path!r}"
        )
    if size != pinned["bytes"]:
        raise HistoricalReplayError(
            f"{label}: provenance byte length does not match pinned identity for {path!r}"
        )
    if not isinstance(digest, str) or _SHA256.fullmatch(digest) is None:
        raise HistoricalReplayError(f"{label}: provenance sha256 must be 64-hex")
    if digest != pinned["sha256"]:
        raise HistoricalReplayError(
            f"{label}: provenance sha256 does not match pinned identity for {path!r}"
        )
    return {
        "repository": repository,
        "commit": commit,
        "path": path,
        "blob": blob,
        "bytes": size,
        "sha256": digest,
    }


def validate_excerpt(reference: Any, label: str, entry_sources: frozenset[str]) -> dict[str, str]:
    """Validate one verbatim excerpt reference inside a corpus entry."""
    data = _require_mapping(reference, label)
    excerpt_id = data.get("id")
    text = data.get("text")
    if excerpt_id not in EXCERPTS:
        raise HistoricalReplayError(f"{label}: unknown corpus excerpt {excerpt_id!r}")
    pinned = EXCERPTS[str(excerpt_id)]
    if pinned["source"] not in entry_sources:
        raise HistoricalReplayError(
            f"{label}: excerpt {excerpt_id!r} is not drawn from an entry source"
        )
    if not isinstance(text, str) or not text:
        raise HistoricalReplayError(f"{label}: excerpt text must be a non-empty string")
    if text != pinned["text"]:
        raise HistoricalReplayError(
            f"{label}: excerpt {excerpt_id!r} does not match pinned verbatim text"
        )
    if _excerpt_digest(text) != pinned["sha256"]:
        raise HistoricalReplayError(
            f"{label}: excerpt {excerpt_id!r} digest does not match pinned identity"
        )
    return {"id": str(excerpt_id), "text": text, "sha256": pinned["sha256"]}


def _validate_replay(entry_id: str, failure_class: str, replay: Any, label: str) -> dict[str, Any]:
    data = _require_mapping(replay, label)
    if failure_class == "oversized-card-topology":
        outcome_ids = data.get("sizing_outcome_ids")
        if not isinstance(outcome_ids, (list, tuple)):
            raise HistoricalReplayError(f"{label}: sizing_outcome_ids must be an array")
        if tuple(outcome_ids) != M02_MEGA_OUTCOME_IDS:
            raise HistoricalReplayError(
                f"{label}: replay must derive exactly the four P2-permitted M02 surfaces"
            )
        return {"sizing_outcome_ids": tuple(outcome_ids)}
    if failure_class == "incomplete-discovery":
        if data.get("acceptance") != "PWV21-REQ-018..033":
            raise HistoricalReplayError(
                f"{label}: replay must bind the full M02 REQ-018..033 acceptance surface"
            )
        if tuple(data.get("partial_attempts", ())) != ("R02", "R06"):
            raise HistoricalReplayError(
                f"{label}: replay must name the historical partial attempts R02/R06"
            )
        if data.get("exhaustive_attempt") != "R09":
            raise HistoricalReplayError(
                f"{label}: replay must name the historical exhaustive attempt R09"
            )
        return {
            "acceptance": "PWV21-REQ-018..033",
            "partial_attempts": ("R02", "R06"),
            "exhaustive_attempt": "R09",
        }
    if failure_class == "literal-only-repair":
        classes = data.get("defect_classes")
        if not isinstance(classes, (list, tuple)) or not classes:
            raise HistoricalReplayError(f"{label}: replay must name derived defect classes")
        unknown = [name for name in classes if name not in M02_DEFECT_CLASS_IDS]
        if unknown:
            raise HistoricalReplayError(
                f"{label}: replay names unknown defect classes: {', '.join(sorted(unknown))}"
            )
        return {"defect_classes": tuple(classes)}
    if failure_class == "convergence-misuse":
        if data.get("review_scope") != M02_CONVERGENCE_REPLAY["review_scope"]:
            raise HistoricalReplayError(f"{label}: replay must bind the card review scope")
        if data.get("discovery_ceiling") != M02_CONVERGENCE_REPLAY["discovery_ceiling"]:
            raise HistoricalReplayError(
                f"{label}: replay must bind the historical five-epoch ceiling"
            )
        if data.get("post_convergence_attempt") != M02_CONVERGENCE_REPLAY["post_convergence_attempt"]:
            raise HistoricalReplayError(
                f"{label}: replay must bind the post-convergence attempt R12"
            )
        return {
            "review_scope": "card",
            "discovery_ceiling": 5,
            "post_convergence_attempt": "R12",
        }
    if failure_class == "terminal-preservation":
        if data.get("terminal_card_id") != TERMINAL_M02["card_id"]:
            raise HistoricalReplayError(
                f"{label}: replay must bind the terminal Card {TERMINAL_M02['card_id']!r}"
            )
        return {"terminal_card_id": TERMINAL_M02["card_id"]}
    raise HistoricalReplayError(f"{label}: unknown failure class for entry {entry_id!r}")


def validate_corpus_entry(entry: Any, label: str) -> dict[str, Any]:
    """Validate one immutable corpus entry and its derivation bindings."""
    data = _require_mapping(entry, label)
    entry_id = data.get("id")
    if not isinstance(entry_id, str) or not entry_id.strip():
        raise HistoricalReplayError(f"{label}: corpus entry id must be a non-empty string")
    failure_class = data.get("failure_class")
    if failure_class not in FAILURE_CLASSES:
        raise HistoricalReplayError(
            f"{label}: unknown failure class {failure_class!r} for entry {entry_id!r}"
        )
    if "verdict" in data:
        raise HistoricalReplayError(
            f"{label}: corpus entry {entry_id!r} is immutable evidence and must not "
            "carry a review verdict"
        )
    summary = data.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise HistoricalReplayError(
            f"{label}: corpus entry {entry_id!r} requires a non-empty summary"
        )
    sources = data.get("sources")
    if not isinstance(sources, (list, tuple)) or not sources:
        raise HistoricalReplayError(
            f"{label}: corpus entry {entry_id!r} must name at least one exact source"
        )
    for source_key in sources:
        if source_key not in SOURCES:
            raise HistoricalReplayError(
                f"{label}: corpus entry {entry_id!r} names unknown source {source_key!r}"
            )
    entry_sources = frozenset(str(key) for key in sources)
    excerpts = data.get("excerpts")
    if not isinstance(excerpts, (list, tuple)) or not excerpts:
        raise HistoricalReplayError(
            f"{label}: corpus entry {entry_id!r} must cite at least one verbatim excerpt"
        )
    records = [
        validate_excerpt(reference, f"{label}.excerpts[{index}]", entry_sources)
        for index, reference in enumerate(excerpts)
    ]
    replay = _validate_replay(entry_id, str(failure_class), data.get("replay"), f"{label}.replay")
    return {
        "id": entry_id,
        "failure_class": failure_class,
        "summary": summary,
        "sources": tuple(sources),
        "excerpts": records,
        "replay": replay,
    }


def validate_corpus(entries: Any) -> list[dict[str, Any]]:
    """Validate the full immutable corpus with unique entry ids."""
    if not isinstance(entries, (list, tuple)) or not entries:
        raise HistoricalReplayError("corpus must be a non-empty array of entries")
    records = [
        validate_corpus_entry(entry, f"corpus[{index}]")
        for index, entry in enumerate(entries)
    ]
    seen: set[str] = set()
    for record in records:
        if record["id"] in seen:
            raise HistoricalReplayError(f"duplicate corpus entry id {record['id']!r}")
        seen.add(record["id"])
    return records


def corpus_entry(entry_id: str) -> dict[str, Any]:
    """Return one validated corpus entry with full provenance records."""
    for entry in CORPUS:
        if entry["id"] == entry_id:
            return validate_corpus_entry(entry, f"corpus.{entry_id}")
    raise HistoricalReplayError(f"unknown corpus entry {entry_id!r}")


def mega_sizing_outcomes() -> list[dict[str, Any]]:
    """Derive the historical M02 mega-Card scope as four separable outcomes.

    The four surfaces are exactly the P2-permitted split from excerpt
    ``p2-m02-seams``; the entry they replay is ``m02-mega-topology``. Each
    outcome carries its provenance so sizing validation and provenance
    validation stay bound to the same replay input.
    """
    provenance = {
        "corpus_entry": "m02-mega-topology",
        "sources": ("m02-card", "p2-plan", "m02-convergence"),
    }
    return [
        {
            "id": "m02-schema-surface",
            "kind": "contract",
            "statement": (
                "Versioned transport-neutral Obligation/Result schemas with "
                "executed golden fixtures."
            ),
            "family": "m02-schema",
            "independently_verifiable": True,
            "independently_useful": True,
            "falsifiable": True,
            "substantial": True,
            "scaffolding_only": False,
            "independently_consumed": False,
            "provenance": provenance,
        },
        {
            "id": "m02-derivation-resolution-surface",
            "kind": "invariant",
            "statement": (
                "PW-owned exact authority resolution with bounded required-source "
                "bundles and deterministic obligation identity."
            ),
            "family": "m02-derivation-resolution",
            "independently_verifiable": True,
            "independently_useful": True,
            "falsifiable": True,
            "substantial": True,
            "scaffolding_only": False,
            "independently_consumed": False,
            "provenance": provenance,
        },
        {
            "id": "m02-acceptance-reconciliation-surface",
            "kind": "invariant",
            "statement": (
                "Minimal freshness fingerprints with stale-result "
                "validation/reconciliation and safe reuse proof."
            ),
            "family": "m02-acceptance-reconciliation",
            "independently_verifiable": True,
            "independently_useful": True,
            "falsifiable": True,
            "substantial": True,
            "scaffolding_only": False,
            "independently_consumed": False,
            "provenance": provenance,
        },
        {
            "id": "m02-mutation-handoff-surface",
            "kind": "acceptance",
            "statement": (
                "Mutation preconditions/postconditions with coordinator-owned "
                "writes, mandatory readback and no direct canonical mutation."
            ),
            "family": "m02-mutation-handoff",
            "independently_verifiable": True,
            "independently_useful": True,
            "falsifiable": True,
            "substantial": True,
            "scaffolding_only": False,
            "independently_consumed": False,
            "provenance": provenance,
        },
    ]


def r02_style_partial_discovery() -> dict[str, Any]:
    """Replay the historical partial-discovery shape: omitted acceptance."""
    return {
        "corpus_entry": "m02-incomplete-discovery",
        "applicable_acceptance": list(M02_ACCEPTANCE_REQS),
        "evaluated_acceptance": list(M02_ACCEPTANCE_REQS[:10]),
        "stopped_at_first_blocker": False,
    }


def first_blocker_stop_discovery() -> dict[str, Any]:
    """Replay stopping at the first blocker instead of continuing the pass."""
    return {
        "corpus_entry": "m02-incomplete-discovery",
        "applicable_acceptance": list(M02_ACCEPTANCE_REQS),
        "evaluated_acceptance": list(M02_ACCEPTANCE_REQS[:3]),
        "stopped_at_first_blocker": True,
    }


def r09_style_exhaustive_discovery() -> dict[str, Any]:
    """Replay the R09 exhaustive shape: full surface, no early stop."""
    return {
        "corpus_entry": "m02-incomplete-discovery",
        "applicable_acceptance": list(M02_ACCEPTANCE_REQS),
        "evaluated_acceptance": list(M02_ACCEPTANCE_REQS),
        "stopped_at_first_blocker": False,
    }


def literal_only_closure_scope() -> dict[str, Any]:
    """Replay literal-only repair evidence: finding fixed, class unnamed."""
    return {
        "corpus_entry": "m02-literal-class-repair",
        "known_findings": ["R09-F01"],
        "defect_classes": [],
        "root_cause_evidence": [],
        "repair_diff": ["tools/policy_kernel.py"],
        "regression_evidence": ["test_literal_r09_f01_example"],
        "reachable_callers": [],
        "consumers": [],
        "providers": [],
        "contracts": [],
        "sibling_representations": ["sibling-rule-input-shape"],
        "negative_space": ["caller-projection-variant"],
    }


def class_level_closure_scope() -> dict[str, Any]:
    """Replay the corrected R09+ shape: whole-class repair with siblings."""
    return {
        "corpus_entry": "m02-literal-class-repair",
        "known_findings": ["R09-F01"],
        "defect_classes": ["r09-f01-caller-projection-derivation"],
        "root_cause_evidence": ["production seam forwards caller projection unchecked"],
        "repair_diff": ["tools/policy_kernel.py"],
        "regression_evidence": ["test_rule_input_derivation_class"],
        "reachable_callers": ["tools/obligation_contract.py"],
        "consumers": ["downstream-obligation-consumer"],
        "providers": ["registry-rule-provider"],
        "contracts": ["execution-obligation-v1"],
        "sibling_representations": ["sibling-rule-input-shape"],
        "negative_space": ["caller-projection-variant"],
    }


def terminal_m02_record() -> dict[str, str]:
    """Return the exact pinned terminal M02 record (positive control)."""
    return dict(TERMINAL_M02)


def assert_terminal_m02_preserved(record: Any, label: str = "terminal_m02") -> dict[str, str]:
    """Require a claimed M02 record to equal the pinned terminal state.

    A reopened Card status, a rewritten result/review blob or commit, a
    flipped terminal verdict, or a non-terminal RED attempt presented as
    terminal all fail. The returned record is the normalized terminal state.
    """
    data = _require_mapping(record, label)
    card_id = data.get("card_id")
    if card_id != TERMINAL_M02["card_id"]:
        raise HistoricalReplayError(
            f"{label}: terminal record binds Card {TERMINAL_M02['card_id']!r}, "
            f"not {card_id!r}"
        )
    status = data.get("card_status")
    if status != "done":
        raise HistoricalReplayError(
            f"{label}: terminal Card {TERMINAL_M02['card_id']!r} must stay done; "
            f"reopening as {status!r} is forbidden"
        )
    for attempt in NON_TERMINAL_M02_ATTEMPTS:
        if data.get("card_review_attempt") == attempt["attempt"] or data.get(
            "milestone_review_attempt"
        ) == attempt["attempt"]:
            raise HistoricalReplayError(
                f"{label}: RED attempt {attempt['attempt']!r} is non-terminal history, "
                "not currently active authority"
            )
    for key in (
        "result_commit",
        "result_blob",
        "card_review_attempt",
        "card_review_verdict",
        "card_review_blob",
        "milestone_review_attempt",
        "milestone_review_verdict",
        "milestone_review_blob",
    ):
        if data.get(key) != TERMINAL_M02[key]:
            raise HistoricalReplayError(
                f"{label}: terminal field {key!r} does not match pinned M02 history; "
                "historical state must not be rewritten"
            )
    return {key: TERMINAL_M02[key] for key in TERMINAL_M02}
