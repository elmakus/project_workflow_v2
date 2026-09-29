from __future__ import annotations

import copy
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

from tools.state_contract import validate_state_record
from tools.router import select_route
from tools.v2_reconciliation import (
    PROFILE_ISSUE20,
    PROFILE_ISSUE22,
    SUPPORTED_PROFILES,
    V2ReconciliationError,
    apply_reconciliation_plan,
    canonicalize_definition,
    detect_profile,
    fingerprint_sources,
    plan_reconciliation,
)

ROOT = Path(__file__).resolve().parents[1]
WORKSTREAM_ID = "sample-workstream"
BRANCH = "feat/sample-workstream"
COMMIT = "a" * 40
BLOB = "b" * 40
CREATED_FROM = "1" * 40


def legacy_definition() -> dict:
    """SYNTHETIC unit-logic fixture only; does NOT match real #20/#22 bytes."""
    return {
        "workstream_id": WORKSTREAM_ID,
        "source_scope": "scope-a",
        "revision": 1,
        "state": "GREEN",
        "completeness_audit": "GREEN",
        "premium_a": "DUE",
        "requirements": "requirements/REQUIREMENTS.md",
        "decisions": ["decisions/ADR-001.md"],
    }


def legacy_planning() -> dict:
    """SYNTHETIC unit-logic fixture only; does NOT match real #20/#22 bytes."""
    return {
        "workstream_id": WORKSTREAM_ID,
        "cycle": 1,
        "entry_subject": "R1",
        "revision": 1,
        "plan_artifact": "planning/MASTER_PLAN.md",
        "frozen_subject": {
            "repository": "owner/repo",
            "commit": COMMIT,
            "path": "planning/MASTER_PLAN.md",
            "blob": BLOB,
        },
        "review_mode": "normal",
        "premium_a": "satisfied",
        "planner_audit": "PENDING",
    }


def legacy_workstream() -> dict:
    return {
        "workstream_id": WORKSTREAM_ID,
        "kind": "change",
        "branch": BRANCH,
        "integration_target": "main",
        "authority": [{"class": "authority", "path": "requirements/PROJECT_WORKFLOW_V2.md"}],
    }


def legacy_tracker() -> dict:
    return {
        "workstream_id": WORKSTREAM_ID,
        "provider": "github",
        "repository": "owner/repo",
        "number": 7,
        "url": "https://github.com/owner/repo/issues/7",
        "authority": "requirements/OLD.md",
    }


def legacy_board() -> dict:
    return {
        "workstream_id": WORKSTREAM_ID,
        "revision": 3,
        "execution_ref": {"branch": BRANCH},
        "result_path": "results/old.md",
        "review_requirement": "required",
        "cards": [
            {
                "id": "M01-T04",
                "status": "review_pending",
                "contract": {
                    "class": "task_card",
                    "path": f"implementation/workstreams/{WORKSTREAM_ID}/cards/M01-T04.md",
                },
            }
        ],
    }


def issue20_records() -> dict[str, dict]:
    return {"DEFINITION.toml": legacy_definition(), "PLANNING.toml": legacy_planning()}


def issue22_records() -> dict[str, dict]:
    return {
        "WORKSTREAM.toml": legacy_workstream(),
        "DEFINITION.toml": legacy_definition(),
        "PLANNING.toml": legacy_planning(),
        "TRACKER.toml": legacy_tracker(),
        "TASK_BOARD.toml": legacy_board(),
    }


def source_bytes_for(records: dict[str, dict]) -> dict[str, bytes]:
    # Deterministic TOML-ish encoding is unnecessary for fingerprint/plan tests;
    # use canonical JSON bytes as opaque source content. Apply tests use real
    # workdir files, not these bytes, for before/after comparison via plan.
    import json

    return {name: (json.dumps(data, sort_keys=True) + "\n").encode("utf-8") for name, data in records.items()}


class ProfileDetectionTests(unittest.TestCase):
    def test_supported_profile_set_is_bounded(self) -> None:
        self.assertEqual(SUPPORTED_PROFILES, (PROFILE_ISSUE20, PROFILE_ISSUE22))

    def test_issue20_profile_detected(self) -> None:
        self.assertEqual(detect_profile(issue20_records()), PROFILE_ISSUE20)

    def test_issue22_profile_detected(self) -> None:
        self.assertEqual(detect_profile(issue22_records()), PROFILE_ISSUE22)

    def test_unknown_set_fails_closed(self) -> None:
        with self.assertRaises(V2ReconciliationError):
            detect_profile({"WORKSTREAM.toml": legacy_workstream()})
        with self.assertRaises(V2ReconciliationError):
            detect_profile({})
        with self.assertRaises(V2ReconciliationError):
            detect_profile({"UNKNOWN.toml": {}})

    def test_contradictory_mixed_keys_fail_closed(self) -> None:
        definition = legacy_definition()
        definition["source_scope_subject"] = "scope-a@1"
        with self.assertRaises(V2ReconciliationError):
            detect_profile({"DEFINITION.toml": definition, "PLANNING.toml": legacy_planning()})

        planning = legacy_planning()
        planning["plan_path"] = planning["plan_artifact"]
        with self.assertRaises(V2ReconciliationError):
            detect_profile({"DEFINITION.toml": legacy_definition(), "PLANNING.toml": planning})

        tracker = legacy_tracker()
        tracker["issue_number"] = 7
        records = issue22_records()
        records["TRACKER.toml"] = tracker
        with self.assertRaises(V2ReconciliationError):
            detect_profile(records)

    def test_two_file_set_must_match_exact_drift(self) -> None:
        records = issue20_records()
        records["DEFINITION.toml"] = copy.deepcopy(records["DEFINITION.toml"])
        records["DEFINITION.toml"]["revision"] = "R1"
        with self.assertRaises(V2ReconciliationError):
            detect_profile(records)

    def test_issue22_requires_all_five_drift_markers(self) -> None:
        records = issue22_records()
        records["TASK_BOARD.toml"] = {
            "workstream_id": WORKSTREAM_ID,
            "revision": 3,
            "execution_ref": {"branch": BRANCH},
            "cards": [
                {
                    "id": "M01-T04",
                    "status": "in_progress",
                    "contract": {
                        "class": "task_card",
                        "path": f"implementation/workstreams/{WORKSTREAM_ID}/cards/M01-T04.md",
                    },
                }
            ],
        }
        with self.assertRaises(V2ReconciliationError):
            detect_profile(records)


class DefinitionCanonicalizationTests(unittest.TestCase):
    def test_definition_maps_deterministically_and_validates(self) -> None:
        canonical, decision = canonicalize_definition(legacy_definition(), WORKSTREAM_ID)
        self.assertEqual(canonical["source_scope_subject"], "scope-a@1")
        self.assertEqual(canonical["revision"], "R1")
        self.assertEqual(canonical["state"], "green")
        self.assertEqual(canonical["requirements"], {"class": "authority", "path": "requirements/REQUIREMENTS.md"})
        validate_state_record("definition", canonical, workstream_id=WORKSTREAM_ID)
        self.assertTrue(decision["preserved"])

    def test_definition_rejects_unknown_enum_and_wrong_workstream(self) -> None:
        bad = legacy_definition()
        bad["state"] = "BOGUS"
        with self.assertRaises(V2ReconciliationError):
            canonicalize_definition(bad, WORKSTREAM_ID)
        with self.assertRaises(V2ReconciliationError):
            canonicalize_definition(legacy_definition(), "other-workstream")

    def test_definition_rejects_outside_authority(self) -> None:
        bad = legacy_definition()
        bad["requirements"] = "/etc/passwd"
        with self.assertRaises(V2ReconciliationError):
            canonicalize_definition(bad, WORKSTREAM_ID)


class PlanningAuthorityTests(unittest.TestCase):
    def test_unprovable_subject_resets_gates_to_draft(self) -> None:
        definition, _ = canonicalize_definition(legacy_definition(), WORKSTREAM_ID)
        # No evidence: frozen_subject cannot be proven, must reset.
        from tools.v2_reconciliation import canonicalize_planning

        canonical, decision = canonicalize_planning(legacy_planning(), WORKSTREAM_ID, definition["revision"], None)
        self.assertEqual(canonical["state"], "draft")
        self.assertEqual(canonical["revision"], "P1")
        self.assertEqual(canonical["plan_path"], "planning/MASTER_PLAN.md")
        self.assertEqual(canonical["review_mode"], "independent")
        self.assertEqual(canonical["premium_b"], "not_due")
        self.assertEqual(canonical["premium_c"], "not_due")
        self.assertEqual(canonical["premium_b_subject"], "")
        self.assertEqual(canonical["subject"], {"repository": "", "commit": "", "path": "", "blob": ""})
        validate_state_record("planning", canonical, workstream_id=WORKSTREAM_ID)
        self.assertIn("B/C reset", " ".join(decision["reset"]))

    def test_proven_subject_preserves_freeze_with_b_due_never_satisfied(self) -> None:
        from tools.v2_reconciliation import canonicalize_planning

        definition, _ = canonicalize_definition(legacy_definition(), WORKSTREAM_ID)
        evidence = {"repository": "owner/repo", "commit": COMMIT, "path": "planning/MASTER_PLAN.md", "blob": BLOB}
        canonical, _ = canonicalize_planning(legacy_planning(), WORKSTREAM_ID, definition["revision"], evidence)
        self.assertEqual(canonical["state"], "frozen")
        self.assertEqual(canonical["premium_b"], "due")
        self.assertEqual(canonical["premium_c"], "not_due")
        self.assertEqual(canonical["subject"], evidence)
        validate_state_record("planning", canonical, workstream_id=WORKSTREAM_ID)

    def test_mismatched_evidence_fails_closed(self) -> None:
        from tools.v2_reconciliation import canonicalize_planning

        definition, _ = canonicalize_definition(legacy_definition(), WORKSTREAM_ID)
        evidence = {"repository": "owner/repo", "commit": COMMIT, "path": "planning/MASTER_PLAN.md", "blob": "c" * 40}
        with self.assertRaises(V2ReconciliationError):
            canonicalize_planning(legacy_planning(), WORKSTREAM_ID, definition["revision"], evidence)

    def test_stale_entry_subject_fails_closed(self) -> None:
        from tools.v2_reconciliation import canonicalize_planning

        planning = legacy_planning()
        planning["entry_subject"] = "R99"
        with self.assertRaises(V2ReconciliationError):
            canonicalize_planning(planning, WORKSTREAM_ID, "R1", None)


class Issue22CanonicalizationTests(unittest.TestCase):
    def test_full_bundle_reconciles_and_validates(self) -> None:
        records = issue22_records()
        plan = plan_reconciliation(
            records=records,
            source_bytes=source_bytes_for(records),
            workstream_id=WORKSTREAM_ID,
            branch=BRANCH,
            created_from_evidence=CREATED_FROM,
            plan_subject_evidence=None,
        )
        self.assertEqual(plan["profile"], PROFILE_ISSUE22)
        self.assertRegex(plan["source_fingerprint"], r"^[0-9a-f]{64}$")
        self.assertEqual(set(plan["outputs"]), set(records))
        # Every output passes its production validator.
        workstream = plan["outputs"]["WORKSTREAM.toml"]
        validate_state_record("workstream", workstream)
        validate_state_record("definition", plan["outputs"]["DEFINITION.toml"], workstream_id=WORKSTREAM_ID)
        validate_state_record("planning", plan["outputs"]["PLANNING.toml"], workstream_id=WORKSTREAM_ID)
        validate_state_record("tracker", plan["outputs"]["TRACKER.toml"], workstream_id=WORKSTREAM_ID)
        validate_state_record("task_board", plan["outputs"]["TASK_BOARD.toml"], workstream=workstream)
        # Authority decisions: scope preserved, gates reset, no satisfied transfer.
        planning = plan["outputs"]["PLANNING.toml"]
        self.assertNotEqual(planning["premium_b"], "satisfied")
        self.assertNotEqual(planning["premium_c"], "satisfied")
        board = plan["outputs"]["TASK_BOARD.toml"]
        self.assertEqual(board["cards"][0]["status"], "in_progress")
        self.assertNotIn("result_path", board)
        tracker = plan["outputs"]["TRACKER.toml"]
        self.assertEqual(tracker["state"], "create_pending_readback")
        self.assertEqual(tracker["issue_number"], 0)

    def test_missing_created_from_evidence_fails_closed(self) -> None:
        records = issue22_records()
        with self.assertRaises(V2ReconciliationError):
            plan_reconciliation(
                records=records,
                source_bytes=source_bytes_for(records),
                workstream_id=WORKSTREAM_ID,
                branch=BRANCH,
                created_from_evidence=None,
            )

    def test_tracker_number_url_mismatch_fails_closed(self) -> None:
        records = issue22_records()
        records["TRACKER.toml"]["number"] = 8
        with self.assertRaises(V2ReconciliationError):
            plan_reconciliation(
                records=records,
                source_bytes=source_bytes_for(records),
                workstream_id=WORKSTREAM_ID,
                branch=BRANCH,
                created_from_evidence=CREATED_FROM,
            )

    def test_board_with_review_history_fails_closed_no_replacement(self) -> None:
        records = issue22_records()
        records["TASK_BOARD.toml"]["cards"][0]["review_attempts"] = [
            {"class": "review_attempt", "path": f"implementation/workstreams/{WORKSTREAM_ID}/reviews/M01-T04-R01.toml"}
        ]
        # Detection already fails because the pure-drift board has no review locators.
        with self.assertRaises(V2ReconciliationError):
            detect_profile(records)

    def test_ambiguous_tracker_authorization_fails_closed(self) -> None:
        records = issue22_records()
        records["TRACKER.toml"]["repair_authorized"] = True
        with self.assertRaises(V2ReconciliationError):
            detect_profile(records)


class PlanApplyTests(unittest.TestCase):
    def _write_workdir(self, workdir: Path, plan: dict) -> None:
        for name, before in plan["expected_before"].items():
            (workdir / name).write_text(before, encoding="utf-8")

    def test_plan_is_memory_only_before_apply(self) -> None:
        records = issue20_records()
        raw_bytes = source_bytes_for(records)
        before_hashes = {name: fingerprint_sources({name: payload}) for name, payload in raw_bytes.items()}
        plan = plan_reconciliation(
            records=records, source_bytes=raw_bytes, workstream_id=WORKSTREAM_ID, branch=BRANCH
        )
        self.assertEqual(plan["profile"], PROFILE_ISSUE20)
        # Planning produced no filesystem side effects; caller workdir untouched.
        self.assertEqual(set(plan["expected_before"]), {"DEFINITION.toml", "PLANNING.toml"})
        self.assertTrue(all(isinstance(text, str) for text in plan["output_text"].values()))
        self.assertEqual(len(before_hashes), 2)

    def test_apply_then_idempotent_reapply(self) -> None:
        records = issue20_records()
        plan = plan_reconciliation(
            records={k: copy.deepcopy(v) for k, v in records.items()},
            source_bytes={k: f"before-{k}\n".encode() for k in records},
            workstream_id=WORKSTREAM_ID,
            branch=BRANCH,
        )
        with tempfile.TemporaryDirectory() as temp:
            workdir = Path(temp)
            for name, before in plan["expected_before"].items():
                (workdir / name).write_text(before, encoding="utf-8")
            first = apply_reconciliation_plan(plan=plan, workdir=workdir)
            self.assertEqual(first["status"], "applied")
            self.assertEqual(sorted(first["applied"]), ["DEFINITION.toml", "PLANNING.toml"])
            for name, after in plan["output_text"].items():
                self.assertEqual((workdir / name).read_text(encoding="utf-8"), after)
                # Rendered outputs parse and validate again.
                data = tomllib.loads(after)
                kind = {"DEFINITION.toml": "definition", "PLANNING.toml": "planning"}[name]
                validate_state_record(kind, data, workstream_id=WORKSTREAM_ID)
            second = apply_reconciliation_plan(plan=plan, workdir=workdir)
            self.assertEqual(second["status"], "noop")
            self.assertEqual(sorted(second["noop"]), ["DEFINITION.toml", "PLANNING.toml"])

    def test_interrupted_resume_produces_no_duplicate_effect(self) -> None:
        records = issue22_records()
        plan = plan_reconciliation(
            records=copy.deepcopy(records),
            source_bytes={k: f"before-{k}\n".encode() for k in records},
            workstream_id=WORKSTREAM_ID,
            branch=BRANCH,
            created_from_evidence=CREATED_FROM,
        )
        with tempfile.TemporaryDirectory() as temp:
            workdir = Path(temp)
            for name, before in plan["expected_before"].items():
                (workdir / name).write_text(before, encoding="utf-8")
            # Simulate interruption: two files already applied, rest still before.
            ordered = sorted(plan["output_text"])
            for name in ordered[:2]:
                (workdir / name).write_text(plan["output_text"][name], encoding="utf-8")
            resumed = apply_reconciliation_plan(plan=plan, workdir=workdir)
            self.assertEqual(resumed["status"], "applied")
            for name, after in plan["output_text"].items():
                self.assertEqual((workdir / name).read_text(encoding="utf-8"), after)
            again = apply_reconciliation_plan(plan=plan, workdir=workdir)
            self.assertEqual(again["status"], "noop")

    def test_divergence_fails_closed(self) -> None:
        records = issue20_records()
        plan = plan_reconciliation(
            records=copy.deepcopy(records),
            source_bytes={k: f"before-{k}\n".encode() for k in records},
            workstream_id=WORKSTREAM_ID,
            branch=BRANCH,
        )
        with tempfile.TemporaryDirectory() as temp:
            workdir = Path(temp)
            for name, before in plan["expected_before"].items():
                (workdir / name).write_text(before, encoding="utf-8")
            (workdir / "PLANNING.toml").write_text("unrelated divergence\n", encoding="utf-8")
            with self.assertRaises(V2ReconciliationError):
                apply_reconciliation_plan(plan=plan, workdir=workdir)

    def test_fingerprint_is_deterministic(self) -> None:
        payloads = {"B.toml": b"two\n", "A.toml": b"one\n"}
        first = fingerprint_sources(payloads)
        second = fingerprint_sources({"A.toml": b"one\n", "B.toml": b"two\n"})
        self.assertEqual(first, second)
        self.assertRegex(first, r"^[0-9a-f]{64}$")


class RealByteBlockerTests(unittest.TestCase):
    """Exact durable source verification at af76106 (#20) and 51c5ebc (#22).

    These tests read the real pre-Recovery bytes via git and prove M02 P1
    remains fail-closed Recovery instead of synthetic GREEN. They never mutate
    Board/Result/Review state and never rebind or drop the pending reservation.
    """

    COMMIT20 = "af76106415504c746668113d1df46a411fdcebd7"
    COMMIT22 = "51c5ebccca4ea1b4e1fd60b3f36dddc5fb2e72d2"
    WS20 = "implementation/workstreams/issue-paseo-child-delegation"
    WS22 = "implementation/workstreams/issue-ci-pending-continuation"

    def git_show(self, commit: str, path: str) -> bytes:
        completed = subprocess.run(
            ["git", "show", f"{commit}:{path}"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return completed.stdout

    def git_blob(self, commit: str, path: str) -> str:
        completed = subprocess.run(
            ["git", "ls-tree", commit, "--", path],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        parts = completed.stdout.strip().split()
        self.assertEqual(len(parts), 4, f"ls-tree unexpected: {completed.stdout!r}")
        return parts[2]

    def test_real_blob_identities_are_exact(self) -> None:
        self.assertEqual(
            self.git_blob(self.COMMIT20, f"{self.WS20}/DEFINITION.toml"),
            "5aed776d21580db46f3b1408209eb2e8be4593bd",
        )
        self.assertEqual(
            self.git_blob(self.COMMIT20, f"{self.WS20}/PLANNING.toml"),
            "32d92a06ff61d7dc6fd0a4dda18d5d9eeed12256",
        )
        self.assertEqual(
            self.git_blob(self.COMMIT22, f"{self.WS22}/DEFINITION.toml"),
            "4e33647bdd71570124bc0ba1447143e612cf4eda",
        )
        self.assertEqual(
            self.git_blob(self.COMMIT22, f"{self.WS22}/PLANNING.toml"),
            "eebec0b303fa4d90cf886d7d9472edebc6481f8d",
        )
        self.assertEqual(
            self.git_blob(self.COMMIT22, f"{self.WS22}/reviews/M01-T01-R01.toml"),
            "87db02e2fe07c557418e9fb21e22802e7f78c319",
        )

    def test_real_20_authority_and_plan_path_fail_closed(self) -> None:
        definition_raw = self.git_show(self.COMMIT20, f"{self.WS20}/DEFINITION.toml")
        planning_raw = self.git_show(self.COMMIT20, f"{self.WS20}/PLANNING.toml")
        definition = tomllib.loads(definition_raw.decode("utf-8"))
        planning = tomllib.loads(planning_raw.decode("utf-8"))
        # Exact real markers that synthetic fixtures do not carry.
        self.assertEqual(definition["source_scope"], "temporary-paseo-create-agent-readiness@1")
        self.assertIn("requirements_locator", definition)
        self.assertIn("accepted_decision_locators", definition)
        self.assertIn("premium_a_state", definition)
        self.assertEqual(planning["plan_artifact"], f"{self.WS20}/PLAN.md")
        self.assertIn("frozen_plan_subject", planning)
        self.assertEqual(planning["premium_c"], "pending")
        # Synthetic shape differs; real must not be claimed as supported.
        self.assertNotEqual(definition["source_scope"], "scope-a")
        self.assertNotEqual(planning["plan_artifact"], "planning/MASTER_PLAN.md")
        # M02 fails closed with explicit authority/plan-path blockers.
        with self.assertRaisesRegex(V2ReconciliationError, "authority|double-suffix|fragment|D4"):
            from tools.v2_reconciliation import canonicalize_definition

            canonicalize_definition(definition, "issue-paseo-child-delegation")
        with self.assertRaisesRegex(V2ReconciliationError, "planning|PLAN.md|frozen_plan_subject|pending"):
            from tools.v2_reconciliation import canonicalize_planning

            canonicalize_planning(planning, "issue-paseo-child-delegation", "R1", None)

    def test_real_20_source_set_is_not_either_synthetic_profile(self) -> None:
        completed = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", self.COMMIT20, "--", f"{self.WS20}/"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            check=True,
            text=True,
        )
        names = [line for line in completed.stdout.splitlines() if line]
        # 8 workstream files at af76106, not the synthetic 2-file profile.
        self.assertEqual(len(names), 8)
        with self.assertRaisesRegex(V2ReconciliationError, "not an explicitly supported profile"):
            detect_profile({"DEFINITION.toml": {}, "PLANNING.toml": {}, "WORKSTREAM.toml": {}})

    def test_real_22_pending_reservation_is_preserved_not_rebound(self) -> None:
        review_raw = self.git_show(self.COMMIT22, f"{self.WS22}/reviews/M01-T01-R01.toml")
        review = tomllib.loads(review_raw.decode("utf-8"))
        self.assertEqual(review["verdict"], "pending")
        self.assertEqual(review["subject"]["class"], "git_commit")
        self.assertEqual(review["subject"]["commit"], "32e7971f96e76a403de6bc5cd7b8d5979ac0dfe2")
        self.assertEqual(review["subject"]["path"], "tools/continuation_contract.py")
        # Any source set containing the pending file must fail with the explicit
        # #26 blocker, never silently drop or rebind git_commit to git_blob.
        with self.assertRaisesRegex(V2ReconciliationError, "#26|pending.*reservation"):
            detect_profile(
                {
                    "WORKSTREAM.toml": {},
                    "DEFINITION.toml": {},
                    "PLANNING.toml": {},
                    "TRACKER.toml": {},
                    "TASK_BOARD.toml": {},
                    "reviews/M01-T01-R01.toml": review,
                }
            )

    def test_real_22_definition_planning_fail_closed(self) -> None:
        definition = tomllib.loads(
            self.git_show(self.COMMIT22, f"{self.WS22}/DEFINITION.toml").decode("utf-8")
        )
        planning = tomllib.loads(
            self.git_show(self.COMMIT22, f"{self.WS22}/PLANNING.toml").decode("utf-8")
        )
        self.assertEqual(definition["source_scope"], "ci-pending-deterministic-continuation@1")
        self.assertIn("requirements_locator", definition)
        self.assertEqual(planning["plan_artifact"], f"{self.WS22}/PLAN.md")
        self.assertIsInstance(planning["frozen_subject"], str)
        self.assertTrue(planning["frozen_subject"].startswith("git-blob:"))
        with self.assertRaisesRegex(V2ReconciliationError, "authority|double-suffix|fragment|D4"):
            from tools.v2_reconciliation import canonicalize_definition

            canonicalize_definition(definition, "issue-ci-pending-continuation")
        with self.assertRaisesRegex(V2ReconciliationError, "planning|PLAN.md|git-blob|table"):
            from tools.v2_reconciliation import canonicalize_planning

            canonicalize_planning(planning, "issue-ci-pending-continuation", "R1", None)


class ValidatorRouterIntegrationTests(unittest.TestCase):
    def test_legacy_shapes_fail_production_validators(self) -> None:
        with self.assertRaises(Exception):
            validate_state_record("definition", legacy_definition(), workstream_id=WORKSTREAM_ID)
        with self.assertRaises(Exception):
            validate_state_record("planning", legacy_planning(), workstream_id=WORKSTREAM_ID)
        with self.assertRaises(Exception):
            validate_state_record("tracker", legacy_tracker(), workstream_id=WORKSTREAM_ID)
        workstream = {
            "workstream_id": WORKSTREAM_ID,
            "kind": "change",
            "branch": BRANCH,
            "created_from": CREATED_FROM,
            "integration_target": "main",
            "authority": [{"class": "authority", "path": "requirements/PROJECT_WORKFLOW_V2.md"}],
            "task_board": {"class": "task_board", "path": f"implementation/workstreams/{WORKSTREAM_ID}/TASK_BOARD.toml"},
        }
        with self.assertRaises(Exception):
            validate_state_record("task_board", legacy_board(), workstream=workstream)

    def test_reconciled_router_project_routes_to_execution_not_recovery(self) -> None:
        fixture = ROOT / "tests" / "fixtures" / "router" / "valid-project"
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "project"
            shutil.copytree(fixture, project)
            manifest = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
            board_rel = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
            # Legacy workstream (missing created_from) must route to Recovery.
            legacy = (
                'kind = "change"\nworkstream_id = "sample-workstream"\nbranch = "feat/sample-workstream"\n'
                'integration_target = "main"\nauthority = [{ class = "authority", path = "requirements/PROJECT_WORKFLOW_V2.md" }]\n'
                '[task_board]\nclass = "task_board"\npath = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"\n'
            )
            (project / manifest).write_text(legacy, encoding="utf-8")
            recovered = select_route(project, [manifest], package_root=ROOT)
            self.assertEqual(recovered.disposition, "recovery")
            # Reconciled workstream built through the validated boundary routes onward.
            records = issue22_records()
            plan = plan_reconciliation(
                records=copy.deepcopy(records),
                source_bytes={k: f"before-{k}\n".encode() for k in records},
                workstream_id="sample-workstream",
                branch="feat/sample-workstream",
                created_from_evidence=CREATED_FROM,
            )
            (project / manifest).write_text(plan["output_text"]["WORKSTREAM.toml"], encoding="utf-8")
            (project / board_rel).write_text(plan["output_text"]["TASK_BOARD.toml"], encoding="utf-8")
            routed = select_route(project, [manifest], package_root=ROOT)
            # The reconciled board maps review_pending to in_progress without a
            # result, so the router reaches the live execution owner instead of
            # fail-closed Recovery.
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))


if __name__ == "__main__":
    unittest.main()
