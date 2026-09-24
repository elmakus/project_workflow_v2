#!/usr/bin/env python3
"""Non-mutating PWv2 adversarial counterexamples for audit 1nf66pps8yiv44rk65rdcv5g.

Run from the repository root at exactly:
4fb4bfb7d7b1481d6f347c182fc96a5a1135e045

Usage:
  python3 audits/swarm/1nf66pps8yiv44rk65rdcv5g/repros/router_counterexamples.py
  python3 audits/swarm/1nf66pps8yiv44rk65rdcv5g/repros/router_counterexamples.py F1
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools.router import select_route  # noqa: E402

TEST_ROUTER = ROOT / "tests" / "test_router.py"
spec = importlib.util.spec_from_file_location("pwv2_exact_test_router", TEST_ROUTER)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load exact tests/test_router.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

RouterTests = mod.RouterTests
MANIFEST = mod.MANIFEST
BOARD = mod.BOARD


def route_pair(route):
    return route.disposition, route.obligation


def f1_stale_git_identity() -> None:
    h = RouterTests()
    temp, project = h.copy_fixture()
    try:
        result_path = h.install_reviewable_result(project, "required")
        h.add_review_attempt(project, "green")
        result_file = project / result_path
        original = result_file.read_text()
        result_file.write_text(
            original.replace(
                "- Tests/readback summary: GREEN",
                "- Tests/readback summary: materially changed after GREEN review",
            )
        )
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F1", route_pair(routed), routed.reason)
        assert route_pair(routed) == ("route", "post_review_finalization")
    finally:
        temp.cleanup()


def f2_done_review_bypass() -> None:
    h = RouterTests()
    temp, project = h.copy_fixture()
    try:
        h.install_reviewable_result(project, "required")
        board = project / BOARD
        board.write_text(
            board.read_text().replace('status = "in_progress"', 'status = "done"', 1)
        )
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F2", route_pair(routed), routed.reason)
        assert route_pair(routed) == ("route", "close")
    finally:
        temp.cleanup()


def f3_plan_review_in_progress_is_red() -> None:
    h = RouterTests()
    temp, project = h.copy_fixture()
    try:
        h.install_green_definition(project)
        h.install_state_record(
            project,
            "planning",
            "planning",
            "PLANNING.toml",
            h.planning_content(state="frozen", premium_b="satisfied"),
        )
        h.install_state_record(
            project,
            "plan_review",
            "plan_review",
            "PLAN_REVIEW.toml",
            h.plan_review_content("pending"),
        )
        review = project / "implementation/workstreams/sample-workstream/PLAN_REVIEW.toml"
        review.write_text(review.read_text().replace('verdict = "pending"', 'verdict = "in_progress"'))
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F3", route_pair(routed), routed.reason)
        assert route_pair(routed) == ("route", "planning")
        assert "RED Plan Review" in routed.reason
    finally:
        temp.cleanup()


def f4_explicit_stop_bypassed() -> None:
    h = RouterTests()
    temp, project = h.copy_fixture()
    try:
        h.install_green_definition(project)
        brainstorm = project / "implementation/workstreams/sample-workstream/BRAINSTORM.toml"
        brainstorm.write_text(
            brainstorm.read_text().replace(
                "explicit_user_stop = false",
                "explicit_user_stop = true",
            )
        )
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F4", route_pair(routed), routed.reason)
        assert route_pair(routed) == ("route", "planning")
    finally:
        temp.cleanup()


CASES = {
    "F1": f1_stale_git_identity,
    "F2": f2_done_review_bypass,
    "F3": f3_plan_review_in_progress_is_red,
    "F4": f4_explicit_stop_bypassed,
}


def main() -> int:
    requested = sys.argv[1:]
    names = requested or list(CASES)
    unknown = [name for name in names if name not in CASES]
    if unknown:
        raise SystemExit(f"unknown case(s): {', '.join(unknown)}")
    for name in names:
        CASES[name]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
