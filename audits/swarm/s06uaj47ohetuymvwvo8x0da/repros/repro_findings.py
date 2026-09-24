#!/usr/bin/env python3
"""Non-mutating regression repros for PWv2 swarm audit s06uaj47ohetuymvwvo8x0da.

Run from any checkout containing exact subject 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045 plus this audit directory:
    python3 audits/swarm/s06uaj47ohetuymvwvo8x0da/repros/repro_findings.py

These tests encode the expected contract behavior. On the audited subject they are
expected to fail until the corresponding defects are repaired.
"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from tools.router import select_route

ROOT = Path(__file__).resolve().parents[4]
FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"
WS_DIR = "implementation/workstreams/sample-workstream"
RESULT = f"{WS_DIR}/results/M01-T04.md"
EVIDENCE = f"{WS_DIR}/evidence/M01-T04.md"


class AdversarialRepros(unittest.TestCase):
    def project(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        project = Path(temp.name) / "project"
        shutil.copytree(FIXTURE, project)
        return project

    def stable_card(self, project: Path, *, review_requirement: str = "none") -> None:
        (project / CARD).write_text(
            "# Fixture Card\n"
            "- Card ID: M01-T04\n"
            "- Included scope: bounded audited implementation\n"
            "- Excluded scope: unrelated work\n"
            "- Authority refs: requirements/REQUIREMENTS.md\n"
            "- Dependencies: none\n"
            "- Acceptance: exact durable behavior is verified\n"
            "- Required tests/readback: regression checks\n"
            f"- Review requirement: {review_requirement}\n"
            "- Technical contract: none\n",
            encoding="utf-8",
        )
        authority = project / "requirements/REQUIREMENTS.md"
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text("# Accepted authority\n", encoding="utf-8")

    def install_result(self, project: Path, *, review_requirement: str = "none") -> None:
        self.stable_card(project, review_requirement=review_requirement)
        evidence = project / EVIDENCE
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text("# Durable evidence\n", encoding="utf-8")
        result_file = project / RESULT
        result_file.parent.mkdir(parents=True, exist_ok=True)
        result_file.write_text(
            "# Card Result\n"
            "- Card ID: M01-T04\n"
            "- Implementation subject: owner/router-fixture@commit:" + ("a" * 40) + "\n"
            f"- Evidence refs: {EVIDENCE}\n"
            "- Tests/readback summary: GREEN\n",
            encoding="utf-8",
        )
        board = project / BOARD
        board.write_text(
            board.read_text(encoding="utf-8")
            + "\n[cards.result]\n"
            + 'class = "result"\n'
            + f'path = "{RESULT}"\n'
            + f'commit = "{"a" * 40}"\n'
            + f'blob = "{"b" * 40}"\n',
            encoding="utf-8",
        )

    def add_review(self, project: Path, verdict: str = "pending") -> None:
        review_path = f"{WS_DIR}/reviews/M01-T04-R01.toml"
        board = project / BOARD
        board.write_text(
            board.read_text(encoding="utf-8").replace(
                'status = "in_progress"\n',
                'status = "in_progress"\n'
                f'review_attempts = [{{ class = "review_attempt", path = "{review_path}" }}]\n',
                1,
            ),
            encoding="utf-8",
        )
        evidence_path = "" if verdict in {"pending", "in_progress"} else f"{WS_DIR}/evidence/review-R01.md"
        if evidence_path:
            ev = project / evidence_path
            ev.parent.mkdir(parents=True, exist_ok=True)
            ev.write_text("# Review evidence\n", encoding="utf-8")
        review = project / review_path
        review.parent.mkdir(parents=True, exist_ok=True)
        review.write_text(
            'workstream_id = "sample-workstream"\n'
            'card_id = "M01-T04"\n'
            'attempt = "R01"\n'
            f'verdict = "{verdict}"\n'
            f'evidence_path = "{evidence_path}"\n'
            '[subject]\n'
            'class = "git_blob"\n'
            'repository = "owner/router-fixture"\n'
            f'commit = "{"a" * 40}"\n'
            f'path = "{RESULT}"\n'
            f'blob = "{"b" * 40}"\n'
            '[acceptance]\n'
            'class = "task_card"\n'
            f'path = "{CARD}"\n'
            '[independence]\n'
            'materially_produced_or_repaired_subject = false\n'
            'basis = "Fresh semantic reviewer context."\n',
            encoding="utf-8",
        )

    def test_F1_satisfied_jit_trigger_preempts_close(self) -> None:
        project = self.project()
        self.install_result(project)
        board = project / BOARD
        board.write_text(
            board.read_text(encoding="utf-8")
            .replace('status = "in_progress"', 'status = "done"', 1)
            + "\n[[jit_triggers]]\n"
            + 'id = "after-M01-T04"\n'
            + 'after_card = "M01-T04"\n'
            + 'state = "satisfied"\n'
            + 'condition = "Predecessor result makes the downstream Card boundary knowable."\n',
            encoding="utf-8",
        )
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        self.assertEqual(
            (routed.disposition, routed.obligation),
            ("route", "execution_prep"),
            "a satisfied JIT obligation must be consumed/materialized before Close",
        )

    def test_F2_done_cannot_bypass_required_pending_review(self) -> None:
        project = self.project()
        self.install_result(project, review_requirement="required")
        self.add_review(project, "pending")
        board = project / BOARD
        board.write_text(
            board.read_text(encoding="utf-8").replace(
                'status = "in_progress"', 'status = "done"', 1
            ),
            encoding="utf-8",
        )
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        self.assertEqual(
            (routed.disposition, routed.obligation),
            ("recovery", "recovery_boundary"),
            "DONE plus a non-GREEN REQUIRED review is contradictory and must fail closed",
        )

    def test_F3_changed_result_bytes_cannot_reuse_green_subject(self) -> None:
        project = self.project()
        self.install_result(project, review_requirement="required")
        self.add_review(project, "green")

        baseline = select_route(project, [MANIFEST], package_root=ROOT)
        self.assertEqual(
            (baseline.disposition, baseline.obligation),
            ("route", "post_review_finalization"),
        )

        result_file = project / RESULT
        result_file.write_text(
            result_file.read_text(encoding="utf-8").replace(
                "owner/router-fixture@commit:" + ("a" * 40),
                "owner/router-fixture@commit:" + ("c" * 40),
            ),
            encoding="utf-8",
        )
        changed = select_route(project, [MANIFEST], package_root=ROOT)
        self.assertIn(
            (changed.disposition, changed.obligation),
            {
                ("recovery", "recovery_boundary"),
                ("route", "review_freeze"),
            },
            "changed result bytes must not retain the old GREEN exact-subject coverage",
        )

    def test_F4_explicit_user_stop_preempts_active_research(self) -> None:
        project = self.project()
        workstream = project / MANIFEST
        workstream.write_text(
            workstream.read_text(encoding="utf-8")
            + "\n[brainstorm]\n"
            + 'class = "brainstorm"\n'
            + f'path = "{WS_DIR}/BRAINSTORM.toml"\n'
            + "\n[research]\n"
            + 'class = "research"\n'
            + f'path = "{WS_DIR}/RESEARCH.toml"\n',
            encoding="utf-8",
        )
        (project / f"{WS_DIR}/BRAINSTORM.toml").write_text(
            'workstream_id = "sample-workstream"\n'
            'scope_id = "scope-a"\n'
            'revision = 1\n'
            'state = "active"\n'
            'challenge_audit = "pending"\n'
            'explicit_user_stop = true\n'
            'promotion_state = "pending"\n'
            'promotion_subject = ""\n',
            encoding="utf-8",
        )
        (project / f"{WS_DIR}/RESEARCH.toml").write_text(
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
            '[[sources]]\nclass = "practitioner_community"\nstatus = "pending"\nweight = "supporting"\n',
            encoding="utf-8",
        )
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        self.assertEqual(
            (routed.disposition, routed.obligation),
            ("stop", "explicit_user_stop"),
            "explicit human stop must preempt subordinate active Research",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
