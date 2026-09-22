from __future__ import annotations

import os
import shutil
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

    def test_ready_card_stale_dependency_fails_closed_before_launch(self) -> None:
        temp, project = self.copy_fixture()
        try:
            dependency = "implementation/workstreams/sample-workstream/results/MISSING.md"
            self.make_ready_card(project, dependencies=dependency)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("not the current DONE predecessor result", routed.reason)
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
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution_prep"))
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

            planning_path.write_text(
                self.planning_content(
                    state="approved", cycle=2, revision="P2",
                    premium_a="satisfied", premium_b="satisfied", premium_c="satisfied",
                )
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution_prep"))

            base = f"owner/repo@{'a' * 40}:planning/MASTER_PLAN.md@{'b' * 40}"
            planning_path.write_text(
                self.planning_content(
                    state="approved", cycle=2, revision="P2", blob="c" * 40,
                    premium_a="satisfied", premium_b="satisfied", premium_c="satisfied",
                    gate_subject=base, review_mode="editorial_exempt",
                    exemption_basis="Wording only; strategy, milestones, coverage and gates unchanged.",
                    exemption_base_subject=base,
                )
            )
            review_path.write_text(self.plan_review_content("green", cycle=2, revision="P2"))
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution_prep"))
            self.assertIn("Editorial/mechanical-only", routed.reason)
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
            result_path = "implementation/workstreams/sample-workstream/results/M01-T04.md"
            (project / CARD).write_text(self.task_card_content())
            authority = project / "requirements" / "REQUIREMENTS.md"
            authority.parent.mkdir(parents=True, exist_ok=True)
            authority.write_text("# Accepted authority\n")
            board = project / BOARD
            board.write_text(
                board.read_text()
                + '\n[cards.result]\nclass = "result"\n'
                + f'path = "{result_path}"\n'
                + f'commit = "{"a" * 40}"\n'
                + f'blob = "{"b" * 40}"\n'
            )
            evidence_dir = project / "implementation/workstreams/sample-workstream/evidence"
            evidence_dir.mkdir(parents=True, exist_ok=True)
            (evidence_dir / "M01-T04.md").write_text("# Verified evidence\n")
            result_file = project / result_path
            result_file.parent.mkdir(parents=True, exist_ok=True)
            result_file.write_text(
                "# Card Result\n"
                "- Card ID: M01-T04\n"
                "- Implementation subject: owner/repo@commit:" + ("a" * 40) + "\n"
                "- Evidence refs: implementation/workstreams/sample-workstream/evidence/M01-T04.md\n"
                "- Tests/readback summary: GREEN\n"
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "result_reconciliation"))
            self.assertIn("do not replay", routed.reason)
            self.assertIn(f"project:{result_path}", routed.read_set)
        finally:
            temp.cleanup()

    def install_reviewable_result(self, project: Path, review_requirement: str) -> str:
        result_path = "implementation/workstreams/sample-workstream/results/M01-T04.md"
        (project / CARD).write_text(self.task_card_content(review_requirement=review_requirement))
        authority = project / "requirements" / "REQUIREMENTS.md"
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text("# Accepted authority\n")
        board = project / BOARD
        board.write_text(
            board.read_text()
            + '\n[cards.result]\nclass = "result"\n'
            + f'path = "{result_path}"\n'
        )
        evidence_dir = project / "implementation/workstreams/sample-workstream/evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        (evidence_dir / "M01-T04.md").write_text("# Verified evidence\n")
        result_file = project / result_path
        result_file.parent.mkdir(parents=True, exist_ok=True)
        result_file.write_text(
            "# Card Result\n"
            "- Card ID: M01-T04\n"
            "- Implementation subject: owner/repo@commit:" + ("a" * 40) + "\n"
            "- Evidence refs: implementation/workstreams/sample-workstream/evidence/M01-T04.md\n"
            "- Tests/readback summary: GREEN\n"
        )
        return result_path

    def add_review_attempt(self, project: Path, verdict: str, attempt: str = "R01") -> str:
        review_path = f"implementation/workstreams/sample-workstream/reviews/M01-T04-{attempt}.toml"
        board = project / BOARD
        board.write_text(
            board.read_text().replace(
                'status = "in_progress"\n',
                'status = "in_progress"\n'
                f'review_attempts = [{{ class = "review_attempt", path = "{review_path}" }}]\n',
                1,
            )
        )
        path = project / review_path
        path.parent.mkdir(parents=True, exist_ok=True)
        evidence = "" if verdict in {"pending", "in_progress"} else "implementation/workstreams/sample-workstream/evidence/review-R01.md"
        if evidence:
            evidence_path = project / evidence
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            evidence_path.write_text("# Review evidence\n")
        path.write_text(
            'workstream_id = "sample-workstream"\n'
            'card_id = "M01-T04"\n'
            f'attempt = "{attempt}"\n'
            f'verdict = "{verdict}"\n'
            f'evidence_path = "{evidence}"\n'
            '[subject]\n'
            'class = "git_blob"\n'
            'repository = "owner/router-fixture"\n'
            f'commit = "{"a" * 40}"\n'
            'path = "implementation/workstreams/sample-workstream/results/M01-T04.md"\n'
            f'blob = "{"b" * 40}"\n'
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
            ("red", "review_correction"),
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
