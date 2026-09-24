#!/usr/bin/env python3
"""Non-mutating PWv2 swarm repros for exact checkout 4fb4bfb7...e045.

Run from the repository root at the audited commit. All mutations happen in
TemporaryDirectory copies of tests/fixtures/router/valid-project.
"""
from __future__ import annotations

import runpy
from pathlib import Path

ns = runpy.run_path("tests/test_router.py")
RouterTests = ns["RouterTests"]
MANIFEST = ns["MANIFEST"]
BOARD = ns["BOARD"]
CARD = ns["CARD"]
select_route = ns["select_route"]

h = RouterTests(methodName="runTest")


def route(project: Path):
    return select_route(project, [MANIFEST], package_root=Path.cwd())


def show(name: str, r) -> None:
    print(f"{name}: {r.disposition}/{r.obligation} subject={r.subject!r}")


temp, project = h.copy_fixture()
try:
    h.install_reviewable_result(project, "required")
    board = project / BOARD
    board.write_text(board.read_text().replace('status = "in_progress"', 'status = "done"', 1))
    r = route(project)
    show("F1 done+required-review-with-no-attempt", r)
    assert (r.disposition, r.obligation) == ("route", "close")
finally:
    temp.cleanup()


temp, project = h.copy_fixture()
try:
    result_path = h.install_reviewable_result(project, "required")
    h.add_review_attempt(project, "green")
    before = route(project)
    result_file = project / result_path
    result_file.write_text(result_file.read_text().replace(
        "- Tests/readback summary: GREEN",
        "- Tests/readback summary: GREEN; CURRENT BYTES CHANGED AFTER REVIEW",
    ))
    after = route(project)
    show("F2a before-result-byte-drift", before)
    show("F2a after-result-byte-drift", after)
    assert before.obligation == "post_review_finalization"
    assert after.obligation == "post_review_finalization"
finally:
    temp.cleanup()


temp, project = h.copy_fixture()
try:
    dep_path = "implementation/workstreams/sample-workstream/results/M01-T03.md"
    commit, blob = "a" * 40, "b" * 40
    dep = f"{dep_path}@{commit}:{blob}"
    h.install_done_predecessor(project, path=dep_path, commit=commit, blob=blob)
    h.make_ready_card(project, dependencies=dep)
    before = route(project)
    (project / dep_path).write_text("# DIFFERENT CURRENT BYTES\n")
    after = route(project)
    show("F2b before-dependency-byte-drift", before)
    show("F2b after-dependency-byte-drift", after)
    assert before.obligation == "execution_prep"
    assert after.obligation == "execution_prep"
finally:
    temp.cleanup()


temp, project = h.copy_fixture()
try:
    h.make_ready_card(project)
    h.install_reviewable_result(project, "none")
    r = route(project)
    show("F3 ready+durable-result", r)
    assert (r.disposition, r.obligation) == ("route", "execution_prep")
finally:
    temp.cleanup()


temp, project = h.copy_fixture()
try:
    h.install_reviewable_result(project, "required")
    h.add_review_attempt(project, "green")
    before = route(project)
    card = project / CARD
    card.write_text(card.read_text().replace(
        "- Acceptance: route only after current launch inputs are valid",
        "- Acceptance: materially changed acceptance after the recorded GREEN review",
    ))
    after = route(project)
    show("F4 before-acceptance-drift", before)
    show("F4 after-acceptance-drift", after)
    assert before.obligation == "post_review_finalization"
    assert after.obligation == "post_review_finalization"
finally:
    temp.cleanup()


temp, project = h.copy_fixture()
try:
    result_path = h.install_reviewable_result(project, "none")
    (project / result_path).write_text(
        "# Card Result\n"
        "- Card ID: M01-T04\n"
        "- Implementation subject: definitely-not-an-immutable-git-subject\n"
        "- Evidence refs: implementation/workstreams/sample-workstream/evidence/DOES_NOT_EXIST.md\n"
        "- Tests/readback summary: GREEN\n"
    )
    r = route(project)
    show("F5 malformed-subject+missing-evidence", r)
    assert (r.disposition, r.obligation) == ("route", "result_reconciliation")
finally:
    temp.cleanup()
