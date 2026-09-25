#!/usr/bin/env python3
"""Non-mutating reproductions for q7m2v9k4x1c8n5r0t6b3p2hz.

Run from a checkout of subject commit 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045.
The script copies the existing router fixture into temporary directories only.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from tools.router import select_route

ROOT = Path(__file__).resolve().parents[4]
FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"
WS = "implementation/workstreams/sample-workstream"


def copied_fixture():
    temp = tempfile.TemporaryDirectory()
    project = Path(temp.name) / "project"
    shutil.copytree(FIXTURE, project)
    return temp, project


def route(project: Path):
    return select_route(project, [MANIFEST], package_root=ROOT)


def stable_card(review_requirement: str) -> str:
    return (
        "# Fixture Card\n"
        "- Card ID: M01-T04\n"
        "- Included scope: exact audit reproduction\n"
        "- Excluded scope: everything else\n"
        "- Authority refs: requirements/PROJECT_WORKFLOW_V2.md\n"
        "- Dependencies: none\n"
        "- Acceptance: preserve exact workflow invariants\n"
        "- Required tests/readback: selector result\n"
        f"- Review requirement: {review_requirement}\n"
        "- Technical contract: none\n"
    )


def valid_result(summary: str) -> str:
    return (
        "# Card Result\n"
        "- Card ID: M01-T04\n"
        f"- Implementation subject: {summary}\n"
        f"- Evidence refs: {WS}/evidence/M01-T04.md\n"
        f"- Tests/readback summary: {summary}\n"
    )


def append_state_locator(project: Path, key: str, klass: str, filename: str, content: str) -> None:
    manifest = project / MANIFEST
    manifest.write_text(
        manifest.read_text()
        + f'\n[{key}]\nclass = "{klass}"\npath = "{WS}/{filename}"\n',
        encoding="utf-8",
    )
    (project / WS / filename).write_text(content, encoding="utf-8")


def promoted_brainstorm(*, state: str = "promoted", explicit_stop: bool = False) -> str:
    return (
        'workstream_id = "sample-workstream"\n'
        'scope_id = "scope-a"\n'
        'revision = 1\n'
        f'state = "{state}"\n'
        'challenge_audit = "green"\n'
        f'explicit_user_stop = {"true" if explicit_stop else "false"}\n'
        'promotion_state = "authorized"\n'
        'promotion_subject = "scope-a@1"\n'
    )


def definition(*, revision: str, requirements: str, state: str = "green") -> str:
    active = state == "active"
    return (
        'workstream_id = "sample-workstream"\n'
        'source_scope_subject = "scope-a@1"\n'
        f'revision = "{revision}"\n'
        f'state = "{state}"\n'
        f'completeness_audit = "{"pending" if active else "green"}"\n'
        f'premium_a = "{"not_due" if active else "satisfied"}"\n'
        + ('decisions = []\n' if active else 'decisions = [{ class = "authority", path = "decisions/ADR-001.md" }]\n')
        + '[requirements]\n'
        + 'class = "authority"\n'
        + f'path = "{requirements}"\n'
    )


def planning(*, state: str, premium_b: str, premium_c: str) -> str:
    subject = f"owner/router-fixture@{'a'*40}:planning/MASTER_PLAN.md@{'b'*40}"
    return (
        'workstream_id = "sample-workstream"\n'
        'cycle = 1\n'
        'entry_subject = "definition:R1|planning-cycle:1"\n'
        'revision = "P1"\n'
        f'state = "{state}"\n'
        'planner_audit = "green"\n'
        'plan_path = "planning/MASTER_PLAN.md"\n'
        'review_mode = "independent"\n'
        'review_exemption_basis = ""\n'
        'review_exemption_base_subject = ""\n'
        'premium_a = "satisfied"\n'
        'premium_a_subject = "definition:R1|planning-cycle:1"\n'
        f'premium_b = "{premium_b}"\n'
        f'premium_b_subject = "{subject}"\n'
        f'premium_c = "{premium_c}"\n'
        f'premium_c_subject = "{subject if premium_c != "not_due" else ""}"\n'
        '[subject]\n'
        'repository = "owner/router-fixture"\n'
        f'commit = "{"a"*40}"\n'
        'path = "planning/MASTER_PLAN.md"\n'
        f'blob = "{"b"*40}"\n'
    )


def plan_review(*, acceptance_path: str) -> str:
    return (
        'workstream_id = "sample-workstream"\n'
        'plan_revision = "P1"\n'
        'planning_cycle = 1\n'
        'attempt = "R01"\n'
        'verdict = "green"\n'
        'evidence_path = "evidence/plan-review-R01.md"\n'
        '[subject]\n'
        'class = "git_blob"\n'
        'repository = "owner/router-fixture"\n'
        f'commit = "{"a"*40}"\n'
        'path = "planning/MASTER_PLAN.md"\n'
        f'blob = "{"b"*40}"\n'
        '[acceptance]\n'
        'class = "authority"\n'
        f'path = "{acceptance_path}"\n'
        '[independence]\n'
        'materially_produced_or_repaired_subject = false\n'
        'basis = "Fresh independent review context."\n'
    )


def repro_f1_done_bypasses_review_and_missing_result() -> None:
    temp, project = copied_fixture()
    try:
        (project / CARD).write_text(stable_card("required"), encoding="utf-8")
        board = project / BOARD
        board.write_text(
            board.read_text(encoding="utf-8")
            .replace('status = "in_progress"', 'status = "done"', 1)
            + '\n[cards.result]\n'
            + 'class = "result"\n'
            + f'path = "{WS}/results/M01-T04.md"\n'
            + f'commit = "{"a"*40}"\n'
            + f'blob = "{"b"*40}"\n',
            encoding="utf-8",
        )
        # Deliberately do not create the result file and do not add any review attempt.
        actual = route(project)
        print("F1", actual.disposition, actual.obligation, actual.reason)
        assert (actual.disposition, actual.obligation) == ("route", "close")
    finally:
        temp.cleanup()


def repro_f2_mutated_result_keeps_green_review() -> None:
    temp, project = copied_fixture()
    try:
        (project / CARD).write_text(stable_card("required"), encoding="utf-8")
        review_path = f"{WS}/reviews/M01-T04-R01.toml"
        result_path = f"{WS}/results/M01-T04.md"
        board = project / BOARD
        board.write_text(
            board.read_text(encoding="utf-8").replace(
                'status = "in_progress"\n',
                'status = "in_progress"\n'
                f'review_attempts = [{{ class = "review_attempt", path = "{review_path}" }}]\n',
                1,
            )
            + '\n[cards.result]\n'
            + 'class = "result"\n'
            + f'path = "{result_path}"\n'
            + f'commit = "{"a"*40}"\n'
            + f'blob = "{"b"*40}"\n',
            encoding="utf-8",
        )
        (project / WS / "results").mkdir(parents=True, exist_ok=True)
        (project / result_path).write_text(valid_result("subject-A"), encoding="utf-8")
        (project / WS / "evidence").mkdir(parents=True, exist_ok=True)
        (project / WS / "evidence/M01-T04.md").write_text("# evidence\n", encoding="utf-8")
        (project / WS / "reviews").mkdir(parents=True, exist_ok=True)
        (project / review_path).write_text(
            'workstream_id = "sample-workstream"\n'
            'card_id = "M01-T04"\n'
            'attempt = "R01"\n'
            'verdict = "green"\n'
            f'evidence_path = "{WS}/evidence/review-R01.md"\n'
            '[subject]\n'
            'class = "git_blob"\n'
            'repository = "owner/router-fixture"\n'
            f'commit = "{"a"*40}"\n'
            f'path = "{result_path}"\n'
            f'blob = "{"b"*40}"\n'
            '[acceptance]\n'
            'class = "task_card"\n'
            f'path = "{CARD}"\n'
            '[independence]\n'
            'materially_produced_or_repaired_subject = false\n'
            'basis = "Fresh independent review context."\n',
            encoding="utf-8",
        )
        before = route(project)
        assert (before.disposition, before.obligation) == ("route", "post_review_finalization")

        # Mutate the actual result content while leaving commit/blob metadata and GREEN review untouched.
        (project / result_path).write_text(valid_result("subject-B-MATERIALLY-DIFFERENT"), encoding="utf-8")
        after = route(project)
        print("F2", after.disposition, after.obligation, after.reason)
        assert (after.disposition, after.obligation) == ("route", "post_review_finalization")
    finally:
        temp.cleanup()


def repro_f3_stale_plan_survives_definition_change() -> None:
    temp, project = copied_fixture()
    try:
        append_state_locator(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", promoted_brainstorm())
        append_state_locator(project, "definition", "definition", "DEFINITION.toml",
                             definition(revision="R1", requirements="requirements/OLD.md"))
        append_state_locator(project, "planning", "planning", "PLANNING.toml",
                             planning(state="approved", premium_b="satisfied", premium_c="satisfied"))
        append_state_locator(project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                             plan_review(acceptance_path="requirements/OLD.md"))
        before = route(project)
        assert (before.disposition, before.obligation) == ("route", "execution")

        # Change accepted Definition revision and authority, but retain old R1 planning/review/gates.
        (project / WS / "DEFINITION.toml").write_text(
            definition(revision="R2", requirements="requirements/NEW.md"),
            encoding="utf-8",
        )
        after = route(project)
        print("F3", after.disposition, after.obligation, after.reason)
        assert (after.disposition, after.obligation) == ("route", "execution")
    finally:
        temp.cleanup()


def repro_f4_nonpromoted_explicit_stop_enters_definition() -> None:
    temp, project = copied_fixture()
    try:
        append_state_locator(
            project, "brainstorm", "brainstorm", "BRAINSTORM.toml",
            promoted_brainstorm(state="active", explicit_stop=True),
        )
        append_state_locator(
            project, "definition", "definition", "DEFINITION.toml",
            definition(revision="R1", requirements="requirements/PROJECT_WORKFLOW_V2.md", state="active"),
        )
        actual = route(project)
        print("F4", actual.disposition, actual.obligation, actual.reason)
        assert (actual.disposition, actual.obligation) == ("route", "definition")
    finally:
        temp.cleanup()


def repro_f5_plan_review_accepts_unrelated_authority() -> None:
    temp, project = copied_fixture()
    try:
        append_state_locator(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", promoted_brainstorm())
        append_state_locator(project, "definition", "definition", "DEFINITION.toml",
                             definition(revision="R1", requirements="requirements/ACCEPTED.md"))
        append_state_locator(project, "planning", "planning", "PLANNING.toml",
                             planning(state="frozen", premium_b="satisfied", premium_c="not_due"))
        append_state_locator(project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                             plan_review(acceptance_path="workflow/ROUTER.md"))
        actual = route(project)
        print("F5", actual.disposition, actual.obligation, actual.reason)
        assert (actual.disposition, actual.obligation) == ("route", "planning")
    finally:
        temp.cleanup()


if __name__ == "__main__":
    repro_f1_done_bypasses_review_and_missing_result()
    repro_f2_mutated_result_keeps_green_review()
    repro_f3_stale_plan_survives_definition_change()
    repro_f4_nonpromoted_explicit_stop_enters_definition()
    repro_f5_plan_review_accepts_unrelated_authority()
    print("All five adverse behaviors reproduced if all assertions pass.")
