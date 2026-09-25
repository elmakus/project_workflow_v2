#!/usr/bin/env python3
"""Non-mutating reproductions for PWv2 adversarial audit b7qtnwcsraaa1fat6o96n77a.

Run inside a checkout of subject commit:
4fb4bfb7d7b1481d6f347c182fc96a5a1135e045

The script copies the repository's router fixture into temporary directories and
calls the real production selector. It never mutates product files in-place.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
TEST_ROUTER = ROOT / "tests" / "test_router.py"


def load_test_module():
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location("pwv2_exact_test_router", TEST_ROUTER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {TEST_ROUTER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


M = load_test_module()
RouterTests = M.RouterTests
select_route = M.select_route
MANIFEST = M.MANIFEST
BOARD = M.BOARD


def fixture_case():
    case = RouterTests(methodName="test_active_card_routes_to_runtime_neutral_execution")
    temp, project = case.copy_fixture()
    return case, temp, project


def f1_same_path_dependency_drift() -> None:
    case, temp, project = fixture_case()
    try:
        dependency_path = "implementation/workstreams/sample-workstream/results/M01-T03.md"
        commit = "a" * 40
        blob = "b" * 40
        dependency = f"{dependency_path}@{commit}:{blob}"
        case.install_done_predecessor(
            project, path=dependency_path, commit=commit, blob=blob
        )
        case.make_ready_card(project, dependencies=dependency)

        # Change only the bytes; both declared identities remain unchanged.
        (project / dependency_path).write_text(
            "# materially changed predecessor result under unchanged locator\n"
        )

        routed = select_route(project, [MANIFEST], package_root=ROOT)
        actual = (routed.disposition, routed.obligation)
        print("F1 actual:", actual, routed.reason)
        assert actual == ("route", "execution_prep"), (
            "F1 no longer reproduces; expected current subject behavior "
            "route/execution_prep"
        )
    finally:
        temp.cleanup()


def f2_done_required_review_bypass() -> None:
    case, temp, project = fixture_case()
    try:
        case.install_reviewable_result(project, "required")
        board = project / BOARD
        board.write_text(
            board.read_text().replace(
                'status = "in_progress"', 'status = "done"', 1
            )
        )

        routed = select_route(project, [MANIFEST], package_root=ROOT)
        actual = (routed.disposition, routed.obligation)
        print("F2 actual:", actual, routed.reason)
        assert actual == ("route", "close"), (
            "F2 no longer reproduces; expected current subject behavior route/close"
        )
    finally:
        temp.cleanup()


def f3_missing_green_evidence() -> None:
    case, temp, project = fixture_case()
    try:
        case.install_reviewable_result(project, "required")
        case.add_review_attempt(project, "green")
        evidence = (
            project
            / "implementation/workstreams/sample-workstream/evidence/review-R01.md"
        )
        evidence.unlink()

        routed = select_route(project, [MANIFEST], package_root=ROOT)
        actual = (routed.disposition, routed.obligation)
        print("F3 actual:", actual, routed.reason)
        assert actual == ("route", "post_review_finalization"), (
            "F3 no longer reproduces; expected current subject behavior "
            "route/post_review_finalization"
        )
    finally:
        temp.cleanup()


def f4_research_redirect() -> None:
    case, temp, project = fixture_case()
    try:
        case.install_board_research(
            project, state="complete", reconciliation="pending"
        )
        research = (
            project / "implementation/workstreams/sample-workstream/RESEARCH.toml"
        )
        research.write_text(
            research.read_text().replace(
                'return_target = "execution_resolution:M01-T04"',
                'return_target = "execution_resolution:M01-T99"',
            )
        )

        routed = select_route(project, [MANIFEST], package_root=ROOT)
        actual = (routed.disposition, routed.obligation, routed.subject)
        print("F4 actual:", actual, routed.reason)
        assert actual == ("route", "execution_resolution", "M01-T99"), (
            "F4 no longer reproduces; expected current subject redirect to M01-T99"
        )
    finally:
        temp.cleanup()


CASES = {
    "f1": f1_same_path_dependency_drift,
    "f2": f2_done_required_review_bypass,
    "f3": f3_missing_green_evidence,
    "f4": f4_research_redirect,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=[*CASES, "all"], default="all")
    args = parser.parse_args()

    selected = CASES.values() if args.case == "all" else [CASES[args.case]]
    for fn in selected:
        fn()
    print("reproduced requested current-subject defect case(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
