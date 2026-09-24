#!/usr/bin/env python3
"""F4: production Plan Review validator accepts unrelated authority acceptance."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools.state_contract import validate_plan_review, validate_planning

A = "a" * 40
B = "b" * 40
subject_key = f"owner/repo@{A}:planning/MASTER_PLAN.md@{B}"

planning = {
    "workstream_id": "sample-workstream",
    "cycle": 1,
    "entry_subject": "definition:R1|planning-cycle:1",
    "revision": "P1",
    "state": "frozen",
    "planner_audit": "green",
    "plan_path": "planning/MASTER_PLAN.md",
    "review_mode": "independent",
    "review_exemption_basis": "",
    "review_exemption_base_subject": "",
    "premium_a": "satisfied",
    "premium_a_subject": "definition:R1|planning-cycle:1",
    "premium_b": "satisfied",
    "premium_b_subject": subject_key,
    "premium_c": "not_due",
    "premium_c_subject": "",
    "subject": {
        "class": "git_blob",
        "repository": "owner/repo",
        "commit": A,
        "path": "planning/MASTER_PLAN.md",
        "blob": B,
    },
}

review = {
    "workstream_id": "sample-workstream",
    "plan_revision": "P1",
    "planning_cycle": 1,
    "attempt": "R01",
    "verdict": "green",
    "evidence_path": "evidence/plan-review-R01.md",
    "subject": {
        "class": "git_blob",
        "repository": "owner/repo",
        "commit": A,
        "path": "planning/MASTER_PLAN.md",
        "blob": B,
    },
    # Syntactically legal authority root, but unrelated to the accepted
    # product Definition/requirements/decisions acceptance surface.
    "acceptance": {"class": "authority", "path": "workflow/ROUTER.md"},
    "independence": {
        "materially_produced_or_repaired_subject": False,
        "basis": "Fresh independent semantic context.",
    },
}

validate_planning(planning, "sample-workstream")
validate_plan_review(review, "sample-workstream", planning)
print("F4 reproduced: unrelated workflow/ROUTER.md acceptance passed GREEN Plan Review validation.")
