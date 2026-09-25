#!/usr/bin/env python3
"""Non-mutating repros for PWv2 adversarial audit v59lpyq5jxrsgegtivvtk470.

Run from repository root at subject commit:
    python3 audits/swarm/v59lpyq5jxrsgegtivvtk470/repros/repro_adversarial.py

Each repro asserts the observed fail-open behavior at the audited subject.
A corrected implementation should make one or more assertions fail.
"""

from pathlib import Path

from tests.test_router import MANIFEST, ROOT, RouterTests
from tools.execution_contract import parse_card_result
from tools.router import select_route


HELPER = RouterTests()


def routed(project: Path):
    return select_route(project, [MANIFEST], package_root=ROOT)


def repro_f1_same_path_changed_dependency_still_launches() -> None:
    temp, project = HELPER.copy_fixture()
    try:
        dep = "implementation/workstreams/sample-workstream/results/M01-T03.md"
        commit = "a" * 40
        blob = "b" * 40
        HELPER.install_done_predecessor(project, path=dep, commit=commit, blob=blob)
        HELPER.make_ready_card(project, dependencies=f"{dep}@{commit}:{blob}")
        assert (routed(project).disposition, routed(project).obligation) == ("route", "execution_prep")

        # Change the dependency bytes only; keep the board/Card commit+blob identity unchanged.
        (project / dep).write_text("# materially changed predecessor result\n", encoding="utf-8")
        actual = routed(project)
        assert (actual.disposition, actual.obligation) == ("route", "execution_prep"), actual
        print("F1 reproduced: same-path changed dependency still launches")
    finally:
        temp.cleanup()


def repro_f2_stale_plan_survives_definition_change() -> None:
    temp, project = HELPER.copy_fixture()
    try:
        HELPER.install_approved_plan(project)
        # Materially change current Definition identity/authority while leaving Planning/Plan Review stale.
        definition = project / "implementation/workstreams/sample-workstream/DEFINITION.toml"
        text = definition.read_text(encoding="utf-8")
        text = text.replace('revision = "R1"', 'revision = "R2"')
        text = text.replace(
            'path = "requirements/REQUIREMENTS.md"',
            'path = "requirements/REQUIREMENTS-R2.md"',
        )
        definition.write_text(text, encoding="utf-8")
        req = project / "requirements/REQUIREMENTS-R2.md"
        req.parent.mkdir(parents=True, exist_ok=True)
        req.write_text("# changed accepted requirements\n", encoding="utf-8")

        actual = routed(project)
        assert (actual.disposition, actual.obligation) == ("route", "execution"), actual
        print("F2 reproduced: stale approved plan remains executable after Definition change")
    finally:
        temp.cleanup()


def repro_f3_non_exact_implementation_subject_is_accepted() -> None:
    text = (
        "# Card Result\n"
        "- Card ID: M03-T02\n"
        "- Implementation subject: banana\n"
        "- Evidence refs: implementation/workstreams/sample-workstream/evidence/build.md\n"
        "- Tests/readback summary: GREEN\n"
    )
    parsed = parse_card_result(text, "M03-T02", "sample-workstream")
    assert parsed["implementation_subject"] == "banana"
    print("F3 reproduced: arbitrary non-exact implementation subject is accepted")


def repro_f4_missing_evidence_does_not_fail_closed() -> None:
    temp, project = HELPER.copy_fixture()
    try:
        HELPER.install_reviewable_result(project, "required")
        evidence = project / "implementation/workstreams/sample-workstream/evidence/M01-T04.md"
        evidence.unlink()
        actual = routed(project)
        assert (actual.disposition, actual.obligation) == ("route", "review_freeze"), actual
        print("F4a reproduced: missing result evidence still yields a reviewable durable result")
    finally:
        temp.cleanup()

    temp, project = HELPER.copy_fixture()
    try:
        HELPER.install_reviewable_result(project, "required")
        HELPER.add_review_attempt(project, "green")
        review_evidence = project / "implementation/workstreams/sample-workstream/evidence/review-R01.md"
        review_evidence.unlink()
        actual = routed(project)
        assert (actual.disposition, actual.obligation) == ("route", "post_review_finalization"), actual
        print("F4b reproduced: missing GREEN review evidence still authorizes finalization")
    finally:
        temp.cleanup()


def repro_f5_plan_review_acceptance_is_not_bound_to_definition() -> None:
    temp, project = HELPER.copy_fixture()
    try:
        HELPER.install_approved_plan(project)
        unrelated = project / "decisions/UNRELATED.md"
        unrelated.parent.mkdir(parents=True, exist_ok=True)
        unrelated.write_text("# unrelated authority\n", encoding="utf-8")

        review = project / "implementation/workstreams/sample-workstream/PLAN_REVIEW.toml"
        text = review.read_text(encoding="utf-8").replace(
            'path = "requirements/REQUIREMENTS.md"',
            'path = "decisions/UNRELATED.md"',
        )
        review.write_text(text, encoding="utf-8")

        actual = routed(project)
        assert (actual.disposition, actual.obligation) == ("route", "execution"), actual
        print("F5 reproduced: unrelated Plan Review acceptance can unlock execution")
    finally:
        temp.cleanup()


if __name__ == "__main__":
    repro_f1_same_path_changed_dependency_still_launches()
    repro_f2_stale_plan_survives_definition_change()
    repro_f3_non_exact_implementation_subject_is_accepted()
    repro_f4_missing_evidence_does_not_fail_closed()
    repro_f5_plan_review_acceptance_is_not_bound_to_definition()
