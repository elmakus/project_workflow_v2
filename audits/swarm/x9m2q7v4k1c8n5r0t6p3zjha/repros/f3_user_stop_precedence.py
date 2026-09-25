from tests.test_router import RouterTests, MANIFEST, ROOT
from tools.router import select_route

t = RouterTests()
temp, project = t.copy_fixture()
try:
    brainstorm = (
        'workstream_id = "sample-workstream"\n'
        'scope_id = "scope-a"\n'
        'revision = 1\n'
        'state = "active"\n'
        'challenge_audit = "pending"\n'
        'explicit_user_stop = true\n'
        'promotion_state = "pending"\n'
        'promotion_subject = ""\n'
    )
    research = (
        'workstream_id = "sample-workstream"\n'
        'state = "active"\n'
        'origin_role = "brainstorming"\n'
        'origin_subject = "scope-a@1"\n'
        'return_target = "brainstorming"\n'
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
    t.install_state_record(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", brainstorm)
    t.install_state_record(project, "research", "research", "RESEARCH.toml", research)

    routed = select_route(project, [MANIFEST], package_root=ROOT)
    print(routed)
    assert (routed.disposition, routed.obligation) == ("route", "research")
    print("REPRODUCED: active Research masked explicit_user_stop")
finally:
    temp.cleanup()
