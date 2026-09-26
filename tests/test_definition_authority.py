#!/usr/bin/env python3
"""RF012 Definition-authority key regressions (H021)."""

from __future__ import annotations

import copy
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.definition_authority import (
    DefinitionAuthorityError,
    build_definition_authority_key,
    derive_current_authority_key,
    parse_definition_authority_key,
)
from tools.exact_locator import git_blob_sha
from tools.router import select_route
from tools.state_contract import (
    ValidationError,
    validate_plan_review,
    validate_planning,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/router/valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
REPOSITORY = "owner/router-fixture"

REQ_PATH = "requirements/REQUIREMENTS.md"
REQ_CONTENT = "# Accepted authority\n"
DEC_PATH = "decisions/ADR-001.md"
DEC_PATH2 = "decisions/ADR-002.md"


def git(project: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(project), *args],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def fresh_project() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    temp = tempfile.TemporaryDirectory()
    project = Path(temp.name) / "project"
    shutil.copytree(FIXTURE, project)
    return temp, project


def fresh_git_project() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    temp, project = fresh_project()
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    subprocess.run(
        ["git", "-C", str(project), "config", "user.email", "rf012@example.invalid"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(project), "config", "user.name", "RF012"], check=True
    )
    return temp, project


def write_authority(project: Path, req_content: str = REQ_CONTENT,
                    dec_content: str = "# Accepted decision\n") -> tuple[str, str]:
    req = project / REQ_PATH
    req.parent.mkdir(parents=True, exist_ok=True)
    req.write_text(req_content)
    dec = project / DEC_PATH
    dec.parent.mkdir(parents=True, exist_ok=True)
    dec.write_text(dec_content)
    return git_blob_sha(req_content.encode()), git_blob_sha(dec_content.encode())


def install_record(project: Path, key: str, klass: str, filename: str, content: str) -> None:
    workstream = project / MANIFEST
    workstream.write_text(
        workstream.read_text()
        + f'\n[{key}]\nclass = "{klass}"\npath = "implementation/workstreams/sample-workstream/{filename}"\n'
    )
    (project / f"implementation/workstreams/sample-workstream/{filename}").write_text(content)


def brainstorm_green() -> str:
    return (
        'workstream_id = "sample-workstream"\n'
        'scope_id = "scope-plan"\n'
        'revision = 1\n'
        'state = "promoted"\n'
        'challenge_audit = "green"\n'
        'explicit_user_stop = false\n'
        'promotion_state = "authorized"\n'
        'promotion_subject = "scope-plan@1"\n'
    )


def definition_green(revision: str = "R1", req_path: str = REQ_PATH,
                     dec_paths: list[str] | None = None) -> str:
    if dec_paths is None:
        dec_paths = [DEC_PATH]
    decs = ", ".join(f'{{ class = "authority", path = "{p}" }}' for p in dec_paths)
    return (
        'workstream_id = "sample-workstream"\n'
        'source_scope_subject = "scope-plan@1"\n'
        f'revision = "{revision}"\n'
        'state = "green"\n'
        'completeness_audit = "green"\n'
        'premium_a = "satisfied"\n'
        f'decisions = [{decs}]\n'
        '[requirements]\nclass = "authority"\n'
        f'path = "{req_path}"\n'
    )


def planning_approved(authority_key: str | None, entry_rev: str = "R1") -> str:
    blob = "b" * 40
    key = f"owner/repo@{'a' * 40}:planning/MASTER_PLAN.md@{blob}"
    authority_line = (
        f'definition_authority_key = "{authority_key}"\n'
        if authority_key is not None
        else ""
    )
    return (
        'workstream_id = "sample-workstream"\n'
        'cycle = 1\n'
        f'entry_subject = "definition:{entry_rev}|planning-cycle:1"\n'
        'revision = "P1"\n'
        'state = "approved"\n'
        'planner_audit = "green"\n'
        'plan_path = "planning/MASTER_PLAN.md"\n'
        'review_mode = "independent"\n'
        'review_exemption_basis = ""\n'
        'review_exemption_base_subject = ""\n'
        'premium_a = "satisfied"\n'
        f'premium_a_subject = "definition:{entry_rev}|planning-cycle:1"\n'
        'premium_b = "satisfied"\n'
        f'premium_b_subject = "{key}"\n'
        'premium_c = "satisfied"\n'
        f'premium_c_subject = "{key}"\n'
        f'{authority_line}'
        '[subject]\n'
        'repository = "owner/repo"\n'
        f'commit = "{"a" * 40}"\n'
        'path = "planning/MASTER_PLAN.md"\n'
        f'blob = "{blob}"\n'
    )


def review_green(authority_key: str | None) -> str:
    blob = "b" * 40
    authority_line = (
        f'definition_authority_key = "{authority_key}"\n'
        if authority_key is not None
        else ""
    )
    return (
        'workstream_id = "sample-workstream"\n'
        'plan_revision = "P1"\n'
        'planning_cycle = 1\n'
        'attempt = "R01"\n'
        'verdict = "green"\n'
        'evidence_path = "evidence/plan-review-R01.md"\n'
        f'{authority_line}'
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


class KeyShapeTests(unittest.TestCase):
    def test_valid_key_parses_and_rebuilds_deterministically(self) -> None:
        req_blob = git_blob_sha(REQ_CONTENT.encode())
        dec_blob = git_blob_sha(b"# Accepted decision\n")
        dec2_blob = git_blob_sha(b"# Second decision\n")
        key = build_definition_authority_key(
            repository=REPOSITORY,
            definition_revision="R1",
            requirements_path=REQ_PATH,
            requirements_blob=req_blob,
            decisions=[(DEC_PATH2, dec2_blob), (DEC_PATH, dec_blob)],
        )
        parsed = parse_definition_authority_key(key, "probe")
        self.assertEqual(parsed["repository"], REPOSITORY)
        self.assertEqual(parsed["definition_revision"], "R1")
        self.assertEqual(parsed["decisions"], sorted([(DEC_PATH, dec_blob), (DEC_PATH2, dec2_blob)]))
        # Rebuild from parsed parts is byte-identical (deterministic).
        rebuilt = build_definition_authority_key(
            repository=parsed["repository"],
            definition_revision=parsed["definition_revision"],
            requirements_path=parsed["requirements_path"],
            requirements_blob=parsed["requirements_blob"],
            decisions=list(parsed["decisions"]),
        )
        self.assertEqual(rebuilt, key)

    def test_malformed_keys_fail_closed(self) -> None:
        req_blob = git_blob_sha(REQ_CONTENT.encode())
        dec_blob = git_blob_sha(b"# Accepted decision\n")
        valid = (
            f"rf012-v1:repository:{REPOSITORY}|definition:R1|"
            f"requirements:{REQ_PATH}@{req_blob}|decisions:{DEC_PATH}@{dec_blob}"
        )
        parse_definition_authority_key(valid, "probe")
        bad_keys = [
            "",
            "not-a-key",
            valid.replace("rf012-v1", "rf012-v2"),
            valid.replace("|definition:R1|", "|definition:|"),
            valid.replace(req_blob, "short"),
            valid.replace(REQ_PATH, "requirements\\\\..\\\\REQUIREMENTS.md"),
            valid.replace(REQ_PATH, "outside/REQUIREMENTS.md"),
            valid.replace("|decisions:", "|decisionsX:"),
            valid.split("|decisions:")[0] + "|decisions:",
            valid + "|extra:segment",
            " " + valid,
            valid + " ",
        ]
        for bad in bad_keys:
            with self.subTest(key=bad[:60]):
                with self.assertRaises(DefinitionAuthorityError):
                    parse_definition_authority_key(bad, "probe")
        # Unsorted and duplicated decisions fail.
        dec2_blob = git_blob_sha(b"# Second decision\n")
        unsorted = (
            f"rf012-v1:repository:{REPOSITORY}|definition:R1|"
            f"requirements:{REQ_PATH}@{req_blob}|"
            f"decisions:{DEC_PATH2}@{dec2_blob},{DEC_PATH}@{dec_blob}"
        )
        with self.assertRaises(DefinitionAuthorityError):
            parse_definition_authority_key(unsorted, "probe")
        duplicated = (
            f"rf012-v1:repository:{REPOSITORY}|definition:R1|"
            f"requirements:{REQ_PATH}@{req_blob}|"
            f"decisions:{DEC_PATH}@{dec_blob},{DEC_PATH}@{dec_blob}"
        )
        with self.assertRaises(DefinitionAuthorityError):
            parse_definition_authority_key(duplicated, "probe")

    def test_planning_and_review_binding_must_match(self) -> None:
        req_blob = git_blob_sha(REQ_CONTENT.encode())
        dec_blob = git_blob_sha(b"# Accepted decision\n")
        key = (
            f"rf012-v1:repository:{REPOSITORY}|definition:R1|"
            f"requirements:{REQ_PATH}@{req_blob}|decisions:{DEC_PATH}@{dec_blob}"
        )
        other = key.replace("definition:R1", "definition:R2")
        planning = {
            "workstream_id": "sample-workstream",
            "cycle": 1,
            "entry_subject": "definition:R1|planning-cycle:1",
            "revision": "P1",
            "state": "approved",
            "planner_audit": "green",
            "plan_path": "planning/MASTER_PLAN.md",
            "review_mode": "independent",
            "review_exemption_basis": "",
            "review_exemption_base_subject": "",
            "premium_a": "satisfied",
            "premium_a_subject": "definition:R1|planning-cycle:1",
            "premium_b": "satisfied",
            "premium_b_subject": f"owner/repo@{'a' * 40}:planning/MASTER_PLAN.md@{'b' * 40}",
            "premium_c": "satisfied",
            "premium_c_subject": f"owner/repo@{'a' * 40}:planning/MASTER_PLAN.md@{'b' * 40}",
            "subject": {
                "repository": "owner/repo",
                "commit": "a" * 40,
                "path": "planning/MASTER_PLAN.md",
                "blob": "b" * 40,
            },
            "definition_authority_key": key,
        }
        validate_planning(planning, "sample-workstream")
        bad_shape = copy.deepcopy(planning)
        bad_shape["definition_authority_key"] = "free-text authority"
        with self.assertRaises(ValidationError):
            validate_planning(bad_shape, "sample-workstream")

        def review_with(key_value: str | None, omit: bool = False) -> dict:
            review: dict = {
                "workstream_id": "sample-workstream",
                "plan_revision": "P1",
                "planning_cycle": 1,
                "attempt": "R01",
                "verdict": "green",
                "evidence_path": "evidence/plan-review-R01.md",
                "subject": {
                    "class": "git_blob",
                    "repository": "owner/repo",
                    "commit": "a" * 40,
                    "path": "planning/MASTER_PLAN.md",
                    "blob": "b" * 40,
                },
                "acceptance": {"class": "authority", "path": REQ_PATH},
                "independence": {
                    "materially_produced_or_repaired_subject": False,
                    "basis": "Fresh semantic review context.",
                },
            }
            if not omit:
                review["definition_authority_key"] = key_value
            return review

        validate_plan_review(review_with(key), "sample-workstream", planning)
        with self.assertRaisesRegex(ValidationError, "do not match"):
            validate_plan_review(review_with(other), "sample-workstream", planning)
        with self.assertRaisesRegex(ValidationError, "both be present or both absent"):
            validate_plan_review(review_with(None, omit=True), "sample-workstream", planning)
        keyless_planning = copy.deepcopy(planning)
        keyless_planning.pop("definition_authority_key")
        validate_planning(keyless_planning, "sample-workstream")
        validate_plan_review(
            review_with(None, omit=True), "sample-workstream", keyless_planning
        )
        with self.assertRaisesRegex(ValidationError, "both be present or both absent"):
            validate_plan_review(review_with(key), "sample-workstream", keyless_planning)


class H021RouterTests(unittest.TestCase):
    def install_h021(self, project: Path, *, planning_key: str | None,
                     review_key: str | None, definition_revision: str = "R1",
                     req_path: str = REQ_PATH, dec_paths: list[str] | None = None) -> None:
        if dec_paths is None:
            dec_paths = [DEC_PATH]
        install_record(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", brainstorm_green())
        install_record(
            project, "definition", "definition", "DEFINITION.toml",
            definition_green(definition_revision, req_path, dec_paths),
        )
        # Ensure default authority files exist unless the case overrides paths.
        for path in {req_path, *dec_paths}:
            target = project / path
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("# Authority bytes\n")
        install_record(
            project, "planning", "planning", "PLANNING.toml",
            planning_approved(planning_key),
        )
        install_record(
            project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
            review_green(review_key),
        )

    def current_key_for(self, project: Path) -> str:
        from tools.state_contract import read_toml
        workstream = read_toml(project / MANIFEST)
        definition = read_toml(project / workstream["definition"]["path"])
        return derive_current_authority_key(
            project_root=project,
            project_repository=REPOSITORY,
            definition=definition,
        )

    def test_r1_baseline_executes_with_valid_unchanged_authority(self) -> None:
        temp, project = fresh_git_project()
        try:
            helper = CoEditedKeyTests()
            commit, blob = helper.install_snapshot(project)
            req_blob = git_blob_sha(REQ_CONTENT.encode())
            dec_blob = git_blob_sha(b"# Accepted decision\n")
            key = build_definition_authority_key(
                repository=REPOSITORY,
                definition_revision="R1",
                requirements_path=REQ_PATH,
                requirements_blob=req_blob,
                decisions=[(DEC_PATH, dec_blob)],
            )
            helper.bind_definition(project)
            install_record(
                project, "planning", "planning", "PLANNING.toml",
                helper.planning_explicit(commit, blob, key),
            )
            install_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                helper.review_explicit(commit, blob, key),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
            self.assertEqual(routed.subject, "M01-T04")
            self.assertIn(f"project:{REQ_PATH}", routed.read_set)
            self.assertIn(f"project:{DEC_PATH}", routed.read_set)
        finally:
            temp.cleanup()

    def test_r2_definition_mutant_with_untouched_planning_fails_closed(self) -> None:
        temp, project = fresh_project()
        try:
            req_blob, dec_blob = write_authority(project)
            key = (
                f"rf012-v1:repository:{REPOSITORY}|definition:R1|"
                f"requirements:{REQ_PATH}@{req_blob}|decisions:{DEC_PATH}@{dec_blob}"
            )
            self.install_h021(
                project, planning_key=key, review_key=key, definition_revision="R2"
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
                routed.reason,
            )
            self.assertIn("stale", routed.reason)
        finally:
            temp.cleanup()

    def test_swapped_requirements_decisions_under_r1_fail_closed(self) -> None:
        temp, project = fresh_project()
        try:
            req_blob, dec_blob = write_authority(project)
            key = (
                f"rf012-v1:repository:{REPOSITORY}|definition:R1|"
                f"requirements:{REQ_PATH}@{req_blob}|decisions:{DEC_PATH}@{dec_blob}"
            )
            swapped_req = "requirements/SWAPPED.md"
            swapped_dec = "decisions/SWAPPED.md"
            (project / swapped_req).parent.mkdir(parents=True, exist_ok=True)
            (project / swapped_req).write_text("# Swapped requirements\n")
            (project / swapped_dec).parent.mkdir(parents=True, exist_ok=True)
            (project / swapped_dec).write_text("# Swapped decision\n")
            self.install_h021(
                project, planning_key=key, review_key=key,
                req_path=swapped_req, dec_paths=[swapped_dec],
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
                routed.reason,
            )
        finally:
            temp.cleanup()

    def test_same_revision_authority_file_mutation_fails_closed(self) -> None:
        temp, project = fresh_project()
        try:
            req_blob, dec_blob = write_authority(project)
            key = (
                f"rf012-v1:repository:{REPOSITORY}|definition:R1|"
                f"requirements:{REQ_PATH}@{req_blob}|decisions:{DEC_PATH}@{dec_blob}"
            )
            self.install_h021(project, planning_key=key, review_key=key)
            (project / REQ_PATH).write_text("# Mutated requirements bytes\n")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
                routed.reason,
            )
            self.assertIn("stale", routed.reason)
        finally:
            temp.cleanup()

    def test_stale_missing_mismatched_bindings_fail_closed(self) -> None:
        # Stale: planning/review bind old blob while live bytes changed.
        temp, project = fresh_project()
        try:
            req_blob, dec_blob = write_authority(project)
            stale = (
                f"rf012-v1:repository:{REPOSITORY}|definition:R1|"
                f"requirements:{REQ_PATH}@{req_blob}|decisions:{DEC_PATH}@{dec_blob}"
            )
            self.install_h021(project, planning_key=stale, review_key=stale)
            (project / DEC_PATH).write_text("# Mutated decision bytes\n")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
        finally:
            temp.cleanup()

        # Missing: keyless planning/review with fake subject and no Git is ambiguous.
        temp, project = fresh_project()
        try:
            write_authority(project)
            self.install_h021(project, planning_key=None, review_key=None)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("freshness failed", routed.reason)
        finally:
            temp.cleanup()

        # Mismatched: planning and review bind different keys.
        temp, project = fresh_project()
        try:
            req_blob, dec_blob = write_authority(project)
            planning_key = (
                f"rf012-v1:repository:{REPOSITORY}|definition:R1|"
                f"requirements:{REQ_PATH}@{req_blob}|decisions:{DEC_PATH}@{dec_blob}"
            )
            review_key = planning_key.replace("definition:R1", "definition:R2")
            self.install_h021(project, planning_key=planning_key, review_key=review_key)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
        finally:
            temp.cleanup()

    def test_path_only_and_free_text_authority_cannot_authorize(self) -> None:
        temp, project = fresh_project()
        try:
            write_authority(project)
            self.install_h021(
                project, planning_key="requirements/REQUIREMENTS.md",
                review_key="requirements/REQUIREMENTS.md",
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
        finally:
            temp.cleanup()

    def test_rf007_unsafe_path_in_definition_fails_closed(self) -> None:
        temp, project = fresh_project()
        try:
            req_blob, dec_blob = write_authority(project)
            key = (
                f"rf012-v1:repository:{REPOSITORY}|definition:R1|"
                f"requirements:{REQ_PATH}@{req_blob}|decisions:{DEC_PATH}@{dec_blob}"
            )
            install_record(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", brainstorm_green())
            install_record(
                project, "definition", "definition", "DEFINITION.toml",
                definition_green("R1", "requirements\\\\..\\\\REQUIREMENTS.md", [DEC_PATH]),
            )
            install_record(
                project, "planning", "planning", "PLANNING.toml", planning_approved(key)
            )
            install_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml", review_green(key)
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
        finally:
            temp.cleanup()


class LegacyDerivationTests(unittest.TestCase):
    def install_legacy_git(self, project: Path, *, plan_content: str = "# Master plan P1\n",
                           req_content: str = REQ_CONTENT,
                           dec_content: str = "# Accepted decision\n") -> tuple[str, str]:
        (project / REQ_PATH).parent.mkdir(parents=True, exist_ok=True)
        (project / REQ_PATH).write_text(req_content)
        (project / DEC_PATH).parent.mkdir(parents=True, exist_ok=True)
        (project / DEC_PATH).write_text(dec_content)
        plan_path = "planning/MASTER_PLAN.md"
        (project / plan_path).parent.mkdir(parents=True, exist_ok=True)
        (project / plan_path).write_text(plan_content)
        definition_path = "implementation/workstreams/sample-workstream/DEFINITION.toml"
        (project / definition_path).parent.mkdir(parents=True, exist_ok=True)
        (project / definition_path).write_text(definition_green("R1"))
        git(project, "add", REQ_PATH, DEC_PATH, plan_path, definition_path)
        git(project, "commit", "-qm", "rf012 snapshot")
        commit = git(project, "rev-parse", "HEAD")
        blob = git(project, "rev-parse", f"HEAD:{plan_path}")
        return commit, blob

    def planning_keyless(self, commit: str, blob: str) -> str:
        key = f"{REPOSITORY}@{commit}:planning/MASTER_PLAN.md@{blob}"
        return (
            'workstream_id = "sample-workstream"\n'
            'cycle = 1\n'
            'entry_subject = "definition:R1|planning-cycle:1"\n'
            'revision = "P1"\n'
            'state = "approved"\n'
            'planner_audit = "green"\n'
            'plan_path = "planning/MASTER_PLAN.md"\n'
            'review_mode = "independent"\n'
            'review_exemption_basis = ""\n'
            'review_exemption_base_subject = ""\n'
            'premium_a = "satisfied"\n'
            'premium_a_subject = "definition:R1|planning-cycle:1"\n'
            'premium_b = "satisfied"\n'
            f'premium_b_subject = "{key}"\n'
            'premium_c = "satisfied"\n'
            f'premium_c_subject = "{key}"\n'
            '[subject]\n'
            f'repository = "{REPOSITORY}"\n'
            f'commit = "{commit}"\n'
            'path = "planning/MASTER_PLAN.md"\n'
            f'blob = "{blob}"\n'
        )

    def review_keyless(self, commit: str, blob: str) -> str:
        return (
            'workstream_id = "sample-workstream"\n'
            'plan_revision = "P1"\n'
            'planning_cycle = 1\n'
            'attempt = "R01"\n'
            'verdict = "green"\n'
            'evidence_path = "evidence/plan-review-R01.md"\n'
            '[subject]\n'
            'class = "git_blob"\n'
            f'repository = "{REPOSITORY}"\n'
            f'commit = "{commit}"\n'
            'path = "planning/MASTER_PLAN.md"\n'
            f'blob = "{blob}"\n'
            '[acceptance]\n'
            'class = "authority"\n'
            'path = "requirements/REQUIREMENTS.md"\n'
            '[independence]\n'
            'materially_produced_or_repaired_subject = false\n'
            'basis = "Fresh semantic review context."\n'
        )

    def test_keyless_with_matching_snapshot_continues(self) -> None:
        temp, project = fresh_git_project()
        try:
            commit, blob = self.install_legacy_git(project)
            install_record(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", brainstorm_green())
            # DEFINITION.toml already committed; bind it in the manifest without overwriting.
            workstream = project / MANIFEST
            workstream.write_text(
                workstream.read_text()
                + '\n[definition]\nclass = "definition"\npath = "implementation/workstreams/sample-workstream/DEFINITION.toml"\n'
            )
            install_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_keyless(commit, blob),
            )
            install_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.review_keyless(commit, blob),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
            self.assertEqual(routed.subject, "M01-T04")
        finally:
            temp.cleanup()

    def test_keyless_with_mutated_authority_fails_closed(self) -> None:
        temp, project = fresh_git_project()
        try:
            commit, blob = self.install_legacy_git(project)
            install_record(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", brainstorm_green())
            workstream = project / MANIFEST
            workstream.write_text(
                workstream.read_text()
                + '\n[definition]\nclass = "definition"\npath = "implementation/workstreams/sample-workstream/DEFINITION.toml"\n'
            )
            install_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_keyless(commit, blob),
            )
            install_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.review_keyless(commit, blob),
            )
            (project / REQ_PATH).write_text("# Mutated after freeze\n")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("stale", routed.reason)
        finally:
            temp.cleanup()

    def test_keyless_with_revision_change_fails_closed(self) -> None:
        temp, project = fresh_git_project()
        try:
            commit, blob = self.install_legacy_git(project)
            install_record(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", brainstorm_green())
            definition_path = project / "implementation/workstreams/sample-workstream/DEFINITION.toml"
            definition_path.write_text(definition_green("R2"))
            workstream = project / MANIFEST
            workstream.write_text(
                workstream.read_text()
                + '\n[definition]\nclass = "definition"\npath = "implementation/workstreams/sample-workstream/DEFINITION.toml"\n'
            )
            install_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_keyless(commit, blob),
            )
            install_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.review_keyless(commit, blob),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
        finally:
            temp.cleanup()

    def test_unrelated_commits_do_not_churn_legacy_key(self) -> None:
        temp, project = fresh_git_project()
        try:
            commit, blob = self.install_legacy_git(project)
            unrelated = project / "implementation/workstreams/sample-workstream/evidence/note.md"
            unrelated.parent.mkdir(parents=True, exist_ok=True)
            unrelated.write_text("# Unrelated future work\n")
            git(project, "add", "implementation/workstreams/sample-workstream/evidence/note.md")
            git(project, "commit", "-qm", "unrelated future consumer commit")
            install_record(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", brainstorm_green())
            workstream = project / MANIFEST
            workstream.write_text(
                workstream.read_text()
                + '\n[definition]\nclass = "definition"\npath = "implementation/workstreams/sample-workstream/DEFINITION.toml"\n'
            )
            install_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_keyless(commit, blob),
            )
            install_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.review_keyless(commit, blob),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
        finally:
            temp.cleanup()


class CoEditedKeyTests(unittest.TestCase):
    """Explicit keys co-edited to live authority must not authorize the old subject."""

    def install_snapshot(self, project: Path) -> tuple[str, str]:
        (project / REQ_PATH).parent.mkdir(parents=True, exist_ok=True)
        (project / REQ_PATH).write_text(REQ_CONTENT)
        (project / DEC_PATH).parent.mkdir(parents=True, exist_ok=True)
        (project / DEC_PATH).write_text("# Accepted decision\n")
        plan_path = "planning/MASTER_PLAN.md"
        (project / plan_path).parent.mkdir(parents=True, exist_ok=True)
        (project / plan_path).write_text("# Master plan P1\n")
        definition_path = "implementation/workstreams/sample-workstream/DEFINITION.toml"
        (project / definition_path).parent.mkdir(parents=True, exist_ok=True)
        (project / definition_path).write_text(definition_green("R1"))
        git(project, "add", REQ_PATH, DEC_PATH, plan_path, definition_path)
        git(project, "commit", "-qm", "rf012 snapshot R1")
        return git(project, "rev-parse", "HEAD"), git(project, "rev-parse", f"HEAD:{plan_path}")

    def planning_explicit(self, commit: str, blob: str, authority_key: str) -> str:
        key = f"{REPOSITORY}@{commit}:planning/MASTER_PLAN.md@{blob}"
        return (
            'workstream_id = "sample-workstream"\n'
            'cycle = 1\n'
            'entry_subject = "definition:R1|planning-cycle:1"\n'
            'revision = "P1"\n'
            'state = "approved"\n'
            'planner_audit = "green"\n'
            'plan_path = "planning/MASTER_PLAN.md"\n'
            'review_mode = "independent"\n'
            'review_exemption_basis = ""\n'
            'review_exemption_base_subject = ""\n'
            'premium_a = "satisfied"\n'
            'premium_a_subject = "definition:R1|planning-cycle:1"\n'
            'premium_b = "satisfied"\n'
            f'premium_b_subject = "{key}"\n'
            'premium_c = "satisfied"\n'
            f'premium_c_subject = "{key}"\n'
            f'definition_authority_key = "{authority_key}"\n'
            '[subject]\n'
            f'repository = "{REPOSITORY}"\n'
            f'commit = "{commit}"\n'
            'path = "planning/MASTER_PLAN.md"\n'
            f'blob = "{blob}"\n'
        )

    def review_explicit(self, commit: str, blob: str, authority_key: str) -> str:
        return (
            'workstream_id = "sample-workstream"\n'
            'plan_revision = "P1"\n'
            'planning_cycle = 1\n'
            'attempt = "R01"\n'
            'verdict = "green"\n'
            'evidence_path = "evidence/plan-review-R01.md"\n'
            f'definition_authority_key = "{authority_key}"\n'
            '[subject]\n'
            'class = "git_blob"\n'
            f'repository = "{REPOSITORY}"\n'
            f'commit = "{commit}"\n'
            'path = "planning/MASTER_PLAN.md"\n'
            f'blob = "{blob}"\n'
            '[acceptance]\n'
            'class = "authority"\n'
            'path = "requirements/REQUIREMENTS.md"\n'
            '[independence]\n'
            'materially_produced_or_repaired_subject = false\n'
            'basis = "Fresh semantic review context."\n'
        )

    def bind_definition(self, project: Path) -> None:
        install_record(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", brainstorm_green())
        workstream = project / MANIFEST
        if "[definition]" not in workstream.read_text():
            workstream.write_text(
                workstream.read_text()
                + '\n[definition]\nclass = "definition"\npath = "implementation/workstreams/sample-workstream/DEFINITION.toml"\n'
            )

    def test_r1_entry_with_coedited_r2_key_fails_closed(self) -> None:
        temp, project = fresh_git_project()
        try:
            commit, blob = self.install_snapshot(project)
            # Live moves to R2; both stored keys are co-edited to the live R2
            # key while entry_subject and the immutable plan subject stay R1.
            (project / "implementation/workstreams/sample-workstream/DEFINITION.toml").write_text(
                definition_green("R2")
            )
            req_blob = git_blob_sha(REQ_CONTENT.encode())
            dec_blob = git_blob_sha(b"# Accepted decision\n")
            live_r2 = build_definition_authority_key(
                repository=REPOSITORY,
                definition_revision="R2",
                requirements_path=REQ_PATH,
                requirements_blob=req_blob,
                decisions=[(DEC_PATH, dec_blob)],
            )
            self.bind_definition(project)
            install_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_explicit(commit, blob, live_r2),
            )
            install_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.review_explicit(commit, blob, live_r2),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
                routed.reason,
            )
        finally:
            temp.cleanup()

    def test_mutation_with_coedited_keys_and_unchanged_subject_fails_closed(self) -> None:
        temp, project = fresh_git_project()
        try:
            commit, blob = self.install_snapshot(project)
            # Same-revision mutation; both stored keys co-edited to the new
            # blobs while entry and the immutable plan subject stay unchanged.
            mutated_req = "# Mutated requirements bytes\n"
            (project / REQ_PATH).write_text(mutated_req)
            req_blob = git_blob_sha(mutated_req.encode())
            dec_blob = git_blob_sha(b"# Accepted decision\n")
            live_mutated = build_definition_authority_key(
                repository=REPOSITORY,
                definition_revision="R1",
                requirements_path=REQ_PATH,
                requirements_blob=req_blob,
                decisions=[(DEC_PATH, dec_blob)],
            )
            self.bind_definition(project)
            install_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_explicit(commit, blob, live_mutated),
            )
            install_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.review_explicit(commit, blob, live_mutated),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
                routed.reason,
            )
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
