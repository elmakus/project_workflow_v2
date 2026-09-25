from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tests.test_router import RouterTests, MANIFEST, CARD
from tools.router import select_route

rt = RouterTests()

# A. Same-path predecessor bytes change while declared dependency identity stays unchanged.
temp, project = rt.copy_fixture()
try:
    dep_path = "implementation/workstreams/sample-workstream/results/M01-T03.md"
    commit = "a" * 40
    blob = "b" * 40
    dep = f"{dep_path}@{commit}:{blob}"
    rt.install_done_predecessor(project, path=dep_path, commit=commit, blob=blob)
    rt.make_ready_card(project, dependencies=dep)
    before = select_route(project, [MANIFEST], package_root=ROOT)
    assert (before.disposition, before.obligation) == ("route", "execution_prep")

    (project / dep_path).write_text("# CHANGED predecessor bytes; metadata intentionally unchanged\n")
    after = select_route(project, [MANIFEST], package_root=ROOT)
    print("dependency drift:", after)
    assert (after.disposition, after.obligation) == ("route", "execution_prep")
finally:
    temp.cleanup()

# B. Reviewed result and acceptance bytes change while declared result/review identities stay unchanged.
temp, project = rt.copy_fixture()
try:
    result_path = rt.install_reviewable_result(project, "required")
    rt.add_review_attempt(project, "green")
    before = select_route(project, [MANIFEST], package_root=ROOT)
    assert (before.disposition, before.obligation) == ("route", "post_review_finalization")

    result_file = project / result_path
    result_file.write_text(
        result_file.read_text().replace(
            "Tests/readback summary: GREEN",
            "Tests/readback summary: MUTATED AFTER GREEN REVIEW",
        )
    )
    card_file = project / CARD
    card_file.write_text(
        card_file.read_text().replace(
            "Acceptance: route only after current launch inputs are valid",
            "Acceptance: materially different post-review acceptance",
        )
    )
    after = select_route(project, [MANIFEST], package_root=ROOT)
    print("reviewed bytes drift:", after)
    assert (after.disposition, after.obligation) == ("route", "post_review_finalization")
    print("BUG REPRODUCED: stale declared identities permit launch/finalization after same-path byte changes.")
finally:
    temp.cleanup()
