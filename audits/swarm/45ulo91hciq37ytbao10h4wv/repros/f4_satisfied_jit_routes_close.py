#!/usr/bin/env python3
from tests.test_router import BOARD, MANIFEST, ROOT, RouterTests
from tools.router import select_route

t = RouterTests("test_active_card_routes_to_runtime_neutral_execution")
temp, project = t.copy_fixture()
try:
    t.install_reviewable_result(project, "none")
    board = project / BOARD
    text = board.read_text(encoding="utf-8").replace('status = "in_progress"', 'status = "done"', 1)
    text += """

[[jit_triggers]]
id = "after-M01-T04"
after_card = "M01-T04"
state = "satisfied"
condition = "DONE result now determines the exact downstream Card boundary."
"""
    board.write_text(text, encoding="utf-8")
    routed = select_route(project, [MANIFEST], package_root=ROOT)
    print(routed.disposition, routed.obligation)
    # Bug: satisfied, unconsumed JIT work is ignored and all-DONE selects Close.
    assert (routed.disposition, routed.obligation) == ("route", "close")
finally:
    temp.cleanup()
