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
        'state = "active"\n'
        'diagnosis_revision = 0\n'
        'repair_subject = ""\n'
        'diagnosis_prior_art_subject = ""\n'
        'diagnosis_prior_art_result = ""\n'
        'response_kind = "none"\n'
        'response_observed = false\n'
        'alignment_state = "pending"\n'
        'alignment_subject = ""\n'
        'micro_fix_candidate = false\n'
    )

    routed = select_route(project, [MANIFEST], package_root=ROOT)
    print(routed)
    print("EXPECTED CONTRACT OWNER: route / intake (diagnosis has no concrete repair subject)")
    assert (routed.disposition, routed.obligation) == ("stop", "issue_alignment")
