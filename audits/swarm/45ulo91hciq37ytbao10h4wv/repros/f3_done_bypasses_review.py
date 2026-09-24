#!/usr/bin/env python3
from tests.test_router import BOARD, MANIFEST, ROOT, RouterTests
from tools.router import select_route

for verdict in ("pending", "red"):
    t = RouterTests("test_active_card_routes_to_runtime_neutral_execution")
    temp, project = t.copy_fixture()
    try:
        t.install_reviewable_result(project, "required")
        t.add_review_attempt(project, verdict)
        board = project / BOARD
        board.write_text(
            board.read_text(encoding="utf-8").replace('status = "in_progress"', 'status = "done"', 1),
            encoding="utf-8",
        )
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print(verdict, routed.disposition, routed.obligation)
        # Bug: REQUIRED pending/RED review disappears behind trusted done status.
        assert (routed.disposition, routed.obligation) == ("route", "close")
    finally:
        temp.cleanup()
