from __future__ import annotations

import copy
import tempfile
import tomllib
import unittest
from pathlib import Path

from tools.state_contract import (
    STATE_RECORD_VALIDATORS,
    ValidationError,
    render_validated_state_record,
    validate_state_record,
    write_validated_state_record,
)


class ValidatedStateWriteBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workstream_id = "sample-workstream"
        self.card_id = "M01-T01"
        self.commit = "a" * 40
        self.blob = "b" * 40
        self.plan_subject = {
            "repository": "owner/repo",
            "commit": self.commit,
            "path": "planning/MASTER_PLAN.md",
            "blob": self.blob,
        }
        self.plan_subject_key = (
            f"owner/repo@{self.commit}:planning/MASTER_PLAN.md@{self.blob}"
        )
        self.workstream = {
            "kind": "change",
            "workstream_id": self.workstream_id,
            "branch": "feat/sample-workstream",
            "created_from": "1" * 40,
            "integration_target": "main",
            "authority": [
                {"class": "authority", "path": "requirements/REQUIREMENTS.md"},
            ],
            "task_board": {
                "class": "task_board",
                "path": "implementation/workstreams/sample-workstream/TASK_BOARD.toml",
            },
        }
        self.planning = {
            "workstream_id": self.workstream_id,
            "cycle": 1,
            "entry_subject": "R1",
            "revision": "P1",
            "state": "frozen",
            "planner_audit": "green",
            "plan_path": "planning/MASTER_PLAN.md",
            "review_mode": "independent",
            "review_exemption_basis": "",
            "review_exemption_base_subject": "",
            "premium_a": "satisfied",
            "premium_a_subject": "R1",
            "premium_b": "due",
            "premium_b_subject": self.plan_subject_key,
            "premium_c": "not_due",
            "premium_c_subject": "",
            "subject": copy.deepcopy(self.plan_subject),
        }

    def records(self) -> dict[str, tuple[dict, dict]]:
        return {
            "workstream": (copy.deepcopy(self.workstream), {}),
            "intake": ({
                "workstream_id": self.workstream_id,
                "kind": "feature",
                "state": "active",
                "diagnosis_revision": 0,
                "repair_subject": "",
                "diagnosis_prior_art_subject": "",
                "diagnosis_prior_art_result": "",
                "response_kind": "none",
                "response_observed": False,
                "alignment_state": "not_required",
                "alignment_subject": "",
                "micro_fix_candidate": False,
            }, {"workstream_id": self.workstream_id}),
            "brainstorm": ({
                "workstream_id": self.workstream_id,
                "scope_id": "scope-a",
                "revision": 1,
                "state": "active",
                "challenge_audit": "pending",
                "explicit_user_stop": False,
                "promotion_state": "pending",
                "promotion_subject": "",
            }, {"workstream_id": self.workstream_id}),
            "research": ({
                "workstream_id": self.workstream_id,
                "state": "active",
                "origin_role": "intake",
                "origin_subject": "subject-a",
                "return_target": "intake",
                "return_reconciliation": "pending",
                "return_result": "",
                "finding": "",
                "limitations": "",
                "conflicts": "",
                "sources": [
                    {"class": "official_upstream", "status": "pending", "weight": "primary"},
                    {"class": "project_runtime", "status": "pending", "weight": "direct"},
                    {"class": "tracker_discussion", "status": "pending", "weight": "supporting"},
                    {"class": "practitioner_community", "status": "pending", "weight": "supporting"},
                ],
            }, {"workstream_id": self.workstream_id}),
            "definition": ({
                "workstream_id": self.workstream_id,
                "source_scope_subject": "scope-a@1",
                "revision": "R1",
                "state": "green",
                "completeness_audit": "green",
                "premium_a": "due",
                "requirements": {"class": "authority", "path": "requirements/REQUIREMENTS.md"},
                "decisions": [{"class": "authority", "path": "decisions/ADR-001.md"}],
            }, {"workstream_id": self.workstream_id}),
            "planning": (copy.deepcopy(self.planning), {"workstream_id": self.workstream_id}),
            "plan_review": ({
                "workstream_id": self.workstream_id,
                "plan_revision": "P1",
                "planning_cycle": 1,
                "attempt": "R01",
                "verdict": "pending",
                "evidence_path": "",
                "subject": {"class": "git_blob", **copy.deepcopy(self.plan_subject)},
                "acceptance": {"class": "authority", "path": "requirements/REQUIREMENTS.md"},
                "independence": {
                    "materially_produced_or_repaired_subject": False,
                    "basis": "Fresh independent context.",
                },
            }, {"workstream_id": self.workstream_id, "planning": copy.deepcopy(self.planning)}),
            "tracker": ({
                "workstream_id": self.workstream_id,
                "provider": "github",
                "repository": "owner/repo",
                "dedup_key": "project-workflow:sample-workstream",
                "state": "discovery",
                "issue_number": 0,
                "candidate_issue_numbers": [],
                "readback_state": "pending",
                "final_pr": 0,
            }, {"workstream_id": self.workstream_id}),
            "task_board": ({
                "workstream_id": self.workstream_id,
                "revision": 1,
                "execution_ref": {"branch": "feat/sample-workstream"},
                "cards": [{
                    "id": self.card_id,
                    "status": "ready",
                    "contract": {
                        "class": "task_card",
                        "path": (
                            "implementation/workstreams/sample-workstream/"
                            f"cards/{self.card_id}.md"
                        ),
                    },
                }],
                "jit_triggers": [],
            }, {"workstream": copy.deepcopy(self.workstream)}),
            "blocker": ({
                "workstream_id": self.workstream_id,
                "card_id": self.card_id,
                "class": "missing_evidence",
                "summary": "Need exact upstream behavior.",
                "evidence_path": "",
            }, {"workstream_id": self.workstream_id, "card_id": self.card_id}),
            "review_attempt": ({
                "workstream_id": self.workstream_id,
                "card_id": self.card_id,
                "attempt": "R01",
                "verdict": "pending",
                "evidence_path": "",
                "subject": {
                    "class": "git_blob",
                    "repository": "owner/repo",
                    "commit": self.commit,
                    "path": "tools/state_contract.py",
                    "blob": self.blob,
                },
                "acceptance": {
                    "class": "task_card",
                    "path": (
                        "implementation/workstreams/sample-workstream/"
                        f"cards/{self.card_id}.md"
                    ),
                },
                "independence": {
                    "materially_produced_or_repaired_subject": False,
                    "basis": "Reviewer did not produce the subject.",
                },
            }, {"workstream_id": self.workstream_id, "card_id": self.card_id}),
            "external_effect": ({
                "obligation_id": self.card_id,
                "operation": "write target branch",
                "target": "owner/repo:refs/heads/feat/sample-workstream",
                "expected_state": "exact committed bytes",
                "readback_state": "verified",
                "observation": "expected_effect",
                "evidence": {
                    "class": "evidence",
                    "path": (
                        "implementation/workstreams/sample-workstream/"
                        "evidence/write-readback.md"
                    ),
                },
            }, {"workstream_id": self.workstream_id}),
        }

    def test_dispatch_registers_every_canonical_toml_record_kind(self) -> None:
        self.assertEqual(set(STATE_RECORD_VALIDATORS), set(self.records()))

    def test_every_registered_record_validates_renders_and_round_trips(self) -> None:
        for kind, (data, context) in self.records().items():
            with self.subTest(kind=kind):
                validate_state_record(kind, data, **context)
                rendered = render_validated_state_record(kind, data, **context)
                self.assertEqual(tomllib.loads(rendered), data)

    def test_contextual_validators_fail_without_current_context(self) -> None:
        records = self.records()
        for kind in (
            "intake", "brainstorm", "research", "definition", "planning",
            "plan_review", "tracker", "task_board", "blocker",
            "review_attempt", "external_effect",
        ):
            with self.subTest(kind=kind), self.assertRaises(ValidationError):
                validate_state_record(kind, records[kind][0])

    def test_stale_shapes_are_rejected_before_persistence(self) -> None:
        records = self.records()
        stale_definition = copy.deepcopy(records["definition"][0])
        stale_definition["revision"] = 1
        stale_planning = copy.deepcopy(records["planning"][0])
        stale_planning["plan_artifact"] = stale_planning.pop("plan_path")
        stale_tracker = copy.deepcopy(records["tracker"][0])
        stale_tracker["number"] = stale_tracker.pop("issue_number")
        stale_board = copy.deepcopy(records["task_board"][0])
        stale_board["cards"][0]["status"] = "review_pending"
        cases = (
            ("definition", stale_definition, records["definition"][1]),
            ("planning", stale_planning, records["planning"][1]),
            ("tracker", stale_tracker, records["tracker"][1]),
            ("task_board", stale_board, records["task_board"][1]),
        )
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "STATE.toml"
            target.write_text("sentinel = true\n", encoding="utf-8")
            for kind, data, context in cases:
                with self.subTest(kind=kind), self.assertRaises(ValidationError):
                    write_validated_state_record(target, kind, data, **context)
                self.assertEqual(target.read_text(encoding="utf-8"), "sentinel = true\n")

    def test_validated_write_is_atomic_and_readable(self) -> None:
        data, context = self.records()["task_board"]
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "TASK_BOARD.toml"
            rendered = write_validated_state_record(target, "task_board", data, **context)
            self.assertEqual(target.read_text(encoding="utf-8"), rendered)
            self.assertEqual(tomllib.loads(rendered), data)

    def test_unknown_record_kind_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValidationError, "unsupported record kind"):
            validate_state_record("made_up", {}, workstream_id=self.workstream_id)


if __name__ == "__main__":
    unittest.main()
