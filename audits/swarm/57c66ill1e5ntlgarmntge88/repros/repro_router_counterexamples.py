#!/usr/bin/env python3
"""Non-mutating PWv2 adversarial reproductions for audit 57c66ill1e5ntlgarmntge88.

Run from any checkout containing this file:
  python audits/swarm/57c66ill1e5ntlgarmntge88/repros/repro_router_counterexamples.py
  python audits/swarm/57c66ill1e5ntlgarmntge88/repros/repro_router_counterexamples.py --case F1

The script copies the repository's official router fixture to a temporary directory
and calls the real production selector. It never writes product/source files.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools.router import select_route  # noqa: E402

spec = importlib.util.spec_from_file_location("pwv2_test_router", ROOT / "tests" / "test_router.py")
assert spec and spec.loader
test_router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_router)

MANIFEST = test_router.MANIFEST
BOARD = test_router.BOARD
CARD = test_router.CARD


def helper():
    return test_router.RouterTests("test_valid_state_selects_same_route_independent_of_runtime_noise")


def f1_result_mutation_after_green() -> None:
    h = helper()
    temp, project = h.copy_fixture()
    try:
        result_rel = h.install_reviewable_result(project, "required")
        h.add_review_attempt(project, "green")
        before = select_route(project, [MANIFEST], package_root=ROOT)
        assert (before.disposition, before.obligation) == ("route", "post_review_finalization")

        result_path = project / result_rel
        original = result_path.read_text()
        result_path.write_text(
            original.replace(
                "- Tests/readback summary: GREEN",
                "- Tests/readback summary: GREEN; bytes mutated after review",
            )
        )
        after = select_route(project, [MANIFEST], package_root=ROOT)
        print("F1 expected recovery/new review after byte mutation; actual:", after.disposition, after.obligation)
        assert (after.disposition, after.obligation) == ("route", "post_review_finalization")
    finally:
        temp.cleanup()


def f2_wrong_acceptance_contract() -> None:
    h = helper()
    temp, project = h.copy_fixture()
    try:
        h.install_reviewable_result(project, "required")
        review_rel = h.add_review_attempt(project, "green")
        review_path = project / review_rel
        wrong = "implementation/workstreams/sample-workstream/cards/archive/M01-T04.md"
        assert not (project / wrong).exists()
        review_path.write_text(review_path.read_text().replace(f'path = "{CARD}"', f'path = "{wrong}"'))
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F2 expected recovery/review freeze for wrong acceptance; actual:", routed.disposition, routed.obligation)
        assert (routed.disposition, routed.obligation) == ("route", "post_review_finalization")
    finally:
        temp.cleanup()


def f3_missing_review_evidence() -> None:
    h = helper()
    temp, project = h.copy_fixture()
    try:
        h.install_reviewable_result(project, "required")
        review_rel = h.add_review_attempt(project, "green")
        review_path = project / review_rel
        existing = project / "implementation/workstreams/sample-workstream/evidence/review-R01.md"
        if existing.exists():
            existing.unlink()
        missing = "implementation/workstreams/sample-workstream/evidence/DOES-NOT-EXIST.md"
        review_path.write_text(
            review_path.read_text().replace(
                "implementation/workstreams/sample-workstream/evidence/review-R01.md",
                missing,
            )
        )
        assert not (project / missing).exists()
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F3 expected recovery for missing terminal evidence; actual:", routed.disposition, routed.obligation)
        assert (routed.disposition, routed.obligation) == ("route", "post_review_finalization")
    finally:
        temp.cleanup()


def f4_orphan_execution_research() -> None:
    h = helper()
    temp, project = h.copy_fixture()
    try:
        workstream = project / MANIFEST
        workstream.write_text(
            workstream.read_text()
            + '\n[research]\nclass = "research"\n'
            + 'path = "implementation/workstreams/sample-workstream/RESEARCH.toml"\n'
        )
        research = project / "implementation/workstreams/sample-workstream/RESEARCH.toml"
        research.write_text(
            'state = "active"\n'
            'workstream_id = "sample-workstream"\n'
            'origin_role = "execution_resolution"\n'
            'origin_subject = "M01-T04"\n'
            'return_target = "execution_resolution:M01-T04"\n'
            'return_reconciliation = "pending"\n'
            'return_result = ""\n'
            'finding = ""\n'
            'limitations = ""\n'
            'conflicts = ""\n'
            '[[sources]]\nclass = "official_upstream"\nstatus = "pending"\nweight = "primary"\n'
            '[[sources]]\nclass = "project_runtime"\nstatus = "pending"\nweight = "direct"\n'
            '[[sources]]\nclass = "tracker_discussion"\nstatus = "pending"\nweight = "supporting"\n'
            '[[sources]]\nclass = "practitioner_community"\nstatus = "pending"\nweight = "supporting"\n'
        )
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F4 expected fail-closed/Board-owned route without Board Research pointer; actual:",
              routed.disposition, routed.obligation)
        print("F4 read_set:", routed.read_set)
        assert (routed.disposition, routed.obligation) == ("route", "research")
        assert f"project:{BOARD}" not in routed.read_set
    finally:
        temp.cleanup()


CASES = {
    "F1": f1_result_mutation_after_green,
    "F2": f2_wrong_acceptance_contract,
    "F3": f3_missing_review_evidence,
    "F4": f4_orphan_execution_research,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=sorted(CASES))
    args = parser.parse_args()
    selected = [args.case] if args.case else list(CASES)
    for name in selected:
        CASES[name]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
