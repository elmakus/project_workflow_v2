#!/usr/bin/env python3
"""Non-mutating PWv2 swarm reproductions for frozen findings F1-F4.

Run from any checkout containing this audit:
    python audits/swarm/69f0g74xooo389jwdz456zmv/repros/repro_router_semantic_gaps.py

The script mutates only TemporaryDirectory fixture copies.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools.router import select_route
from tests.test_router import RouterTests, MANIFEST


def route_tuple(route):
    return [route.disposition, route.obligation, route.subject, route.owner_module]


def stale_dependency_bytes():
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        dependency_path = "implementation/workstreams/sample-workstream/results/M01-T03.md"
        commit = "a" * 40
        blob = "b" * 40
        dependency = f"{dependency_path}@{commit}:{blob}"
        helper.install_done_predecessor(
            project, path=dependency_path, commit=commit, blob=blob
        )
        helper.make_ready_card(project, dependencies=dependency)

        before = select_route(project, [MANIFEST], package_root=ROOT)
        (project / dependency_path).write_text(
            "# CHANGED BYTES WITH UNCHANGED DECLARED COMMIT/BLOB\n",
            encoding="utf-8",
        )
        after = select_route(project, [MANIFEST], package_root=ROOT)

        assert (before.disposition, before.obligation) == ("route", "execution_prep")
        # Defect: same-path changed bytes should invalidate the immutable binding.
        assert (after.disposition, after.obligation) == ("route", "execution_prep")
        return {"before": route_tuple(before), "after_changed_bytes": route_tuple(after)}
    finally:
        temp.cleanup()


def research_masks_user_stop():
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        helper.install_state_record(
            project,
            "brainstorm",
            "brainstorm",
            "BRAINSTORM.toml",
            (
                'workstream_id = "sample-workstream"\n'
                'scope_id = "scope-stop"\n'
                'revision = 1\n'
                'state = "active"\n'
                'challenge_audit = "pending"\n'
                'explicit_user_stop = true\n'
                'promotion_state = "pending"\n'
                'promotion_subject = ""\n'
            ),
        )
        helper.install_state_record(
            project,
            "research",
            "research",
            "RESEARCH.toml",
            (
                'state = "active"\n'
                'workstream_id = "sample-workstream"\n'
                'origin_role = "brainstorming"\n'
                'origin_subject = "scope-stop@1"\n'
                'return_target = "brainstorming"\n'
                'return_reconciliation = "pending"\n'
                'return_result = ""\n'
                'finding = ""\n'
                'limitations = ""\n'
                'conflicts = ""\n'
                '[[sources]]\n'
                'class = "official_upstream"\n'
                'status = "pending"\n'
                'weight = "primary"\n'
                '[[sources]]\n'
                'class = "project_runtime"\n'
                'status = "pending"\n'
                'weight = "direct"\n'
                '[[sources]]\n'
                'class = "tracker_discussion"\n'
                'status = "pending"\n'
                'weight = "supporting"\n'
                '[[sources]]\n'
                'class = "practitioner_community"\n'
                'status = "pending"\n'
                'weight = "supporting"\n'
            ),
        )

        routed = select_route(project, [MANIFEST], package_root=ROOT)
        # Defect: durable explicit user stop is shadowed by the earlier Research return.
        assert (routed.disposition, routed.obligation) == ("route", "research")
        return {"route": route_tuple(routed)}
    finally:
        temp.cleanup()


def failed_result_is_accepted():
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        result_path = helper.install_reviewable_result(project, "none")
        result_file = project / result_path
        result_file.write_text(
            result_file.read_text(encoding="utf-8").replace(
                "Tests/readback summary: GREEN",
                "Tests/readback summary: FAILED",
            ),
            encoding="utf-8",
        )
        evidence = (
            project
            / "implementation/workstreams/sample-workstream/evidence/M01-T04.md"
        )
        evidence.unlink()

        routed = select_route(project, [MANIFEST], package_root=ROOT)
        # Defect: failed summary + absent named evidence still counts as a valid result.
        assert (routed.disposition, routed.obligation) == (
            "route",
            "result_reconciliation",
        )
        return {
            "route": route_tuple(routed),
            "evidence_exists": evidence.exists(),
            "tests_summary_in_file": "FAILED",
        }
    finally:
        temp.cleanup()


def wrong_plan_review_acceptance():
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        helper.install_green_definition(project)
        helper.install_state_record(
            project,
            "planning",
            "planning",
            "PLANNING.toml",
            helper.planning_content(state="frozen", premium_b="satisfied"),
        )
        wrong_acceptance = "requirements/NOT_CURRENT.md"
        review = helper.plan_review_content("green").replace(
            'path = "requirements/REQUIREMENTS.md"',
            f'path = "{wrong_acceptance}"',
        )
        helper.install_state_record(
            project,
            "plan_review",
            "plan_review",
            "PLAN_REVIEW.toml",
            review,
        )

        assert not (project / wrong_acceptance).exists()
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        # Defect: GREEN is accepted despite a wrong/nonexistent acceptance surface.
        assert (routed.disposition, routed.obligation) == ("route", "planning")
        return {
            "route": route_tuple(routed),
            "wrong_acceptance": wrong_acceptance,
            "wrong_acceptance_exists": False,
        }
    finally:
        temp.cleanup()


def main():
    results = {
        "F1_stale_dependency_bytes": stale_dependency_bytes(),
        "F2_research_masks_user_stop": research_masks_user_stop(),
        "F3_failed_result_is_accepted": failed_result_is_accepted(),
        "F4_wrong_plan_review_acceptance": wrong_plan_review_acceptance(),
    }
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
