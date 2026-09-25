#!/usr/bin/env python3
"""Non-mutating reproductions for material findings in PWv2 swarm audit.

Run from repository root at subject commit (or this audit branch):
    python3 audits/swarm/yc80f4r9jz0jn7b0vzdv424d/repros/repro_material_findings.py
"""

from tests.test_router import BOARD, MANIFEST, ROOT, RouterTests
from tools.router import select_route


def f1_explicit_stop_loses_precedence() -> None:
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        helper.install_green_definition(project)
        brainstorm = project / "implementation/workstreams/sample-workstream/BRAINSTORM.toml"
        brainstorm.write_text(
            brainstorm.read_text().replace(
                "explicit_user_stop = false",
                "explicit_user_stop = true",
            )
        )
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F1:", routed.disposition, routed.obligation, routed.reason)
        assert (routed.disposition, routed.obligation) == ("route", "planning")
    finally:
        temp.cleanup()


def f2_changed_result_bytes_keep_green_review() -> None:
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        result_rel = helper.install_reviewable_result(project, "required")
        helper.add_review_attempt(project, "green")

        before = select_route(project, [MANIFEST], package_root=ROOT)
        assert (before.disposition, before.obligation) == (
            "route",
            "post_review_finalization",
        )

        result_file = project / result_rel
        result_file.write_text(
            "# Card Result\n"
            "- Card ID: M01-T04\n"
            "- Implementation subject: owner/repo@commit:"
            + ("c" * 40)
            + "\n"
            "- Evidence refs: "
            "implementation/workstreams/sample-workstream/evidence/M01-T04.md\n"
            "- Tests/readback summary: materially changed but parse-valid\n"
        )

        after = select_route(project, [MANIFEST], package_root=ROOT)
        print("F2:", after.disposition, after.obligation, after.reason)
        assert (after.disposition, after.obligation) == (
            "route",
            "post_review_finalization",
        )
    finally:
        temp.cleanup()


def f3_done_card_bypasses_pending_required_review() -> None:
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        helper.install_reviewable_result(project, "required")
        helper.add_review_attempt(project, "pending")

        board = project / BOARD
        board.write_text(
            board.read_text().replace(
                'status = "in_progress"',
                'status = "done"',
                1,
            )
        )

        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F3:", routed.disposition, routed.obligation, routed.reason)
        assert (routed.disposition, routed.obligation) == ("route", "close")
    finally:
        temp.cleanup()


if __name__ == "__main__":
    f1_explicit_stop_loses_precedence()
    f2_changed_result_bytes_keep_green_review()
    f3_done_card_bypasses_pending_required_review()
    print("All three material defect reproductions observed.")
