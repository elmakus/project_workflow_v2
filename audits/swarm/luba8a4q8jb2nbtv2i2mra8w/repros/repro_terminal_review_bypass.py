#!/usr/bin/env python3
"""Non-mutating reproductions for terminal/review integrity defects.

Run from an exact checkout of:
4fb4bfb7d7b1481d6f347c182fc96a5a1135e045

    python3 audits/swarm/luba8a4q8jb2nbtv2i2mra8w/repros/repro_terminal_review_bypass.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from tests.test_router import BOARD, CARD, MANIFEST, ROOT, RouterTests  # noqa: E402
from tools.router import select_route  # noqa: E402


def route(project: Path):
    return select_route(project, [MANIFEST], package_root=ROOT)


def assert_route(result, obligation: str) -> None:
    actual = (result.disposition, result.obligation)
    expected = ("route", obligation)
    print(actual, result.reason)
    assert actual == expected, (actual, expected)


def case_done_missing_result() -> None:
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        result_path = "implementation/workstreams/sample-workstream/results/M01-T04.md"
        board = project / BOARD
        board.write_text(
            board.read_text().replace('status = "in_progress"', 'status = "done"', 1)
            + '\n[cards.result]\n'
            + 'class = "result"\n'
            + f'path = "{result_path}"\n'
            + f'commit = "{"a" * 40}"\n'
            + f'blob = "{"b" * 40}"\n'
        )
        assert not (project / result_path).exists()
        assert_route(route(project), "close")
    finally:
        temp.cleanup()


def case_done_required_review_missing() -> None:
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        helper.install_reviewable_result(project, "required")
        board = project / BOARD
        board.write_text(board.read_text().replace('status = "in_progress"', 'status = "done"', 1))
        assert_route(route(project), "close")
    finally:
        temp.cleanup()


def case_done_red_review_ignored() -> None:
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        helper.install_reviewable_result(project, "required")
        helper.add_review_attempt(project, "red")
        board = project / BOARD
        board.write_text(board.read_text().replace('status = "in_progress"', 'status = "done"', 1))
        assert_route(route(project), "close")
    finally:
        temp.cleanup()


def case_green_missing_evidence_finalizes() -> None:
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        helper.install_reviewable_result(project, "required")
        review_path = helper.add_review_attempt(project, "green")
        review = project / review_path
        review.write_text(
            review.read_text().replace(
                'evidence_path = "implementation/workstreams/sample-workstream/evidence/review-R01.md"',
                'evidence_path = "missing/review-evidence.md"',
            )
        )
        assert not (project / "missing/review-evidence.md").exists()
        assert_route(route(project), "post_review_finalization")
    finally:
        temp.cleanup()


def case_changed_active_card_acceptance_reuses_green() -> None:
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        helper.install_reviewable_result(project, "required")
        helper.add_review_attempt(project, "green")
        card = project / CARD
        before = card.read_text()
        after = before.replace(
            "- Acceptance: route only after current launch inputs are valid",
            "- Acceptance: materially changed acceptance that was never reviewed",
        )
        assert before != after
        card.write_text(after)
        assert_route(route(project), "post_review_finalization")
    finally:
        temp.cleanup()


if __name__ == "__main__":
    case_done_missing_result()
    case_done_required_review_missing()
    case_done_red_review_ignored()
    case_green_missing_evidence_finalizes()
    case_changed_active_card_acceptance_reuses_green()
    print("reproduced terminal/review integrity defects")
