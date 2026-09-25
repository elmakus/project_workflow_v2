from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tests.test_router import RouterTests, MANIFEST, CARD
from tools.router import select_route

rt = RouterTests()
temp, project = rt.copy_fixture()
try:
    rt.install_intake(project, (
        'workstream_id = "sample-workstream"\n'
        'kind = "issue"\n'
        'state = "active"\n'
        'diagnosis_revision = 2\n'
        'repair_subject = "repair:v2"\n'
        'diagnosis_prior_art_subject = ""\n'
        'diagnosis_prior_art_result = ""\n'
        'response_kind = "none"\n'
        'response_observed = false\n'
        'alignment_state = "pending"\n'
        'alignment_subject = ""\n'
        'micro_fix_candidate = false\n'
    ))
    research = (
        rt.issue_research_content("repair:v2")
        .replace('state = "consumed"', 'state = "complete"')
        .replace('return_target = "intake"', 'return_target = "definition"')
        .replace('return_reconciliation = "applied"', 'return_reconciliation = "pending"')
        .replace('return_result = "evidence/intake-prior-art.md"', 'return_result = ""')
    )
    rt.install_state_record(project, "research", "research", "RESEARCH.toml", research)
    routed = select_route(project, [MANIFEST], package_root=ROOT)
    print(routed)
    assert (routed.disposition, routed.obligation) == ("route", "definition")
    print("BUG REPRODUCED: Intake-origin Research jumped directly to Definition.")
finally:
    temp.cleanup()
