#!/usr/bin/env python3
"""Reproduce Task Board lifecycle states that the exact subject routes fail-open."""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from tools.router import select_route

ROOT = Path(__file__).resolve().parents[4]
FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"
RESULT = "implementation/workstreams/sample-workstream/results/M01-T04.md"
REVIEW = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"


def card_text(review: str) -> str:
    return (
        "# Probe Card\n"
        "- Card ID: M01-T04\n"
        "- Included scope: reproduce lifecycle coherence\n"
        "- Excluded scope: product changes\n"
        "- Authority refs: requirements/REQUIREMENTS.md\n"
        "- Dependencies: none\n"
        "- Acceptance: route from durable state only\n"
        "- Required tests/readback: this probe\n"
        f"- Review requirement: {review}\n"
        "- Technical contract: none\n"
    )


def result_text(summary: str = "GREEN") -> str:
    return (
        "# Card Result\n"
        "- Card ID: M01-T04\n"
        "- Implementation subject: owner/router-fixture@commit:" + ("a" * 40) + "\n"
        "- Evidence refs: implementation/workstreams/sample-workstream/evidence/result.md\n"
        f"- Tests/readback summary: {summary}\n"
    )


def review_text(verdict: str) -> str:
    evidence = "" if verdict in {"pending", "in_progress"} else (
        "implementation/workstreams/sample-workstream/evidence/review.md"
    )
    return (
        'workstream_id = "sample-workstream"\n'
        'card_id = "M01-T04"\n'
        'attempt = "R01"\n'
        f'verdict = "{verdict}"\n'
        f'evidence_path = "{evidence}"\n'
        '[subject]\n'
        'class = "git_blob"\n'
        'repository = "owner/router-fixture"\n'
        f'commit = "{"a" * 40}"\n'
        f'path = "{RESULT}"\n'
        f'blob = "{"b" * 40}"\n'
        '[acceptance]\n'
        'class = "task_card"\n'
        f'path = "{CARD}"\n'
        '[independence]\n'
        'materially_produced_or_repaired_subject = false\n'
        'basis = "Independent probe reviewer."\n'
    )


def prepare(project: Path, status: str, review_requirement: str, verdict: str | None) -> None:
    (project / CARD).write_text(card_text(review_requirement))
    authority = project / "requirements/REQUIREMENTS.md"
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("# authority\n")
    result = project / RESULT
    result.parent.mkdir(parents=True, exist_ok=True)
    result.write_text(result_text())
    board = project / BOARD
    text = board.read_text().replace(
        'status = "in_progress"\n',
        f'status = "{status}"\n'
        + (f'review_attempts = [{{ class = "review_attempt", path = "{REVIEW}" }}]\n' if verdict else ""),
        1,
    )
    text += (
        '\n[cards.result]\n'
        'class = "result"\n'
        f'path = "{RESULT}"\n'
        f'commit = "{"a" * 40}"\n'
        f'blob = "{"b" * 40}"\n'
    )
    board.write_text(text)
    if verdict:
        review = project / REVIEW
        review.parent.mkdir(parents=True, exist_ok=True)
        review.write_text(review_text(verdict))


def run_case(status: str, review_requirement: str, verdict: str | None) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp) / "project"
        shutil.copytree(FIXTURE, project)
        prepare(project, status, review_requirement, verdict)
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print(status, review_requirement, verdict, "=>", routed.disposition, routed.obligation)
        print("read_set:", routed.read_set)


if __name__ == "__main__":
    # Material F1: a DONE Card with an unresolved REQUIRED review is not rejected;
    # the selector reaches Close without reading the Card/result/review.
    run_case("done", "required", "pending")
    run_case("done", "required", "red")

    # Sibling lifecycle contradiction: READY plus a durable result re-enters prep.
    run_case("ready", "none", None)
