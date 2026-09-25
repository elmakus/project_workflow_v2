#!/usr/bin/env python3
"""Non-mutating adversarial repros for PWv2 subject 4fb4bfb7... Run from repository root."""

from pathlib import Path
from tools.router import select_route
from tests.test_router import RouterTests, MANIFEST, BOARD

H = RouterTests(methodName="runTest")

def show(name, routed):
    print(name, "=>", routed.disposition, routed.obligation, routed.subject, "|", routed.reason)

# F1: required review bypassed by status=done.
tmp, p = H.copy_fixture()
try:
    H.install_reviewable_result(p, "required")
    board = p / BOARD
    board.write_text(board.read_text().replace('status = "in_progress"', 'status = "done"', 1))
    show("F1 required-review result marked done", select_route(p, [MANIFEST], package_root=Path.cwd()))
finally:
    tmp.cleanup()

# F2: same-path dependency content changes while declared identities remain unchanged.
tmp, p = H.copy_fixture()
try:
    dep = "implementation/workstreams/sample-workstream/results/M01-T03.md"
    commit, blob = "a" * 40, "b" * 40
    H.install_done_predecessor(p, path=dep, commit=commit, blob=blob)
    H.make_ready_card(p, dependencies=f"{dep}@{commit}:{blob}")
    show("F2 before same-path drift", select_route(p, [MANIFEST], package_root=Path.cwd()))
    (p / dep).write_text("# changed content with unchanged declared commit/blob\n")
    show("F2 after same-path drift", select_route(p, [MANIFEST], package_root=Path.cwd()))
finally:
    tmp.cleanup()

# F3: GREEN review evidence disappears.
tmp, p = H.copy_fixture()
try:
    H.install_reviewable_result(p, "required")
    H.add_review_attempt(p, "green")
    ev = p / "implementation/workstreams/sample-workstream/evidence/review-R01.md"
    ev.unlink()
    show("F3 green review with missing evidence", select_route(p, [MANIFEST], package_root=Path.cwd()))
finally:
    tmp.cleanup()

# F4: Definition revision changes but approved Planning remains R1-bound.
tmp, p = H.copy_fixture()
try:
    H.install_approved_plan(p)
    d = p / "implementation/workstreams/sample-workstream/DEFINITION.toml"
    d.write_text(d.read_text().replace('revision = "R1"', 'revision = "R2"', 1))
    show("F4 stale approved plan after Definition R2", select_route(p, [MANIFEST], package_root=Path.cwd()))
finally:
    tmp.cleanup()

# F5: explicit user stop masked by downstream Definition.
tmp, p = H.copy_fixture()
try:
    H.install_green_definition(p)
    b = p / "implementation/workstreams/sample-workstream/BRAINSTORM.toml"
    b.write_text(b.read_text().replace("explicit_user_stop = false", "explicit_user_stop = true", 1))
    show("F5 explicit stop with GREEN Definition", select_route(p, [MANIFEST], package_root=Path.cwd()))
finally:
    tmp.cleanup()

# F6: satisfied JIT trigger is ignored by all-DONE close routing.
tmp, p = H.copy_fixture()
try:
    H.install_reviewable_result(p, "none")
    board = p / BOARD
    text = board.read_text().replace('status = "in_progress"', 'status = "done"', 1)
    text += (
        '\n[[jit_triggers]]\n'
        'id = "after-M01-T04"\n'
        'after_card = "M01-T04"\n'
        'state = "satisfied"\n'
        'condition = "Materialize downstream Card from predecessor result."\n'
    )
    board.write_text(text)
    show("F6 satisfied JIT with all cards done", select_route(p, [MANIFEST], package_root=Path.cwd()))
finally:
    tmp.cleanup()
