#!/usr/bin/env python3
"""RF009 Research-provenance seam regressions (H014/H016).

H014: a complete Research record routes to its declared return target only
when the exact origin-to-return binding is proved from a real owning subject;
mismatched or nonexistent origins fail closed to Recovery instead of routing
the declared target.

H016: Intake prior-art bindings prove exact consumed-Research result
provenance through an RF007 exact locator; forged bindings, missing Research
and mismatched results cannot present stable issue alignment.
"""

from __future__ import annotations

import copy
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.router import select_route
from tools.state_contract import ValidationError, validate_intake

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/router/valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
INTAKE = "implementation/workstreams/sample-workstream/INTAKE.toml"
RESEARCH = "implementation/workstreams/sample-workstream/RESEARCH.toml"
REPOSITORY = "owner/router-fixture"

SOURCES_CHECKED = (
    '[[sources]]\nclass = "official_upstream"\nstatus = "checked"\nweight = "primary"\n'
    '[[sources]]\nclass = "project_runtime"\nstatus = "checked"\nweight = "direct"\n'
    '[[sources]]\nclass = "tracker_discussion"\nstatus = "not_relevant"\nweight = "supporting"\n'
    '[[sources]]\nclass = "practitioner_community"\nstatus = "unavailable"\nweight = "supporting"\n'
)


def research_content(
    *,
    state: str,
    origin_role: str,
    origin_subject: str,
    return_target: str,
    reconciliation: str = "pending",
    return_result: str = "",
) -> str:
    return (
        f'state = "{state}"\n'
        'workstream_id = "sample-workstream"\n'
        f'origin_role = "{origin_role}"\n'
        f'origin_subject = "{origin_subject}"\n'
        f'return_target = "{return_target}"\n'
        f'return_reconciliation = "{reconciliation}"\n'
        f'return_result = "{return_result}"\n'
        'finding = "Bounded provenance finding."\n'
        'limitations = "none"\n'
        'conflicts = "No material conflicts observed."\n'
        f"{SOURCES_CHECKED}"
    )


def proof_table(*, commit: str, blob: str, path: str = RESEARCH,
                repository: str = REPOSITORY, klass: str = "research") -> str:
    return (
        "[diagnosis_prior_art_proof]\n"
        f'class = "{klass}"\n'
        f'repository = "{repository}"\n'
        f'commit = "{commit}"\n'
        f'path = "{path}"\n'
        f'blob = "{blob}"\n'
    )


def intake_content(
    *,
    repair_subject: str = "repair:v1",
    binding: tuple[str, str] | None = None,
    proof: str = "",
    response_kind: str = "none",
    response_observed: bool = False,
) -> str:
    subject, result = binding if binding is not None else ("", "")
    observed = "true" if response_observed else "false"
    text = (
        'workstream_id = "sample-workstream"\n'
        'kind = "issue"\n'
        'state = "active"\n'
        "diagnosis_revision = 1\n"
        f'repair_subject = "{repair_subject}"\n'
        f'diagnosis_prior_art_subject = "{subject}"\n'
        f'diagnosis_prior_art_result = "{result}"\n'
        f'response_kind = "{response_kind}"\n'
        f"response_observed = {observed}\n"
        'alignment_state = "pending"\n'
        'alignment_subject = ""\n'
        "micro_fix_candidate = false\n"
    )
    return text + proof


def brainstorm_content(*, scope_id: str = "scope-a", revision: int = 2) -> str:
    return (
        'workstream_id = "sample-workstream"\n'
        f'scope_id = "{scope_id}"\n'
        f"revision = {revision}\n"
        'state = "active"\n'
        'challenge_audit = "pending"\n'
        "explicit_user_stop = false\n"
        'promotion_state = "pending"\n'
        'promotion_subject = ""\n'
    )


def definition_content(*, source_scope: str = "scope-a@2", revision: str = "R1") -> str:
    return (
        'workstream_id = "sample-workstream"\n'
        f'source_scope_subject = "{source_scope}"\n'
        f'revision = "{revision}"\n'
        'state = "active"\n'
        'completeness_audit = "pending"\n'
        'premium_a = "not_due"\n'
        'decisions = []\n'
        '[requirements]\nclass = "authority"\npath = "requirements/REQUIREMENTS.md"\n'
    )


class ResearchProvenanceTests(unittest.TestCase):
    def copy_git_project(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(FIXTURE, project)
        subprocess.run(["git", "init", "-q", str(project)], check=True)
        subprocess.run(
            ["git", "-C", str(project), "config", "user.email", "rf009@example.invalid"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(project), "config", "user.name", "RF009"], check=True
        )
        return temp, project

    def install_state_record(self, project: Path, key: str, klass: str,
                             filename: str, content: str) -> None:
        workstream = project / MANIFEST
        workstream.write_text(
            workstream.read_text()
            + f'\n[{key}]\nclass = "{klass}"\n'
            + f'path = "implementation/workstreams/sample-workstream/{filename}"\n'
        )
        (project / f"implementation/workstreams/sample-workstream/{filename}").write_text(content)

    def install_board_research(self, project: Path, content: str) -> None:
        board = project / BOARD
        board.write_text(
            board.read_text()
            + '\n[research_obligation]\nclass = "research"\n'
            + f'path = "{RESEARCH}"\n'
        )
        (project / RESEARCH).write_text(content)

    @staticmethod
    def commit_relpath(project: Path, relpath: str) -> tuple[str, str]:
        subprocess.run(["git", "-C", str(project), "add", relpath], check=True)
        subprocess.run(
            ["git", "-C", str(project), "commit", "-q", "-m", f"rf009 {relpath}"],
            check=True,
        )
        commit = subprocess.run(
            ["git", "-C", str(project), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        blob = subprocess.run(
            ["git", "-C", str(project), "rev-parse", f"HEAD:{relpath}"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        return commit, blob

    def commit_consumed_intake_research(self, project: Path, subject: str,
                                       result: str) -> tuple[str, str]:
        (project / RESEARCH).write_text(research_content(
            state="consumed",
            origin_role="intake",
            origin_subject=subject,
            return_target="intake",
            reconciliation="applied",
            return_result=result,
        ))
        return self.commit_relpath(project, RESEARCH)

    def assert_recovery(self, project: Path, fragment: str):
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        self.assertEqual(
            (routed.disposition, routed.obligation), ("recovery", "recovery_boundary")
        )
        self.assertIn(fragment, routed.reason)
        return routed

    # H014 origin/return binding.

    def test_h014_intake_origin_to_brainstorming_return_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_state_record(project, "intake", "intake", "INTAKE.toml",
                                      intake_content(repair_subject="repair:v1"))
            self.install_state_record(project, "research", "research", "RESEARCH.toml",
                                      research_content(
                                          state="complete",
                                          origin_role="intake",
                                          origin_subject="repair:v1",
                                          return_target="brainstorming",
                                      ))
            routed = self.assert_recovery(project, "research origin/return binding")
            self.assertNotEqual(routed.subject, "brainstorming")
        finally:
            temp.cleanup()

    def test_h014_definition_origin_to_intake_return_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_state_record(project, "brainstorm", "brainstorm",
                                      "BRAINSTORM.toml", brainstorm_content())
            self.install_state_record(project, "definition", "definition",
                                      "DEFINITION.toml", definition_content())
            self.install_state_record(project, "research", "research", "RESEARCH.toml",
                                      research_content(
                                          state="complete",
                                          origin_role="definition",
                                          origin_subject="R1",
                                          return_target="intake",
                                      ))
            self.assert_recovery(project, "research origin/return binding")
        finally:
            temp.cleanup()

    def test_h014_nonexistent_scope_origin_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_state_record(project, "brainstorm", "brainstorm",
                                      "BRAINSTORM.toml", brainstorm_content())
            self.install_state_record(project, "research", "research", "RESEARCH.toml",
                                      research_content(
                                          state="complete",
                                          origin_role="brainstorming",
                                          origin_subject="scope@99",
                                          return_target="brainstorming",
                                      ))
            self.assert_recovery(project, "research origin/return binding")
        finally:
            temp.cleanup()

    def test_h014_sibling_origin_scope_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_state_record(project, "brainstorm", "brainstorm",
                                      "BRAINSTORM.toml", brainstorm_content())
            self.install_state_record(project, "research", "research", "RESEARCH.toml",
                                      research_content(
                                          state="complete",
                                          origin_role="brainstorming",
                                          origin_subject="scope-b@2",
                                          return_target="brainstorming",
                                      ))
            self.assert_recovery(project, "research origin/return binding")
        finally:
            temp.cleanup()

    def test_h014_missing_owning_record_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_state_record(project, "research", "research", "RESEARCH.toml",
                                      research_content(
                                          state="complete",
                                          origin_role="brainstorming",
                                          origin_subject="scope-a@2",
                                          return_target="brainstorming",
                                      ))
            self.assert_recovery(project, "research origin/return binding")
        finally:
            temp.cleanup()

    def test_h014_stale_revision_origin_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_state_record(project, "brainstorm", "brainstorm",
                                      "BRAINSTORM.toml", brainstorm_content(revision=3))
            self.install_state_record(project, "research", "research", "RESEARCH.toml",
                                      research_content(
                                          state="complete",
                                          origin_role="brainstorming",
                                          origin_subject="scope-a@2",
                                          return_target="brainstorming",
                                      ))
            self.assert_recovery(project, "research origin/return binding")
        finally:
            temp.cleanup()

    def test_h014_malformed_brainstorm_owner_with_matching_subject_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_state_record(project, "brainstorm", "brainstorm",
                                      "BRAINSTORM.toml", (
                                          'workstream_id = "sample-workstream"\n'
                                          'scope_id = "scope-a"\n'
                                          "revision = 2\n"
                                          'state = "promoted"\n'
                                          'challenge_audit = "green"\n'
                                          "explicit_user_stop = false\n"
                                          'promotion_state = "pending"\n'
                                          'promotion_subject = ""\n'
                                      ))
            self.install_state_record(project, "research", "research", "RESEARCH.toml",
                                      research_content(
                                          state="complete",
                                          origin_role="brainstorming",
                                          origin_subject="scope-a@2",
                                          return_target="brainstorming",
                                      ))
            self.assert_recovery(project, "promoted state requires exact user authorization")
        finally:
            temp.cleanup()

    def test_h014_malformed_intake_owner_with_matching_subject_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_state_record(project, "intake", "intake", "INTAKE.toml", (
                'workstream_id = "sample-workstream"\n'
                'kind = "issue"\n'
                'state = "active"\n'
                "diagnosis_revision = 1\n"
                'repair_subject = "repair:v1"\n'
                'diagnosis_prior_art_subject = ""\n'
                'diagnosis_prior_art_result = ""\n'
                'response_kind = "none"\n'
                "response_observed = true\n"
                'alignment_state = "pending"\n'
                'alignment_subject = ""\n'
                "micro_fix_candidate = false\n"
            ))
            self.install_state_record(project, "research", "research", "RESEARCH.toml",
                                      research_content(
                                          state="complete",
                                          origin_role="intake",
                                          origin_subject="repair:v1",
                                          return_target="intake",
                                      ))
            self.assert_recovery(project, "response_observed must match response_kind")
        finally:
            temp.cleanup()

    def test_h014_malformed_definition_owner_with_matching_subject_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_state_record(project, "definition", "definition",
                                      "DEFINITION.toml", (
                                          'workstream_id = "sample-workstream"\n'
                                          'source_scope_subject = "scope-a@2"\n'
                                          'revision = "R1"\n'
                                          'state = "active"\n'
                                          'completeness_audit = "pending"\n'
                                          'premium_a = "not_due"\n'
                                          'decisions = "not-an-array"\n'
                                          '[requirements]\nclass = "authority"\npath = "requirements/REQUIREMENTS.md"\n'
                                      ))
            self.install_state_record(project, "research", "research", "RESEARCH.toml",
                                      research_content(
                                          state="complete",
                                          origin_role="definition",
                                          origin_subject="R1",
                                          return_target="definition",
                                      ))
            self.assert_recovery(project, "decisions must be an array")
        finally:
            temp.cleanup()

    def test_h014_applied_reconciliation_does_not_bypass_binding(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_state_record(project, "intake", "intake", "INTAKE.toml",
                                      intake_content(repair_subject="repair:v1"))
            self.install_state_record(project, "research", "research", "RESEARCH.toml",
                                      research_content(
                                          state="complete",
                                          origin_role="intake",
                                          origin_subject="repair:v1",
                                          return_target="definition",
                                          reconciliation="applied",
                                          return_result="evidence/applied.md",
                                      ))
            self.assert_recovery(project, "research origin/return binding")
        finally:
            temp.cleanup()

    def test_h014_board_execution_role_mismatch_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_board_research(project, research_content(
                state="complete",
                origin_role="execution",
                origin_subject="M01-T04",
                return_target="execution_resolution:M01-T04",
            ))
            self.assert_recovery(project, "research origin/return binding")
        finally:
            temp.cleanup()

    def test_h014_board_execution_subject_mismatch_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_board_research(project, research_content(
                state="complete",
                origin_role="execution",
                origin_subject="M01-T04",
                return_target="execution:M01-T05",
            ))
            self.assert_recovery(project, "research origin/return binding")
        finally:
            temp.cleanup()

    def test_h014_board_execution_unknown_card_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_board_research(project, research_content(
                state="complete",
                origin_role="execution",
                origin_subject="M01-T99",
                return_target="execution:M01-T99",
            ))
            self.assert_recovery(project, "research origin/return binding")
        finally:
            temp.cleanup()

    # H016 consumed prior-art provenance.

    def test_h016_forged_binding_without_research_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            dangling = "1" * 40
            self.install_state_record(
                project, "intake", "intake", "INTAKE.toml",
                intake_content(
                    repair_subject="repair:v9",
                    binding=("repair:v9", "forged-string"),
                    proof=proof_table(commit=dangling, blob="2" * 40),
                ),
            )
            self.assert_recovery(project, "prior-art proof")
        finally:
            temp.cleanup()

    def test_h016_binding_mismatched_vs_consumed_result_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            commit, blob = self.commit_consumed_intake_research(
                project, "repair:v1", "evidence/real-prior-art.md"
            )
            self.install_state_record(
                project, "intake", "intake", "INTAKE.toml",
                intake_content(
                    repair_subject="repair:v1",
                    binding=("repair:v1", "evidence/forged-prior-art.md"),
                    proof=proof_table(commit=commit, blob=blob),
                ),
            )
            self.assert_recovery(project, "prior-art proof")
        finally:
            temp.cleanup()

    def test_h016_binding_subject_mismatched_vs_proof_origin_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            commit, blob = self.commit_consumed_intake_research(
                project, "repair:v2", "evidence/intake-prior-art.md"
            )
            self.install_state_record(
                project, "intake", "intake", "INTAKE.toml",
                intake_content(
                    repair_subject="repair:v1",
                    binding=("repair:v1", "evidence/intake-prior-art.md"),
                    proof=proof_table(commit=commit, blob=blob),
                ),
            )
            self.assert_recovery(project, "prior-art proof")
        finally:
            temp.cleanup()

    def test_h016_binding_without_proof_table_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_state_record(
                project, "intake", "intake", "INTAKE.toml",
                intake_content(
                    repair_subject="repair:v1",
                    binding=("repair:v1", "evidence/intake-prior-art.md"),
                ),
            )
            self.assert_recovery(project, "prior-art proof")
        finally:
            temp.cleanup()

    def test_h016_proof_blob_mismatch_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            commit, _blob = self.commit_consumed_intake_research(
                project, "repair:v1", "evidence/intake-prior-art.md"
            )
            self.install_state_record(
                project, "intake", "intake", "INTAKE.toml",
                intake_content(
                    repair_subject="repair:v1",
                    binding=("repair:v1", "evidence/intake-prior-art.md"),
                    proof=proof_table(commit=commit, blob="3" * 40),
                ),
            )
            self.assert_recovery(project, "prior-art proof")
        finally:
            temp.cleanup()

    def test_h016_proof_path_traversal_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_state_record(
                project, "intake", "intake", "INTAKE.toml",
                intake_content(
                    repair_subject="repair:v1",
                    binding=("repair:v1", "evidence/intake-prior-art.md"),
                    proof=proof_table(commit="4" * 40, blob="5" * 40,
                                      path="../escape/RESEARCH.toml"),
                ),
            )
            self.assert_recovery(project, "prior-art proof")
        finally:
            temp.cleanup()

    def test_h016_proof_wrong_workstream_path_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_state_record(
                project, "intake", "intake", "INTAKE.toml",
                intake_content(
                    repair_subject="repair:v1",
                    binding=("repair:v1", "evidence/intake-prior-art.md"),
                    proof=proof_table(
                        commit="4" * 40, blob="5" * 40,
                        path="implementation/workstreams/other/RESEARCH.toml",
                    ),
                ),
            )
            self.assert_recovery(project, "prior-art proof")
        finally:
            temp.cleanup()

    def test_h016_proof_repository_mismatch_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            commit, blob = self.commit_consumed_intake_research(
                project, "repair:v1", "evidence/intake-prior-art.md"
            )
            self.install_state_record(
                project, "intake", "intake", "INTAKE.toml",
                intake_content(
                    repair_subject="repair:v1",
                    binding=("repair:v1", "evidence/intake-prior-art.md"),
                    proof=proof_table(commit=commit, blob=blob,
                                      repository="other/repo"),
                ),
            )
            self.assert_recovery(project, "prior-art proof")
        finally:
            temp.cleanup()

    def test_h016_proof_pointing_at_live_mutation_fails_closed(self) -> None:
        temp, project = self.copy_git_project()
        try:
            commit, blob = self.commit_consumed_intake_research(
                project, "repair:v1", "evidence/intake-prior-art.md"
            )
            (project / RESEARCH).write_text(research_content(
                state="consumed",
                origin_role="intake",
                origin_subject="repair:v1",
                return_target="intake",
                reconciliation="applied",
                return_result="evidence/rewritten-result.md",
            ))
            self.install_state_record(
                project, "intake", "intake", "INTAKE.toml",
                intake_content(
                    repair_subject="repair:v1",
                    binding=("repair:v1", "evidence/rewritten-result.md"),
                    proof=proof_table(commit=commit, blob=blob),
                ),
            )
            self.assert_recovery(project, "prior-art proof")
        finally:
            temp.cleanup()

    # Exact positives continue deterministically.

    def test_valid_intake_origin_return_routes_intake(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_state_record(project, "intake", "intake", "INTAKE.toml",
                                      intake_content(repair_subject="repair:v1"))
            self.install_state_record(project, "research", "research", "RESEARCH.toml",
                                      research_content(
                                          state="complete",
                                          origin_role="intake",
                                          origin_subject="repair:v1",
                                          return_target="intake",
                                      ))
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "intake"))
        finally:
            temp.cleanup()

    def test_valid_brainstorming_origin_return_routes_brainstorming(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_state_record(project, "brainstorm", "brainstorm",
                                      "BRAINSTORM.toml", brainstorm_content())
            self.install_state_record(project, "research", "research", "RESEARCH.toml",
                                      research_content(
                                          state="complete",
                                          origin_role="brainstorming",
                                          origin_subject="scope-a@2",
                                          return_target="brainstorming",
                                      ))
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "brainstorming"))
        finally:
            temp.cleanup()

    def test_valid_promoted_brainstorm_owner_routes_brainstorming(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_state_record(project, "brainstorm", "brainstorm",
                                      "BRAINSTORM.toml", (
                                          'workstream_id = "sample-workstream"\n'
                                          'scope_id = "scope-a"\n'
                                          "revision = 2\n"
                                          'state = "promoted"\n'
                                          'challenge_audit = "green"\n'
                                          "explicit_user_stop = false\n"
                                          'promotion_state = "authorized"\n'
                                          'promotion_subject = "scope-a@2"\n'
                                      ))
            self.install_state_record(project, "research", "research", "RESEARCH.toml",
                                      research_content(
                                          state="complete",
                                          origin_role="brainstorming",
                                          origin_subject="scope-a@2",
                                          return_target="brainstorming",
                                      ))
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "brainstorming"))
        finally:
            temp.cleanup()

    def test_valid_intake_owner_with_binding_routes_intake(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_state_record(
                project, "intake", "intake", "INTAKE.toml",
                intake_content(
                    repair_subject="repair:v1",
                    binding=("repair:v1", "evidence/intake-prior-art.md"),
                    proof=proof_table(commit="a" * 40, blob="b" * 40),
                ),
            )
            self.install_state_record(project, "research", "research", "RESEARCH.toml",
                                      research_content(
                                          state="complete",
                                          origin_role="intake",
                                          origin_subject="repair:v1",
                                          return_target="intake",
                                      ))
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "intake"))
        finally:
            temp.cleanup()

    def test_valid_definition_origin_return_routes_definition(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_state_record(project, "brainstorm", "brainstorm",
                                      "BRAINSTORM.toml", brainstorm_content())
            self.install_state_record(project, "definition", "definition",
                                      "DEFINITION.toml", definition_content())
            self.install_state_record(project, "research", "research", "RESEARCH.toml",
                                      research_content(
                                          state="complete",
                                          origin_role="definition",
                                          origin_subject="R1",
                                          return_target="definition",
                                      ))
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "definition"))
        finally:
            temp.cleanup()

    def test_valid_board_execution_return_routes_owner(self) -> None:
        temp, project = self.copy_git_project()
        try:
            self.install_board_research(project, research_content(
                state="complete",
                origin_role="execution_resolution",
                origin_subject="M01-T04",
                return_target="execution_resolution:M01-T04",
            ))
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation), ("route", "execution_resolution")
            )
        finally:
            temp.cleanup()

    def test_exact_consumed_binding_with_proof_stops_issue_alignment(self) -> None:
        temp, project = self.copy_git_project()
        try:
            commit, blob = self.commit_consumed_intake_research(
                project, "repair:v1", "evidence/intake-prior-art.md"
            )
            self.install_state_record(
                project, "intake", "intake", "INTAKE.toml",
                intake_content(
                    repair_subject="repair:v1",
                    binding=("repair:v1", "evidence/intake-prior-art.md"),
                    proof=proof_table(commit=commit, blob=blob),
                ),
            )
            self.install_state_record(project, "research", "research", "RESEARCH.toml",
                                      (project / RESEARCH).read_text())
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "issue_alignment"))
            self.assertIn(f"project-git:{REPOSITORY}@{commit}:{RESEARCH}@{blob}",
                          routed.read_set)
        finally:
            temp.cleanup()

    def test_slot_reuse_with_proof_preserves_alignment(self) -> None:
        temp, project = self.copy_git_project()
        try:
            commit, blob = self.commit_consumed_intake_research(
                project, "repair:v2", "evidence/intake-prior-art.md"
            )
            (project / RESEARCH).write_text(research_content(
                state="consumed",
                origin_role="brainstorming",
                origin_subject="scope-a@2",
                return_target="brainstorming",
                reconciliation="applied",
                return_result="evidence/brainstorm-followup.md",
            ))
            self.install_state_record(
                project, "intake", "intake", "INTAKE.toml",
                intake_content(
                    repair_subject="repair:v2",
                    binding=("repair:v2", "evidence/intake-prior-art.md"),
                    proof=proof_table(commit=commit, blob=blob),
                    response_kind="question",
                    response_observed=True,
                ),
            )
            self.install_state_record(project, "research", "research", "RESEARCH.toml",
                                      (project / RESEARCH).read_text())
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "brainstorming"))
            self.assertNotIn("diagnosis prior-art Research", routed.reason)
        finally:
            temp.cleanup()


class PriorArtProofShapeTests(unittest.TestCase):
    def base_intake(self) -> dict:
        return {
            "workstream_id": "sample-workstream",
            "kind": "issue",
            "state": "active",
            "diagnosis_revision": 1,
            "repair_subject": "repair:v1",
            "diagnosis_prior_art_subject": "repair:v1",
            "diagnosis_prior_art_result": "evidence/intake-prior-art.md",
            "response_kind": "none",
            "response_observed": False,
            "alignment_state": "pending",
            "alignment_subject": "",
            "micro_fix_candidate": False,
            "diagnosis_prior_art_proof": {
                "class": "research",
                "repository": "owner/repo",
                "commit": "a" * 40,
                "path": "implementation/workstreams/sample-workstream/RESEARCH.toml",
                "blob": "b" * 40,
            },
        }

    def test_binding_with_wellformed_proof_is_shape_valid(self) -> None:
        validate_intake(self.base_intake(), "sample-workstream")

    def test_binding_without_proof_fails_shape(self) -> None:
        intake = self.base_intake()
        intake.pop("diagnosis_prior_art_proof")
        with self.assertRaisesRegex(ValidationError, "prior-art proof"):
            validate_intake(intake, "sample-workstream")

    def test_dangling_proof_without_binding_fails_shape(self) -> None:
        intake = self.base_intake()
        intake["diagnosis_prior_art_subject"] = ""
        intake["diagnosis_prior_art_result"] = ""
        with self.assertRaisesRegex(ValidationError, "prior-art proof"):
            validate_intake(intake, "sample-workstream")

    def test_non_issue_with_proof_fails_shape(self) -> None:
        intake = self.base_intake()
        intake.update({
            "kind": "feature",
            "repair_subject": "",
            "diagnosis_prior_art_subject": "",
            "diagnosis_prior_art_result": "",
            "alignment_state": "not_required",
        })
        with self.assertRaisesRegex(ValidationError, "prior-art proof"):
            validate_intake(intake, "sample-workstream")

    def test_malformed_proof_fails_shape(self) -> None:
        for mutate, fragment in (
            (lambda proof: proof.update({"commit": "zz"}), "commit"),
            (lambda proof: proof.update({"blob": "zz"}), "blob"),
            (lambda proof: proof.update({"class": "evidence"}), "class"),
            (lambda proof: proof.update({"path": "../escape.toml"}), "path"),
            (lambda proof: proof.update({"repository": ""}), "repository"),
            (lambda proof: proof.update({"extra": "smuggled"}), "field"),
        ):
            with self.subTest(fragment=fragment):
                intake = self.base_intake()
                proof = copy.deepcopy(intake["diagnosis_prior_art_proof"])
                mutate(proof)
                intake["diagnosis_prior_art_proof"] = proof
                with self.assertRaisesRegex(ValidationError, "prior-art proof"):
                    validate_intake(intake, "sample-workstream")


if __name__ == "__main__":
    unittest.main()
