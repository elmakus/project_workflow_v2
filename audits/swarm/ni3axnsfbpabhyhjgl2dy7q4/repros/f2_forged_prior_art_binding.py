#!/usr/bin/env python3
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools.router import select_route

FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"

with tempfile.TemporaryDirectory() as tmp:
    project = Path(tmp) / "project"
    shutil.copytree(FIXTURE, project)

    manifest = project / MANIFEST
    manifest.write_text(
        manifest.read_text()
        + '\n[intake]\nclass = "intake"\n'
        + 'path = "implementation/workstreams/sample-workstream/INTAKE.toml"\n'
    )
    intake = project / "implementation/workstreams/sample-workstream/INTAKE.toml"
    intake.write_text(
        'workstream_id = "sample-workstream"\n'
        'kind = "issue"\n'
        'state = "complete"\n'
        'diagnosis_revision = 1\n'
        'repair_subject = "repair:v1"\n'
        'diagnosis_prior_art_subject = "repair:v1"\n'
        'diagnosis_prior_art_result = "forged:never-produced"\n'
        'response_kind = "authorization"\n'
        'response_observed = true\n'
        'alignment_state = "authorized"\n'
        'alignment_subject = "repair:v1"\n'
        'micro_fix_candidate = true\n'
    )

    routed = select_route(project, [MANIFEST], package_root=ROOT)
    print(routed)
    print("No Research record exists, yet the fabricated non-empty result binding satisfies the gate.")
    assert (routed.disposition, routed.obligation) == ("route", "execution")
    assert not any("RESEARCH.toml" in item for item in routed.read_set)
