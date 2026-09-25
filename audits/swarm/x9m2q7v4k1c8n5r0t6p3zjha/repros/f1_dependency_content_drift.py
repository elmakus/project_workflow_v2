from tests.test_router import RouterTests, MANIFEST, ROOT
from tools.router import select_route

t = RouterTests()
temp, project = t.copy_fixture()
try:
    path = "implementation/workstreams/sample-workstream/results/M01-T03.md"
    commit = "a" * 40
    blob = "b" * 40
    dep = f"{path}@{commit}:{blob}"
    t.install_done_predecessor(project, path=path, commit=commit, blob=blob)
    t.make_ready_card(project, dependencies=dep)

    (project / path).write_text("# materially changed predecessor result\n")

    routed = select_route(project, [MANIFEST], package_root=ROOT)
    print(routed)
    assert (routed.disposition, routed.obligation) == ("route", "execution_prep")
    print("REPRODUCED: changed dependency content was not detected; expected Recovery")
finally:
    temp.cleanup()
