#!/usr/bin/env python3
"""Non-mutating PWv2 adversarial reproductions for audit sdcia5015cuyksv7guxzxuw6.

Run from an exact checkout of:
4fb4bfb7d7b1481d6f347c182fc96a5a1135e045

This script only uses TemporaryDirectory-backed copies of the existing router
fixture and invokes the production selector.
"""

from pathlib import Path

from tests.test_router import RouterTests, MANIFEST, ROOT, BOARD, CARD
from tools.router import select_route


def route(project: Path):
    return select_route(project, [MANIFEST], package_root=ROOT)


def f1_done_bypasses_required_review() -> None:
    h = RouterTests()
    temp, project = h.copy_fixture()
    try:
        h.install_reviewable_result(project, "required")
        board = project / BOARD
        board.write_text(board.read_text().replace('status = "in_progress"', 'status = "done"', 1))
        got = route(project)
        print("F1", got.disposition, got.obligation)
        assert (got.disposition, got.obligation) == ("route", "close")
    finally:
        temp.cleanup()


def f2_green_review_acceptance_can_drift() -> None:
    h = RouterTests()
    temp, project = h.copy_fixture()
    try:
        h.install_reviewable_result(project, "required")
        h.add_review_attempt(project, "green")

        alternate = "implementation/workstreams/sample-workstream/cards/archive/M01-T04.md"
        alternate_path = project / alternate
        alternate_path.parent.mkdir(parents=True, exist_ok=True)
        alternate_path.write_text(
            h.task_card_content(review_requirement="required").replace(
                "- Acceptance: route only after current launch inputs are valid",
                "- Acceptance: materially changed acceptance surface",
            )
        )

        board = project / BOARD
        board.write_text(board.read_text().replace(f'path = "{CARD}"', f'path = "{alternate}"', 1))
        got = route(project)
        print("F2", got.disposition, got.obligation)
        assert (got.disposition, got.obligation) == ("route", "post_review_finalization")
    finally:
        temp.cleanup()


def f3_same_path_bytes_do_not_invalidate_git_identity() -> None:
    h = RouterTests()

    # Dependency launch case.
    temp, project = h.copy_fixture()
    try:
        dep_path = "implementation/workstreams/sample-workstream/results/M01-T03.md"
        commit = "a" * 40
        blob = "b" * 40
        dep = f"{dep_path}@{commit}:{blob}"
        h.install_done_predecessor(project, path=dep_path, commit=commit, blob=blob)
        h.make_ready_card(project, dependencies=dep)
        (project / dep_path).write_text("# materially changed bytes, locator unchanged\n")
        got = route(project)
        print("F3-dependency", got.disposition, got.obligation)
        assert (got.disposition, got.obligation) == ("route", "execution_prep")
    finally:
        temp.cleanup()

    # Reviewed current-result case.
    temp, project = h.copy_fixture()
    try:
        result_path = h.install_reviewable_result(project, "required")
        h.add_review_attempt(project, "green")
        p = project / result_path
        p.write_text(
            p.read_text().replace(
                "- Implementation subject: owner/repo@commit:" + ("a" * 40),
                "- Implementation subject: owner/repo@commit:" + ("c" * 40),
            )
        )
        got = route(project)
        print("F3-result", got.disposition, got.obligation)
        assert (got.disposition, got.obligation) == ("route", "post_review_finalization")
    finally:
        temp.cleanup()


def f4_ready_with_result_reenters_execution_prep() -> None:
    h = RouterTests()
    temp, project = h.copy_fixture()
    try:
        h.install_reviewable_result(project, "none")
        board = project / BOARD
        board.write_text(board.read_text().replace('status = "in_progress"', 'status = "ready"', 1))
        got = route(project)
        print("F4", got.disposition, got.obligation)
        assert (got.disposition, got.obligation) == ("route", "execution_prep")
    finally:
        temp.cleanup()


def f5_terminal_review_is_mutable_in_place() -> None:
    h = RouterTests()
    temp, project = h.copy_fixture()
    try:
        h.install_reviewable_result(project, "required")
        review_rel = h.add_review_attempt(project, "red")
        before = route(project)
        print("F5-before", before.disposition, before.obligation)
        assert (before.disposition, before.obligation) == ("route", "execution_resolution")

        review_path = project / review_rel
        review_path.write_text(review_path.read_text().replace('verdict = "red"', 'verdict = "green"', 1))

        after = route(project)
        print("F5-after", after.disposition, after.obligation)
        assert (after.disposition, after.obligation) == ("route", "post_review_finalization")
    finally:
        temp.cleanup()


if __name__ == "__main__":
    f1_done_bypasses_required_review()
    f2_green_review_acceptance_can_drift()
    f3_same_path_bytes_do_not_invalidate_git_identity()
    f4_ready_with_result_reenters_execution_prep()
    f5_terminal_review_is_mutable_in_place()
    print("All five adverse behaviors reproduced if assertions pass.")
