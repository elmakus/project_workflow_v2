#!/usr/bin/env python3
"""Non-mutating reproductions for audit ze8eya3df1xsxsb7q93smiac.

Run from a checkout of subject commit
4fb4bfb7d7b1481d6f347c182fc96a5a1135e045 (or this audit branch).
The script copies the canonical router fixture into temp directories and invokes
the real tools.router.select_route. It does not modify product files.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from tools.router import select_route

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"
RESULT = "implementation/workstreams/sample-workstream/results/M01-T04.md"
RESULT_EVIDENCE = "implementation/workstreams/sample-workstream/evidence/M01-T04.md"
REVIEW = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
REVIEW_EVIDENCE = "implementation/workstreams/sample-workstream/evidence/review-R01.md"
COMMIT = "a" * 40
BLOB = "b" * 40


def fixture_copy() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    temp = tempfile.TemporaryDirectory()
    project = Path(temp.name) / "project"
    shutil.copytree(FIXTURE, project)
    return temp, project


def full_card(project: Path, requirement: str = "required") -> None:
    p = project / CARD
    p.write_text(
        "# Fixture Card\n"
        "- Card ID: M01-T04\n"
        "- Included scope: exact audit reproduction\n"
        "- Excluded scope: unrelated work\n"
        "- Authority refs: requirements/REQUIREMENTS.md\n"
        "- Dependencies: none\n"
        "- Acceptance: acceptance-v1\n"
        "- Required tests/readback: tests-v1\n"
        f"- Review requirement: {requirement}\n"
        "- Technical contract: none\n",
        encoding="utf-8",
    )
    auth = project / "requirements/REQUIREMENTS.md"
    auth.parent.mkdir(parents=True, exist_ok=True)
    auth.write_text("# accepted authority\n", encoding="utf-8")


def add_result(project: Path) -> None:
    board = project / BOARD
    board.write_text(
        board.read_text(encoding="utf-8")
        + "\n[cards.result]\n"
        + 'class = "result"\n'
        + f'path = "{RESULT}"\n'
        + f'commit = "{COMMIT}"\n'
        + f'blob = "{BLOB}"\n',
        encoding="utf-8",
    )
    ev = project / RESULT_EVIDENCE
    ev.parent.mkdir(parents=True, exist_ok=True)
    ev.write_text("# result evidence\n", encoding="utf-8")
    result = project / RESULT
    result.parent.mkdir(parents=True, exist_ok=True)
    result.write_text(
        "# Card Result\n"
        "- Card ID: M01-T04\n"
        f"- Implementation subject: owner/repo@commit:{COMMIT}\n"
        f"- Evidence refs: {RESULT_EVIDENCE}\n"
        "- Tests/readback summary: GREEN-v1\n",
        encoding="utf-8",
    )


def add_green_review(project: Path) -> None:
    board = project / BOARD
    board.write_text(
        board.read_text(encoding="utf-8").replace(
            'status = "in_progress"\n',
            'status = "in_progress"\n'
            f'review_attempts = [{{ class = "review_attempt", path = "{REVIEW}" }}]\n',
            1,
        ),
        encoding="utf-8",
    )
    ev = project / REVIEW_EVIDENCE
    ev.parent.mkdir(parents=True, exist_ok=True)
    ev.write_text("# review evidence\n", encoding="utf-8")
    review = project / REVIEW
    review.parent.mkdir(parents=True, exist_ok=True)
    review.write_text(
        'workstream_id = "sample-workstream"\n'
        'card_id = "M01-T04"\n'
        'attempt = "R01"\n'
        'verdict = "green"\n'
        f'evidence_path = "{REVIEW_EVIDENCE}"\n'
        '[subject]\n'
        'class = "git_blob"\n'
        'repository = "owner/router-fixture"\n'
        f'commit = "{COMMIT}"\n'
        f'path = "{RESULT}"\n'
        f'blob = "{BLOB}"\n'
        '[acceptance]\n'
        'class = "task_card"\n'
        f'path = "{CARD}"\n'
        '[independence]\n'
        'materially_produced_or_repaired_subject = false\n'
        'basis = "Fresh semantic reviewer context."\n',
        encoding="utf-8",
    )


def route(project: Path):
    return select_route(project, [MANIFEST], package_root=ROOT)


def repro_satisfied_jit_routes_close() -> None:
    temp, project = fixture_copy()
    try:
        full_card(project, "none")
        add_result(project)
        board = project / BOARD
        text = board.read_text(encoding="utf-8").replace(
            'status = "in_progress"', 'status = "done"', 1
        )
        text += (
            "\n[[jit_triggers]]\n"
            'id = "after-M01-T04"\n'
            'after_card = "M01-T04"\n'
            'state = "satisfied"\n'
            'condition = "DONE predecessor result now determines downstream Card."\n'
        )
        board.write_text(text, encoding="utf-8")
        got = route(project)
        assert (got.disposition, got.obligation) == ("route", "close"), got
        print("F1 actual:", got.disposition, got.obligation)
    finally:
        temp.cleanup()


def repro_done_bypasses_required_review() -> None:
    temp, project = fixture_copy()
    try:
        full_card(project, "required")
        add_result(project)
        board = project / BOARD
        board.write_text(
            board.read_text(encoding="utf-8").replace(
                'status = "in_progress"', 'status = "done"', 1
            ),
            encoding="utf-8",
        )
        got = route(project)
        assert (got.disposition, got.obligation) == ("route", "close"), got
        print("F2 actual:", got.disposition, got.obligation)
    finally:
        temp.cleanup()


def reviewable_fixture() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    temp, project = fixture_copy()
    full_card(project, "required")
    add_result(project)
    add_green_review(project)
    initial = route(project)
    assert initial.obligation == "post_review_finalization", initial
    return temp, project


def repro_changed_result_reuses_stale_claimed_blob() -> None:
    temp, project = reviewable_fixture()
    try:
        result = project / RESULT
        result.write_text(
            result.read_text(encoding="utf-8").replace(
                "GREEN-v1", "MATERIALLY-CHANGED-v2"
            ),
            encoding="utf-8",
        )
        got = route(project)
        assert got.obligation == "post_review_finalization", got
        print("F3 actual:", got.disposition, got.obligation)
    finally:
        temp.cleanup()


def repro_changed_acceptance_reuses_green_review() -> None:
    temp, project = reviewable_fixture()
    try:
        card = project / CARD
        card.write_text(
            card.read_text(encoding="utf-8").replace(
                "Acceptance: acceptance-v1", "Acceptance: acceptance-v2"
            ),
            encoding="utf-8",
        )
        got = route(project)
        assert got.obligation == "post_review_finalization", got
        print("F4 actual:", got.disposition, got.obligation)
    finally:
        temp.cleanup()


def repro_missing_evidence_still_finalizes() -> None:
    temp, project = reviewable_fixture()
    try:
        (project / RESULT_EVIDENCE).unlink()
        (project / REVIEW_EVIDENCE).unlink()
        got = route(project)
        assert got.obligation == "post_review_finalization", got
        print("F5 actual:", got.disposition, got.obligation)
    finally:
        temp.cleanup()


if __name__ == "__main__":
    repro_satisfied_jit_routes_close()
    repro_done_bypasses_required_review()
    repro_changed_result_reuses_stale_claimed_blob()
    repro_changed_acceptance_reuses_green_review()
    repro_missing_evidence_still_finalizes()
