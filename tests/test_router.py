from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.router import PRIORITY_FOUNDATION, REAL_STOP_FOUNDATION, classify_jit_refinement, select_route

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"


class RouterTests(unittest.TestCase):
    def copy_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(FIXTURE, project)
        return temp, project

    def test_valid_state_selects_same_route_independent_of_runtime_noise(self) -> None:
        expected = None
        for noise in (
            {},
            {"RUNTIME": "chatgpt", "MODEL_ID": "one", "SESSION_ID": "alpha"},
            {"RUNTIME": "codex", "MODEL_ID": "two", "SESSION_ID": "beta"},
        ):
            with patch.dict(os.environ, noise, clear=False):
                routed = select_route(FIXTURE, [MANIFEST], package_root=ROOT)
            semantic = (routed.disposition, routed.obligation, routed.subject, routed.owner_module)
            expected = expected or semantic
            self.assertEqual(semantic, expected)
        self.assertEqual(expected, ("route", "execution", "M01-T04", "workflow/EXECUTION.md"))

    def test_progressive_disclosure_read_set_is_exact(self) -> None:
        routed = select_route(FIXTURE, [MANIFEST], package_root=ROOT)
        self.assertEqual(
            routed.read_set,
            (
                "package:workflow/ROUTER.md",
                "project:PROJECT.md",
                f"project:{MANIFEST}",
                "package:policy/mechanical_policy.json",
                "package:workflow/POLICY_KERNEL.md",
                f"project:{BOARD}",
                f"project:{CARD}",
            ),
        )
        joined = "\n".join(routed.read_set)
        self.assertNotIn("migration/UNRELATED.md", joined)
        self.assertNotIn("untrusted/ISSUE_TEXT.md", joined)
        self.assertNotIn("templates/", joined)

    def task_card_content(
        self, *, dependencies: str = "none", technical_contract: str = "none",
        review_requirement: str = "none",
    ) -> str:
        return (
            "# Fixture Card\n"
            "- Card ID: M01-T04\n"
            "- Included scope: prove launch readiness\n"
            "- Excluded scope: runtime-specific orchestration\n"
            "- Authority refs: requirements/REQUIREMENTS.md\n"
            f"- Dependencies: {dependencies}\n"
            "- Acceptance: route only after current launch inputs are valid\n"
            "- Required tests/readback: production router fixture\n"
            f"- Review requirement: {review_requirement}\n"
            f"- Technical contract: {technical_contract}\n"
        )

    def make_ready_card(self, project: Path, *, dependencies: str = "none",
                        technical_contract: str = "none") -> None:
        board = project / BOARD
        board.write_text(board.read_text().replace('status = "in_progress"', 'status = "ready"'))
        card = project / CARD
        card.write_text(self.task_card_content(
            dependencies=dependencies,
            technical_contract=technical_contract,
        ))
        authority = project / "requirements" / "REQUIREMENTS.md"
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text("# Accepted authority\n")

    def test_ready_card_launch_refresh_is_runtime_neutral_and_progressive(self) -> None:
        for noise in (
            {"RUNTIME": "codex", "MODEL_ID": "one", "WORKER_ID": "alpha"},
            {"RUNTIME": "pi", "MODEL_ID": "two", "WORKER_ID": "beta"},
        ):
            temp, project = self.copy_fixture()
            try:
                self.make_ready_card(project)
                with patch.dict(os.environ, noise, clear=False):
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                self.assertEqual((routed.disposition, routed.obligation), ("route", "execution_prep"))
                self.assertEqual(routed.subject, "M01-T04")
                self.assertIn("project:requirements/REQUIREMENTS.md", routed.read_set)
                self.assertFalse(any("openspec/" in item or "contracts/" in item for item in routed.read_set))
            finally:
                temp.cleanup()

    @staticmethod
    def git_identity_for(project: Path, relpath: str) -> tuple[str, str]:
        """Commit one fixture file and return its real (commit, blob) identity."""
        if not (project / ".git").exists():
            subprocess.run(["git", "init", "-q", str(project)], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.email", "fixture@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.name", "Fixture"], check=True)
        subprocess.run(["git", "-C", str(project), "add", relpath], check=True)
        subprocess.run(["git", "-C", str(project), "commit", "-q", "-m", f"fixture {relpath}"], check=True)
        commit = subprocess.run(
            ["git", "-C", str(project), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        blob = subprocess.run(
            ["git", "-C", str(project), "rev-parse", f"HEAD:{relpath}"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        return commit, blob

    @staticmethod
    def board_result_identity(project: Path) -> tuple[str, str]:
        """Return the current board result (commit, blob) for the active Card."""
        section = (project / BOARD).read_text().split("[cards.result]", 1)[1]
        commit = re.search(r'commit = "([0-9a-f]{40})"', section).group(1)  # type: ignore[union-attr]
        blob = re.search(r'blob = "([0-9a-f]{40})"', section).group(1)  # type: ignore[union-attr]
        return commit, blob

    def commit_result_version(self, project: Path, result_path: str, content: str) -> tuple[str, str]:
        """Write new result bytes, commit them, and rebind the board locator."""
        old_commit, old_blob = self.board_result_identity(project)
        (project / result_path).write_text(content)
        commit, blob = self.git_identity_for(project, result_path)
        board = project / BOARD
        board.write_text(
            board.read_text()
            .replace(f'commit = "{old_commit}"', f'commit = "{commit}"', 1)
            .replace(f'blob = "{old_blob}"', f'blob = "{blob}"', 1)
        )
        return commit, blob

    def install_done_predecessor(
        self, project: Path, *, path: str,
    ) -> tuple[str, str]:
        result_path = project / path
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text("# predecessor result\n")
        commit, blob = self.git_identity_for(project, path)
        board = project / BOARD
        existing = board.read_text()
        predecessor = (
            '[[cards]]\n'
            'id = "M01-T03"\n'
            'status = "done"\n'
            '[cards.contract]\n'
            'class = "task_card"\n'
            'path = "implementation/workstreams/sample-workstream/cards/M01-T03.md"\n'
            '[cards.result]\n'
            'class = "result"\n'
            f'path = "{path}"\n'
            f'commit = "{commit}"\n'
            f'blob = "{blob}"\n\n'
        )
        board.write_text(existing.replace('[[cards]]\n', predecessor + '[[cards]]\n', 1))
        predecessor_card = project / "implementation/workstreams/sample-workstream/cards/M01-T03.md"
        predecessor_card.write_text("# predecessor Card\n")
        return commit, blob

    def test_ready_card_stale_dependency_fails_closed_before_launch(self) -> None:
        temp, project = self.copy_fixture()
        try:
            dependency_path = "implementation/workstreams/sample-workstream/results/M01-T03.md"
            commit, blob = self.install_done_predecessor(project, path=dependency_path)
            dependency = f"{dependency_path}@{commit}:{blob}"
            self.make_ready_card(project, dependencies=dependency)

            current = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((current.disposition, current.obligation), ("route", "execution_prep"))

            new_commit = "c" * 40
            new_blob = "d" * 40
            board = project / BOARD
            board.write_text(
                board.read_text()
                .replace(f'commit = "{commit}"', f'commit = "{new_commit}"')
                .replace(f'blob = "{blob}"', f'blob = "{new_blob}"')
            )
            (project / dependency_path).write_text("# materially changed predecessor result\n")

            stale = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((stale.disposition, stale.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("no longer matches the exact current DONE predecessor result", stale.reason)
        finally:
            temp.cleanup()

    def test_technical_contract_is_loaded_only_when_card_selects_it(self) -> None:
        temp, project = self.copy_fixture()
        try:
            contract = "contracts/sample-api.md"
            self.make_ready_card(project, technical_contract=contract)
            contract_path = project / contract
            contract_path.parent.mkdir(parents=True, exist_ok=True)
            contract_path.write_text("# Material API contract\n")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution_prep"))
            self.assertIn(f"project:{contract}", routed.read_set)
        finally:
            temp.cleanup()

    def test_jit_refinement_classification_separates_authority_layers(self) -> None:
        self.assertEqual(classify_jit_refinement("bounded_execution_detail")[0], "execution_prep")
        self.assertEqual(classify_jit_refinement("strategy")[0], "planning")
        self.assertEqual(classify_jit_refinement("product_or_global_intent")[0], "definition")
        self.assertEqual(classify_jit_refinement("missing_facts")[0], "research")
        with self.assertRaisesRegex(Exception, "unknown JIT"):
            classify_jit_refinement("runtime_model_missing")

    def test_new_managed_intent_routes_to_common_intake_without_board(self) -> None:
        for entry, subject in (
            ("new_managed_intent", "change"),
            ("new_issue", "issue"),
            ("new_feature", "feature"),
        ):
            with self.subTest(entry=entry):
                routed = select_route(FIXTURE, [MANIFEST], package_root=ROOT, entry=entry)
                self.assertEqual((routed.disposition, routed.obligation, routed.subject), ("route", "intake", subject))
                self.assertEqual(routed.owner_module, "workflow/INTAKE.md")
                self.assertEqual(routed.read_set, ("package:workflow/ROUTER.md", "project:PROJECT.md"))


    def install_intake(self, project: Path, content: str) -> None:
        workstream = project / MANIFEST
        original = workstream.read_text()
        workstream.write_text(original + '\n[intake]\nclass = "intake"\npath = "implementation/workstreams/sample-workstream/INTAKE.toml"\n')
        intake = project / "implementation/workstreams/sample-workstream/INTAKE.toml"
        intake.write_text(content)


    def install_state_record(self, project: Path, key: str, klass: str, filename: str, content: str) -> None:
        workstream = project / MANIFEST
        workstream.write_text(
            workstream.read_text()
            + f'\n[{key}]\nclass = "{klass}"\npath = "implementation/workstreams/sample-workstream/{filename}"\n'
        )
        record = project / f"implementation/workstreams/sample-workstream/{filename}"
        record.write_text(content)


    def install_green_definition(self, project: Path) -> None:
        self.install_state_record(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", (
            'workstream_id = "sample-workstream"\n'
            'scope_id = "scope-plan"\n'
            'revision = 1\n'
            'state = "promoted"\n'
            'challenge_audit = "green"\n'
            'explicit_user_stop = false\n'
            'promotion_state = "authorized"\n'
            'promotion_subject = "scope-plan@1"\n'
        ))
        self.install_state_record(project, "definition", "definition", "DEFINITION.toml", (
            'workstream_id = "sample-workstream"\n'
            'source_scope_subject = "scope-plan@1"\n'
            'revision = "R1"\n'
            'state = "green"\n'
            'completeness_audit = "green"\n'
            'premium_a = "satisfied"\n'
            'decisions = [{ class = "authority", path = "decisions/ADR-001.md" }]\n'
            '[requirements]\nclass = "authority"\npath = "requirements/REQUIREMENTS.md"\n'
        ))

    def planning_content(
        self, *, state: str, premium_b: str = "not_due", premium_c: str = "not_due",
        cycle: int = 1, premium_a: str = "satisfied", premium_a_subject: str | None = None,
        revision: str = "P1", blob: str | None = None, gate_subject: str | None = None,
        review_mode: str = "independent", exemption_basis: str = "",
        exemption_base_subject: str = "",
        exemption_classification: tuple[str, str, str, str] | None = None,
    ) -> str:
        blob = blob or ("b" * 40)
        premium_a_subject = premium_a_subject or f"definition:R1|planning-cycle:{cycle}"
        key = f"owner/repo@{'a' * 40}:planning/MASTER_PLAN.md@{blob}"
        gate_key = gate_subject or key
        frozen = state in {"frozen", "approved"}
        return (
            'workstream_id = "sample-workstream"\n'
            f'cycle = {cycle}\n'
            f'entry_subject = "definition:R1|planning-cycle:{cycle}"\n'
            f'revision = "{revision}"\n'
            f'state = "{state}"\n'
            f'planner_audit = "{"green" if frozen else "pending"}"\n'
            'plan_path = "planning/MASTER_PLAN.md"\n'
            f'review_mode = "{review_mode}"\n'
            f'review_exemption_basis = "{exemption_basis}"\n'
            f'review_exemption_base_subject = "{exemption_base_subject}"\n'
            f'premium_a = "{premium_a}"\n'
            f'premium_a_subject = "{premium_a_subject}"\n'
            f'premium_b = "{premium_b}"\n'
            f'premium_b_subject = "{gate_key if premium_b != "not_due" else ""}"\n'
            f'premium_c = "{premium_c}"\n'
            f'premium_c_subject = "{gate_key if premium_c != "not_due" else ""}"\n'
            '[subject]\n'
            f'repository = "{"owner/repo" if frozen else ""}"\n'
            f'commit = "{"a" * 40 if frozen else ""}"\n'
            f'path = "{"planning/MASTER_PLAN.md" if frozen else ""}"\n'
            f'blob = "{blob if frozen else ""}"\n'
            + (
                (
                    '[review_exemption_classification]\n'
                    'class = "git_blob"\n'
                    f'repository = "{exemption_classification[0]}"\n'
                    f'commit = "{exemption_classification[1]}"\n'
                    f'path = "{exemption_classification[2]}"\n'
                    f'blob = "{exemption_classification[3]}"\n'
                )
                if exemption_classification is not None
                else ""
            )
        )

    def plan_review_content(
        self, verdict: str = "pending", *, blob: str | None = None,
        cycle: int = 1, revision: str = "P1",
    ) -> str:
        blob = blob or ("b" * 40)
        evidence = "" if verdict == "pending" else "evidence/plan-review-R01.md"
        return (
            'workstream_id = "sample-workstream"\n'
            f'plan_revision = "{revision}"\n'
            f'planning_cycle = {cycle}\n'
            'attempt = "R01"\n'
            f'verdict = "{verdict}"\n'
            f'evidence_path = "{evidence}"\n'
            '[subject]\n'
            'class = "git_blob"\n'
            'repository = "owner/repo"\n'
            f'commit = "{"a" * 40}"\n'
            'path = "planning/MASTER_PLAN.md"\n'
            f'blob = "{blob}"\n'
            '[acceptance]\n'
            'class = "authority"\n'
            'path = "requirements/REQUIREMENTS.md"\n'
            '[independence]\n'
            'materially_produced_or_repaired_subject = false\n'
            'basis = "Fresh semantic review context."\n'
        )

    def tracker_content(self, state: str) -> str:
        issue = 7 if state == "linked" else 0
        candidates = "[7, 8]" if state == "ambiguous" else "[]"
        readback = {
            "discovery": "pending",
            "create_pending_readback": "uncertain",
            "linked": "verified",
            "ambiguous": "uncertain",
            "unavailable": "not_applicable",
        }[state]
        return (
            'workstream_id = "sample-workstream"\n'
            'provider = "github"\n'
            'repository = "owner/repo"\n'
            'dedup_key = "project-workflow:sample-workstream"\n'
            f'state = "{state}"\n'
            f'issue_number = {issue}\n'
            f'candidate_issue_numbers = {candidates}\n'
            f'readback_state = "{readback}"\n'
            'final_pr = 0\n'
        )

    def issue_research_content(self, subject: str) -> str:
        return (
            'state = "consumed"\n'
            'workstream_id = "sample-workstream"\n'
            'origin_role = "intake"\n'
            f'origin_subject = "{subject}"\n'
            'return_target = "intake"\n'
            'return_reconciliation = "applied"\n'
            'return_result = "evidence/intake-prior-art.md"\n'
            'finding = "Proportional issue-diagnosis prior art checked."\n'
            'limitations = "none"\n'
            'conflicts = "No material conflicts observed."\n'
            '[[sources]]\nclass = "official_upstream"\nstatus = "checked"\nweight = "primary"\n'
            '[[sources]]\nclass = "project_runtime"\nstatus = "checked"\nweight = "direct"\n'
            '[[sources]]\nclass = "tracker_discussion"\nstatus = "not_relevant"\nweight = "supporting"\n'
            '[[sources]]\nclass = "practitioner_community"\nstatus = "unavailable"\nweight = "supporting"\n'
        )

    def test_issue_diagnosis_requires_exact_consumed_prior_art_research(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_intake(project, (
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
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "intake"))
            self.assertIn("prior-art Research", routed.reason)

            self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                self.issue_research_content("repair:v1"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "intake"))
            self.assertIn("exact current repair subject", routed.reason)

            research_path = project / "implementation/workstreams/sample-workstream/RESEARCH.toml"
            research_path.write_text(self.issue_research_content("repair:v2"))
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "intake"))
            self.assertIn("persist its exact subject/result binding", routed.reason)

            intake_path = project / "implementation/workstreams/sample-workstream/INTAKE.toml"
            intake_path.write_text(
                intake_path.read_text().replace(
                    'diagnosis_prior_art_subject = ""\n'
                    'diagnosis_prior_art_result = ""\n',
                    'diagnosis_prior_art_subject = "repair:v2"\n'
                    'diagnosis_prior_art_result = "evidence/intake-prior-art.md"\n',
                )
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "issue_alignment"))
        finally:
            temp.cleanup()

    def test_issue_without_post_diagnosis_response_is_real_alignment_stop(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_intake(project, (
                'workstream_id = "sample-workstream"\n'
                'kind = "issue"\n'
                'state = "active"\n'
                'diagnosis_revision = 1\n'
                'repair_subject = "repair:v1"\n'
                'diagnosis_prior_art_subject = "repair:v1"\n'
                'diagnosis_prior_art_result = "evidence/intake-prior-art.md"\n'
                'response_kind = "none"\n'
                'response_observed = false\n'
                'alignment_state = "pending"\n'
                'alignment_subject = ""\n'
                'micro_fix_candidate = false\n'
            ))
            self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                self.issue_research_content("repair:v1"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "issue_alignment"))
            self.assertEqual(routed.owner_module, "workflow/INTAKE.md")
            self.assertNotIn(f"project:{BOARD}", routed.read_set)
        finally:
            temp.cleanup()

    def test_issue_question_continues_alignment_without_authorizing_repair(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_intake(project, (
                'workstream_id = "sample-workstream"\n'
                'kind = "issue"\n'
                'state = "active"\n'
                'diagnosis_revision = 1\n'
                'repair_subject = "repair:v1"\n'
                'diagnosis_prior_art_subject = "repair:v1"\n'
                'diagnosis_prior_art_result = "evidence/intake-prior-art.md"\n'
                'response_kind = "question"\n'
                'response_observed = true\n'
                'alignment_state = "pending"\n'
                'alignment_subject = ""\n'
                'micro_fix_candidate = false\n'
            ))
            self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                self.issue_research_content("repair:v1"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "brainstorming"))
            self.assertEqual(routed.owner_module, "workflow/BRAINSTORMING.md")
            self.assertNotIn(f"project:{BOARD}", routed.read_set)
        finally:
            temp.cleanup()

    def test_later_brainstorming_research_does_not_erase_issue_diagnosis_prior_art(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_intake(project, (
                'workstream_id = "sample-workstream"\n'
                'kind = "issue"\n'
                'state = "active"\n'
                'diagnosis_revision = 2\n'
                'repair_subject = "repair:v2"\n'
                'diagnosis_prior_art_subject = "repair:v2"\n'
                'diagnosis_prior_art_result = "evidence/intake-prior-art.md"\n'
                'response_kind = "question"\n'
                'response_observed = true\n'
                'alignment_state = "pending"\n'
                'alignment_subject = ""\n'
                'micro_fix_candidate = false\n'
            ))
            later_research = (
                'state = "consumed"\n'
                'workstream_id = "sample-workstream"\n'
                'origin_role = "brainstorming"\n'
                'origin_subject = "repair:v2:question"\n'
                'return_target = "brainstorming"\n'
                'return_reconciliation = "applied"\n'
                'return_result = "evidence/brainstorm-followup.md"\n'
                'finding = "Follow-up fact checked."\n'
                'limitations = "none"\n'
                'conflicts = "No material conflicts observed."\n'
                '[[sources]]\nclass = "official_upstream"\nstatus = "checked"\nweight = "primary"\n'
                '[[sources]]\nclass = "project_runtime"\nstatus = "checked"\nweight = "direct"\n'
                '[[sources]]\nclass = "tracker_discussion"\nstatus = "not_relevant"\nweight = "supporting"\n'
                '[[sources]]\nclass = "practitioner_community"\nstatus = "unavailable"\nweight = "supporting"\n'
            )
            self.install_state_record(
                project, "research", "research", "RESEARCH.toml", later_research,
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "brainstorming"))
            self.assertNotIn("diagnosis prior-art Research", routed.reason)
        finally:
            temp.cleanup()


    def test_completed_authorized_issue_continues_to_existing_board(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_intake(project, (
                'workstream_id = "sample-workstream"\n'
                'kind = "issue"\n'
                'state = "complete"\n'
                'diagnosis_revision = 2\n'
                'repair_subject = "repair:v2"\n'
                'diagnosis_prior_art_subject = "repair:v2"\n'
                'diagnosis_prior_art_result = "evidence/intake-prior-art.md"\n'
                'response_kind = "authorization"\n'
                'response_observed = true\n'
                'alignment_state = "authorized"\n'
                'alignment_subject = "repair:v2"\n'
                'micro_fix_candidate = true\n'
            ))
            self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                self.issue_research_content("repair:v2"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
            self.assertIn("project:implementation/workstreams/sample-workstream/INTAKE.toml", routed.read_set)
            self.assertIn(f"project:{BOARD}", routed.read_set)
        finally:
            temp.cleanup()


    def test_completed_preboard_intake_routes_without_manufacturing_board(self) -> None:
        cases = (
            (
                'workstream_id = "sample-workstream"\n'
                'kind = "feature"\n'
                'state = "complete"\n'
                'diagnosis_revision = 0\n'
                'repair_subject = ""\n'
                'diagnosis_prior_art_subject = ""\n'
                'diagnosis_prior_art_result = ""\n'
                'response_kind = "none"\n'
                'response_observed = false\n'
                'alignment_state = "not_required"\n'
                'alignment_subject = ""\n'
                'micro_fix_candidate = false\n',
                ("route", "brainstorming"),
            ),
            (
                'workstream_id = "sample-workstream"\n'
                'kind = "issue"\n'
                'state = "complete"\n'
                'diagnosis_revision = 2\n'
                'repair_subject = "repair:v2"\n'
                'diagnosis_prior_art_subject = "repair:v2"\n'
                'diagnosis_prior_art_result = "evidence/intake-prior-art.md"\n'
                'response_kind = "authorization"\n'
                'response_observed = true\n'
                'alignment_state = "authorized"\n'
                'alignment_subject = "repair:v2"\n'
                'micro_fix_candidate = true\n',
                ("route", "execution_prep"),
            ),
        )
        for intake_content, expected in cases:
            temp, project = self.copy_fixture()
            try:
                self.install_intake(project, intake_content)
                if 'kind = "issue"' in intake_content:
                    self.install_state_record(
                        project, "research", "research", "RESEARCH.toml",
                        self.issue_research_content("repair:v2"),
                    )
                workstream = project / MANIFEST
                text = workstream.read_text()
                text = text.replace(
                    '\n[task_board]\nclass = "task_board"\npath = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"\n',
                    '\n',
                )
                workstream.write_text(text)
                routed = select_route(project, [MANIFEST], package_root=ROOT)
                self.assertEqual((routed.disposition, routed.obligation), expected)
                self.assertNotIn(f"project:{BOARD}", routed.read_set)
            finally:
                temp.cleanup()

    def test_stale_issue_alignment_fails_closed_to_recovery(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_intake(project, (
                'workstream_id = "sample-workstream"\n'
                'kind = "issue"\n'
                'state = "complete"\n'
                'diagnosis_revision = 3\n'
                'repair_subject = "repair:v3"\n'
                'diagnosis_prior_art_subject = "repair:v3"\n'
                'diagnosis_prior_art_result = "evidence/intake-prior-art.md"\n'
                'response_kind = "authorization"\n'
                'response_observed = true\n'
                'alignment_state = "authorized"\n'
                'alignment_subject = "repair:v2"\n'
                'micro_fix_candidate = true\n'
            ))
            self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                self.issue_research_content("repair:v3"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
        finally:
            temp.cleanup()


    def test_active_and_completed_research_route_to_exact_owner(self) -> None:
        base = (
            'workstream_id = "sample-workstream"\n'
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
            '[[sources]]\nclass = "practitioner_community"\nstatus = "pending"\nweight = "supporting"\n'
        )
        temp, project = self.copy_fixture()
        try:
            self.install_state_record(project, "research", "research", "RESEARCH.toml", 'state = "active"\n' + base)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "research"))
            self.assertNotIn(f"project:{BOARD}", routed.read_set)
        finally:
            temp.cleanup()

        complete = (
            'state = "complete"\n'
            'workstream_id = "sample-workstream"\n'
            'origin_role = "brainstorming"\n'
            'origin_subject = "scope-a@1"\n'
            'return_target = "brainstorming"\n'
            'return_reconciliation = "pending"\n'
            'return_result = ""\n'
            'finding = "bounded finding"\n'
            'limitations = "none"\n'
            'conflicts = "No material conflicts observed."\n'
            '[[sources]]\nclass = "official_upstream"\nstatus = "checked"\nweight = "primary"\n'
            '[[sources]]\nclass = "project_runtime"\nstatus = "checked"\nweight = "direct"\n'
            '[[sources]]\nclass = "tracker_discussion"\nstatus = "not_relevant"\nweight = "supporting"\n'
            '[[sources]]\nclass = "practitioner_community"\nstatus = "unavailable"\nweight = "supporting"\n'
        )
        temp, project = self.copy_fixture()
        try:
            self.install_state_record(project, "research", "research", "RESEARCH.toml", complete)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "brainstorming"))
            self.assertIn("reconciled", routed.reason)
        finally:
            temp.cleanup()

    def test_brainstorming_requires_challenge_and_exact_definition_promotion(self) -> None:
        temp, project = self.copy_fixture()
        try:
            ready = (
                'workstream_id = "sample-workstream"\n'
                'scope_id = "scope-a"\n'
                'revision = 2\n'
                'state = "ready_for_definition"\n'
                'challenge_audit = "green"\n'
                'explicit_user_stop = false\n'
                'promotion_state = "pending"\n'
                'promotion_subject = ""\n'
            )
            self.install_state_record(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", ready)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "definition_promotion"))
            self.assertEqual(routed.subject, "scope-a@2")
        finally:
            temp.cleanup()

        temp, project = self.copy_fixture()
        try:
            promoted = (
                'workstream_id = "sample-workstream"\n'
                'scope_id = "scope-a"\n'
                'revision = 2\n'
                'state = "promoted"\n'
                'challenge_audit = "green"\n'
                'explicit_user_stop = false\n'
                'promotion_state = "authorized"\n'
                'promotion_subject = "scope-a@2"\n'
            )
            self.install_state_record(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", promoted)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "definition"))
        finally:
            temp.cleanup()

    def test_definition_green_stops_at_premium_a_before_planning(self) -> None:
        temp, project = self.copy_fixture()
        try:
            promoted = (
                'workstream_id = "sample-workstream"\n'
                'scope_id = "scope-a"\n'
                'revision = 2\n'
                'state = "promoted"\n'
                'challenge_audit = "green"\n'
                'explicit_user_stop = false\n'
                'promotion_state = "authorized"\n'
                'promotion_subject = "scope-a@2"\n'
            )
            self.install_state_record(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", promoted)
            definition = (
                'workstream_id = "sample-workstream"\n'
                'source_scope_subject = "scope-a@2"\n'
                'revision = "R1"\n'
                'state = "green"\n'
                'completeness_audit = "green"\n'
                'premium_a = "due"\n'
                'decisions = [{ class = "authority", path = "decisions/ADR-001.md" }]\n'
                '[requirements]\nclass = "authority"\npath = "requirements/REQUIREMENTS.md"\n'
            )
            self.install_state_record(project, "definition", "definition", "DEFINITION.toml", definition)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "premium_A"))
            self.assertEqual(routed.owner_module, "workflow/DEFINITION.md")
            self.assertIn("best available model/context", routed.reason)
            self.assertIn("package:workflow/USER_STOP.md", routed.read_set)
        finally:
            temp.cleanup()

    def test_definition_source_mismatch_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            promoted = (
                'workstream_id = "sample-workstream"\n'
                'scope_id = "scope-a"\n'
                'revision = 2\n'
                'state = "promoted"\n'
                'challenge_audit = "green"\n'
                'explicit_user_stop = false\n'
                'promotion_state = "authorized"\n'
                'promotion_subject = "scope-a@2"\n'
            )
            self.install_state_record(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", promoted)
            definition = (
                'workstream_id = "sample-workstream"\n'
                'source_scope_subject = "scope-a@1"\n'
                'revision = "R1"\n'
                'state = "active"\n'
                'completeness_audit = "pending"\n'
                'premium_a = "not_due"\n'
                'decisions = []\n'
                '[requirements]\nclass = "authority"\npath = "requirements/REQUIREMENTS.md"\n'
            )
            self.install_state_record(project, "definition", "definition", "DEFINITION.toml", definition)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
        finally:
            temp.cleanup()


    def test_planning_routes_after_exact_premium_a_satisfaction(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "planning"))

            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="draft"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "planning"))
        finally:
            temp.cleanup()

    def test_frozen_plan_stops_at_b_then_routes_fresh_plan_review(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="frozen", premium_b="due"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "premium_B"))
            self.assertIn("best-available", routed.reason)
            self.assertIn("package:workflow/USER_STOP.md", routed.read_set)
        finally:
            temp.cleanup()

        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="frozen", premium_b="satisfied"),
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("pending"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "plan_review"))
            self.assertEqual(routed.owner_module, "workflow/PLAN_REVIEW.md")
        finally:
            temp.cleanup()

    def test_green_plan_review_consumes_to_c_before_execution_prep(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="frozen", premium_b="satisfied"),
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("green"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "planning"))
            self.assertIn("consumed", routed.reason)
        finally:
            temp.cleanup()

        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="approved", premium_b="satisfied", premium_c="due"),
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("green"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "premium_C"))
            self.assertIn("lighter/cheaper", routed.reason)
            self.assertIn("package:workflow/USER_STOP.md", routed.read_set)
        finally:
            temp.cleanup()

        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="approved", premium_b="satisfied", premium_c="satisfied"),
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("green"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            # Co-bound live Board takes precedence over plan JIT: fixture Board
            # holds M01-T04 in_progress without a result, so Execution owns it.
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
            self.assertEqual(routed.subject, "M01-T04")
            self.assertIn(f"project:{BOARD}", routed.read_set)
        finally:
            temp.cleanup()

    def test_material_replan_repeats_a_b_review_c_and_editorial_exemption_skips_new_review(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            planning_path = project / "implementation/workstreams/sample-workstream/PLANNING.toml"
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="draft", cycle=2, revision="P2", premium_a="due"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "premium_A"))
            self.assertEqual(routed.subject, "definition:R1|planning-cycle:2")
            self.assertIn("best available model/context", routed.reason)
            self.assertIn("package:workflow/USER_STOP.md", routed.read_set)

            planning_path.write_text(
                self.planning_content(state="draft", cycle=2, revision="P2", premium_a="satisfied")
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "planning"))

            planning_path.write_text(
                self.planning_content(
                    state="frozen", cycle=2, revision="P2",
                    premium_a="satisfied", premium_b="due",
                )
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "premium_B"))
            self.assertIn("package:workflow/USER_STOP.md", routed.read_set)

            planning_path.write_text(
                self.planning_content(
                    state="frozen", cycle=2, revision="P2",
                    premium_a="satisfied", premium_b="satisfied",
                )
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("green", cycle=2, revision="P2"),
            )
            review_path = project / "implementation/workstreams/sample-workstream/PLAN_REVIEW.toml"
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "planning"))

            planning_path.write_text(
                self.planning_content(
                    state="approved", cycle=2, revision="P2",
                    premium_a="satisfied", premium_b="satisfied", premium_c="due",
                )
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "premium_C"))
            self.assertIn("package:workflow/USER_STOP.md", routed.read_set)

            planning_path.write_text(
                self.planning_content(
                    state="approved", cycle=2, revision="P2",
                    premium_a="satisfied", premium_b="satisfied", premium_c="satisfied",
                )
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            # Co-bound live Board preempts plan JIT; M01-T04 is in_progress.
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
            self.assertIn(f"project:{BOARD}", routed.read_set)

            base = f"owner/repo@{'a' * 40}:planning/MASTER_PLAN.md@{'b' * 40}"
            exemption_classification = self.install_editorial_classification(
                project, cycle=2, revision="P2"
            )
            planning_path.write_text(
                self.planning_content(
                    state="approved", cycle=2, revision="P2", blob="c" * 40,
                    premium_a="satisfied", premium_b="satisfied", premium_c="satisfied",
                    gate_subject=base, review_mode="editorial_exempt",
                    exemption_basis="Wording only; strategy, milestones, coverage and gates unchanged.",
                    exemption_base_subject=base,
                    exemption_classification=exemption_classification,
                )
            )
            review_path.write_text(self.plan_review_content("green", cycle=2, revision="P2"))
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            # Valid editorial exemption still dispatches the co-bound live Board.
            self.assertNotEqual(routed.disposition, "recovery", routed.reason)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
            self.assertEqual(routed.subject, "M01-T04")
            self.assertIn(f"project:{BOARD}", routed.read_set)
        finally:
            temp.cleanup()

    def test_editorial_basis_without_immutable_classification_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            base = f"owner/repo@{'a' * 40}:planning/MASTER_PLAN.md@{'b' * 40}"
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(
                    state="approved", cycle=2, revision="P2", blob="c" * 40,
                    premium_b="satisfied", premium_c="satisfied",
                    gate_subject=base, review_mode="editorial_exempt",
                    exemption_basis="wording only",
                    exemption_base_subject=base,
                ),
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("green", cycle=2, revision="P2"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("classification", routed.reason)
        finally:
            temp.cleanup()

    def test_editorial_classification_wrong_blob_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            base = f"owner/repo@{'a' * 40}:planning/MASTER_PLAN.md@{'b' * 40}"
            proof = list(self.install_editorial_classification(
                project, cycle=2, revision="P2"
            ))
            proof[3] = "d" * 40
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(
                    state="approved", cycle=2, revision="P2", blob="c" * 40,
                    premium_b="satisfied", premium_c="satisfied",
                    gate_subject=base, review_mode="editorial_exempt",
                    exemption_basis="wording only",
                    exemption_base_subject=base,
                    exemption_classification=tuple(proof),
                ),
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("green", cycle=2, revision="P2"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("blob does not match", routed.reason)
        finally:
            temp.cleanup()

    def test_stale_premium_cycle_and_wrong_review_subject_fail_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(
                    state="draft", cycle=2,
                    premium_a_subject="definition:R1|planning-cycle:1",
                ),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
        finally:
            temp.cleanup()

        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="frozen", premium_b="satisfied"),
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("pending", blob="c" * 40),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
        finally:
            temp.cleanup()

    def test_premium_b_satisfied_without_plan_review_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="frozen", premium_b="satisfied"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
        finally:
            temp.cleanup()

    def install_editorial_classification(
        self,
        project: Path,
        *,
        cycle: int = 1,
        revision: str = "P1",
        base_blob: str = "b" * 40,
        changed_blob: str = "c" * 40,
    ) -> tuple[str, str, str, str]:
        path = (
            "implementation/workstreams/sample-workstream/"
            f"planning_classifications/{revision}-E01.toml"
        )
        target = project / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            'workstream_id = "sample-workstream"\n'
            f'planning_cycle = {cycle}\n'
            f'plan_revision = "{revision}"\n'
            'verdict = "green"\n'
            'classification = "editorial_only"\n'
            'inspected_diff_evidence = "Exact immutable old/new plan blobs were semantically compared; only editorial wording changed."\n'
            '[base_subject]\n'
            'class = "git_blob"\n'
            'repository = "owner/repo"\n'
            f'commit = "{"a" * 40}"\n'
            'path = "planning/MASTER_PLAN.md"\n'
            f'blob = "{base_blob}"\n'
            '[changed_subject]\n'
            'class = "git_blob"\n'
            'repository = "owner/repo"\n'
            f'commit = "{"a" * 40}"\n'
            'path = "planning/MASTER_PLAN.md"\n'
            f'blob = "{changed_blob}"\n'
            '[unchanged]\n'
            'strategy = true\n'
            'milestone_topology = true\n'
            'requirement_coverage = true\n'
            'gates = true\n'
            'acceptance_semantics = true\n'
            '[independence]\n'
            'materially_produced_or_repaired_changed_subject = false\n'
            'basis = "Fresh semantic classifier did not author or repair the changed subject."\n'
        )
        if not (project / ".git").exists():
            subprocess.run(["git", "init", "-q", str(project)], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.email", "fixture@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.name", "Fixture"], check=True)
        subprocess.run(["git", "-C", str(project), "add", path], check=True)
        subprocess.run(["git", "-C", str(project), "commit", "-q", "-m", f"fixture {revision} editorial proof"], check=True)
        commit = subprocess.run(
            ["git", "-C", str(project), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        blob = subprocess.run(
            ["git", "-C", str(project), "rev-parse", f"HEAD:{path}"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        return ("owner/router-fixture", commit, path, blob)

    def install_approved_plan(self, project: Path) -> None:
        self.install_green_definition(project)
        self.install_state_record(
            project, "planning", "planning", "PLANNING.toml",
            self.planning_content(state="approved", premium_b="satisfied", premium_c="satisfied"),
        )
        self.install_state_record(
            project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
            self.plan_review_content("green"),
        )

    def install_editorial_plan(self, project: Path) -> None:
        self.install_green_definition(project)
        base = f"owner/repo@{'a' * 40}:planning/MASTER_PLAN.md@{'b' * 40}"
        exemption_classification = self.install_editorial_classification(project)
        self.install_state_record(
            project, "planning", "planning", "PLANNING.toml",
            self.planning_content(
                state="approved", blob="c" * 40,
                premium_b="satisfied", premium_c="satisfied",
                gate_subject=base, review_mode="editorial_exempt",
                exemption_basis="Wording only; strategy, milestones, coverage and gates unchanged.",
                exemption_base_subject=base,
                exemption_classification=exemption_classification,
            ),
        )
        self.install_state_record(
            project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
            self.plan_review_content("green"),
        )

    def remove_board_locator(self, project: Path) -> None:
        workstream = project / MANIFEST
        text = workstream.read_text()
        text = text.replace(
            '\n[task_board]\nclass = "task_board"\npath = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"\n',
            '\n',
        )
        workstream.write_text(text)

    def test_approved_plan_with_live_board_dispatches_board_precedence(self) -> None:
        cases = (
            ("no_result", None, "none", ("route", "execution")),
            ("result_no_review", None, "none_result", ("route", "result_reconciliation")),
            ("pending", "pending", "required", ("route", "review")),
            ("green", "green", "required", ("route", "post_review_finalization")),
            ("red", "red", "required", ("route", "execution_resolution")),
        )
        for name, verdict, requirement, expected in cases:
            temp, project = self.copy_fixture()
            try:
                with self.subTest(case=name):
                    self.install_approved_plan(project)
                    if name != "no_result":
                        review_requirement = "none" if requirement == "none_result" else requirement
                        self.install_reviewable_result(project, review_requirement)
                        if verdict is not None:
                            self.add_review_attempt(project, verdict)
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                    self.assertEqual((routed.disposition, routed.obligation), expected)
                    self.assertEqual(routed.subject, "M01-T04")
                    self.assertIn(f"project:{BOARD}", routed.read_set)
                    if verdict == "red":
                        self.assertEqual(routed.owner_module, "workflow/RECOVERY.md")
            finally:
                temp.cleanup()

    def test_editorial_exempt_with_live_board_dispatches_board_precedence(self) -> None:
        for verdict, expected, owner in (
            (None, ("route", "execution"), "workflow/EXECUTION.md"),
            ("red", ("route", "execution_resolution"), "workflow/RECOVERY.md"),
        ):
            temp, project = self.copy_fixture()
            try:
                with self.subTest(verdict=verdict):
                    self.install_editorial_plan(project)
                    if verdict is not None:
                        self.install_reviewable_result(project, "required")
                        self.add_review_attempt(project, verdict)
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                    self.assertNotEqual(routed.disposition, "recovery", routed.reason)
                    self.assertEqual((routed.disposition, routed.obligation), expected)
                    self.assertEqual(routed.owner_module, owner)
                    self.assertEqual(routed.subject, "M01-T04")
                    self.assertIn(f"project:{BOARD}", routed.read_set)
            finally:
                temp.cleanup()

    def test_cobound_invalid_board_fails_closed(self) -> None:
        for plan in ("approved", "editorial"):
            temp, project = self.copy_fixture()
            try:
                with self.subTest(plan=plan):
                    if plan == "approved":
                        self.install_approved_plan(project)
                    else:
                        self.install_editorial_plan(project)
                    board = project / BOARD
                    board.write_text(board.read_text().replace(
                        'branch = "feat/sample-workstream"', 'branch = "feat/other"',
                    ))
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                    self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            finally:
                temp.cleanup()

    def test_approved_plan_with_seams_validates_cobound_board_decisions(self) -> None:
        seams = (
            '[[seams]]\n'
            'id = "BOOT-A"\n'
            'class = "required_seam"\n'
            'intent = "Review closure stays standalone."\n'
            '[[seams]]\n'
            'id = "helper-less-derivation"\n'
            'class = "preferred_seam"\n'
            'intent = "Helper-less derivation is its own outcome."\n'
        )
        preserved = (
            '[[seam_decisions]]\n'
            'seam_id = "BOOT-A"\n'
            'decision = "preserved"\n'
            '[[seam_decisions]]\n'
            'seam_id = "helper-less-derivation"\n'
            'decision = "preserved"\n'
        )
        merged_required = preserved.replace(
            'seam_id = "BOOT-A"\ndecision = "preserved"',
            'seam_id = "BOOT-A"\ndecision = "merged"',
        )
        cases = (
            ("valid", preserved, ("route", "execution"), None),
            ("required_merge", merged_required, ("recovery", "recovery_boundary"),
             "must not merge a required_seam"),
            ("missing_decision", "", ("recovery", "recovery_boundary"),
             "require durable per-seam JIT decisions"),
        )
        for name, decisions, expected, reason in cases:
            temp, project = self.copy_fixture()
            try:
                with self.subTest(case=name):
                    self.install_approved_plan(project)
                    planning = project / "implementation/workstreams/sample-workstream/PLANNING.toml"
                    planning.write_text(planning.read_text() + seams)
                    if decisions:
                        board = project / BOARD
                        board.write_text(board.read_text() + decisions)
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                    self.assertEqual((routed.disposition, routed.obligation), expected)
                    if reason is None:
                        self.assertEqual(routed.subject, "M01-T04")
                    else:
                        self.assertIn(reason, routed.reason)
                    self.assertIn(f"project:{BOARD}", routed.read_set)
            finally:
                temp.cleanup()

    def test_plan_gate_without_board_owns_plan_jit(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_approved_plan(project)
            self.remove_board_locator(project)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution_prep"))
            self.assertEqual(routed.owner_module, "workflow/EXECUTION_PREP.md")
            self.assertNotIn(f"project:{BOARD}", routed.read_set)
        finally:
            temp.cleanup()

        temp, project = self.copy_fixture()
        try:
            self.install_editorial_plan(project)
            self.remove_board_locator(project)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertNotEqual(routed.disposition, "recovery", routed.reason)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution_prep"))
            self.assertIn("Exact independent GREEN editorial-only classification", routed.reason)
            self.assertNotIn(f"project:{BOARD}", routed.read_set)
        finally:
            temp.cleanup()


    def test_tracker_discovery_and_pending_create_route_to_github_issues(self) -> None:
        for state, expected_reason in (
            ("discovery", "discovery/dedup"),
            ("create_pending_readback", "readback before any retry"),
        ):
            temp, project = self.copy_fixture()
            try:
                self.install_state_record(
                    project, "tracker", "tracker", "TRACKER.toml",
                    self.tracker_content(state),
                )
                routed = select_route(project, [MANIFEST], package_root=ROOT)
                self.assertEqual((routed.disposition, routed.obligation), ("route", "github_issues"))
                self.assertEqual(routed.owner_module, "workflow/GITHUB_ISSUES.md")
                self.assertIn(expected_reason, routed.reason)
                self.assertNotIn(f"project:{BOARD}", routed.read_set)
            finally:
                temp.cleanup()

    def test_tracker_ambiguity_fails_closed_without_duplicate_create(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_state_record(
                project, "tracker", "tracker", "TRACKER.toml",
                self.tracker_content("ambiguous"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("creating another tracker is forbidden", routed.reason)
        finally:
            temp.cleanup()

    def test_linked_or_unavailable_tracker_does_not_become_authority(self) -> None:
        for state in ("linked", "unavailable"):
            temp, project = self.copy_fixture()
            try:
                self.install_state_record(
                    project, "tracker", "tracker", "TRACKER.toml",
                    self.tracker_content(state),
                )
                routed = select_route(project, [MANIFEST], package_root=ROOT)
                self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
                self.assertIn(f"project:{BOARD}", routed.read_set)
            finally:
                temp.cleanup()

    def test_missing_or_ambiguous_selection_routes_to_recovery(self) -> None:
        for selected in ([], [MANIFEST, MANIFEST]):
            with self.subTest(selected=selected):
                routed = select_route(FIXTURE, selected, package_root=ROOT)
                self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
                self.assertIn("package:workflow/RECOVERY.md", routed.read_set)

    def test_invalid_binding_and_legacy_policy_fail_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            board = project / BOARD
            original = board.read_text()
            board.write_text(original.replace('branch = "feat/sample-workstream"', 'branch = "feat/other"'))
            self.assertEqual(select_route(project, [MANIFEST], package_root=ROOT).disposition, "recovery")

            board.write_text(original.replace("revision = 3", 'revision = 3\nexecution_policy = "chatgpt_only"'))
            self.assertEqual(select_route(project, [MANIFEST], package_root=ROOT).disposition, "recovery")
        finally:
            temp.cleanup()

    def test_missing_cross_workstream_and_escape_locators_fail_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            workstream = project / MANIFEST
            original = workstream.read_text()
            workstream.write_text(original.replace(
                "implementation/workstreams/sample-workstream/TASK_BOARD.toml",
                "implementation/workstreams/other/TASK_BOARD.toml",
            ))
            self.assertEqual(select_route(project, [MANIFEST], package_root=ROOT).disposition, "recovery")
            self.assertEqual(select_route(project, ["../outside.toml"], package_root=ROOT).disposition, "recovery")
        finally:
            temp.cleanup()

    def test_active_card_routes_to_runtime_neutral_execution(self) -> None:
        routed = select_route(FIXTURE, [MANIFEST], package_root=ROOT)
        self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
        self.assertIn("runtime-neutral implementation", routed.reason)
        self.assertNotEqual(routed.disposition, "real_stop")

    def test_durable_semantic_result_routes_to_reconciliation_without_replay(self) -> None:
        temp, project = self.copy_fixture()
        try:
            result_path = self.install_reviewable_result(project, "none")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "result_reconciliation"))
            self.assertIn("do not replay", routed.reason)
            self.assertIn(f"project:{result_path}", routed.read_set)
        finally:
            temp.cleanup()

    def result_version_content(self, *, subject: str) -> str:
        return (
            "# Card Result\n"
            "- Card ID: M01-T04\n"
            f"- Implementation subject: {subject}\n"
            "- Evidence refs: implementation/workstreams/sample-workstream/evidence/M01-T04.md\n"
            "- Tests/readback summary: GREEN\n"
        )

    def install_reviewable_result(self, project: Path, review_requirement: str) -> str:
        result_path = "implementation/workstreams/sample-workstream/results/M01-T04.md"
        (project / CARD).write_text(self.task_card_content(review_requirement=review_requirement))
        authority = project / "requirements" / "REQUIREMENTS.md"
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text("# Accepted authority\n")
        evidence_dir = project / "implementation/workstreams/sample-workstream/evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        (evidence_dir / "M01-T04.md").write_text("# Verified evidence\n")
        result_file = project / result_path
        result_file.parent.mkdir(parents=True, exist_ok=True)
        result_file.write_text(
            self.result_version_content(subject="owner/repo@commit:" + ("a" * 40))
        )
        commit, blob = self.git_identity_for(project, result_path)
        board = project / BOARD
        board.write_text(
            board.read_text()
            + '\n[cards.result]\nclass = "result"\n'
            + f'path = "{result_path}"\n'
            + f'commit = "{commit}"\n'
            + f'blob = "{blob}"\n'
        )
        return result_path

    def add_review_attempt(
        self,
        project: Path,
        verdict: str,
        attempt: str = "R01",
        *,
        review_kind: str | None = "discovery",
        source_discovery_attempt: str = "",
        discovery_complete: bool = False,
        finding_ids: tuple[str, ...] = (),
        defect_class_ids: tuple[str, ...] = (),
        failed_defect_class_ids: tuple[str, ...] = (),
        review_scope: str = "card",
        review_epoch: str = "E01",
        epoch_reset_basis: str = "",
        post_convergence_validation: bool = False,
        convergence_basis: str = "",
        subject_commit: str | None = None,
        subject_blob: str | None = None,
    ) -> str:
        review_path = f"implementation/workstreams/sample-workstream/reviews/M01-T04-{attempt}.toml"
        locator = f'{{ class = "review_attempt", path = "{review_path}" }}'
        board = project / BOARD
        board_text = board.read_text()
        lines = board_text.splitlines()
        for index, line in enumerate(lines):
            if line.startswith("review_attempts = ["):
                existing = line.removeprefix("review_attempts = [").removesuffix("]")
                lines[index] = f"review_attempts = [{existing}, {locator}]"
                break
        else:
            board_text = board_text.replace(
                'status = "in_progress"\n',
                'status = "in_progress"\n'
                f'review_attempts = [{locator}]\n',
                1,
            )
            lines = board_text.splitlines()
        board.write_text("\n".join(lines) + "\n")

        path = project / review_path
        path.parent.mkdir(parents=True, exist_ok=True)
        evidence = "" if verdict in {"pending", "in_progress"} else f"implementation/workstreams/sample-workstream/evidence/review-{attempt}.md"
        if evidence:
            evidence_path = project / evidence
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            evidence_path.write_text("# Review evidence\n")
        board_commit, board_blob = self.board_result_identity(project)
        commit = subject_commit or board_commit
        blob = subject_blob or board_blob
        extra = ""
        if review_kind == "discovery" and verdict in {"green", "red"}:
            discovery_complete = True
            if verdict == "red":
                if not finding_ids:
                    finding_ids = ("F-default",)
                if not defect_class_ids:
                    defect_class_ids = ("class-default",)
        if review_kind == "closure_verification" and not defect_class_ids:
            defect_class_ids = ("class-default",)
        if review_kind == "closure_verification" and verdict == "red" and not failed_defect_class_ids:
            failed_defect_class_ids = defect_class_ids
        if review_kind is not None:
            ids = ", ".join(f'"{item}"' for item in finding_ids)
            classes = ", ".join(f'"{item}"' for item in defect_class_ids)
            failed_classes = ", ".join(f'"{item}"' for item in failed_defect_class_ids)
            extra = (
                f'review_kind = "{review_kind}"\n'
                f'source_discovery_attempt = "{source_discovery_attempt}"\n'
                f'discovery_complete = {"true" if discovery_complete else "false"}\n'
                f'material_finding_ids = [{ids}]\n'
                f'review_scope = "{review_scope}"\n'
                f'review_epoch = "{review_epoch}"\n'
                f'epoch_reset_basis = "{epoch_reset_basis}"\n'
                f'material_defect_class_ids = [{classes}]\n'
                f'failed_material_defect_class_ids = [{failed_classes}]\n'
                f'post_convergence_validation = {"true" if post_convergence_validation else "false"}\n'
                f'convergence_basis = "{convergence_basis}"\n'
            )
            if review_kind == "discovery" and verdict == "red":
                for finding_id in finding_ids:
                    extra += (
                        "[[finding_severity]]\n"
                        f'id = "{finding_id}"\n'
                        'surface = "correctness"\n'
                        f'evidence = "{evidence}#{finding_id}"\n'
                    )
        path.write_text(
            'workstream_id = "sample-workstream"\n'
            'card_id = "M01-T04"\n'
            f'attempt = "{attempt}"\n'
            f'verdict = "{verdict}"\n'
            f'evidence_path = "{evidence}"\n'
            + extra
            + '[subject]\n'
            'class = "git_blob"\n'
            'repository = "owner/router-fixture"\n'
            f'commit = "{commit}"\n'
            'path = "implementation/workstreams/sample-workstream/results/M01-T04.md"\n'
            f'blob = "{blob}"\n'
            '[acceptance]\n'
            'class = "task_card"\n'
            f'path = "{CARD}"\n'
            '[independence]\n'
            'materially_produced_or_repaired_subject = false\n'
            'basis = "Fresh semantic reviewer context."\n'
        )
        return review_path

    def test_required_review_blocks_until_green_then_routes_finalization(self) -> None:
        for verdict, expected in (
            (None, "review_freeze"),
            ("pending", "review"),
            ("in_progress", "review"),
            ("green", "post_review_finalization"),
            ("red", "execution_resolution"),
        ):
            temp, project = self.copy_fixture()
            try:
                self.install_reviewable_result(project, "required")
                if verdict is not None:
                    self.add_review_attempt(project, verdict)
                routed = select_route(project, [MANIFEST], package_root=ROOT)
                self.assertEqual((routed.disposition, routed.obligation), ("route", expected))
            finally:
                temp.cleanup()

    def test_epoch_reset_rejects_unaccepted_authority_root_in_router(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            self.add_review_attempt(
                project,
                "red",
                "R01",
                finding_ids=("F1",),
                defect_class_ids=("class-a",),
            )
            review_path = self.add_review_attempt(
                project,
                "pending",
                "R02",
                review_epoch="E02",
                epoch_reset_basis="Claimed accepted redesign",
            )
            path = project / review_path
            text = path.read_text()
            text = text.replace(
                "[subject]\n",
                '[epoch_reset_subject]\n'
                'class = "accepted_redesign"\n'
                'repository = "owner/router-fixture"\n'
                f'commit = "{"c" * 40}"\n'
                'path = "requirements/UNACCEPTED_DRAFT.md"\n'
                f'blob = "{"d" * 40}"\n'
                "\n[subject]\n",
                1,
            )
            path.write_text(text)

            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("exact accepted authority", routed.reason)
        finally:
            temp.cleanup()

    def test_epoch_reset_rejects_fabricated_exact_accepted_subject(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            self.add_review_attempt(
                project,
                "red",
                "R01",
                finding_ids=("F1",),
                defect_class_ids=("class-a",),
            )
            review_path = self.add_review_attempt(
                project,
                "pending",
                "R02",
                review_epoch="E02",
                epoch_reset_basis="Claimed accepted redesign",
            )
            path = project / review_path
            text = path.read_text()
            text = text.replace(
                "[subject]\n",
                '[epoch_reset_subject]\n'
                'class = "accepted_redesign"\n'
                'repository = "owner/router-fixture"\n'
                f'commit = "{"c" * 40}"\n'
                f'path = "{CARD}"\n'
                f'blob = "{"d" * 40}"\n'
                "\n[subject]\n",
                1,
            )
            path.write_text(text)

            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("exact Git readback", routed.reason)
        finally:
            temp.cleanup()

    def test_preconvergence_closure_after_epoch_reset_fails_closed_in_router(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")

            source_path = self.add_review_attempt(
                project,
                "red",
                "R01",
                finding_ids=("F1",),
                defect_class_ids=("class-a",),
            )
            source = project / source_path
            source_lines = source.read_text().splitlines()
            convergence_prefixes = (
                "review_scope = ",
                "review_epoch = ",
                "epoch_reset_basis = ",
                "material_defect_class_ids = ",
                "failed_material_defect_class_ids = ",
                "post_convergence_validation = ",
                "convergence_basis = ",
            )
            source.write_text(
                "\n".join(
                    line for line in source_lines
                    if not line.startswith(convergence_prefixes)
                )
                + "\n"
            )

            self.add_review_attempt(
                project,
                "green",
                "R02",
                review_kind="closure_verification",
                source_discovery_attempt="R01",
                finding_ids=("F1",),
                defect_class_ids=("class-a",),
            )
            reset_path = self.add_review_attempt(
                project,
                "red",
                "R03",
                review_kind="closure_verification",
                source_discovery_attempt="R01",
                finding_ids=("F1",),
                defect_class_ids=("class-a",),
                failed_defect_class_ids=("class-a",),
                review_epoch="E02",
                epoch_reset_basis="Accepted Task Card redesign establishes E02.",
                subject_blob="e" * 40,
            )
            reset = project / reset_path
            board_commit, _ = self.board_result_identity(project)
            reset_text = reset.read_text().replace(
                f'commit = "{board_commit}"',
                f'commit = "{"c" * 40}"',
                1,
            )
            reset_text = reset_text.replace(
                "[subject]\n",
                '[epoch_reset_subject]\n'
                'class = "accepted_redesign"\n'
                'repository = "owner/router-fixture"\n'
                f'commit = "{"c" * 40}"\n'
                f'path = "{CARD}"\n'
                f'blob = "{"d" * 40}"\n'
                "\n[subject]\n",
                1,
            )
            reset.write_text(reset_text)

            reset_blobs = {
                ("owner/router-fixture", "c" * 40, CARD): "d" * 40,
                ("owner/router-fixture", "a" * 40, CARD): "f" * 40,
            }
            with patch(
                "tools.router.project_git_blob_reader",
                return_value=lambda repository, commit, path: reset_blobs.get(
                    (repository, commit, path)
                ),
            ):
                routed = select_route(project, [MANIFEST], package_root=ROOT)

            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("initial convergence-aware epoch", routed.reason)
        finally:
            temp.cleanup()

    def test_active_legacy_shaped_review_attempt_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            self.add_review_attempt(project, "pending", review_kind=None)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("explicit review_kind", routed.reason)
        finally:
            temp.cleanup()

    def test_green_closure_requires_all_known_findings_before_fresh_discovery(self) -> None:
        temp, project = self.copy_fixture()
        try:
            result_path = self.install_reviewable_result(project, "required")
            self.add_review_attempt(
                project,
                "red",
                "R01",
                review_kind="discovery",
                discovery_complete=True,
                finding_ids=("F1", "F2"),
            )

            _, repaired_blob = self.commit_result_version(
                project, result_path,
                self.result_version_content(subject="repaired implementation v2"),
            )
            self.add_review_attempt(
                project,
                "green",
                "R02",
                review_kind="closure_verification",
                source_discovery_attempt="R01",
                finding_ids=("F1",),
                subject_blob=repaired_blob,
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "review_freeze"))
            self.assertIn("another closure-verification", routed.reason)

            self.add_review_attempt(
                project,
                "green",
                "R03",
                review_kind="closure_verification",
                source_discovery_attempt="R01",
                finding_ids=("F2",),
                subject_blob=repaired_blob,
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "review_freeze"))
            self.assertIn("fresh full-scope discovery", routed.reason)

            self.add_review_attempt(
                project,
                "green",
                "R04",
                review_kind="discovery",
                discovery_complete=True,
                finding_ids=(),
                subject_blob=repaired_blob,
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "post_review_finalization"),
            )
        finally:
            temp.cleanup()

    def test_fifth_new_card_defect_class_routes_review_convergence(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            for index in range(5):
                discovery_id = f"R{index * 2 + 1:02d}"
                self.add_review_attempt(
                    project,
                    "red",
                    discovery_id,
                    finding_ids=(f"F{index}",),
                    defect_class_ids=(f"class-{index}",),
                )
                if index < 4:
                    self.add_review_attempt(
                        project,
                        "green",
                        f"R{index * 2 + 2:02d}",
                        review_kind="closure_verification",
                        source_discovery_attempt=discovery_id,
                        finding_ids=(f"F{index}",),
                        defect_class_ids=(f"class-{index}",),
                    )

            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "review_convergence"))
            self.assertIn("ceiling", routed.reason)
        finally:
            temp.cleanup()

    def test_card_scope_mismatch_cannot_trigger_milestone_or_final_ceiling(self) -> None:
        for scope, discoveries in (("final", 3), ("milestone", 4)):
            with self.subTest(review_scope=scope):
                temp, project = self.copy_fixture()
                try:
                    self.install_reviewable_result(project, "required")
                    for index in range(discoveries):
                        discovery_id = f"R{index * 2 + 1:02d}"
                        self.add_review_attempt(
                            project,
                            "red",
                            discovery_id,
                            finding_ids=(f"F{index}",),
                            defect_class_ids=(f"class-{index}",),
                            review_scope=scope,
                        )
                        if index < discoveries - 1:
                            self.add_review_attempt(
                                project,
                                "green",
                                f"R{index * 2 + 2:02d}",
                                review_kind="closure_verification",
                                source_discovery_attempt=discovery_id,
                                finding_ids=(f"F{index}",),
                                defect_class_ids=(f"class-{index}",),
                                review_scope=scope,
                            )
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                    self.assertEqual(
                        (routed.disposition, routed.obligation),
                        ("recovery", "recovery_boundary"),
                    )
                    self.assertIn("expected", routed.reason)
                finally:
                    temp.cleanup()
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            for index in range(3):
                discovery_id = f"R{index * 2 + 1:02d}"
                self.add_review_attempt(
                    project,
                    "red",
                    discovery_id,
                    finding_ids=(f"F{index}",),
                    defect_class_ids=(f"class-{index}",),
                )
                if index < 2:
                    self.add_review_attempt(
                        project,
                        "green",
                        f"R{index * 2 + 2:02d}",
                        review_kind="closure_verification",
                        source_discovery_attempt=discovery_id,
                        finding_ids=(f"F{index}",),
                        defect_class_ids=(f"class-{index}",),
                    )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "execution_resolution"),
            )
        finally:
            temp.cleanup()

    def test_known_class_recurrence_does_not_consume_new_discovery_epoch(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            self.add_review_attempt(
                project, "red", "R01",
                finding_ids=("F1",), defect_class_ids=("class-a",),
            )
            self.add_review_attempt(
                project, "green", "R02",
                review_kind="closure_verification",
                source_discovery_attempt="R01",
                finding_ids=("F1",), defect_class_ids=("class-a",),
            )
            self.add_review_attempt(
                project, "red", "R03",
                finding_ids=("F2",), defect_class_ids=("class-a",),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution_resolution"))
        finally:
            temp.cleanup()

    def test_third_failed_closure_round_routes_review_convergence(self) -> None:
        temp, project = self.copy_fixture()
        try:
            result_path = self.install_reviewable_result(project, "required")
            self.add_review_attempt(
                project, "red", "R01",
                finding_ids=("F1",), defect_class_ids=("class-a",),
            )
            for attempt, version in (
                ("R02", "v2"),
                ("R03", "v3"),
                ("R04", "v4"),
            ):
                _, subject_blob = self.commit_result_version(
                    project, result_path,
                    self.result_version_content(subject=f"repair attempt {version}"),
                )
                self.add_review_attempt(
                    project,
                    "red",
                    attempt,
                    review_kind="closure_verification",
                    source_discovery_attempt="R01",
                    finding_ids=("F1",),
                    defect_class_ids=("class-a",),
                    subject_blob=subject_blob,
                )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "review_convergence"))
        finally:
            temp.cleanup()

    def test_repeated_red_closure_same_subject_does_not_consume_repair_rounds(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            self.add_review_attempt(
                project, "red", "R01",
                finding_ids=("F1",), defect_class_ids=("class-a",),
            )
            for attempt in ("R02", "R03", "R04"):
                self.add_review_attempt(
                    project,
                    "red",
                    attempt,
                    review_kind="closure_verification",
                    source_discovery_attempt="R01",
                    finding_ids=("F1",),
                    defect_class_ids=("class-a",),
                )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution_resolution"))
        finally:
            temp.cleanup()

    def test_convergence_closure_freezes_one_post_validation_and_red_routes_structural(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            for index in range(5):
                discovery_id = f"R{index * 2 + 1:02d}"
                finding = f"F{index}"
                defect = f"class-{index}"
                self.add_review_attempt(
                    project, "red", discovery_id,
                    finding_ids=(finding,), defect_class_ids=(defect,),
                )
                self.add_review_attempt(
                    project, "green", f"R{index * 2 + 2:02d}",
                    review_kind="closure_verification",
                    source_discovery_attempt=discovery_id,
                    finding_ids=(finding,), defect_class_ids=(defect,),
                )

            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "review_freeze"))
            self.assertIn("post-convergence", routed.reason)

            self.add_review_attempt(
                project,
                "red",
                "R11",
                finding_ids=("F-post",),
                defect_class_ids=("class-post",),
                post_convergence_validation=True,
                convergence_basis="Main convergence/root-cause analysis C01",
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "review_structural_resolution"),
            )
            self.assertIn("post-convergence", routed.reason)
        finally:
            temp.cleanup()

    def test_changed_result_after_terminal_review_requires_new_attempt(self) -> None:
        temp, project = self.copy_fixture()
        try:
            result_path = self.install_reviewable_result(project, "required")
            self.add_review_attempt(project, "green")
            self.commit_result_version(
                project, result_path,
                self.result_version_content(subject="changed implementation v2"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "review_freeze"))
            self.assertIn("changed", routed.reason)
        finally:
            temp.cleanup()

    def test_active_review_for_changed_result_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            result_path = self.install_reviewable_result(project, "required")
            self.add_review_attempt(project, "pending")
            self.commit_result_version(
                project, result_path,
                self.result_version_content(subject="changed implementation v2"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("stale", routed.reason)
        finally:
            temp.cleanup()

    def install_board_research(self, project: Path, *, state: str, reconciliation: str = "pending") -> None:
        board = project / BOARD
        board.write_text(
            board.read_text()
            + '\n[research_obligation]\nclass = "research"\n'
            + 'path = "implementation/workstreams/sample-workstream/RESEARCH.toml"\n'
        )
        result = "" if reconciliation == "pending" else "implementation/workstreams/sample-workstream/evidence/research-return.md"
        research = project / "implementation/workstreams/sample-workstream/RESEARCH.toml"
        research.write_text(
            f'state = "{state}"\n'
            'workstream_id = "sample-workstream"\n'
            'origin_role = "execution_resolution"\n'
            'origin_subject = "M01-T04"\n'
            'return_target = "execution_resolution:M01-T04"\n'
            f'return_reconciliation = "{reconciliation}"\n'
            f'return_result = "{result}"\n'
            'finding = "Recovered exact evidence."\n'
            'limitations = "none"\n'
            'conflicts = "none"\n'
            '[[sources]]\nclass = "official_upstream"\nstatus = "not_relevant"\nweight = "primary"\n'
            '[[sources]]\nclass = "project_runtime"\nstatus = "checked"\nweight = "direct"\n'
            '[[sources]]\nclass = "tracker_discussion"\nstatus = "not_relevant"\nweight = "supporting"\n'
            '[[sources]]\nclass = "practitioner_community"\nstatus = "not_relevant"\nweight = "supporting"\n'
        )

    def test_task_board_research_return_is_recovered_before_execution(self) -> None:
        for state, reconciliation, expected in (
            ("active", "pending", "research"),
            ("complete", "pending", "execution_resolution"),
            ("complete", "applied", "execution_resolution"),
            ("consumed", "applied", "research_cleanup"),
        ):
            temp, project = self.copy_fixture()
            try:
                self.install_board_research(project, state=state, reconciliation=reconciliation)
                routed = select_route(project, [MANIFEST], package_root=ROOT)
                self.assertEqual((routed.disposition, routed.obligation), ("route", expected))
            finally:
                temp.cleanup()

    def install_blocker(self, project: Path, blocker_class: str) -> None:
        blocker_path = "implementation/workstreams/sample-workstream/blockers/M01-T04.toml"
        board = project / BOARD
        board.write_text(
            board.read_text()
            .replace('status = "in_progress"', 'status = "blocked"', 1)
            .replace(
                '[cards.contract]\n',
                f'[cards.blocker]\nclass = "blocker"\npath = "{blocker_path}"\n\n[cards.contract]\n',
                1,
            )
        )
        path = project / blocker_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            'workstream_id = "sample-workstream"\n'
            'card_id = "M01-T04"\n'
            f'class = "{blocker_class}"\n'
            'summary = "Exact blocker."\n'
            'evidence_path = ""\n'
        )

    def test_blocker_classification_does_not_turn_every_blocker_into_user_stop(self) -> None:
        for blocker_class, expected_disposition, expected_obligation in (
            ("missing_evidence", "route", "research_handoff"),
            ("human_authority", "stop", "user_stop"),
            ("runtime_access_input", "stop", "blocker_stop"),
        ):
            temp, project = self.copy_fixture()
            try:
                self.install_blocker(project, blocker_class)
                routed = select_route(project, [MANIFEST], package_root=ROOT)
                self.assertEqual(
                    (routed.disposition, routed.obligation),
                    (expected_disposition, expected_obligation),
                )
            finally:
                temp.cleanup()

    def test_all_terminal_cards_route_to_close_not_directly_to_stop(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "none")
            board = project / BOARD
            board.write_text(board.read_text().replace('status = "in_progress"', 'status = "done"', 1))
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "close"))
            self.assertEqual(routed.owner_module, "workflow/CLOSE.md")
            self.assertIn("decides whether approved scope is durably complete", routed.reason)
            self.assertNotIn("package:workflow/FORK_RELEASE_VERSIONING.md", routed.read_set)
        finally:
            temp.cleanup()

    def test_priority_and_real_stop_foundations_are_runtime_neutral(self) -> None:
        self.assertEqual(
            PRIORITY_FOUNDATION,
            (
                "explicit_human_or_premium_boundary",
                "independent_review_or_red_correction",
                "research_return",
                "result_reconciliation",
                "current_card",
                "next_legal_stage",
            ),
        )
        self.assertIn("premium_gate", REAL_STOP_FOUNDATION)
        self.assertIn("independence_boundary", REAL_STOP_FOUNDATION)
        combined = " ".join(PRIORITY_FOUNDATION + REAL_STOP_FOUNDATION)
        for forbidden in ("chatgpt", "codex", "model_id", "session_id", "worker_id"):
            self.assertNotIn(forbidden, combined)


if __name__ == "__main__":
    unittest.main()
