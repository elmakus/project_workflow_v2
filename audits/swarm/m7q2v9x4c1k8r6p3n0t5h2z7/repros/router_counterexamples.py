#!/usr/bin/env python3
"""Non-mutating PWv2 adversarial repros for commit 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045."""
from __future__ import annotations
import shutil, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.router import select_route

FIXTURE = ROOT / "tests/fixtures/router/valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"
WS = "implementation/workstreams/sample-workstream"
A40, B40 = "a" * 40, "b" * 40

def copy_fixture():
    td = tempfile.TemporaryDirectory()
    p = Path(td.name) / "project"
    shutil.copytree(FIXTURE, p)
    return td, p

def add_locator(p, key, klass, filename, body):
    m = p / MANIFEST
    m.write_text(m.read_text() + f'\n[{key}]\nclass = "{klass}"\npath = "{WS}/{filename}"\n')
    (p / WS / filename).write_text(body)

def valid_card(review="required"):
    return (
        "# Card\n- Card ID: M01-T04\n- Included scope: bounded\n- Excluded scope: none\n"
        "- Authority refs: requirements/REQUIREMENTS.md\n- Dependencies: none\n"
        "- Acceptance: observable\n- Required tests/readback: tests\n"
        f"- Review requirement: {review}\n- Technical contract: none\n"
    )

def install_result(p, status="in_progress", review="required"):
    (p / CARD).write_text(valid_card(review))
    (p / "requirements").mkdir(exist_ok=True)
    (p / "requirements/REQUIREMENTS.md").write_text("# authority\n")
    rp = f"{WS}/results/M01-T04.md"
    (p / WS / "results").mkdir(exist_ok=True)
    (p / WS / "evidence").mkdir(exist_ok=True)
    (p / WS / "evidence/result.md").write_text("# evidence\n")
    (p / rp).write_text(
        "# Result\n- Card ID: M01-T04\n"
        f"- Implementation subject: owner/router-fixture@{A40}\n"
        f"- Evidence refs: {WS}/evidence/result.md\n"
        "- Tests/readback summary: GREEN-v1\n"
    )
    b = p / BOARD
    text = b.read_text().replace('status = "in_progress"', f'status = "{status}"', 1)
    text += f'\n[cards.result]\nclass = "result"\npath = "{rp}"\ncommit = "{A40}"\nblob = "{B40}"\n'
    b.write_text(text)
    return rp

def add_green_review(p, evidence_exists=True):
    rr = f"{WS}/reviews/M01-T04-R01.toml"
    b = p / BOARD
    b.write_text(b.read_text().replace(
        'status = "in_progress"\n\n[cards.contract]',
        f'status = "in_progress"\nreview_attempts = [{{ class = "review_attempt", path = "{rr}" }}]\n\n[cards.contract]',
        1,
    ))
    ev = f"{WS}/evidence/review-R01.md"
    if evidence_exists:
        (p / ev).write_text("# review evidence\n")
    q = p / rr
    q.parent.mkdir(exist_ok=True)
    q.write_text(
        'workstream_id = "sample-workstream"\ncard_id = "M01-T04"\nattempt = "R01"\nverdict = "green"\n'
        f'evidence_path = "{ev}"\n'
        f'[subject]\nclass = "git_blob"\nrepository = "owner/router-fixture"\ncommit = "{A40}"\n'
        f'path = "{WS}/results/M01-T04.md"\nblob = "{B40}"\n'
        f'[acceptance]\nclass = "task_card"\npath = "{CARD}"\n'
        '[independence]\nmaterially_produced_or_repaired_subject = false\nbasis = "Fresh independent context."\n'
    )

def f1():
    td,p=copy_fixture()
    try:
        add_locator(p,"brainstorm","brainstorm","BRAINSTORM.toml",
            'workstream_id = "sample-workstream"\nscope_id = "scope"\nrevision = 1\nstate = "promoted"\n'
            'challenge_audit = "green"\nexplicit_user_stop = true\npromotion_state = "authorized"\npromotion_subject = "scope@1"\n')
        add_locator(p,"definition","definition","DEFINITION.toml",
            'workstream_id = "sample-workstream"\nsource_scope_subject = "scope@1"\nrevision = "R1"\nstate = "active"\n'
            'completeness_audit = "pending"\npremium_a = "not_due"\ndecisions = []\n'
            '[requirements]\nclass = "authority"\npath = "requirements/REQUIREMENTS.md"\n')
        r=select_route(p,[MANIFEST],package_root=ROOT)
        assert (r.disposition,r.obligation)==("route","definition"), r
        print("F1 reproduced:",r.disposition,r.obligation,"expected explicit_user_stop")
    finally: td.cleanup()

def f2():
    td,p=copy_fixture()
    try:
        b=p/BOARD
        b.write_text(b.read_text()+f'\n[research_obligation]\nclass = "research"\npath = "{WS}/RESEARCH.toml"\n')
        (p/WS/"RESEARCH.toml").write_text(
            'state = "complete"\nworkstream_id = "sample-workstream"\norigin_role = "execution_resolution"\n'
            'origin_subject = "M01-T04"\nreturn_target = "execution:M99-T99"\nreturn_reconciliation = "pending"\n'
            'return_result = ""\nfinding = "facts"\nlimitations = "none"\nconflicts = "none"\n'
            '[[sources]]\nclass = "official_upstream"\nstatus = "not_relevant"\nweight = "primary"\n'
            '[[sources]]\nclass = "project_runtime"\nstatus = "checked"\nweight = "direct"\n'
            '[[sources]]\nclass = "tracker_discussion"\nstatus = "not_relevant"\nweight = "supporting"\n'
            '[[sources]]\nclass = "practitioner_community"\nstatus = "not_relevant"\nweight = "supporting"\n')
        r=select_route(p,[MANIFEST],package_root=ROOT)
        assert (r.disposition,r.obligation,r.subject)==("route","execution","M99-T99"), r
        print("F2 reproduced:",r.disposition,r.obligation,r.subject)
    finally: td.cleanup()

def f3():
    td,p=copy_fixture()
    try:
        add_locator(p,"brainstorm","brainstorm","BRAINSTORM.toml",
            'workstream_id = "sample-workstream"\nscope_id = "scope"\nrevision = 1\nstate = "promoted"\nchallenge_audit = "green"\n'
            'explicit_user_stop = false\npromotion_state = "authorized"\npromotion_subject = "scope@1"\n')
        add_locator(p,"definition","definition","DEFINITION.toml",
            'workstream_id = "sample-workstream"\nsource_scope_subject = "scope@1"\nrevision = "R2"\nstate = "green"\n'
            'completeness_audit = "green"\npremium_a = "satisfied"\n'
            'decisions = [{ class = "authority", path = "decisions/ADR-001.md" }]\n'
            '[requirements]\nclass = "authority"\npath = "requirements/REQUIREMENTS.md"\n')
        key=f"owner/router-fixture@{A40}:planning/MASTER_PLAN.md@{B40}"
        add_locator(p,"planning","planning","PLANNING.toml",
            'workstream_id = "sample-workstream"\ncycle = 1\nentry_subject = "definition:R1|planning-cycle:1"\nrevision = "P1"\n'
            'state = "approved"\nplanner_audit = "green"\nplan_path = "planning/MASTER_PLAN.md"\nreview_mode = "independent"\n'
            'review_exemption_basis = ""\nreview_exemption_base_subject = ""\npremium_a = "satisfied"\n'
            'premium_a_subject = "definition:R1|planning-cycle:1"\npremium_b = "satisfied"\n'
            f'premium_b_subject = "{key}"\npremium_c = "satisfied"\npremium_c_subject = "{key}"\n'
            f'[subject]\nrepository = "owner/router-fixture"\ncommit = "{A40}"\npath = "planning/MASTER_PLAN.md"\nblob = "{B40}"\n')
        add_locator(p,"plan_review","plan_review","PLAN_REVIEW.toml",
            'workstream_id = "sample-workstream"\nplan_revision = "P1"\nplanning_cycle = 1\nattempt = "R01"\nverdict = "green"\n'
            f'evidence_path = "{WS}/evidence/plan-review.md"\n'
            f'[subject]\nclass = "git_blob"\nrepository = "owner/router-fixture"\ncommit = "{A40}"\npath = "planning/MASTER_PLAN.md"\nblob = "{B40}"\n'
            '[acceptance]\nclass = "authority"\npath = "requirements/REQUIREMENTS.md"\n'
            '[independence]\nmaterially_produced_or_repaired_subject = false\nbasis = "Fresh independent context."\n')
        (p/WS/"evidence").mkdir(exist_ok=True); (p/WS/"evidence/plan-review.md").write_text("# evidence\n")
        r=select_route(p,[MANIFEST],package_root=ROOT)
        assert (r.disposition,r.obligation,r.subject)==("route","execution","M01-T04"), r
        print("F3 reproduced:",r.disposition,r.obligation,r.subject,"with Definition R2 / Planning R1")
    finally: td.cleanup()

def f4():
    td,p=copy_fixture()
    try:
        install_result(p,status="done",review="required")
        r=select_route(p,[MANIFEST],package_root=ROOT)
        assert (r.disposition,r.obligation)==("route","close"), r
        print("F4 reproduced:",r.disposition,r.obligation,"without review attempts")
    finally: td.cleanup()

def f5():
    td,p=copy_fixture()
    try:
        rp=install_result(p,review="required"); add_green_review(p,True)
        before=select_route(p,[MANIFEST],package_root=ROOT)
        (p/rp).write_text((p/rp).read_text().replace("GREEN-v1","GREEN-v2-mutated-after-review"))
        after=select_route(p,[MANIFEST],package_root=ROOT)
        assert before.obligation==after.obligation=="post_review_finalization", (before,after)
        print("F5 reproduced: finalization survives result-byte drift with unchanged metadata")
    finally: td.cleanup()

def f6():
    td,p=copy_fixture()
    try:
        install_result(p,status="done",review="none")
        b=p/BOARD
        b.write_text(b.read_text()+'\n[[jit_triggers]]\nid = "J1"\nafter_card = "M01-T04"\nstate = "satisfied"\ncondition = "materialize downstream card"\n')
        r=select_route(p,[MANIFEST],package_root=ROOT)
        assert (r.disposition,r.obligation)==("route","close"), r
        print("F6 reproduced:",r.disposition,r.obligation,"with satisfied JIT trigger")
    finally: td.cleanup()

def f7():
    td,p=copy_fixture()
    try:
        install_result(p,review="required"); add_green_review(p,False)
        r=select_route(p,[MANIFEST],package_root=ROOT)
        assert (r.disposition,r.obligation)==("route","post_review_finalization"), r
        print("F7 reproduced:",r.disposition,r.obligation,"with missing evidence file")
    finally: td.cleanup()

if __name__=="__main__":
    for fn in (f1,f2,f3,f4,f5,f6,f7): fn()
