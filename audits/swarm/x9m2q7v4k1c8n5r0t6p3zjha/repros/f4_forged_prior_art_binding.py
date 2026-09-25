from tests.test_router import RouterTests, MANIFEST, ROOT
from tools.router import select_route

t = RouterTests()
temp, project = t.copy_fixture()
try:
    intake = (
        'workstream_id = "sample-workstream"\n'
        'kind = "issue"\n'
        'state = "complete"\n'
        'diagnosis_revision = 1\n'
        'repair_subject = "repair:forged-prior-art:v1"\n'
        'diagnosis_prior_art_subject = "repair:forged-prior-art:v1"\n'
        'diagnosis_prior_art_result = "forged-no-research"\n'
        'response_kind = "authorization"\n'
        'response_observed = true\n'
        'alignment_state = "authorized"\n'
        'alignment_subject = "repair:forged-prior-art:v1"\n'
        'micro_fix_candidate = true\n'
    )
    t.install_intake(project, intake)

    routed = select_route(project, [MANIFEST], package_root=ROOT)
    print(routed)
    assert (routed.disposition, routed.obligation) == ("route", "execution")
    print("REPRODUCED: forged prior-art binding bypassed mandatory Intake Research")
finally:
    temp.cleanup()
