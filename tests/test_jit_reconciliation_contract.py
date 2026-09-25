from __future__ import annotations

import copy
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.live_finding_contract import (
    DOWNSTREAM_DISPOSITIONS,
    MATERIALITY_ASPECTS,
    RECONCILIATION_STATES,
    LiveFindingError,
    parse_acceptance_decision,
    parse_reconciliation_decision,
    require_reconciled_trigger_consumption,
    validate_finding_trigger_gates,
    validate_live_finding,
    validate_live_findings,
    verify_finding_trigger_records,
    verify_reconciliation_decision,
)
from tools.router import select_route
from tools.state_contract import (
    ValidationError,
    read_toml,
    validate_board,
)

ROOT = Path(__file__).resolve().parents[1]
VALID = ROOT / "tests" / "fixtures" / "state" / "valid"
ROUTER_FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
ROUTER_MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
ROUTER_BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"

WORKSTREAM_ID = "sample-workstream"
TRIGGER_ID = "after-M01-T01"


def _downstream(
    trigger: str = TRIGGER_ID,
    aspect: str = "semantics",
    reconciliation: str = "pending",
    *,
    material_ref: str | None = None,
    acceptance: dict | None = None,
) -> dict:
    table: dict = {
        "disposition": "material",
        "trigger": trigger,
        "aspect": aspect,
        "material_evidence_refs": [
            material_ref
            or f"implementation/workstreams/{WORKSTREAM_ID}/evidence/LF-001-material.md"
        ],
        "reconciliation": reconciliation,
    }
    if acceptance is not None:
        table["acceptance"] = acceptance
    return table


def _reconciliation_acceptance(
    stage: str = "execution",
    path: str | None = None,
) -> dict:
    if path is None:
        path = (
            f"implementation/workstreams/{WORKSTREAM_ID}"
            "/findings/LF-001.reconciliation.toml"
        )
    return {
        "stage": stage,
        "record": {"class": "finding_reconciliation", "path": path},
    }


def _reconciliation_decision(
    finding_id: str = "LF-001",
    finding_class: str = "implementation_defect",
    trigger_id: str = TRIGGER_ID,
    accepting_stage: str = "execution",
    decision: str = "reconciled",
) -> str:
    return (
        f"finding_id = \"{finding_id}\"\n"
        f"finding_class = \"{finding_class}\"\n"
        f"trigger_id = \"{trigger_id}\"\n"
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


def _material_finding(finding_id: str = "LF-001", **overrides) -> dict:
    downstream = overrides.pop("downstream", _downstream())
    return _finding(finding_id, downstream=downstream, **overrides)


def _reconciled_finding(finding_id: str = "LF-001", **overrides) -> dict:
    owner = overrides.get("owner_stage", "execution")
    downstream = overrides.pop(
        "downstream",
        _downstream(
            reconciliation="reconciled",
            acceptance=_reconciliation_acceptance(stage=owner),
        ),
    )
    return _finding(finding_id, downstream=downstream, **overrides)


def _validate(record: dict, workstream_id: str = WORKSTREAM_ID) -> dict:
    return validate_live_finding(
        record, "task_board.live_findings[0]", workstream_id=workstream_id
    )


def _trigger(
    trigger_id: str = TRIGGER_ID,
    after_card: str = "M01-T01",
    state: str = "satisfied",
) -> dict:
    return {
        "id": trigger_id,
        "after_card": after_card,
        "state": state,
        "condition": "Downstream boundary depends on the predecessor result.",
    }


def _board_with(
    findings: list[dict] | None,
    triggers: list[dict] | None = None,
) -> dict:
    board = read_toml(VALID / "TASK_BOARD.toml")
    if findings is None:
        board.pop("live_findings", None)
    else:
        board["live_findings"] = findings
    if triggers is not None:
        board["jit_triggers"] = triggers
    return board


class DownstreamVocabularyTests(unittest.TestCase):
    def test_disposition_aspect_and_state_vocabularies_are_exact(self) -> None:
        self.assertEqual(DOWNSTREAM_DISPOSITIONS, frozenset({"material", "unrelated"}))
        self.assertEqual(
            MATERIALITY_ASPECTS, frozenset({"authority", "topology", "semantics"})
        )
        self.assertEqual(RECONCILIATION_STATES, frozenset({"pending", "reconciled"}))


class DownstreamDispositionTests(unittest.TestCase):
    def test_absent_downstream_validates_and_never_blocks(self) -> None:
        validated = _validate(_finding())
        self.assertIsNone(validated["downstream"])
        findings = validate_live_findings([_finding()], WORKSTREAM_ID)
        self.assertEqual(
            validate_finding_trigger_gates(findings, [_trigger(state="consumed")]),
            {},
        )

    def test_explicit_unrelated_validates_and_never_blocks(self) -> None:
        validated = _validate(_finding(downstream={"disposition": "unrelated"}))
        self.assertEqual(validated["downstream"], {"disposition": "unrelated"})
        findings = validate_live_findings(
            [_finding(downstream={"disposition": "unrelated"})], WORKSTREAM_ID
        )
        self.assertEqual(
            validate_finding_trigger_gates(findings, [_trigger(state="consumed")]),
            {},
        )

    def test_unrelated_must_not_claim_targeting_or_reconciliation(self) -> None:
        for extra in (
            {"trigger": TRIGGER_ID},
            {"aspect": "semantics"},
            {"material_evidence_refs": [
                f"implementation/workstreams/{WORKSTREAM_ID}/evidence/LF-001-material.md"
            ]},
            {"reconciliation": "pending"},
            {"acceptance": _reconciliation_acceptance()},
        ):
            with self.subTest(extra=sorted(extra)):
                downstream = {"disposition": "unrelated"}
                downstream.update(extra)
                with self.assertRaisesRegex(LiveFindingError, "unrelated"):
                    _validate(_finding(downstream=downstream))

    def test_unknown_disposition_fails_closed(self) -> None:
        for disposition in ("maybe", "material,unrelated", "", None):
            with self.subTest(disposition=disposition):
                with self.assertRaisesRegex(LiveFindingError, "disposition"):
                    _validate(_finding(downstream={"disposition": disposition}))

    def test_non_table_downstream_fails_closed(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "downstream"):
            _validate(_finding(downstream="material"))

    def test_unexpected_downstream_keys_fail_closed(self) -> None:
        downstream = _downstream()
        downstream["approved"] = True
        with self.assertRaisesRegex(LiveFindingError, "unexpected downstream"):
            _validate(_finding(downstream=downstream))

    def test_free_prose_reconciliation_claims_fail_closed(self) -> None:
        for key in ("reconciliation_basis", "statement"):
            with self.subTest(key=key):
                downstream = _downstream()
                downstream[key] = "Execution Prep reconciled the trigger."
                with self.assertRaisesRegex(LiveFindingError, "free-prose"):
                    _validate(_finding(downstream=downstream))

    def test_material_requires_exact_trigger_aspect_evidence_and_state(self) -> None:
        base = _downstream()
        for key in (
            "trigger",
            "aspect",
            "material_evidence_refs",
            "reconciliation",
        ):
            with self.subTest(missing=key):
                downstream = dict(base)
                del downstream[key]
                with self.assertRaises(LiveFindingError):
                    _validate(_finding(downstream=downstream))

    def test_empty_trigger_id_fails_closed(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "trigger"):
            _validate(_finding(downstream=_downstream(trigger="  ")))

    def test_each_materiality_aspect_validates(self) -> None:
        for aspect in ("authority", "topology", "semantics"):
            with self.subTest(aspect=aspect):
                validated = _validate(_finding(downstream=_downstream(aspect=aspect)))
                assert validated["downstream"] is not None
                self.assertEqual(validated["downstream"]["aspect"], aspect)

    def test_ambiguous_aspect_fails_closed(self) -> None:
        for aspect in ("authority,topology", "multiple", "", None):
            with self.subTest(aspect=aspect):
                with self.assertRaisesRegex(LiveFindingError, "aspect"):
                    _validate(_finding(downstream=_downstream(aspect=aspect)))

    def test_materiality_evidence_free_targeting_fails_closed(self) -> None:
        downstream = _downstream()
        downstream["material_evidence_refs"] = []
        with self.assertRaisesRegex(LiveFindingError, "evidence"):
            _validate(_finding(downstream=downstream))

    def test_foreign_materiality_evidence_fails_closed(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "evidence ref"):
            _validate(
                _finding(downstream=_downstream(material_ref="evidence/stray.md"))
            )

    def test_tracker_materiality_evidence_fails_closed(self) -> None:
        for ref in ("https://github.com/owner/repo/issues/12", "owner/repo#12"):
            with self.subTest(ref=ref):
                with self.assertRaisesRegex(LiveFindingError, "tracker"):
                    _validate(_finding(downstream=_downstream(material_ref=ref)))

    def test_duplicate_materiality_evidence_fails_closed(self) -> None:
        ref = f"implementation/workstreams/{WORKSTREAM_ID}/evidence/LF-001-material.md"
        downstream = _downstream()
        downstream["material_evidence_refs"] = [ref, ref]
        with self.assertRaisesRegex(LiveFindingError, "duplicate evidence"):
            _validate(_finding(downstream=downstream))

    def test_speculative_hardening_can_never_be_material(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "speculative"):
            _validate(_finding(
                finding_class="speculative_future_hardening",
                owner_stage="none",
                downstream=_downstream(),
            ))

    def test_speculative_hardening_stays_non_blocking(self) -> None:
        for downstream in (None, {"disposition": "unrelated"}):
            with self.subTest(downstream=downstream):
                record = _finding(
                    finding_class="speculative_future_hardening",
                    owner_stage="none",
                )
                if downstream is not None:
                    record["downstream"] = downstream
                validated = _validate(record)
                self.assertIn(
                    validated["downstream"], (None, {"disposition": "unrelated"})
                )
                findings = validate_live_findings([record], WORKSTREAM_ID)
                self.assertEqual(
                    validate_finding_trigger_gates(
                        findings, [_trigger(state="consumed")]
                    ),
                    {},
                )


class ReconciliationCitationTests(unittest.TestCase):
    def test_pending_reconciliation_must_not_claim_acceptance(self) -> None:
        downstream = _downstream(
            reconciliation="pending",
            acceptance=_reconciliation_acceptance(),
        )
        with self.assertRaisesRegex(LiveFindingError, "pending reconciliation"):
            _validate(_finding(downstream=downstream))

    def test_reconciled_reconciliation_requires_acceptance(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "reconciliation"):
            _validate(_finding(downstream=_downstream(reconciliation="reconciled")))
        with self.assertRaisesRegex(LiveFindingError, "reconciliation"):
            _validate(_finding(downstream=_downstream(
                reconciliation="reconciled", acceptance="execution accepted",
            )))

    def test_reconciliation_requires_owning_stage_match(self) -> None:
        downstream = _downstream(
            reconciliation="reconciled",
            acceptance=_reconciliation_acceptance(stage="planning"),
        )
        with self.assertRaisesRegex(LiveFindingError, "owning stage"):
            _validate(_finding(downstream=downstream))

    def test_worker_self_authorization_cannot_reconcile(self) -> None:
        for stage in ("worker", "worker_1", "worker-2", "Worker", "worker:main"):
            with self.subTest(stage=stage):
                downstream = _downstream(
                    reconciliation="reconciled",
                    acceptance=_reconciliation_acceptance(stage=stage),
                )
                with self.assertRaisesRegex(LiveFindingError, "self-authorization"):
                    _validate(_finding(downstream=downstream))

    def test_reconciliation_rejects_unknown_record_class(self) -> None:
        for record_class in (
            "finding_acceptance",
            "tracker",
            "evidence",
            "review_attempt",
            "result",
        ):
            with self.subTest(record_class=record_class):
                acceptance = _reconciliation_acceptance()
                acceptance["record"]["class"] = record_class
                downstream = _downstream(
                    reconciliation="reconciled", acceptance=acceptance
                )
                with self.assertRaisesRegex(LiveFindingError, "record class"):
                    _validate(_finding(downstream=downstream))

    def test_reconciliation_rejects_tracker_record_path(self) -> None:
        for path in (
            "owner/repo#12",
            "https://github.com/owner/repo/issues/12",
        ):
            with self.subTest(path=path):
                downstream = _downstream(
                    reconciliation="reconciled",
                    acceptance=_reconciliation_acceptance(path=path),
                )
                with self.assertRaisesRegex(LiveFindingError, "tracker"):
                    _validate(_finding(downstream=downstream))

    def test_reconciliation_rejects_foreign_record_path(self) -> None:
        downstream = _downstream(
            reconciliation="reconciled",
            acceptance=_reconciliation_acceptance(path="findings/stray.toml"),
        )
        with self.assertRaisesRegex(LiveFindingError, "record path"):
            _validate(_finding(downstream=downstream))

    def test_reconciliation_rejects_free_form_statement(self) -> None:
        acceptance = _reconciliation_acceptance()
        acceptance["statement"] = "See owner/repo#12, LGTM, consume it."
        downstream = _downstream(reconciliation="reconciled", acceptance=acceptance)
        with self.assertRaisesRegex(LiveFindingError, "statement"):
            _validate(_finding(downstream=downstream))

    def test_reconciliation_rejects_unexpected_acceptance_keys(self) -> None:
        acceptance = _reconciliation_acceptance()
        acceptance["approved"] = True
        downstream = _downstream(reconciliation="reconciled", acceptance=acceptance)
        with self.assertRaisesRegex(LiveFindingError, "unexpected reconciliation"):
            _validate(_finding(downstream=downstream))

    def test_valid_reconciled_citation_validates(self) -> None:
        validated = _validate(_reconciled_finding())
        assert validated["downstream"] is not None
        self.assertEqual(
            validated["downstream"]["acceptance"]["record"],
            {
                "class": "finding_reconciliation",
                "path": (
                    "implementation/workstreams/sample-workstream"
                    "/findings/LF-001.reconciliation.toml"
                ),
            },
        )

    def test_unknown_reconciliation_state_fails_closed(self) -> None:
        for state in ("approved", "tracker_approved", "done", "", None):
            with self.subTest(state=state):
                with self.assertRaisesRegex(LiveFindingError, "reconciliation"):
                    _validate(_finding(downstream=_downstream(reconciliation=state)))


class TriggerGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workstream = read_toml(VALID / "WORKSTREAM.toml")

    def test_pending_material_holds_waiting_and_satisfied_triggers(self) -> None:
        for state in ("waiting", "satisfied"):
            with self.subTest(state=state):
                findings = validate_live_findings(
                    [_material_finding()], WORKSTREAM_ID
                )
                self.assertEqual(
                    validate_finding_trigger_gates(findings, [_trigger(state=state)]),
                    {TRIGGER_ID: ["LF-001"]},
                )
                validate_board(
                    _board_with([_material_finding()], [_trigger(state=state)]),
                    self.workstream,
                )

    def test_pending_material_blocks_consumed_trigger(self) -> None:
        findings = validate_live_findings([_material_finding()], WORKSTREAM_ID)
        with self.assertRaisesRegex(LiveFindingError, "cannot be consumed"):
            validate_finding_trigger_gates(findings, [_trigger(state="consumed")])
        board = _board_with([_material_finding()], [_trigger(state="consumed")])
        with self.assertRaisesRegex(ValidationError, "cannot be consumed"):
            validate_board(board, self.workstream)

    def test_reconciled_material_permits_consumption_without_erasing_history(self) -> None:
        findings = validate_live_findings([_reconciled_finding()], WORKSTREAM_ID)
        self.assertEqual(
            validate_finding_trigger_gates(findings, [_trigger(state="consumed")]),
            {},
        )
        board = _board_with([_reconciled_finding()], [_trigger(state="consumed")])
        validate_board(board, self.workstream)
        self.assertEqual(board["live_findings"][0]["downstream"]["reconciliation"],
                         "reconciled")

    def test_unrelated_finding_never_blocks_consumed_trigger(self) -> None:
        record = _finding(downstream={"disposition": "unrelated"})
        findings = validate_live_findings([record], WORKSTREAM_ID)
        self.assertEqual(
            validate_finding_trigger_gates(findings, [_trigger(state="consumed")]),
            {},
        )
        validate_board(
            _board_with([record], [_trigger(state="consumed")]), self.workstream
        )

    def test_finding_without_downstream_never_blocks_consumed_trigger(self) -> None:
        findings = validate_live_findings([_finding()], WORKSTREAM_ID)
        self.assertEqual(
            validate_finding_trigger_gates(findings, [_trigger(state="consumed")]),
            {},
        )
        validate_board(
            _board_with([_finding()], [_trigger(state="consumed")]), self.workstream
        )

    def test_unknown_trigger_targeting_fails_closed(self) -> None:
        record = _material_finding(downstream=_downstream(trigger="after-unknown"))
        findings = validate_live_findings([record], WORKSTREAM_ID)
        with self.assertRaisesRegex(LiveFindingError, "unknown JIT trigger"):
            validate_finding_trigger_gates(findings, [_trigger()])
        board = _board_with([record], [_trigger()])
        with self.assertRaisesRegex(ValidationError, "unknown JIT trigger"):
            validate_board(board, self.workstream)

    def test_removed_trigger_stales_targeting(self) -> None:
        record = _material_finding()
        findings = validate_live_findings([record], WORKSTREAM_ID)
        with self.assertRaisesRegex(LiveFindingError, "unknown JIT trigger"):
            validate_finding_trigger_gates(findings, [])
        board = _board_with([record], [])
        with self.assertRaisesRegex(ValidationError, "unknown JIT trigger"):
            validate_board(board, self.workstream)

    def test_one_pending_finding_blocks_despite_sibling_reconciliation(self) -> None:
        first = _reconciled_finding("LF-001")
        second = _material_finding("LF-002")
        findings = validate_live_findings([first, second], WORKSTREAM_ID)
        self.assertEqual(
            validate_finding_trigger_gates(findings, [_trigger(state="satisfied")]),
            {TRIGGER_ID: ["LF-002"]},
        )
        board = _board_with([first, second], [_trigger(state="consumed")])
        with self.assertRaisesRegex(ValidationError, "LF-002"):
            validate_board(board, self.workstream)

    def test_targeting_another_trigger_leaves_this_trigger_unheld(self) -> None:
        record = _material_finding(downstream=_downstream(trigger="after-M01-T02"))
        triggers = [_trigger(), _trigger("after-M01-T02", "M01-T02", "waiting")]
        findings = validate_live_findings([record], WORKSTREAM_ID)
        self.assertEqual(
            validate_finding_trigger_gates(findings, triggers),
            {"after-M01-T02": ["LF-001"]},
        )

    def test_malformed_trigger_sets_fail_closed(self) -> None:
        findings = validate_live_findings([_material_finding()], WORKSTREAM_ID)
        with self.assertRaisesRegex(LiveFindingError, "jit_triggers"):
            validate_finding_trigger_gates(findings, "after-M01-T01")
        with self.assertRaisesRegex(LiveFindingError, "must be a table"):
            validate_finding_trigger_gates(findings, ["after-M01-T01"])
        with self.assertRaisesRegex(LiveFindingError, "non-empty string"):
            validate_finding_trigger_gates(findings, [_trigger(trigger_id="  ")])

    def test_board_without_triggers_or_findings_remains_valid(self) -> None:
        board = _board_with(None, [])
        board.pop("jit_triggers", None)
        validate_board(board, self.workstream)
        self.assertEqual(validate_finding_trigger_gates({}, []), {})


class ConsumptionGuardTests(unittest.TestCase):
    def _board(self, findings: list[dict], trigger_state: str = "satisfied") -> dict:
        return {
            "workstream_id": WORKSTREAM_ID,
            "jit_triggers": [_trigger(state=trigger_state)],
            "live_findings": findings,
        }

    def test_unknown_trigger_consumption_fails_closed(self) -> None:
        board = self._board([_material_finding()])
        with self.assertRaisesRegex(LiveFindingError, "does not exist"):
            require_reconciled_trigger_consumption(board, "after-unknown")

    def test_consumption_requires_workstream_board(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "Task Board table"):
            require_reconciled_trigger_consumption([], TRIGGER_ID)
        with self.assertRaisesRegex(LiveFindingError, "workstream-bound"):
            require_reconciled_trigger_consumption({"jit_triggers": []}, TRIGGER_ID)

    def test_pending_material_blocks_consumption_by_name_and_owner(self) -> None:
        board = self._board([_material_finding()])
        with self.assertRaisesRegex(LiveFindingError, "LF-001.*execution"):
            require_reconciled_trigger_consumption(board, TRIGGER_ID)

    def test_unrelated_and_absent_findings_do_not_block_consumption(self) -> None:
        board = self._board([
            _finding("LF-001", downstream={"disposition": "unrelated"}),
            _finding("LF-002"),
        ])
        self.assertEqual(
            require_reconciled_trigger_consumption(board, TRIGGER_ID), TRIGGER_ID
        )

    def test_targeting_another_trigger_does_not_block_consumption(self) -> None:
        board = self._board([_material_finding(
            downstream=_downstream(trigger="after-other")
        )])
        board["jit_triggers"].append(_trigger("after-other", "M01-T01", "waiting"))
        self.assertEqual(
            require_reconciled_trigger_consumption(board, TRIGGER_ID), TRIGGER_ID
        )
        with self.assertRaisesRegex(LiveFindingError, "after-other"):
            require_reconciled_trigger_consumption(board, "after-other")

    def test_reconciled_citation_permits_consumption_without_reader(self) -> None:
        board = self._board([_reconciled_finding()])
        self.assertEqual(
            require_reconciled_trigger_consumption(board, TRIGGER_ID), TRIGGER_ID
        )

    def test_consumption_reader_rejects_unreadable_materiality_evidence(self) -> None:
        board = self._board([_reconciled_finding()])
        with self.assertRaisesRegex(LiveFindingError, "cannot be read back"):
            require_reconciled_trigger_consumption(
                board, TRIGGER_ID, record_reader=lambda path: None
            )

    def test_consumption_reader_rejects_unreadable_decision(self) -> None:
        board = self._board([_reconciled_finding()])
        evidence = (
            f"implementation/workstreams/{WORKSTREAM_ID}/evidence/LF-001-material.md"
        )
        with self.assertRaisesRegex(LiveFindingError, "reconciliation record"):
            require_reconciled_trigger_consumption(
                board,
                TRIGGER_ID,
                record_reader=lambda path: "# evidence\n" if path == evidence else None,
            )

    def test_consumption_reader_rejects_forged_decision(self) -> None:
        board = self._board([_reconciled_finding()])
        findings_prefix = f"implementation/workstreams/{WORKSTREAM_ID}/findings/"
        with self.assertRaisesRegex(LiveFindingError, "another trigger"):
            require_reconciled_trigger_consumption(
                board,
                TRIGGER_ID,
                record_reader=(
                    lambda path: _reconciliation_decision(trigger_id="after-other")
                    if path.startswith(findings_prefix)
                    else "# evidence\n"
                ),
            )

    def test_consumption_reader_accepts_verified_reconciliation(self) -> None:
        board = self._board([_reconciled_finding()])
        findings_prefix = f"implementation/workstreams/{WORKSTREAM_ID}/findings/"
        self.assertEqual(
            require_reconciled_trigger_consumption(
                board,
                TRIGGER_ID,
                record_reader=(
                    lambda path: _reconciliation_decision()
                    if path.startswith(findings_prefix)
                    else "# evidence\n"
                ),
            ),
            TRIGGER_ID,
        )

    def test_classification_authorization_does_not_release_trigger_hold(self) -> None:
        record = _material_finding()
        record["authorization"] = "owning_stage_accepted"
        record["acceptance"] = {
            "stage": "execution",
            "record": {
                "class": "finding_acceptance",
                "path": (
                    f"implementation/workstreams/{WORKSTREAM_ID}/findings/LF-001.toml"
                ),
            },
        }
        board = self._board([record])
        with self.assertRaisesRegex(LiveFindingError, "held by pending"):
            require_reconciled_trigger_consumption(board, TRIGGER_ID)

    def test_reconciliation_without_classification_authorization_releases_hold(self) -> None:
        board = self._board([_reconciled_finding()])
        findings_prefix = f"implementation/workstreams/{WORKSTREAM_ID}/findings/"
        self.assertEqual(
            require_reconciled_trigger_consumption(
                board,
                TRIGGER_ID,
                record_reader=(
                    lambda path: _reconciliation_decision()
                    if path.startswith(findings_prefix)
                    else "# evidence\n"
                ),
            ),
            TRIGGER_ID,
        )


class ReconciliationDecisionTests(unittest.TestCase):
    def test_valid_decision_document_parses(self) -> None:
        decision = parse_reconciliation_decision(
            _reconciliation_decision(), "findings/LF-001.reconciliation.toml"
        )
        self.assertEqual(decision, {
            "finding_id": "LF-001",
            "finding_class": "implementation_defect",
            "trigger_id": TRIGGER_ID,
            "accepting_stage": "execution",
            "decision": "reconciled",
        })

    def test_acceptance_shaped_document_cannot_prove_reconciliation(self) -> None:
        text = (
            "finding_id = \"LF-001\"\n"
            "finding_class = \"implementation_defect\"\n"
            "accepting_stage = \"execution\"\n"
            "decision = \"accepted\"\n"
        )
        with self.assertRaisesRegex(LiveFindingError, "decision fields"):
            parse_reconciliation_decision(text, "findings/LF-001.toml")

    def test_reconciliation_shaped_document_cannot_prove_acceptance(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "decision fields"):
            parse_acceptance_decision(
                _reconciliation_decision(), "findings/LF-001.reconciliation.toml"
            )

    def test_accepted_verdict_cannot_prove_reconciliation(self) -> None:
        finding = _validate(_reconciled_finding())
        assert finding["downstream"] is not None
        with self.assertRaisesRegex(LiveFindingError, "explicit reconciled"):
            verify_reconciliation_decision(
                finding,
                finding["downstream"],
                "findings/LF-001.reconciliation.toml",
                _reconciliation_decision(decision="accepted"),
            )

    def test_non_toml_and_wrong_shaped_documents_fail(self) -> None:
        finding = _validate(_reconciled_finding())
        assert finding["downstream"] is not None
        with self.assertRaisesRegex(LiveFindingError, "decision fields"):
            verify_reconciliation_decision(
                finding, finding["downstream"], "findings/note.md",
                "# unrelated meeting notes\n",
            )
        with self.assertRaisesRegex(LiveFindingError, "decision fields"):
            verify_reconciliation_decision(
                finding, finding["downstream"], "findings/red.toml",
                "verdict = \"red\"\n",
            )
        with self.assertRaisesRegex(LiveFindingError, "decision fields"):
            verify_reconciliation_decision(
                finding, finding["downstream"], "findings/extra.toml",
                _reconciliation_decision() + "tracker = \"owner/repo#12\"\n",
            )

    def test_empty_decision_field_fails(self) -> None:
        text = _reconciliation_decision().replace(
            'trigger_id = "after-M01-T01"', 'trigger_id = "  "'
        )
        with self.assertRaisesRegex(LiveFindingError, "non-empty string"):
            parse_reconciliation_decision(text, "findings/empty.toml")

    def test_decision_for_another_finding_class_trigger_or_stage_fails(self) -> None:
        finding = _validate(_reconciled_finding())
        assert finding["downstream"] is not None
        cases = [
            ({"finding_id": "LF-999"}, "unrelated decisions"),
            ({"finding_class": "accepted_authority_defect"}, "mismatched classes"),
            ({"trigger_id": "after-other"}, "another trigger"),
            ({"accepting_stage": "planning"}, "owning stage"),
            ({"decision": "rejected"}, "explicit reconciled"),
        ]
        for kwargs, message in cases:
            with self.subTest(kwargs=kwargs):
                with self.assertRaisesRegex(LiveFindingError, message):
                    verify_reconciliation_decision(
                        finding,
                        finding["downstream"],
                        "findings/LF-001.reconciliation.toml",
                        _reconciliation_decision(
                            finding_id=kwargs.get("finding_id", "LF-001"),
                            finding_class=kwargs.get(
                                "finding_class", "implementation_defect"),
                            trigger_id=kwargs.get("trigger_id", TRIGGER_ID),
                            accepting_stage=kwargs.get("accepting_stage", "execution"),
                            decision=kwargs.get("decision", "reconciled"),
                        ),
                    )

    def test_unreadable_decision_fails_verification(self) -> None:
        finding = _validate(_reconciled_finding())
        assert finding["downstream"] is not None
        with self.assertRaisesRegex(LiveFindingError, "cannot be read back"):
            verify_reconciliation_decision(
                finding, finding["downstream"],
                "findings/LF-001.reconciliation.toml", None,
            )


class TriggerRecordVerificationTests(unittest.TestCase):
    def _board(self, findings: list[dict], trigger_state: str = "satisfied") -> dict:
        return {
            "workstream_id": WORKSTREAM_ID,
            "jit_triggers": [_trigger(state=trigger_state)],
            "live_findings": findings,
        }

    def test_board_without_material_findings_verifies_trivially(self) -> None:
        for findings in (
            None,
            [],
            [_finding()],
            [_finding(downstream={"disposition": "unrelated"})],
        ):
            with self.subTest(findings=findings):
                board = {
                    "workstream_id": WORKSTREAM_ID,
                    "jit_triggers": [_trigger(state="consumed")],
                    "live_findings": findings,
                }

                def _reader(path: str) -> str | None:
                    raise AssertionError("reader must not be called")

                verify_finding_trigger_records(board, record_reader=_reader)

    def test_unreadable_materiality_evidence_fails_verification(self) -> None:
        board = self._board([_material_finding()])
        with self.assertRaisesRegex(LiveFindingError, "cannot be read back"):
            verify_finding_trigger_records(board, record_reader=lambda path: None)

    def test_readable_materiality_evidence_verifies_pending(self) -> None:
        board = self._board([_material_finding()])
        verify_finding_trigger_records(
            board, record_reader=lambda path: "# evidence\n"
        )

    def test_matching_reconciliation_document_verifies(self) -> None:
        board = self._board([_reconciled_finding()], "consumed")
        findings_prefix = f"implementation/workstreams/{WORKSTREAM_ID}/findings/"
        verify_finding_trigger_records(
            board,
            record_reader=(
                lambda path: _reconciliation_decision()
                if path.startswith(findings_prefix)
                else "# evidence\n"
            ),
        )

    def test_unreadable_reconciliation_record_fails_verification(self) -> None:
        board = self._board([_reconciled_finding()])
        evidence = (
            f"implementation/workstreams/{WORKSTREAM_ID}/evidence/LF-001-material.md"
        )
        with self.assertRaisesRegex(LiveFindingError, "reconciliation record"):
            verify_finding_trigger_records(
                board,
                record_reader=lambda path: "# evidence\n" if path == evidence else None,
            )

    def test_unrelated_readable_file_cannot_prove_reconciliation(self) -> None:
        board = self._board([_reconciled_finding()])
        with self.assertRaisesRegex(LiveFindingError, "decision fields"):
            verify_finding_trigger_records(
                board, record_reader=lambda path: "# unrelated meeting notes\n"
            )

    def test_acceptance_shaped_content_cannot_prove_reconciliation(self) -> None:
        board = self._board([_reconciled_finding()])
        acceptance_text = (
            "finding_id = \"LF-001\"\n"
            "finding_class = \"implementation_defect\"\n"
            "accepting_stage = \"execution\"\n"
            "decision = \"accepted\"\n"
        )
        findings_prefix = f"implementation/workstreams/{WORKSTREAM_ID}/findings/"
        with self.assertRaisesRegex(LiveFindingError, "decision fields"):
            verify_finding_trigger_records(
                board,
                record_reader=(
                    lambda path: acceptance_text
                    if path.startswith(findings_prefix)
                    else "# evidence\n"
                ),
            )

    def test_decision_for_another_trigger_fails_verification(self) -> None:
        board = self._board([_reconciled_finding()])
        findings_prefix = f"implementation/workstreams/{WORKSTREAM_ID}/findings/"
        with self.assertRaisesRegex(LiveFindingError, "another trigger"):
            verify_finding_trigger_records(
                board,
                record_reader=(
                    lambda path: _reconciliation_decision(trigger_id="after-other")
                    if path.startswith(findings_prefix)
                    else "# evidence\n"
                ),
            )

    def test_dangling_targeting_fails_verification(self) -> None:
        board = self._board(
            [_material_finding(downstream=_downstream(trigger="after-gone"))]
        )
        with self.assertRaisesRegex(LiveFindingError, "unknown JIT trigger"):
            verify_finding_trigger_records(
                board, record_reader=lambda path: "# evidence\n"
            )

    def test_consumed_pending_contradiction_fails_verification(self) -> None:
        board = self._board([_material_finding()], "consumed")
        with self.assertRaisesRegex(LiveFindingError, "cannot be consumed"):
            verify_finding_trigger_records(
                board, record_reader=lambda path: "# evidence\n"
            )

    def test_verification_requires_workstream_board(self) -> None:
        with self.assertRaisesRegex(LiveFindingError, "Task Board table"):
            verify_finding_trigger_records([], record_reader=lambda path: None)
        with self.assertRaisesRegex(LiveFindingError, "workstream-bound"):
            verify_finding_trigger_records(
                {"live_findings": []}, record_reader=lambda path: None
            )


class RouterHoldTests(unittest.TestCase):
    """Satisfied-but-blocked triggers hold JIT materialization at the router."""

    def copy_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(ROUTER_FIXTURE, project)
        return temp, project

    def _board_text(
        self,
        cards_toml: str,
        audits_toml: str,
        triggers_toml: str,
        findings_toml: str,
    ) -> str:
        return (
            "workstream_id = \"sample-workstream\"\n"
            "revision = 3\n"
            "\n"
            "[execution_ref]\n"
            "branch = \"feat/sample-workstream\"\n"
            "\n"
            f"{cards_toml}\n"
            f"{audits_toml}\n"
            f"{triggers_toml}\n"
            f"{findings_toml}\n"
        )

    def _done_card_toml(self, card_id: str = "M01-T03") -> str:
        return (
            "[[cards]]\n"
            f"id = \"{card_id}\"\n"
            "status = \"done\"\n"
            "[cards.contract]\n"
            "class = \"task_card\"\n"
            f"path = \"implementation/workstreams/sample-workstream/cards/{card_id}.md\"\n"
            "[cards.result]\n"
            "class = \"result\"\n"
            f"path = \"implementation/workstreams/sample-workstream/results/{card_id}.md\"\n"
        )

    def _planned_card_toml(self, card_id: str = "M01-T05") -> str:
        audits = (
            "[[sizing_audits]]\n"
            f"card_id = \"{card_id}\"\n"
            "decision = \"single\"\n"
            "rebuttal_class = \"\"\n"
            "rebuttal = \"\"\n"
            "[[sizing_audits.outcomes]]\n"
            "id = \"router-hold\"\n"
            "kind = \"invariant\"\n"
            "statement = \"Affected-JIT hold keeps the satisfied trigger until reconciliation.\"\n"
            "family = \"routing\"\n"
            "independently_verifiable = true\n"
            "independently_useful = true\n"
            "falsifiable = true\n"
            "substantial = true\n"
            "scaffolding_only = false\n"
            "independently_consumed = false\n"
            "[sizing_audits.dimensions]\n"
            "independent_implementability = \"Durable independent implementability statement.\"\n"
            "falsifiability_testability = \"Durable falsifiability testability statement.\"\n"
            "reviewability = \"Durable reviewability statement.\"\n"
            "invariant_contract_family = \"Durable invariant contract family statement.\"\n"
            "dependency_ordering = \"Durable dependency ordering statement.\"\n"
            "atomic_mutation_migration = \"Durable atomic mutation migration statement.\"\n"
            "cross_surface_coupling = \"Durable cross surface coupling statement.\"\n"
            "\n"
            "[[topology_audits]]\n"
            f"card_id = \"{card_id}\"\n"
            "risk = \"simple\"\n"
            "triggers = []\n"
            "risk_basis = \"Single coherent outcome in one invariant family with no seam merge, milestone absorption or material deviation.\"\n"
            "review_scope = \"card_local\"\n"
            "atomicity_rationale_class = \"\"\n"
            "atomicity_rationale = \"\"\n"
        )
        card = (
            "[[cards]]\n"
            f"id = \"{card_id}\"\n"
            "status = \"planned\"\n"
            "[cards.contract]\n"
            "class = \"task_card\"\n"
            f"path = \"implementation/workstreams/sample-workstream/cards/{card_id}.md\"\n"
        )
        return card, audits

    def _trigger_toml(
        self,
        trigger_id: str = "after-M01-T03",
        after_card: str = "M01-T03",
        state: str = "satisfied",
    ) -> str:
        return (
            "[[jit_triggers]]\n"
            f"id = \"{trigger_id}\"\n"
            f"after_card = \"{after_card}\"\n"
            f"state = \"{state}\"\n"
            "condition = \"Downstream boundary depends on the predecessor result.\"\n"
        )

    def _finding_toml(
        self,
        finding_class: str = "planning_execution_prep_fidelity_defect",
        owner: str = "execution_prep",
        disposition: str = "material",
        reconciliation: str = "pending",
        trigger_id: str = "after-M01-T03",
    ) -> str:
        toml = (
            "[[live_findings]]\n"
            "id = \"LF-001\"\n"
            f"finding_class = \"{finding_class}\"\n"
            "observed = \"Live execution exposed a material downstream observation.\"\n"
            "evidence_refs = ["
            "\"implementation/workstreams/sample-workstream/evidence/LF-001.md\""
            "]\n"
            f"owner_stage = \"{owner}\"\n"
            "authorization = \"none\"\n"
            "tracker_locators = []\n"
            "[live_findings.downstream]\n"
            f"disposition = \"{disposition}\"\n"
        )
        if disposition == "material":
            toml += (
                f"trigger = \"{trigger_id}\"\n"
                "aspect = \"topology\"\n"
                "material_evidence_refs = ["
                "\"implementation/workstreams/sample-workstream/evidence/LF-001-material.md\""
                "]\n"
                f"reconciliation = \"{reconciliation}\"\n"
            )
        if disposition == "material" and reconciliation == "reconciled":
            toml += (
                "[live_findings.downstream.acceptance]\n"
                f"stage = \"{owner}\"\n"
                "[live_findings.downstream.acceptance.record]\n"
                "class = \"finding_reconciliation\"\n"
                "path = \"implementation/workstreams/sample-workstream/findings/LF-001.reconciliation.toml\"\n"
            )
        return toml

    def _write_records(
        self,
        project: Path,
        *,
        evidence: bool = True,
        material: bool = True,
        decision: str | None = None,
    ) -> None:
        base = project / "implementation" / "workstreams" / "sample-workstream"
        if evidence:
            target = base / "evidence" / "LF-001.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# Live-finding durable evidence\n")
        if material:
            target = base / "evidence" / "LF-001-material.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# Materiality decision evidence\n")
        if decision is not None:
            target = base / "findings" / "LF-001.reconciliation.toml"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(decision)

    def _hold_board(self, findings_toml: str) -> str:
        card, audits = self._planned_card_toml()
        return self._board_text(
            self._done_card_toml() + "\n" + card,
            audits,
            self._trigger_toml(),
            findings_toml,
        )

    def test_satisfied_blocked_trigger_holds_jit_materialization(self) -> None:
        temp, project = self.copy_fixture()
        try:
            (project / ROUTER_BOARD).write_text(
                self._hold_board(self._finding_toml())
            )
            self._write_records(project)
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "finding_reconciliation", "after-M01-T03"),
            )
            self.assertEqual(routed.owner_module, "workflow/EXECUTION_PREP.md")
            self.assertIn("LF-001", routed.reason)
            self.assertIn("after-M01-T03", routed.reason)
        finally:
            temp.cleanup()

    def test_unrelated_finding_does_not_hold_materialization(self) -> None:
        temp, project = self.copy_fixture()
        try:
            (project / ROUTER_BOARD).write_text(
                self._hold_board(self._finding_toml(disposition="unrelated"))
            )
            self._write_records(project, material=False)
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "execution_prep"),
            )
        finally:
            temp.cleanup()

    def test_reconciled_verified_finding_releases_materialization(self) -> None:
        temp, project = self.copy_fixture()
        try:
            (project / ROUTER_BOARD).write_text(
                self._hold_board(self._finding_toml(reconciliation="reconciled"))
            )
            self._write_records(
                project,
                decision=_reconciliation_decision(
                    finding_class="planning_execution_prep_fidelity_defect",
                    trigger_id="after-M01-T03",
                    accepting_stage="execution_prep",
                ),
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "execution_prep"),
            )
        finally:
            temp.cleanup()

    def test_missing_materiality_evidence_recovers_at_router(self) -> None:
        temp, project = self.copy_fixture()
        try:
            (project / ROUTER_BOARD).write_text(
                self._hold_board(self._finding_toml())
            )
            self._write_records(project, material=False)
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("materiality", routed.reason)
        finally:
            temp.cleanup()

    def test_missing_reconciliation_record_recovers_at_router(self) -> None:
        temp, project = self.copy_fixture()
        try:
            (project / ROUTER_BOARD).write_text(
                self._hold_board(self._finding_toml(reconciliation="reconciled"))
            )
            self._write_records(project)
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("reconciliation", routed.reason)
        finally:
            temp.cleanup()

    def test_forged_reconciliation_decision_recovers_at_router(self) -> None:
        temp, project = self.copy_fixture()
        try:
            (project / ROUTER_BOARD).write_text(
                self._hold_board(self._finding_toml(reconciliation="reconciled"))
            )
            self._write_records(
                project,
                decision=_reconciliation_decision(
                    finding_class="planning_execution_prep_fidelity_defect",
                    trigger_id="after-other",
                    accepting_stage="execution_prep",
                ),
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("reconciliation", routed.reason)
        finally:
            temp.cleanup()

    def test_hold_does_not_preempt_unrelated_active_work(self) -> None:
        temp, project = self.copy_fixture()
        try:
            board = project / ROUTER_BOARD
            board.write_text(
                board.read_text()
                + "\n"
                + self._done_card_toml()
                + "\n"
                + self._trigger_toml()
                + "\n"
                + self._finding_toml(
                    finding_class="implementation_defect", owner="execution"
                )
            )
            self._write_records(project)
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution", "M01-T04"),
            )
        finally:
            temp.cleanup()

    def test_consumed_pending_contradiction_recovers_at_router(self) -> None:
        temp, project = self.copy_fixture()
        try:
            card, audits = self._planned_card_toml()
            (project / ROUTER_BOARD).write_text(
                self._board_text(
                    self._done_card_toml() + "\n" + card,
                    audits,
                    self._trigger_toml(state="consumed"),
                    self._finding_toml(),
                )
            )
            self._write_records(project)
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("cannot be consumed", routed.reason)
        finally:
            temp.cleanup()


class HistoryPreservationTests(unittest.TestCase):
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
                verify_finding_trigger_records(
                    board,
                    record_reader=lambda path: (_ for _ in ()).throw(
                        AssertionError("reader must not be called")
                    ),
                )

    def test_consumed_trigger_without_findings_remains_valid(self) -> None:
        workstream = read_toml(VALID / "WORKSTREAM.toml")
        board = _board_with(None, [_trigger(state="consumed")])
        validate_board(board, workstream)

    def test_pre_gate_finding_without_downstream_stays_non_blocking(self) -> None:
        workstream = read_toml(VALID / "WORKSTREAM.toml")
        board = _board_with([_finding()], [_trigger(state="consumed")])
        validate_board(board, workstream)

    def test_runtime_identity_in_downstream_is_rejected(self) -> None:
        workstream = read_toml(VALID / "WORKSTREAM.toml")
        downstream = _downstream()
        downstream["worker_id"] = "worker-1"
        board = _board_with(
            [_finding(downstream=downstream)], [_trigger(state="satisfied")]
        )
        with self.assertRaisesRegex(ValidationError, "prohibited canonical key"):
            validate_board(board, workstream)


if __name__ == "__main__":
    unittest.main()
