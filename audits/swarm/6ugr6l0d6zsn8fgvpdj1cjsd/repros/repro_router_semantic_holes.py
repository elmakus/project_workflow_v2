#!/usr/bin/env python3
"""Non-mutating adversarial reproductions for audit 6ugr6l0d6zsn8fgvpdj1cjsd.

Run from the repository root at subject commit
4fb4bfb7d7b1481d6f347c182fc96a5a1135e045.

The script only copies the repository's disposable router fixture to temporary
directories. It does not modify product code or canonical workflow state.
"""

from __future__ import annotations

import tomllib

from tests.test_router import (
    BOARD,
    CARD,
    FIXTURE,
    MANIFEST,
    ROOT,
    RouterTests,
)
from tools.router import select_route
from tools.state_contract import (
    ValidationError,
    parse_task_card,
    validate_brainstorm,
    validate_definition,
    validate_research,
)


def semantic(route):
    return route.disposition, route.obligation, route.subject


def f1_same_path_dependency_mutation() -> None:
    case = RouterTests()
    temp, project = case.copy_fixture()
    try:
        dep_path = "implementation/workstreams/sample-workstream/results/M01-T03.md"
        commit = "a" * 40
        blob = "b" * 40
        exact = f"{dep_path}@{commit}:{blob}"
        case.install_done_predecessor(project, path=dep_path, commit=commit, blob=blob)
        case.make_ready_card(project, dependencies=exact)

        before = select_route(project, [MANIFEST], package_root=ROOT)
        assert semantic(before)[:2] == ("route", "execution_prep")

        # Mutate the exact path without changing the board/Card's declared
        # commit+blob labels. A real immutable-identity check must reject this.
        (project / dep_path).write_text("# changed bytes at the same path\n")
        after = select_route(project, [MANIFEST], package_root=ROOT)

        print("F1 dependency:", semantic(after))
        assert semantic(after)[:2] == ("route", "execution_prep"), semantic(after)
    finally:
        temp.cleanup()


def f1_same_path_reviewed_result_mutation() -> None:
    case = RouterTests()
    temp, project = case.copy_fixture()
    try:
        result_path = case.install_reviewable_result(project, "required")
        case.add_review_attempt(project, "green")

        before = select_route(project, [MANIFEST], package_root=ROOT)
        assert semantic(before)[:2] == ("route", "post_review_finalization")

        result_file = project / result_path
        result_file.write_text(
            result_file.read_text().replace(
                "Tests/readback summary: GREEN",
                "Tests/readback summary: MUTATED AFTER GREEN REVIEW",
            )
        )
        after = select_route(project, [MANIFEST], package_root=ROOT)

        print("F1 review:", semantic(after))
        assert semantic(after)[:2] == ("route", "post_review_finalization"), semantic(after)
    finally:
        temp.cleanup()


def _active_research(workstream_id: str, origin_role: str, origin_subject: str, return_target: str) -> str:
    return (
        'state = "active"\n'
        f'workstream_id = "{workstream_id}"\n'
        f'origin_role = "{origin_role}"\n'
        f'origin_subject = "{origin_subject}"\n'
        f'return_target = "{return_target}"\n'
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


def f2_research_bypasses_explicit_user_stop() -> None:
    case = RouterTests()
    temp, project = case.copy_fixture()
    try:
        brainstorm = (
            'workstream_id = "sample-workstream"\n'
            'scope_id = "scope-stop"\n'
            'revision = 1\n'
            'state = "active"\n'
            'challenge_audit = "pending"\n'
            'explicit_user_stop = true\n'
            'promotion_state = "pending"\n'
            'promotion_subject = ""\n'
        )
        research = _active_research(
            "sample-workstream", "brainstorming", "scope-stop@1", "brainstorming"
        )
        validate_brainstorm(tomllib.loads(brainstorm), "sample-workstream")
        validate_research(tomllib.loads(research), "sample-workstream")

        case.install_state_record(
            project, "brainstorm", "brainstorm", "BRAINSTORM.toml", brainstorm
        )
        case.install_state_record(
            project, "research", "research", "RESEARCH.toml", research
        )

        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F2 explicit stop:", semantic(routed))
        assert semantic(routed)[:2] == ("route", "research"), semantic(routed)
    finally:
        temp.cleanup()


def f2_research_bypasses_premium_a() -> None:
    case = RouterTests()
    temp, project = case.copy_fixture()
    try:
        brainstorm = (
            'workstream_id = "sample-workstream"\n'
            'scope_id = "scope-premium"\n'
            'revision = 1\n'
            'state = "promoted"\n'
            'challenge_audit = "green"\n'
            'explicit_user_stop = false\n'
            'promotion_state = "authorized"\n'
            'promotion_subject = "scope-premium@1"\n'
        )
        definition = (
            'workstream_id = "sample-workstream"\n'
            'source_scope_subject = "scope-premium@1"\n'
            'revision = "R1"\n'
            'state = "green"\n'
            'completeness_audit = "green"\n'
            'premium_a = "due"\n'
            'decisions = [{ class = "authority", path = "decisions/ADR-001.md" }]\n'
            '[requirements]\nclass = "authority"\npath = "requirements/REQUIREMENTS.md"\n'
        )
        research = _active_research(
            "sample-workstream", "definition", "R1", "definition"
        )
        validate_brainstorm(tomllib.loads(brainstorm), "sample-workstream")
        validate_definition(tomllib.loads(definition), "sample-workstream")
        validate_research(tomllib.loads(research), "sample-workstream")

        case.install_state_record(
            project, "brainstorm", "brainstorm", "BRAINSTORM.toml", brainstorm
        )
        case.install_state_record(
            project, "definition", "definition", "DEFINITION.toml", definition
        )
        case.install_state_record(
            project, "research", "research", "RESEARCH.toml", research
        )

        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F2 premium A:", semantic(routed))
        assert semantic(routed)[:2] == ("route", "research"), semantic(routed)
    finally:
        temp.cleanup()


def f3_ready_result_is_ignored() -> None:
    case = RouterTests()
    temp, project = case.copy_fixture()
    try:
        case.install_reviewable_result(project, "none")
        board = project / BOARD
        board.write_text(
            board.read_text().replace('status = "in_progress"', 'status = "ready"', 1)
        )

        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F3:", semantic(routed))
        assert semantic(routed)[:2] == ("route", "execution_prep"), semantic(routed)
    finally:
        temp.cleanup()


def f4_active_malformed_card_executes() -> None:
    routed = select_route(FIXTURE, [MANIFEST], package_root=ROOT)
    print("F4 route:", semantic(routed))
    assert semantic(routed)[:2] == ("route", "execution"), semantic(routed)

    text = (FIXTURE / CARD).read_text()
    try:
        parse_task_card(text, "M01-T04", "sample-workstream")
    except ValidationError as exc:
        print("F4 stable-card validator rejects the same Card:", exc)
    else:
        raise AssertionError("fixture Card unexpectedly satisfied the stable Task Card contract")


def main() -> None:
    f1_same_path_dependency_mutation()
    f1_same_path_reviewed_result_mutation()
    f2_research_bypasses_explicit_user_stop()
    f2_research_bypasses_premium_a()
    f3_ready_result_is_ignored()
    f4_active_malformed_card_executes()
    print("All four material defect classes reproduced.")


if __name__ == "__main__":
    main()
