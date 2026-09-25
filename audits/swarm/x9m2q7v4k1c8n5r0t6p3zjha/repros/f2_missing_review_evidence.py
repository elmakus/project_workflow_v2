from tests.test_router import RouterTests, MANIFEST, ROOT
from tools.router import select_route

t = RouterTests()
temp, project = t.copy_fixture()
try:
    t.install_reviewable_result(project, "required")
    t.add_review_attempt(project, "green")

    evidence = project / "implementation/workstreams/sample-workstream/evidence/review-R01.md"
    evidence.unlink()

    routed = select_route(project, [MANIFEST], package_root=ROOT)
    print(routed)
    assert (routed.disposition, routed.obligation) == ("route", "post_review_finalization")
    print("REPRODUCED: GREEN review finalized with missing terminal evidence")
finally:
    temp.cleanup()
