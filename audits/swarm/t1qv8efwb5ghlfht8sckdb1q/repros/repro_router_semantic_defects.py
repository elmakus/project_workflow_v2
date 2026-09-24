#!/usr/bin/env python3
"""Non-mutating PWv2 adversarial reproductions for audit t1qv8efwb5ghlfht8sckdb1q.

Run from the repository root at subject commit:
    python audits/swarm/t1qv8efwb5ghlfht8sckdb1q/repros/repro_router_semantic_defects.py
"""

from tests.test_router import RouterTests, MANIFEST, BOARD, CARD
from tools.router import select_route


def route(project):
    r = select_route(project, [MANIFEST])
    return r.disposition, r.obligation


def f1_unresolved_exact_dependency():
    t = RouterTests()
    temp, project = t.copy_fixture()
    try:
        result_path = "implementation/workstreams/sample-workstream/results/M01-T03.md"
        commit = "c" * 40
        blob = "d" * 40
        dep = f"{result_path}@{commit}:{blob}"
        t.install_done_predecessor(project, path=result_path, commit=commit, blob=blob)
        t.make_ready_card(project, dependencies=dep)
        got = route(project)
        assert got == ("route", "execution_prep"), got
        return got
    finally:
        temp.cleanup()


def f2_explicit_stop_bypassed_by_definition():
    t = RouterTests()
    temp, project = t.copy_fixture()
    try:
        t.install_green_definition(project)
        p = project / "implementation/workstreams/sample-workstream/BRAINSTORM.toml"
        p.write_text(p.read_text().replace("explicit_user_stop = false", "explicit_user_stop = true"))
        got = route(project)
        assert got == ("route", "planning"), got
        return got
    finally:
        temp.cleanup()


def f3_done_bypasses_required_review():
    t = RouterTests()
    temp, project = t.copy_fixture()
    try:
        t.install_reviewable_result(project, "required")
        p = project / BOARD
        p.write_text(p.read_text().replace('status = "in_progress"', 'status = "done"', 1))
        got = route(project)
        assert got == ("route", "close"), got
        return got
    finally:
        temp.cleanup()


def f4_stale_plan_survives_definition_revision_change():
    t = RouterTests()
    temp, project = t.copy_fixture()
    try:
        t.install_green_definition(project)
        t.install_state_record(
            project, "planning", "planning", "PLANNING.toml",
            t.planning_content(state="approved", premium_b="satisfied", premium_c="satisfied"),
        )
        t.install_state_record(
            project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
            t.plan_review_content("green"),
        )
        p = project / "implementation/workstreams/sample-workstream/DEFINITION.toml"
        p.write_text(p.read_text().replace('revision = "R1"', 'revision = "R2"', 1))
        got = route(project)
        assert got == ("route", "execution"), got
        return got
    finally:
        temp.cleanup()


def f5_green_review_survives_acceptance_mutation():
    t = RouterTests()
    temp, project = t.copy_fixture()
    try:
        t.install_reviewable_result(project, "required")
        t.add_review_attempt(project, "green")
        before = route(project)
        assert before == ("route", "post_review_finalization"), before

        p = project / CARD
        p.write_text(
            p.read_text().replace(
                "- Acceptance: route only after current launch inputs are valid",
                "- Acceptance: materially different terminal behavior is now required",
                1,
            )
        )
        after = route(project)
        assert after == ("route", "post_review_finalization"), after
        return before, after
    finally:
        temp.cleanup()


def main():
    cases = [
        ("F1 unresolved exact dependency", f1_unresolved_exact_dependency),
        ("F2 explicit stop bypass", f2_explicit_stop_bypassed_by_definition),
        ("F3 DONE required-review bypass", f3_done_bypasses_required_review),
        ("F4 stale plan after Definition revision", f4_stale_plan_survives_definition_revision_change),
        ("F5 GREEN review after acceptance mutation", f5_green_review_survives_acceptance_mutation),
    ]
    for name, fn in cases:
        print(f"{name}: {fn()}")


if __name__ == "__main__":
    main()
