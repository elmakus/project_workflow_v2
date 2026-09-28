from __future__ import annotations

import copy
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.live_finding_contract import (
    AUTHORITY_MUTATION_KINDS,
    LIVE_FINDING_CLASSES,
    LIVE_FINDING_OWNERS,
    LiveFindingError,
    classify_live_finding_owner,
    live_finding_owner_module,
    require_classified_authority_mutation,
    tracker_cannot_authorize,
    validate_live_finding,
    validate_live_findings,
    verify_live_finding_records,
)
from tools.router import select_route
from tools.state_contract import (
    ValidationError,
    read_toml,
    validate_board,
    validate_review_history,
)

ROOT = Path(__file__).resolve().parents[1]
VALID = ROOT / "tests" / "fixtures" / "state" / "valid"
ROUTER_FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
ROUTER_MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
ROUTER_BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"

WORKSTREAM_ID = "sample-workstream"


def _acceptance(
    stage: str = "execution",
    path: str | None = None,
) -> dict:
    if path is None:
        path = (
            f"implementation/workstreams/{WORKSTREAM_ID}/findings/LF-001.toml"
        )
    return {
        "stage": stage,
        "record": {"class": "finding_acceptance", "path": path},
    }


def _decision(
    finding_id: str = "LF-001",
    finding_class: str = "implementation_defect",
    accepting_stage: str = "execution",
    decision: str = "accepted",
) -> str:
    return (
        f"finding_id = \"{finding_id}\"\n"
        f"finding_class = \"{finding_class}\"\n"
        f"accepting_stage = \"{accepting_stage}\"\n"
        f"decision = \"{decision}\"\n"
    )


def _finding(finding_id: str = "LF-001", **overrides) -> dict:
    record = {
        "id": finding_id,
        "finding_class": "implementation_defect",
        "observed": (
            "Live execution showed the retry helper returning success without "
            "writing the durable result locator."
        ),
        "evidence_refs": [
            f"implementation/workstreams/{WORKSTREAM_ID}/evidence/{finding_id}.md",
        ],
        "owner_stage": "execution",
        "authorization": "none",
        "tracker_locators": [],
    }
    record.update(overrides)
    return record


def _authorized_finding(finding_id: str = "LF-001", **overrides) -> dict:
    record = _finding(finding_id, **overrides)
    record["authorization"] = "owning_stage_accepted"
    record["acceptance"] = _acceptance(stage=record["owner_stage"])
    return record


def _validate(record: dict, workstream_id: str = WORKSTREAM_ID) -> dict:
    return validate_live_finding(
        record, "task_board.live_findings[0]", workstream_id=workstream_id
    )


class FiveClassTests(unittest.TestCase):
    def test_five_accepted_classes_each_validate_with_owning_stage(self) -> None:
        cases = [
            ("implementation_defect", "execution"),
            ("review_process_realization_defect", "review"),
            ("planning_execution_prep_fidelity_defect", "execution_prep"),
            ("accepted_authority_defect", "planning"),
            ("speculative_future_hardening", "none"),
        ]
        self.assertEqual(
            {case[0] for case in cases},
            set(LIVE_FINDING_CLASSES),
        )
        for index, (finding_class, owner) in enumerate(cases):
            with self.subTest(finding_class=finding_class):
                record = _validate(_finding(
                    f"LF-{index:03d}",
                    finding_class=finding_class,
                    owner_stage=owner,
                ))
                self.assertEqual(record["finding_class"], finding_class)
                self.assertEqual(record["owner_stage"], owner)

    def test_accepted_authority_defect_names_owning_accepted_stage(self) -> None:
        self.assertEqual(
            LIVE_FINDING_OWNERS["accepted_authority_defect"],
            frozenset({"planning", "definition", "brainstorming"}),
        )
        for index, owner in enumerate(("planning", "definition", "brainstorming")):
            with self.subTest(owner=owner):
                record = _validate(_finding(
                    f"LF-A{index}",
                    finding_class="accepted_authority_defect",
                    owner_stage=owner,
                ))
                self.assertEqual(record["owner_stage"], owner)

    def test_owner_stages_map_to_canonical_workflow_modules(self) -> None:
        self.assertEqual(live_finding_owner_module("execution"), "workflow/EXECUTION.md")
        self.assertEqual(live_finding_owner_module("review"), "workflow/REVIEW.md")
        self.assertEqual(
            live_finding_owner_module("execution_prep"), "workflow/EXECUTION_PREP.md"
        )
        self.assertEqual(live_finding_owner_module("planning"), "workflow/PLANNING.md")
        self.assertEqual(
            live_finding_owner_module("definition"), "workflow/DEFINITION.md"
        )
        self.assertEqual(
            live_finding_owner_module("brainstorming"), "workflow/BRAINSTORMING.md"
        )
        self.assertEqual(live_finding_owner_module("none"), "")
        with self.assertRaisesRegex(LiveFindingError, "unknown live-finding owner"):
            live_finding_owner_module("tracker")

    def test_classify_owner_rejects_wrong_boundary(self) -> None:
        self.assertEqual(
            classify_live_finding_owner(
                finding_class="planning_execution_prep_fidelity_defect",
                owner_stage="execution_prep",
            ),
            "execution_prep",
        )
        with self.assertRaisesRegex(LiveFindingError, "requires owner stage"):
            classify_live_finding_owner(
                finding_class="implementation_defect", owner_stage="planning"
            )
        with self.assertRaisesRegex(LiveFindingError, "unknown live-finding class"):
            classify_live_finding_owner(
                finding_class="tracker_consensus", owner_stage="execution"
            )


class ClassificationValidationTests(unittest.TestCase):
    def test_missing_class_fails_closed(self) -> None:
        record = _finding()
        del record["finding_class"]
        with self.assertRaisesRegex(LiveFindingError, "missing or ambiguous"):
            _validate(record)

    def test_unknown_class_fails_closed(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "missing or ambiguous"):
            _validate(_finding(finding_class="runtime_anomaly"))

    def test_ambiguous_class_fails_closed(self) -> None:
        for ambiguous in (
            "implementation_defect,review_process_realization_defect",
            "multiple",
            "",
        ):
            with self.subTest(ambiguous=ambiguous):
                with self.assertRaisesRegex(LiveFindingError, "missing or ambiguous"):
                    _validate(_finding(finding_class=ambiguous))

    def test_empty_observed_facts_fail_closed(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "observed"):
            _validate(_finding(observed="  "))

    def test_evidence_free_classification_fails_closed(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "evidence"):
            _validate(_finding(evidence_refs=[]))

    def test_foreign_evidence_path_fails_closed(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "evidence ref"):
            _validate(_finding(evidence_refs=["evidence/stray.md"]))

    def test_duplicate_evidence_refs_fail_closed(self) -> None:
        ref = f"implementation/workstreams/{WORKSTREAM_ID}/evidence/LF-001.md"
        with self.assertRaisesRegex(LiveFindingError, "duplicate evidence"):
            _validate(_finding(evidence_refs=[ref, ref]))

    def test_tracker_evidence_pointer_fails_closed(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "tracker"):
            _validate(_finding(
                evidence_refs=[
                    "https://github.com/owner/repo/issues/12",
                ],
            ))

    def test_implementation_defect_outside_execution_fails_closed(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "requires owner stage"):
            _validate(_finding(owner_stage="planning"))

    def test_accepted_authority_defect_outside_accepted_stages_fails(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "requires owner stage"):
            _validate(_finding(
                finding_class="accepted_authority_defect",
                owner_stage="execution",
            ))

    def test_speculative_hardening_must_not_name_mutation_owner(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "requires owner stage"):
            _validate(_finding(
                finding_class="speculative_future_hardening",
                owner_stage="execution",
            ))

    def test_speculative_hardening_must_not_be_promoted(self) -> None:
        record = _finding(
            finding_class="speculative_future_hardening",
            owner_stage="none",
            authorization="owning_stage_accepted",
        )
        record["acceptance"] = _acceptance(stage="none")
        with self.assertRaisesRegex(LiveFindingError, "speculative"):
            _validate(record)

    def test_unauthorized_finding_must_not_claim_acceptance(self) -> None:
        record = _finding()
        record["acceptance"] = _acceptance()
        with self.assertRaisesRegex(LiveFindingError, "not approval"):
            _validate(record)

    def test_free_prose_basis_cannot_prove_acceptance(self) -> None:
        record = _finding(authorization="owning_stage_accepted")
        record["authorization_basis"] = "Execution accepted the correction."
        with self.assertRaisesRegex(LiveFindingError, "verifiable acceptance"):
            _validate(record)

    def test_accepted_authorization_requires_acceptance_record(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "acceptance"):
            _validate(_finding(authorization="owning_stage_accepted"))

    def test_acceptance_requires_owning_stage_match(self) -> None:
        record = _authorized_finding()
        record["acceptance"] = _acceptance(stage="planning")
        with self.assertRaisesRegex(LiveFindingError, "owning stage"):
            _validate(record)

    def test_acceptance_rejects_unknown_record_class(self) -> None:
        for record_class in ("tracker", "evidence", "review_attempt", "result"):
            with self.subTest(record_class=record_class):
                record = _authorized_finding()
                record["acceptance"] = _acceptance()
                record["acceptance"]["record"]["class"] = record_class
                with self.assertRaisesRegex(LiveFindingError, "record class"):
                    _validate(record)

    def test_acceptance_rejects_tracker_record_path(self) -> None:
        for path in (
            "owner/repo#12",
            "https://github.com/owner/repo/issues/12",
        ):
            with self.subTest(path=path):
                record = _authorized_finding()
                record["acceptance"] = _acceptance(path=path)
                with self.assertRaisesRegex(LiveFindingError, "tracker"):
                    _validate(record)

    def test_acceptance_rejects_free_form_statement(self) -> None:
        for statement in ("  ", "See owner/repo#12, LGTM, ship it."):
            with self.subTest(statement=statement):
                record = _authorized_finding()
                record["acceptance"] = _acceptance()
                record["acceptance"]["statement"] = statement
                with self.assertRaisesRegex(LiveFindingError, "statement"):
                    _validate(record)

    def test_authorized_classification_validates_decision_citation(self) -> None:
        validated = _validate(_authorized_finding())
        self.assertEqual(
            validated["acceptance"]["record"],
            {
                "class": "finding_acceptance",
                "path": (
                    "implementation/workstreams/sample-workstream"
                    "/findings/LF-001.toml"
                ),
            },
        )

    def test_tracker_style_authority_claims_fail_closed(self) -> None:
        for key in (
            "scope_approved",
            "repair_authorized",
            "authority_mutated",
            "epoch_reset",
        ):
            with self.subTest(key=key):
                record = _finding()
                record[key] = True
                with self.assertRaisesRegex(LiveFindingError, "cannot approve scope"):
                    _validate(record)

    def test_duplicate_finding_ids_fail_closed(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "duplicate finding id"):
            validate_live_findings(
                [_finding("LF-001"), _finding("LF-001")], WORKSTREAM_ID
            )

    def test_missing_findings_array_preserves_historical_boards(self) -> None:
        self.assertEqual(validate_live_findings(None, WORKSTREAM_ID), {})
        self.assertEqual(validate_live_findings([], WORKSTREAM_ID), {})

    def test_unknown_authorization_fails_closed(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "unknown authorization"):
            _validate(_finding(authorization="tracker_approved"))


class AuthorityMutationGuardTests(unittest.TestCase):
    def test_unclassified_observation_cannot_mutate_authority(self) -> None:
        self.assertEqual(
            AUTHORITY_MUTATION_KINDS,
            frozenset({
                "scope_approval",
                "repair_authorization",
                "authority_mutation",
                "epoch_reset",
            }),
        )
        for mutation in sorted(AUTHORITY_MUTATION_KINDS):
            with self.subTest(mutation=mutation):
                with self.assertRaisesRegex(
                    LiveFindingError, "unclassified material observation"
                ):
                    require_classified_authority_mutation(None, mutation=mutation)

    def test_observed_without_authorization_is_not_approval(self) -> None:
        finding = _validate(_finding())
        with self.assertRaisesRegex(LiveFindingError, "not approval"):
            require_classified_authority_mutation(
                finding, mutation="repair_authorization"
            )

    def test_speculative_hardening_cannot_authorize_mutation(self) -> None:
        finding = _validate(_finding(
            finding_class="speculative_future_hardening",
            owner_stage="none",
        ))
        with self.assertRaisesRegex(LiveFindingError, "speculative"):
            require_classified_authority_mutation(
                finding, mutation="scope_approval"
            )

    def test_evidence_free_claim_cannot_mutate_authority(self) -> None:
        finding = dict(_validate(_authorized_finding()))
        finding["evidence_refs"] = []
        with self.assertRaisesRegex(LiveFindingError, "evidence"):
            require_classified_authority_mutation(
                finding, mutation="authority_mutation"
            )

    def test_tracker_sourced_claim_cannot_mutate_authority(self) -> None:
        finding = dict(_validate(_authorized_finding()))
        finding["evidence_refs"] = ["https://github.com/owner/repo/issues/12"]
        with self.assertRaisesRegex(LiveFindingError, "tracker"):
            require_classified_authority_mutation(
                finding, mutation="epoch_reset"
            )

    def test_missing_acceptance_never_authorizes_mutation(self) -> None:
        finding = dict(_validate(_authorized_finding()))
        finding.pop("acceptance")
        with self.assertRaisesRegex(LiveFindingError, "decision record"):
            require_classified_authority_mutation(
                finding, mutation="repair_authorization"
            )

    def test_statement_form_never_authorizes_mutation(self) -> None:
        finding = dict(_validate(_authorized_finding()))
        finding["acceptance"] = dict(finding["acceptance"])
        finding["acceptance"]["statement"] = "See owner/repo#12, LGTM."
        with self.assertRaisesRegex(LiveFindingError, "statement"):
            require_classified_authority_mutation(
                finding, mutation="repair_authorization"
            )

    def test_wrong_class_citation_never_authorizes_mutation(self) -> None:
        for record_class in ("evidence", "review_attempt", "result"):
            with self.subTest(record_class=record_class):
                finding = dict(_validate(_authorized_finding()))
                finding["acceptance"] = _acceptance()
                finding["acceptance"]["record"]["class"] = record_class
                with self.assertRaisesRegex(
                    LiveFindingError, "finding_acceptance"
                ):
                    require_classified_authority_mutation(
                        finding, mutation="repair_authorization"
                    )

    def test_foreign_stage_acceptance_cannot_authorize_mutation(self) -> None:
        finding = dict(_validate(_authorized_finding()))
        finding["acceptance"] = _acceptance(stage="planning")
        with self.assertRaisesRegex(LiveFindingError, "owning stage"):
            require_classified_authority_mutation(
                finding, mutation="repair_authorization"
            )

    def test_tracker_acceptance_record_cannot_authorize_mutation(self) -> None:
        finding = dict(_validate(_authorized_finding()))
        finding["acceptance"] = _acceptance(path="owner/repo#12")
        with self.assertRaisesRegex(LiveFindingError, "tracker"):
            require_classified_authority_mutation(
                finding, mutation="scope_approval"
            )

    def test_classified_authorized_mutation_returns_owning_stage(self) -> None:
        finding = _validate(_authorized_finding(
            finding_class="accepted_authority_defect",
            owner_stage="planning",
        ))
        self.assertEqual(
            require_classified_authority_mutation(
                finding, mutation="authority_mutation"
            ),
            "planning",
        )

    def test_unknown_mutation_kind_fails_closed(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "unknown authority mutation"):
            require_classified_authority_mutation(_finding(), mutation="close_issue")


class TrackerNonAuthorityTests(unittest.TestCase):
    def test_tracker_cannot_approve_authorize_mutate_reset_or_classify(self) -> None:
        expectations = {
            "scope": "approve scope",
            "repair": "authorize repair",
            "authority": "mutate accepted authority",
            "epoch_reset": "reset review epochs",
            "classification": "substitute for durable",
        }
        for kind, message in expectations.items():
            with self.subTest(kind=kind):
                with self.assertRaisesRegex(LiveFindingError, message):
                    tracker_cannot_authorize(kind)

    def test_unknown_tracker_kind_fails_closed(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "unknown tracker"):
            tracker_cannot_authorize("merge")

    def test_tracker_locators_are_untrusted_input_only(self) -> None:
        record = _validate(_finding(tracker_locators=["owner/repo#12"]))
        self.assertEqual(record["tracker_locators"], ["owner/repo#12"])
        with self.assertRaisesRegex(LiveFindingError, "evidence"):
            _validate(_finding(evidence_refs=[], tracker_locators=["owner/repo#12"]))
        with self.assertRaisesRegex(LiveFindingError, "tracker_locators"):
            _validate(_finding(tracker_locators=["  "]))


class BoardIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workstream = read_toml(VALID / "WORKSTREAM.toml")

    def test_board_accepts_valid_live_findings(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["live_findings"] = [
            _finding("LF-001"),
            _finding(
                "LF-002",
                finding_class="planning_execution_prep_fidelity_defect",
                owner_stage="execution_prep",
            ),
        ]
        validate_board(board, self.workstream)

    def test_board_rejects_wrong_owner_routing(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["live_findings"] = [_finding(owner_stage="planning")]
        with self.assertRaisesRegex(ValidationError, "requires owner stage"):
            validate_board(board, self.workstream)

    def test_board_rejects_tracker_evidence(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["live_findings"] = [_finding(
            evidence_refs=["https://github.com/owner/repo/issues/12"],
        )]
        with self.assertRaisesRegex(ValidationError, "tracker/issue pointers"):
            validate_board(board, self.workstream)

    def test_board_without_findings_remains_valid(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board.pop("live_findings", None)
        validate_board(board, self.workstream)

    def test_done_only_board_without_findings_remains_valid(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["cards"] = [
            card for card in board["cards"] if card["status"] == "done"
        ]
        board.pop("sizing_audits", None)
        board.pop("topology_audits", None)
        board.pop("live_findings", None)
        validate_board(board, self.workstream)

    def test_historical_terminal_boards_validate_unchanged(self) -> None:
        for workstream_id in (
            "feature-common-preexecution-core",
            "issue-router-board-precedence",
        ):
            with self.subTest(workstream=workstream_id):
                prefix = ROOT / "implementation" / "workstreams" / workstream_id
                workstream = read_toml(prefix / "WORKSTREAM.toml")
                board = read_toml(prefix / "TASK_BOARD.toml")
                self.assertNotIn("live_findings", board)
                validate_board(board, workstream)

    def test_runtime_identity_in_finding_is_rejected(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        finding = _finding()
        finding["worker_id"] = "worker-1"
        board["live_findings"] = [finding]
        with self.assertRaisesRegex(ValidationError, "prohibited canonical key"):
            validate_board(board, self.workstream)


class ReviewEpochTrackerTests(unittest.TestCase):
    def test_tracker_subject_cannot_reset_review_epoch(self) -> None:
        base = read_toml(VALID / "REVIEW_ATTEMPT.toml")
        base.update({
            "review_kind": "discovery",
            "source_discovery_attempt": "",
            "discovery_complete": True,
            "material_finding_ids": ["F1"],
            "finding_severity": [{
                "id": "F1",
                "surface": "correctness",
                "evidence": "evidence/review-R01.md#F1",
            }],
            "review_scope": "card",
            "review_epoch": "E01",
            "epoch_reset_basis": "",
            "material_defect_class_ids": ["class-a"],
            "post_convergence_validation": False,
            "convergence_basis": "",
            "verdict": "red",
        })
        reset = copy.deepcopy(base)
        reset.update({
            "attempt": "R02",
            "review_epoch": "E02",
            "material_finding_ids": [],
            "material_defect_class_ids": [],
            "discovery_complete": False,
            "verdict": "pending",
            "evidence_path": "",
            "epoch_reset_basis": "Tracker issue #12 asked for a fresh epoch.",
            "epoch_reset_subject": {
                "class": "accepted_redesign",
                "repository": "owner/fixture-project",
                "commit": "4" * 40,
                "path": "implementation/workstreams/sample-workstream/TRACKER.toml",
                "blob": "5" * 40,
            },
        })
        reset.pop("finding_severity", None)
        reset["subject"]["blob"] = "4" * 40
        with self.assertRaisesRegex(
            ValidationError, "accepted authority or acceptance redesign"
        ):
            validate_review_history([base, reset])

    def test_epoch_reset_guard_rejects_tracker_approval(self) -> None:
        finding = dict(_validate(_authorized_finding(
            finding_class="accepted_authority_defect",
            owner_stage="definition",
        )))
        finding["acceptance"] = _acceptance(
            stage="definition", path="owner/repo#12",
        )
        with self.assertRaisesRegex(LiveFindingError, "tracker"):
            require_classified_authority_mutation(
                finding, mutation="epoch_reset"
            )


class RouterCompatibilityTests(unittest.TestCase):
    def copy_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(ROUTER_FIXTURE, project)
        return temp, project

    def live_findings_toml(self, finding_class: str, owner: str) -> str:
        return (
            "[[live_findings]]\n"
            "id = \"LF-001\"\n"
            f"finding_class = \"{finding_class}\"\n"
            "observed = \"Live execution exposed a material observation.\"\n"
            "evidence_refs = ["
            "\"implementation/workstreams/sample-workstream/evidence/LF-001.md\""
            "]\n"
            f"owner_stage = \"{owner}\"\n"
            "authorization = \"none\"\n"
            "tracker_locators = [\"owner/repo#12\"]\n"
        )

    def write_evidence(self, project: Path, name: str = "LF-001.md") -> None:
        evidence = (project / "implementation" / "workstreams"
                    / "sample-workstream" / "evidence" / name)
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text("# Live-finding durable evidence\n")

    def test_classified_finding_does_not_change_legal_route(self) -> None:
        temp, project = self.copy_fixture()
        try:
            board = project / ROUTER_BOARD
            board.write_text(
                board.read_text()
                + self.live_findings_toml("implementation_defect", "execution")
            )
            self.write_evidence(project)
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution", "M01-T04"),
            )
            self.assertIn(
                "project:implementation/workstreams/sample-workstream/evidence/LF-001.md",
                routed.read_set,
            )
        finally:
            temp.cleanup()

    def test_speculative_finding_alone_is_not_a_blocker(self) -> None:
        temp, project = self.copy_fixture()
        try:
            board = project / ROUTER_BOARD
            board.write_text(
                board.read_text()
                + self.live_findings_toml(
                    "speculative_future_hardening", "none"
                )
            )
            self.write_evidence(project)
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution", "M01-T04"),
            )
        finally:
            temp.cleanup()

    def authorized_findings_toml(self) -> str:
        return (
            "[[live_findings]]\n"
            "id = \"LF-001\"\n"
            "finding_class = \"implementation_defect\"\n"
            "observed = \"Live execution exposed a material observation.\"\n"
            "evidence_refs = ["
            "\"implementation/workstreams/sample-workstream/evidence/LF-001.md\""
            "]\n"
            "owner_stage = \"execution\"\n"
            "authorization = \"owning_stage_accepted\"\n"
            "tracker_locators = []\n"
            "[live_findings.acceptance]\n"
            "stage = \"execution\"\n"
            "[live_findings.acceptance.record]\n"
            "class = \"finding_acceptance\"\n"
            "path = \"implementation/workstreams/sample-workstream/findings/LF-001.toml\"\n"
        )

    def write_decision(self, project: Path, text: str | None = None) -> None:
        decision = (project / "implementation" / "workstreams"
                    / "sample-workstream" / "findings" / "LF-001.toml")
        decision.parent.mkdir(parents=True, exist_ok=True)
        decision.write_text(text if text is not None else _decision())

    def test_authorized_finding_with_verified_acceptance_routes(self) -> None:
        temp, project = self.copy_fixture()
        try:
            board = project / ROUTER_BOARD
            board.write_text(
                board.read_text() + self.authorized_findings_toml()
            )
            self.write_evidence(project)
            self.write_decision(project)
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution", "M01-T04"),
            )
        finally:
            temp.cleanup()

    def test_missing_acceptance_record_recovers_at_router(self) -> None:
        temp, project = self.copy_fixture()
        try:
            board = project / ROUTER_BOARD
            board.write_text(
                board.read_text() + self.authorized_findings_toml()
            )
            self.write_evidence(project)
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("acceptance", routed.reason)
        finally:
            temp.cleanup()

    def test_unrelated_decision_content_recovers_at_router(self) -> None:
        temp, project = self.copy_fixture()
        try:
            board = project / ROUTER_BOARD
            board.write_text(
                board.read_text() + self.authorized_findings_toml()
            )
            self.write_evidence(project)
            self.write_decision(project, "# unrelated meeting notes\n")
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("acceptance", routed.reason)
        finally:
            temp.cleanup()

    def test_invalid_finding_recovers_on_board_validation(self) -> None:
        temp, project = self.copy_fixture()
        try:
            board = project / ROUTER_BOARD
            board.write_text(
                board.read_text()
                + self.live_findings_toml("implementation_defect", "planning")
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("owner stage", routed.reason)
        finally:
            temp.cleanup()


class IntakeTrustRepairTests(unittest.TestCase):
    """Nonexistent evidence and self-asserted prose must not become authority."""

    def copy_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(ROUTER_FIXTURE, project)
        return temp, project

    def test_missing_evidence_file_recovers_at_router(self) -> None:
        temp, project = self.copy_fixture()
        try:
            board = project / ROUTER_BOARD
            board.write_text(board.read_text() + (
                "[[live_findings]]\n"
                "id = \"LF-001\"\n"
                "finding_class = \"implementation_defect\"\n"
                "observed = \"Live execution exposed a material observation.\"\n"
                "evidence_refs = ["
                "\"implementation/workstreams/sample-workstream/evidence/LF-001.md\""
                "]\n"
                "owner_stage = \"execution\"\n"
                "authorization = \"none\"\n"
                "tracker_locators = []\n"
            ))
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("evidence", routed.reason)
        finally:
            temp.cleanup()

    def test_arbitrary_prose_basis_cannot_prove_acceptance(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "acceptance"):
            _validate(_finding(
                authorization="owning_stage_accepted",
                authorization_basis="Execution accepted the correction.",
            ))

    def test_guard_rejects_prose_based_authorization(self) -> None:
        finding = _finding(
            authorization="owning_stage_accepted",
            authorization_basis="Execution accepted the correction.",
        )
        with self.assertRaises(LiveFindingError):
            require_classified_authority_mutation(
                finding, mutation="authority_mutation"
            )

    def test_tracker_shorthand_evidence_reports_tracker_source(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "tracker"):
            _validate(_finding(evidence_refs=["owner/repo#12"]))

    def test_tracker_shorthand_cannot_become_authorization(self) -> None:
        finding = _finding(
            authorization="owning_stage_accepted",
            authorization_basis="See owner/repo#12 for approval.",
        )
        with self.assertRaises(LiveFindingError):
            require_classified_authority_mutation(
                finding, mutation="repair_authorization"
            )


class RecordVerificationTests(unittest.TestCase):
    def board_with(self, findings: list[dict]) -> dict:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["live_findings"] = findings
        return board

    def test_unreadable_evidence_fails_verification(self) -> None:
        board = self.board_with([_finding("LF-001")])
        with self.assertRaisesRegex(LiveFindingError, "cannot be read back"):
            verify_live_finding_records(board, record_reader=lambda path: None)

    def test_readable_evidence_verifies(self) -> None:
        board = self.board_with([_finding("LF-001")])
        verify_live_finding_records(
            board, record_reader=lambda path: "# evidence\n"
        )

    def test_unreadable_acceptance_record_fails_verification(self) -> None:
        board = self.board_with([_authorized_finding()])
        evidence = (
            f"implementation/workstreams/{WORKSTREAM_ID}/evidence/LF-001.md"
        )
        with self.assertRaisesRegex(LiveFindingError, "acceptance record"):
            verify_live_finding_records(
                board,
                record_reader=lambda path: "# evidence\n" if path == evidence else None,
            )

    def test_matching_decision_document_verifies(self) -> None:
        board = self.board_with([_authorized_finding()])
        findings = f"implementation/workstreams/{WORKSTREAM_ID}/findings/"
        verify_live_finding_records(
            board,
            record_reader=(
                lambda path: _decision()
                if path.startswith(findings)
                else "# evidence\n"
            ),
        )

    def test_unrelated_readable_file_cannot_prove_acceptance(self) -> None:
        board = self.board_with([_authorized_finding()])
        with self.assertRaisesRegex(LiveFindingError, "decision"):
            verify_live_finding_records(
                board,
                record_reader=lambda path: "# unrelated meeting notes\n",
            )

    def test_red_attempt_document_cannot_prove_acceptance(self) -> None:
        board = self.board_with([_authorized_finding(
            "LF-003",
            finding_class="review_process_realization_defect",
            owner_stage="review",
        )])
        with self.assertRaisesRegex(LiveFindingError, "decision"):
            verify_live_finding_records(
                board, record_reader=lambda path: 'verdict = "red"\n'
            )

    def test_decision_for_another_finding_fails_verification(self) -> None:
        board = self.board_with([_authorized_finding()])
        findings = f"implementation/workstreams/{WORKSTREAM_ID}/findings/"
        with self.assertRaisesRegex(LiveFindingError, "unrelated decisions"):
            verify_live_finding_records(
                board,
                record_reader=(
                    lambda path: _decision(finding_id="LF-999")
                    if path.startswith(findings)
                    else "# evidence\n"
                ),
            )

    def test_decision_with_mismatched_class_fails_verification(self) -> None:
        board = self.board_with([_authorized_finding()])
        findings = f"implementation/workstreams/{WORKSTREAM_ID}/findings/"
        with self.assertRaisesRegex(LiveFindingError, "mismatched classes"):
            verify_live_finding_records(
                board,
                record_reader=(
                    lambda path: _decision(
                        finding_class="accepted_authority_defect"
                    )
                    if path.startswith(findings)
                    else "# evidence\n"
                ),
            )

    def test_decision_by_foreign_stage_fails_verification(self) -> None:
        board = self.board_with([_authorized_finding()])
        findings = f"implementation/workstreams/{WORKSTREAM_ID}/findings/"
        with self.assertRaisesRegex(LiveFindingError, "owning stage"):
            verify_live_finding_records(
                board,
                record_reader=(
                    lambda path: _decision(accepting_stage="planning")
                    if path.startswith(findings)
                    else "# evidence\n"
                ),
            )

    def test_non_accepted_decision_fails_verification(self) -> None:
        board = self.board_with([_authorized_finding()])
        findings = f"implementation/workstreams/{WORKSTREAM_ID}/findings/"
        with self.assertRaisesRegex(LiveFindingError, "explicit accepted"):
            verify_live_finding_records(
                board,
                record_reader=(
                    lambda path: _decision(decision="rejected")
                    if path.startswith(findings)
                    else "# evidence\n"
                ),
            )

    def test_decision_with_extra_fields_fails_verification(self) -> None:
        board = self.board_with([_authorized_finding()])
        findings = f"implementation/workstreams/{WORKSTREAM_ID}/findings/"
        with self.assertRaisesRegex(LiveFindingError, "decision fields"):
            verify_live_finding_records(
                board,
                record_reader=(
                    lambda path: _decision() + 'tracker = "owner/repo#12"\n'
                    if path.startswith(findings)
                    else "# evidence\n"
                ),
            )

    def test_board_without_findings_verifies_trivially(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board.pop("live_findings", None)
        verify_live_finding_records(
            board,
            record_reader=lambda path: (_ for _ in ()).throw(
                AssertionError("reader must not be called")
            ),
        )


if __name__ == "__main__":
    unittest.main()
