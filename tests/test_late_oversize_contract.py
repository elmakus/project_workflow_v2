from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from tools.late_oversize_contract import (
    LateOversizeError,
    bound_handoff_hold,
    classify_execution_return,
    classify_worker_topology_action,
    pending_late_return,
    unfinished_residual_scope,
    validate_late_return,
    validate_late_returns,
)
from tools.router import classify_jit_refinement, select_route
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


def _outcome(outcome_id: str = "residual-retry", **overrides) -> dict:
    record = {
        "id": outcome_id,
        "kind": "invariant",
        "statement": "Bounded retry policy with its own contract and fixtures.",
        "family": "retry-policy",
        "independently_verifiable": True,
        "independently_useful": True,
        "falsifiable": True,
        "substantial": True,
        "scaffolding_only": False,
        "independently_consumed": False,
    }
    record.update(overrides)
    return record


def _late_return(card_id: str = "M01-T02", **overrides) -> dict:
    record = {
        "card_id": card_id,
        "origin": "execution",
        "origin_attempt": "",
        "origin_attempt_path": "",
        "state": "pending",
        "residual_card": "",
        "jit_resolutions": [],
        "material_evidence": (
            "Load testing during execution exposed a second separable "
            "review-worthy outcome: bounded retry policy, independently "
            "falsifiable from the preserved core envelope."
        ),
        "preserved_refs": [
            "implementation/workstreams/sample-workstream/evidence/M01-T02-core.md",
        ],
        "preserved_basis": (
            "Core envelope validation passes alone and stays valid/useful "
            "while the residual retry scope is RED."
        ),
        "residual_scope": (
            "Remaining unaccepted retry-policy scope returns to Execution Prep "
            "for bounded re-decomposition."
        ),
        "residual_outcomes": [_outcome()],
        "residual_trigger": "after-M01-T02",
        "bounded_correction_applies": False,
        "not_bug_basis": (
            "Retry policy is a separable review-worthy outcome needing its own "
            "execution/result/review lifecycle, not a defect in the preserved core."
        ),
        "merges_required_seam": False,
        "seam_basis": (
            "Residual scope stays inside accepted Planning seams; no required "
            "seam is merged by this return."
        ),
        "preserves_history": True,
        "claims_green": False,
    }
    record.update(overrides)
    return record


def _cards(card_id: str = "M01-T02", status: str = "in_progress",
           attempts: list | None = None) -> list[dict]:
    return [{"id": card_id, "status": status,
             "review_attempts": attempts or []}]


def _triggers(trigger_id: str = "after-M01-T02",
              after_card: str = "M01-T02",
              state: str = "waiting") -> list[dict]:
    return [{"id": trigger_id, "after_card": after_card, "state": state,
             "condition": "Residual late-oversize scope awaits re-decomposition."}]


def _board_with_return(workstream_id: str = "sample-workstream",
                       card_id: str = "M01-T02",
                       status: str = "in_progress",
                       attempts: list | None = None,
                       trigger_state: str = "waiting",
                       **return_overrides) -> dict:
    board = read_toml(VALID / "TASK_BOARD.toml")
    for card in board["cards"]:
        if card["id"] == card_id:
            card["status"] = status
            if attempts is not None:
                card["review_attempts"] = attempts
    board["jit_triggers"] = _triggers(
        trigger_id="after-M01-T02", after_card="M01-T02",
        state=trigger_state,
    )
    record = _late_return(card_id=card_id, **return_overrides)
    if workstream_id != "sample-workstream":
        record["preserved_refs"] = [
            ref.replace("sample-workstream", workstream_id)
            for ref in record.get("preserved_refs", [])
        ]
    board["late_oversize_returns"] = [record]
    return board


class ReturnRecordTests(unittest.TestCase):
    def test_valid_execution_origin_return(self) -> None:
        record = validate_late_return(
            _late_return(), "task_board.late_oversize_returns[0]",
            cards_by_id={c["id"]: c for c in _cards()},
            triggers_by_id={t["id"]: t for t in _triggers()},
            workstream_id="sample-workstream",
        )
        self.assertEqual(record["card_id"], "M01-T02")
        self.assertEqual(record["origin"], "execution")

    def test_valid_review_origin_requires_prior_attempt_history(self) -> None:
        attempts = [{
            "class": "review_attempt",
            "path": "implementation/workstreams/sample-workstream/reviews/M01-T02-R01.toml",
        }]
        record = validate_late_return(
            _late_return(
                origin="review", origin_attempt="M01-T02-R01",
                origin_attempt_path="implementation/workstreams/sample-workstream/reviews/M01-T02-R01.toml",
            ),
            "task_board.late_oversize_returns[0]",
            cards_by_id={c["id"]: c for c in _cards(attempts=attempts)},
            triggers_by_id={t["id"]: t for t in _triggers()},
            workstream_id="sample-workstream",
        )
        self.assertEqual(record["origin_attempt"], "M01-T02-R01")

    def test_review_origin_without_history_is_rejected(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "review_attempt"):
            validate_late_return(
                _late_return(
                    origin="review", origin_attempt="M01-T02-R01",
                    origin_attempt_path="implementation/workstreams/sample-workstream/reviews/M01-T02-R01.toml",
                ),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards()},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_review_origin_requires_attempt_binding(self) -> None:
        attempts = [{
            "class": "review_attempt",
            "path": "implementation/workstreams/sample-workstream/reviews/M01-T02-R01.toml",
        }]
        with self.assertRaisesRegex(LateOversizeError, "origin_attempt"):
            validate_late_return(
                _late_return(origin="review", origin_attempt=""),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards(attempts=attempts)},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_execution_origin_must_not_claim_review_attempt(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "origin_attempt"):
            validate_late_return(
                _late_return(origin="execution", origin_attempt="M01-T02-R01"),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards()},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_unknown_origin_is_rejected(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "unknown origin"):
            validate_late_return(
                _late_return(origin="planning"),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards()},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_return_claiming_green_is_rejected(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "must not claim GREEN"):
            validate_late_return(
                _late_return(claims_green=True),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards()},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_return_must_preserve_history(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "preserves_history"):
            validate_late_return(
                _late_return(preserves_history=False),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards()},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_return_must_not_merge_required_seam(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "required_seam"):
            validate_late_return(
                _late_return(merges_required_seam=True),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards()},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_bounded_correction_must_stay_in_card(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "bounded correction"):
            validate_late_return(
                _late_return(bounded_correction_applies=True),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards()},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_empty_material_evidence_fails_closed(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "material_evidence"):
            validate_late_return(
                _late_return(material_evidence="  "),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards()},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_empty_residual_scope_fails_closed(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "residual_scope"):
            validate_late_return(
                _late_return(residual_scope=""),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards()},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_empty_preserved_basis_fails_closed(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "preserved_basis"):
            validate_late_return(
                _late_return(preserved_basis=""),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards()},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_empty_preserved_refs_allowed_with_explicit_basis(self) -> None:
        record = validate_late_return(
            _late_return(
                preserved_refs=[],
                preserved_basis="No independently valid evidence exists yet; "
                                "all durable work belongs to the residual scope.",
            ),
            "task_board.late_oversize_returns[0]",
            cards_by_id={c["id"]: c for c in _cards()},
            triggers_by_id={t["id"]: t for t in _triggers()},
            workstream_id="sample-workstream",
        )
        self.assertEqual(record["preserved_refs"], [])

    def test_foreign_preserved_ref_is_rejected(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "preserved_refs"):
            validate_late_return(
                _late_return(preserved_refs=["evidence/stray.md"]),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards()},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_trivial_structural_residual_is_rejected(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "structural"):
            validate_late_return(
                _late_return(residual_outcomes=[_outcome(kind="file")]),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards()},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_insubstantial_residual_is_rejected_as_fragment(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "not substantial enough"):
            validate_late_return(
                _late_return(residual_outcomes=[_outcome(substantial=False)]),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards()},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_non_separable_residual_is_rejected(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "separable"):
            validate_late_return(
                _late_return(
                    residual_outcomes=[_outcome(independently_useful=False)]
                ),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards()},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_empty_residual_outcomes_rejected(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "residual_outcomes"):
            validate_late_return(
                _late_return(residual_outcomes=[]),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards()},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_dangling_residual_trigger_is_rejected(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "residual_trigger"):
            validate_late_return(
                _late_return(residual_trigger="after-unknown"),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards()},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_consumed_trigger_cannot_hold_residual(self) -> None:
        triggers = _triggers(state="consumed")
        with self.assertRaisesRegex(LateOversizeError, "waiting"):
            validate_late_return(
                _late_return(),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards()},
                triggers_by_id={t["id"]: t for t in triggers},
                workstream_id="sample-workstream",
            )

    def test_foreign_predecessor_trigger_is_rejected(self) -> None:
        triggers = _triggers(after_card="M01-T01")
        with self.assertRaisesRegex(LateOversizeError, "after the returning Card"):
            validate_late_return(
                _late_return(),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards()},
                triggers_by_id={t["id"]: t for t in triggers},
                workstream_id="sample-workstream",
            )

    def test_return_on_non_active_card_is_rejected(self) -> None:
        for status in ("planned", "ready", "blocked"):
            with self.subTest(status=status):
                with self.assertRaisesRegex(LateOversizeError, "in_progress"):
                    validate_late_return(
                        _late_return(),
                        "task_board.late_oversize_returns[0]",
                        cards_by_id={c["id"]: c
                                     for c in _cards(status=status)},
                        triggers_by_id={t["id"]: t for t in _triggers()},
                        workstream_id="sample-workstream",
                    )

    def test_done_card_cannot_hold_any_return(self) -> None:
        for state, residual in (("pending", ""), ("residual_bound", "M01-T03")):
            with self.subTest(state=state):
                cards = _cards(status="done") + [
                    {"id": "M01-T03", "status": "planned",
                     "review_attempts": []}
                ]
                with self.assertRaisesRegex(
                    LateOversizeError, "reserved for accepted"
                ):
                    validate_late_return(
                        _late_return(state=state, residual_card=residual),
                        "task_board.late_oversize_returns[0]",
                        cards_by_id={c["id"]: c for c in cards},
                        triggers_by_id={t["id"]: t for t in _triggers()},
                        workstream_id="sample-workstream",
                    )

    def test_duplicate_returns_for_one_card_are_rejected(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "duplicate"):
            validate_late_returns(
                [_late_return(), _late_return()], _cards(), _triggers(),
                "sample-workstream",
            )

    def test_return_for_unknown_card_is_rejected(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "unknown card_id"):
            validate_late_returns(
                [_late_return(card_id="M09-T99")], _cards(), _triggers(),
                "sample-workstream",
            )

    def test_missing_returns_array_is_valid(self) -> None:
        self.assertEqual(
            validate_late_returns(None, _cards(), _triggers(),
                                  "sample-workstream"), {},
        )


class WorkerAuthorityTests(unittest.TestCase):
    def test_worker_self_broaden_is_rejected(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "must not silently broaden"):
            classify_worker_topology_action(
                broadens_scope=True, merges_cards=False, splits_card=False,
                rewrites_card=False, main_authorized_return=False,
            )

    def test_worker_self_merge_is_rejected(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "must not silently"):
            classify_worker_topology_action(
                broadens_scope=False, merges_cards=True, splits_card=False,
                rewrites_card=False, main_authorized_return=False,
            )

    def test_worker_self_split_is_rejected(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "must not silently"):
            classify_worker_topology_action(
                broadens_scope=False, merges_cards=False, splits_card=True,
                rewrites_card=False, main_authorized_return=False,
            )

    def test_worker_card_rewrite_is_rejected(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "must not silently"):
            classify_worker_topology_action(
                broadens_scope=False, merges_cards=False, splits_card=False,
                rewrites_card=True, main_authorized_return=False,
            )

    def test_authorized_topology_evidence_routes_to_execution_prep(self) -> None:
        owner = classify_worker_topology_action(
            broadens_scope=False, merges_cards=False, splits_card=True,
            rewrites_card=False, main_authorized_return=True,
        )
        self.assertEqual(owner, "execution_prep")

    def test_ordinary_worker_return_stays_in_execution(self) -> None:
        owner = classify_worker_topology_action(
            broadens_scope=False, merges_cards=False, splits_card=False,
            rewrites_card=False, main_authorized_return=False,
        )
        self.assertEqual(owner, "execution")


class ExecutionReturnTests(unittest.TestCase):
    def test_late_evidence_returns_to_execution_prep(self) -> None:
        self.assertEqual(
            classify_execution_return(
                acceptance_valid=False, real_blocker=False,
                late_oversize_evidence=True,
            ),
            "return_to_execution_prep",
        )

    def test_late_evidence_never_reconciles_as_green(self) -> None:
        self.assertEqual(
            classify_execution_return(
                acceptance_valid=True, real_blocker=False,
                late_oversize_evidence=True,
            ),
            "return_to_execution_prep",
        )

    def test_real_blocker_keeps_precedence(self) -> None:
        self.assertEqual(
            classify_execution_return(
                acceptance_valid=True, real_blocker=True,
                late_oversize_evidence=True,
            ),
            "block",
        )

    def test_ordinary_classification_is_unchanged(self) -> None:
        self.assertEqual(
            classify_execution_return(
                acceptance_valid=False, real_blocker=False,
                late_oversize_evidence=False,
            ),
            "correct",
        )
        self.assertEqual(
            classify_execution_return(
                acceptance_valid=True, real_blocker=False,
                late_oversize_evidence=False,
            ),
            "reconcile",
        )

    def test_jit_refinement_routes_late_return_to_execution_prep(self) -> None:
        owner, _ = classify_jit_refinement("late_oversize_return")
        self.assertEqual(owner, "execution_prep")


class BoardBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workstream = read_toml(VALID / "WORKSTREAM.toml")

    def test_board_accepts_valid_execution_return(self) -> None:
        board = _board_with_return()
        validate_board(board, self.workstream)
        pending = pending_late_return(board)
        self.assertEqual(pending, "M01-T02")

    def test_board_without_returns_has_no_pending_return(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        validate_board(board, self.workstream)
        self.assertIsNone(pending_late_return(board))

    def test_board_accepts_review_origin_with_history(self) -> None:
        attempts = [{
            "class": "review_attempt",
            "path": "implementation/workstreams/sample-workstream/reviews/M01-T02-R01.toml",
        }]
        board = _board_with_return(
            attempts=attempts, origin="review",
            origin_attempt="M01-T02-R01",
            origin_attempt_path="implementation/workstreams/sample-workstream/reviews/M01-T02-R01.toml",
        )
        validate_board(board, self.workstream)
        self.assertEqual(
            board["cards"][1]["review_attempts"], attempts,
        )

    def test_board_rejects_return_claiming_green(self) -> None:
        board = _board_with_return(claims_green=True)
        with self.assertRaisesRegex(ValidationError, "must not claim GREEN"):
            validate_board(board, self.workstream)

    def test_board_rejects_return_on_done_card(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["jit_triggers"] = [{
            "id": "after-M01-T01", "after_card": "M01-T01",
            "state": "waiting",
            "condition": "Stale trigger retained for the negative fixture.",
        }]
        board["late_oversize_returns"] = [_late_return(card_id="M01-T01")]
        with self.assertRaisesRegex(ValidationError, "reserved for accepted"):
            validate_board(board, self.workstream)

    def test_board_rejects_return_erasing_review_history(self) -> None:
        board = _board_with_return(
            origin="review", origin_attempt="M01-T02-R01",
            origin_attempt_path="implementation/workstreams/sample-workstream/reviews/M01-T02-R01.toml",
        )
        with self.assertRaisesRegex(ValidationError, "review_attempt"):
            validate_board(board, self.workstream)

    def test_board_rejects_residual_bounded_correction(self) -> None:
        board = _board_with_return(bounded_correction_applies=True)
        with self.assertRaisesRegex(ValidationError, "bounded correction"):
            validate_board(board, self.workstream)

    def test_board_rejects_trivial_residual_fragment(self) -> None:
        board = _board_with_return(
            residual_outcomes=[_outcome(kind="step")],
        )
        with self.assertRaisesRegex(ValidationError, "structural"):
            validate_board(board, self.workstream)

    def test_board_rejects_return_merging_required_seam(self) -> None:
        board = _board_with_return(merges_required_seam=True)
        with self.assertRaisesRegex(ValidationError, "required_seam"):
            validate_board(board, self.workstream)

    def test_board_rejects_dangling_residual_trigger(self) -> None:
        board = _board_with_return(residual_trigger="after-unknown")
        with self.assertRaisesRegex(ValidationError, "residual_trigger"):
            validate_board(board, self.workstream)

    def test_board_rejects_consumed_residual_trigger(self) -> None:
        board = _board_with_return(trigger_state="consumed")
        with self.assertRaisesRegex(ValidationError, "DONE predecessor result"):
            validate_board(board, self.workstream)

    def test_return_does_not_excuse_missing_sizing_audit(self) -> None:
        board = _board_with_return()
        board.pop("sizing_audits", None)
        with self.assertRaisesRegex(ValidationError, "missing durable sizing audit"):
            validate_board(board, self.workstream)

    def test_return_does_not_excuse_missing_topology_audit(self) -> None:
        board = _board_with_return()
        board.pop("topology_audits", None)
        with self.assertRaisesRegex(ValidationError, "missing durable topology audit"):
            validate_board(board, self.workstream)

    def test_downstream_residual_card_requires_fresh_audits(self) -> None:
        board = _board_with_return()
        board["cards"].append({
            "id": "M01-T03", "status": "planned",
            "contract": {
                "class": "task_card",
                "path": "implementation/workstreams/sample-workstream/cards/M01-T03.md",
            },
        })
        with self.assertRaisesRegex(ValidationError, "missing durable sizing audit"):
            validate_board(board, self.workstream)

    def test_runtime_identity_in_return_is_rejected(self) -> None:
        board = _board_with_return()
        board["late_oversize_returns"][0]["worker_id"] = "worker-1"
        with self.assertRaisesRegex(ValidationError, "prohibited canonical key"):
            validate_board(board, self.workstream)


class RouterRecoveryTests(unittest.TestCase):
    def copy_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(ROUTER_FIXTURE, project)
        return temp, project

    def late_return_toml(self, card_id: str = "M01-T04",
                         **overrides: str) -> str:
        fields = {
            "origin": "execution",
            "origin_attempt": "",
            "material_evidence": (
                "Load testing during execution exposed a second separable "
                "review-worthy outcome."
            ),
            "preserved_basis": (
                "Core routing validation passes alone and stays useful while "
                "the residual scope is RED."
            ),
            "residual_scope": (
                "Remaining unaccepted scope returns for bounded re-decomposition."
            ),
            "residual_trigger": "after-M01-T04",
            "not_bug_basis": "Separable review-worthy outcome, not a core defect.",
            "seam_basis": "No required seam is merged by this return.",
        }
        fields.update(overrides)
        outcome = (
            "[[late_oversize_returns.residual_outcomes]]\n"
            "id = \"residual-retry\"\n"
            "kind = \"invariant\"\n"
            "statement = \"Bounded retry policy with its own contract.\"\n"
            "family = \"retry-policy\"\n"
            "independently_verifiable = true\n"
            "independently_useful = true\n"
            "falsifiable = true\n"
            "substantial = true\n"
            "scaffolding_only = false\n"
            "independently_consumed = false\n"
        )
        return (
            "[[jit_triggers]]\n"
            "id = \"after-M01-T04\"\n"
            f"after_card = \"{card_id}\"\n"
            "state = \"waiting\"\n"
            "condition = \"Residual late-oversize scope awaits re-decomposition.\"\n"
            "[[late_oversize_returns]]\n"
            f"card_id = \"{card_id}\"\n"
            f"origin = \"{fields['origin']}\"\n"
            f"origin_attempt = \"{fields['origin_attempt']}\"\n"
            "origin_attempt_path = \"\"\n"
            "state = \"pending\"\n"
            "residual_card = \"\"\n"
            f"material_evidence = \"{fields['material_evidence']}\"\n"
            "preserved_refs = ["
            "\"implementation/workstreams/sample-workstream/evidence/M01-T04-core.md\""
            "]\n"
            f"preserved_basis = \"{fields['preserved_basis']}\"\n"
            f"residual_scope = \"{fields['residual_scope']}\"\n"
            f"residual_trigger = \"{fields['residual_trigger']}\"\n"
            "bounded_correction_applies = false\n"
            f"not_bug_basis = \"{fields['not_bug_basis']}\"\n"
            "merges_required_seam = false\n"
            f"seam_basis = \"{fields['seam_basis']}\"\n"
            "preserves_history = true\n"
            "claims_green = false\n"
            f"{outcome}"
        )

    def install_return(self, project: Path, text: str,
                       with_evidence: bool = True) -> None:
        board = project / ROUTER_BOARD
        board.write_text(board.read_text() + text)
        if with_evidence:
            evidence = (project / "implementation" / "workstreams"
                        / "sample-workstream" / "evidence" / "M01-T04-core.md")
            evidence.parent.mkdir(parents=True, exist_ok=True)
            evidence.write_text("# Preserved core evidence\n")

    def test_pending_return_routes_to_execution_prep(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_return(project, self.late_return_toml())
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution_prep", "M01-T04"),
            )
            self.assertEqual(routed.owner_module,
                             "workflow/EXECUTION_PREP.md")
            self.assertIn("late-oversize", routed.reason)
            self.assertIn(
                "project:implementation/workstreams/sample-workstream/evidence/M01-T04-core.md",
                routed.read_set,
            )
        finally:
            temp.cleanup()

    def test_missing_preserved_evidence_recovers(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_return(project, self.late_return_toml(),
                                with_evidence=False)
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("preserved evidence", routed.reason)
        finally:
            temp.cleanup()

    def test_invalid_return_recovers_on_board_validation(self) -> None:
        temp, project = self.copy_fixture()
        try:
            text = self.late_return_toml().replace(
                "bounded_correction_applies = false",
                "bounded_correction_applies = true",
            )
            self.install_return(project, text)
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("bounded correction", routed.reason)
        finally:
            temp.cleanup()

    def test_return_is_runtime_neutral(self) -> None:
        import os
        from unittest.mock import patch

        temp, project = self.copy_fixture()
        try:
            self.install_return(project, self.late_return_toml())
            for noise in ({"RUNTIME": "chatgpt", "MODEL_ID": "one"},
                          {"RUNTIME": "codex", "MODEL_ID": "two"}):
                with patch.dict(os.environ, noise, clear=False):
                    routed = select_route(project, [ROUTER_MANIFEST],
                                          package_root=ROOT)
                self.assertEqual(
                    (routed.disposition, routed.obligation, routed.subject),
                    ("route", "execution_prep", "M01-T04"),
                )
        finally:
            temp.cleanup()


class HistoryRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workstream = read_toml(VALID / "WORKSTREAM.toml")

    def test_done_only_board_without_returns_remains_valid(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["cards"] = [card for card in board["cards"]
                          if card["status"] == "done"]
        board.pop("sizing_audits", None)
        board.pop("topology_audits", None)
        board.pop("late_oversize_returns", None)
        validate_board(board, self.workstream)
        self.assertIsNone(pending_late_return(board))

    def test_m02_mega_scope_replays_as_separable_residual(self) -> None:
        outcomes = [
            _outcome("m02-obligation-result-contracts", kind="contract",
                     statement="Versioned Obligation/Result contracts.",
                     family="execution-contracts"),
            _outcome("m02-authority-resolution", kind="invariant",
                     statement="PW-owned exact authority resolution.",
                     family="authority-resolution"),
            _outcome("m02-identity-freshness", kind="invariant",
                     statement="Deterministic identity and stale reconciliation.",
                     family="result-identity"),
            _outcome("m02-governed-mutation", kind="acceptance",
                     statement="Governed mutation with mandatory readback.",
                     family="governed-mutation"),
        ]
        board = _board_with_return(residual_outcomes=outcomes)
        validate_board(board, self.workstream)
        self.assertEqual(
            len(board["late_oversize_returns"][0]["residual_outcomes"]), 4,
        )


def _sizing_audit(card_id: str, outcomes: list[dict] | None = None) -> dict:
    if outcomes is None:
        outcomes = [_outcome()]
    return {
        "card_id": card_id,
        "decision": "single",
        "rebuttal_class": "",
        "rebuttal": "",
        "outcomes": outcomes,
        "dimensions": {
            "independent_implementability": "Builds and passes alone.",
            "falsifiability_testability": "Own failing check before GREEN.",
            "reviewability": "One bounded Card review covers it.",
            "invariant_contract_family": "Single retry-policy family.",
            "dependency_ordering": "Launches after the handoff trigger.",
            "atomic_mutation_migration": "No joint atomic landing.",
            "cross_surface_coupling": "No shared mutable surface.",
        },
    }


def _topology_audit(card_id: str) -> dict:
    return {
        "card_id": card_id,
        "risk": "simple",
        "triggers": [],
        "risk_basis": "Single coherent outcome in one invariant family.",
        "review_scope": "card_local",
        "atomicity_rationale_class": "",
        "atomicity_rationale": "",
    }


def _bind_residual(board: dict, original_id: str = "M01-T02",
                   residual_id: str = "M01-T03") -> dict:
    board["cards"].append({
        "id": residual_id, "status": "planned",
        "contract": {
            "class": "task_card",
            "path": f"implementation/workstreams/sample-workstream/cards/{residual_id}.md",
        },
    })
    residuals: list[dict] = []
    for record in board["late_oversize_returns"]:
        if record["card_id"] == original_id:
            record["state"] = "residual_bound"
            record["residual_card"] = residual_id
            residuals = record.get("residual_outcomes", [])
    mirrored = []
    for outcome in residuals:
        copy = dict(outcome)
        copy.pop("allocated_to", None)
        mirrored.append(copy)
    board.setdefault("sizing_audits", []).append(
        _sizing_audit(residual_id, mirrored or None)
    )
    board.setdefault("topology_audits", []).append(_topology_audit(residual_id))
    return board


class OriginBindingTests(unittest.TestCase):
    """Review origin_attempt must bind one exact attempt on the returning Card."""

    def _attempts(self) -> list[dict]:
        return [
            {"class": "review_attempt",
             "path": "implementation/workstreams/sample-workstream/reviews/M01-T02-R01.toml"},
            {"class": "review_attempt",
             "path": "implementation/workstreams/sample-workstream/reviews/M01-T02-R02.toml"},
        ]

    def test_exact_locator_binding_selects_one_attempt(self) -> None:
        record = validate_late_return(
            _late_return(
                origin="review", origin_attempt="M01-T02-R02",
                origin_attempt_path="implementation/workstreams/sample-workstream/reviews/M01-T02-R02.toml",
            ),
            "task_board.late_oversize_returns[0]",
            cards_by_id={c["id"]: c for c in _cards(attempts=self._attempts())},
            triggers_by_id={t["id"]: t for t in _triggers()},
            workstream_id="sample-workstream",
        )
        self.assertEqual(
            record["origin_attempt_path"],
            "implementation/workstreams/sample-workstream/reviews/M01-T02-R02.toml",
        )

    def test_fabricated_attempt_path_is_rejected(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "not a durable review attempt"):
            validate_late_return(
                _late_return(
                    origin="review", origin_attempt="M01-T02-R99",
                    origin_attempt_path="implementation/workstreams/sample-workstream/reviews/M01-T02-R99.toml",
                ),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards(attempts=self._attempts())},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_foreign_card_attempt_path_is_rejected(self) -> None:
        cards = _cards(attempts=self._attempts()) + [{
            "id": "M01-T03", "status": "planned", "review_attempts": [{
                "class": "review_attempt",
                "path": "implementation/workstreams/sample-workstream/reviews/M01-T03-R01.toml",
            }],
        }]
        with self.assertRaisesRegex(LateOversizeError, "not a durable review attempt"):
            validate_late_return(
                _late_return(
                    origin="review", origin_attempt="M01-T03-R01",
                    origin_attempt_path="implementation/workstreams/sample-workstream/reviews/M01-T03-R01.toml",
                ),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in cards},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_review_origin_requires_locator_path(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "origin_attempt_path"):
            validate_late_return(
                _late_return(
                    origin="review", origin_attempt="M01-T02-R01",
                    origin_attempt_path="",
                ),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards(attempts=self._attempts())},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )

    def test_execution_origin_must_not_claim_locator_path(self) -> None:
        with self.assertRaisesRegex(LateOversizeError, "origin_attempt_path"):
            validate_late_return(
                _late_return(
                    origin="execution",
                    origin_attempt_path="implementation/workstreams/sample-workstream/reviews/M01-T02-R01.toml",
                ),
                "task_board.late_oversize_returns[0]",
                cards_by_id={c["id"]: c for c in _cards(attempts=self._attempts())},
                triggers_by_id={t["id"]: t for t in _triggers()},
                workstream_id="sample-workstream",
            )


class CoverageTests(unittest.TestCase):
    """Bound returns must cover every residual outcome downstream."""

    def setUp(self) -> None:
        self.workstream = read_toml(VALID / "WORKSTREAM.toml")

    def _anchor_audit(self, board: dict, card_id: str = "M01-T03") -> dict:
        for audit in board["sizing_audits"]:
            if audit["card_id"] == card_id:
                return audit
        raise AssertionError(f"missing anchor audit for {card_id}")

    def _record(self, board: dict, card_id: str = "M01-T02") -> dict:
        for record in board["late_oversize_returns"]:
            if record["card_id"] == card_id:
                return record
        raise AssertionError(f"missing return for {card_id}")

    def test_unrelated_anchor_audit_is_rejected(self) -> None:
        board = _bind_residual(_board_with_return())
        self._anchor_audit(board)["outcomes"] = [_outcome(
            "unrelated-scope",
            statement="Something else entirely.",
            family="other",
        )]
        with self.assertRaisesRegex(ValidationError, "no covering outcome"):
            validate_board(board, self.workstream)

    def test_relabelled_statement_is_rejected(self) -> None:
        board = _bind_residual(_board_with_return())
        self._anchor_audit(board)["outcomes"][0]["statement"] = (
            "Reworded retry policy."
        )
        with self.assertRaisesRegex(ValidationError, "changed"):
            validate_board(board, self.workstream)

    def test_changed_kind_is_rejected(self) -> None:
        board = _bind_residual(_board_with_return())
        self._anchor_audit(board)["outcomes"][0]["kind"] = "acceptance"
        with self.assertRaisesRegex(ValidationError, "changed"):
            validate_board(board, self.workstream)

    def test_partially_covered_residuals_rejected(self) -> None:
        board = _board_with_return(
            residual_outcomes=[_outcome("first"), _outcome("second")]
        )
        board = _bind_residual(board)
        audit = self._anchor_audit(board)
        audit["outcomes"] = [audit["outcomes"][0]]
        with self.assertRaisesRegex(ValidationError, "no covering outcome"):
            validate_board(board, self.workstream)

    def test_duplicate_residual_outcome_ids_rejected(self) -> None:
        board = _board_with_return(
            residual_outcomes=[_outcome("dup"), _outcome("dup")]
        )
        with self.assertRaisesRegex(ValidationError, "duplicate outcome id"):
            validate_board(board, self.workstream)

    def test_missing_anchor_audit_is_rejected(self) -> None:
        board = _bind_residual(_board_with_return(status="returned"))
        for card in board["cards"]:
            if card["id"] == "M01-T03":
                card["status"] = "done"
                card["result"] = {
                    "class": "result",
                    "path": "implementation/workstreams/sample-workstream/results/M01-T03.md",
                }
        board["sizing_audits"] = [
            audit for audit in board["sizing_audits"]
            if audit["card_id"] != "M01-T03"
        ]
        with self.assertRaisesRegex(ValidationError, "sizing audit"):
            validate_board(board, self.workstream)

    def test_split_anchor_across_card_and_trigger_is_valid(self) -> None:
        board = _board_with_return(
            residual_outcomes=[_outcome("first"), _outcome("second")]
        )
        board = _bind_residual(board)
        audit = self._anchor_audit(board)
        audit["decision"] = "split"
        audit["outcomes"][0]["allocated_to"] = "card:M01-T03"
        audit["outcomes"][1]["allocated_to"] = "jit:after-M01-T03"
        board["jit_triggers"].append({
            "id": "after-M01-T03", "after_card": "M01-T03",
            "state": "waiting",
            "condition": "Second residual outcome awaits its own Card.",
        })
        validate_board(board, self.workstream)

    def test_pending_forbids_resolutions(self) -> None:
        board = _board_with_return(jit_resolutions=[
            {"trigger": "after-M01-T02", "card": "M01-T03"},
        ])
        with self.assertRaisesRegex(ValidationError, "must not claim"):
            validate_board(board, self.workstream)

    def test_resolution_unknown_trigger_is_rejected(self) -> None:
        board = _bind_residual(_board_with_return())
        self._record(board)["jit_resolutions"] = [
            {"trigger": "after-nope", "card": "M01-T03"},
        ]
        with self.assertRaisesRegex(ValidationError, "unknown JIT trigger"):
            validate_board(board, self.workstream)

    def test_resolution_unknown_card_is_rejected(self) -> None:
        board = _bind_residual(_board_with_return())
        self._record(board)["jit_resolutions"] = [
            {"trigger": "after-M01-T02", "card": "M01-T99"},
        ]
        with self.assertRaisesRegex(ValidationError, "unknown Card"):
            validate_board(board, self.workstream)

    def test_resolution_unconsumed_trigger_is_rejected(self) -> None:
        board = _board_with_return(
            residual_outcomes=[_outcome("first"), _outcome("second")]
        )
        board = _bind_residual(board)
        audit = self._anchor_audit(board)
        audit["decision"] = "split"
        audit["outcomes"][0]["allocated_to"] = "card:M01-T03"
        audit["outcomes"][1]["allocated_to"] = "jit:after-M01-T03"
        board["jit_triggers"].append({
            "id": "after-M01-T03", "after_card": "M01-T03",
            "state": "waiting",
            "condition": "Second residual outcome awaits its own Card.",
        })
        board["cards"].append({
            "id": "M01-T04", "status": "done",
            "contract": {
                "class": "task_card",
                "path": "implementation/workstreams/sample-workstream/cards/M01-T04.md",
            },
            "result": {
                "class": "result",
                "path": "implementation/workstreams/sample-workstream/results/M01-T04.md",
            },
        })
        self._record(board)["jit_resolutions"] = [
            {"trigger": "after-M01-T03", "card": "M01-T04"},
        ]
        with self.assertRaisesRegex(ValidationError, "consumed"):
            validate_board(board, self.workstream)

    def test_resolution_unreferenced_trigger_is_rejected(self) -> None:
        board = _bind_residual(_board_with_return())
        board["jit_triggers"].append({
            "id": "after-M01-T01", "after_card": "M01-T01",
            "state": "consumed",
            "condition": "Historical DONE predecessor consumed.",
        })
        self._record(board)["jit_resolutions"] = [
            {"trigger": "after-M01-T01", "card": "M01-T01"},
        ]
        with self.assertRaisesRegex(ValidationError, "not allocated"):
            validate_board(board, self.workstream)

    def test_resolution_duplicate_trigger_is_rejected(self) -> None:
        board = self._resolved_board()
        self._record(board)["jit_resolutions"].append(
            {"trigger": "after-M01-T03", "card": "M01-T04"}
        )
        with self.assertRaisesRegex(ValidationError, "duplicate"):
            validate_board(board, self.workstream)

    def test_resolution_to_original_is_rejected(self) -> None:
        board = self._resolved_board()
        self._record(board)["jit_resolutions"] = [
            {"trigger": "after-M01-T03", "card": "M01-T02"},
        ]
        with self.assertRaisesRegex(ValidationError, "different Card"):
            validate_board(board, self.workstream)

    def test_valid_resolution_is_accepted(self) -> None:
        validate_board(self._resolved_board(), self.workstream)

    def _resolved_board(self) -> dict:
        board = _board_with_return(
            residual_outcomes=[_outcome("first"), _outcome("second")]
        )
        board = _bind_residual(board)
        audit = self._anchor_audit(board)
        audit["decision"] = "split"
        audit["outcomes"][0]["allocated_to"] = "card:M01-T03"
        audit["outcomes"][1]["allocated_to"] = "jit:after-M01-T03"
        for card in board["cards"]:
            if card["id"] == "M01-T03":
                card["status"] = "done"
                card["result"] = {
                    "class": "result",
                    "path": "implementation/workstreams/sample-workstream/results/M01-T03.md",
                }
        board["jit_triggers"].append({
            "id": "after-M01-T03", "after_card": "M01-T03",
            "state": "consumed",
            "condition": "Second residual outcome materialized its own Card.",
        })
        board["cards"].append({
            "id": "M01-T04", "status": "done",
            "contract": {
                "class": "task_card",
                "path": "implementation/workstreams/sample-workstream/cards/M01-T04.md",
            },
            "result": {
                "class": "result",
                "path": "implementation/workstreams/sample-workstream/results/M01-T04.md",
            },
        })
        self._record(board)["jit_resolutions"] = [
            {"trigger": "after-M01-T03", "card": "M01-T04"},
        ]
        return board


class UnfinishedScopeTests(unittest.TestCase):
    """Close-time residual-outcome graph walk."""

    def setUp(self) -> None:
        self.workstream = read_toml(VALID / "WORKSTREAM.toml")

    def _done_card(self, board: dict, card_id: str) -> None:
        for card in board["cards"]:
            if card["id"] == card_id:
                card["status"] = "done"
                card["result"] = {
                    "class": "result",
                    "path": f"implementation/workstreams/sample-workstream/results/{card_id}.md",
                }

    def test_complete_single_outcome_returns_none(self) -> None:
        board = _bind_residual(_board_with_return(status="returned"))
        self._done_card(board, "M01-T03")
        validate_board(board, self.workstream)
        self.assertIsNone(unfinished_residual_scope(board))

    def test_pending_return_is_unfinished(self) -> None:
        board = _board_with_return()
        gap = unfinished_residual_scope(board)
        assert gap is not None
        self.assertIn("pending", gap)

    def test_waiting_trigger_blocks_close(self) -> None:
        board = _board_with_return(
            residual_outcomes=[_outcome("first"), _outcome("second")]
        )
        board = _bind_residual(board)
        for card in board["cards"]:
            if card["id"] == "M01-T02":
                card["status"] = "returned"
            if card["id"] == "M01-T03":
                card["status"] = "done"
                card["result"] = {
                    "class": "result",
                    "path": "implementation/workstreams/sample-workstream/results/M01-T03.md",
                }
        for audit in board["sizing_audits"]:
            if audit["card_id"] == "M01-T03":
                audit["decision"] = "split"
                audit["outcomes"][0]["allocated_to"] = "card:M01-T03"
                audit["outcomes"][1]["allocated_to"] = "jit:after-M01-T03"
        board["jit_triggers"].append({
            "id": "after-M01-T03", "after_card": "M01-T03",
            "state": "waiting",
            "condition": "Second residual outcome awaits its own Card.",
        })
        validate_board(board, self.workstream)
        gap = unfinished_residual_scope(board)
        assert gap is not None
        self.assertIn("second", gap)
        self.assertIn("after-M01-T03", gap)

    def test_chained_handoff_completes(self) -> None:
        board = _bind_residual(_board_with_return(status="returned"))
        for card in board["cards"]:
            if card["id"] == "M01-T03":
                card["status"] = "returned"
        board["cards"].append({
            "id": "M01-T04", "status": "done",
            "contract": {
                "class": "task_card",
                "path": "implementation/workstreams/sample-workstream/cards/M01-T04.md",
            },
            "result": {
                "class": "result",
                "path": "implementation/workstreams/sample-workstream/results/M01-T04.md",
            },
        })
        board["jit_triggers"].append({
            "id": "after-M01-T03", "after_card": "M01-T03",
            "state": "waiting",
            "condition": "Chained handoff parking.",
        })
        board["sizing_audits"].append(_sizing_audit("M01-T04"))
        chained = _late_return(
            card_id="M01-T03", state="residual_bound",
            residual_card="M01-T04",
            residual_trigger="after-M01-T03",
        )
        chained["preserved_refs"] = [
            "implementation/workstreams/sample-workstream/evidence/M01-T03-core.md",
        ]
        board["late_oversize_returns"].append(chained)
        validate_board(board, self.workstream)
        self.assertIsNone(unfinished_residual_scope(board))

    def test_chained_handoff_dropping_scope_blocks_close(self) -> None:
        board = _bind_residual(_board_with_return(status="returned"))
        for card in board["cards"]:
            if card["id"] == "M01-T03":
                card["status"] = "returned"
        board["cards"].append({
            "id": "M01-T04", "status": "done",
            "contract": {
                "class": "task_card",
                "path": "implementation/workstreams/sample-workstream/cards/M01-T04.md",
            },
            "result": {
                "class": "result",
                "path": "implementation/workstreams/sample-workstream/results/M01-T04.md",
            },
        })
        board["jit_triggers"].append({
            "id": "after-M01-T03", "after_card": "M01-T03",
            "state": "waiting",
            "condition": "Chained handoff parking.",
        })
        reframed = _sizing_audit("M01-T04", [_outcome("reframed")])
        board["sizing_audits"].append(reframed)
        chained = _late_return(
            card_id="M01-T03", state="residual_bound",
            residual_card="M01-T04",
            residual_outcomes=[_outcome("reframed")],
            residual_trigger="after-M01-T03",
        )
        chained["preserved_refs"] = [
            "implementation/workstreams/sample-workstream/evidence/M01-T03-core.md",
        ]
        board["late_oversize_returns"].append(chained)
        validate_board(board, self.workstream)
        gap = unfinished_residual_scope(board)
        assert gap is not None
        self.assertIn("not carried by the chained return", gap)

    def test_circular_handoff_blocks_close(self) -> None:
        board = _bind_residual(_board_with_return(status="returned"))
        for card in board["cards"]:
            if card["id"] == "M01-T03":
                card["status"] = "returned"
        for audit in board["sizing_audits"]:
            if audit["card_id"] == "M01-T02":
                audit["outcomes"] = [_outcome()]
        board["jit_triggers"].append({
            "id": "after-M01-T03", "after_card": "M01-T03",
            "state": "waiting",
            "condition": "Circular handoff parking.",
        })
        chained = _late_return(
            card_id="M01-T03", state="residual_bound",
            residual_card="M01-T02",
            residual_trigger="after-M01-T03",
        )
        chained["preserved_refs"] = [
            "implementation/workstreams/sample-workstream/evidence/M01-T03-core.md",
        ]
        board["late_oversize_returns"].append(chained)
        validate_board(board, self.workstream)
        gap = unfinished_residual_scope(board)
        assert gap is not None
        self.assertIn("cycles", gap)


class LifecycleTests(unittest.TestCase):
    """pending -> residual_bound -> non-GREEN terminal handoff lifecycle."""

    def setUp(self) -> None:
        self.workstream = read_toml(VALID / "WORKSTREAM.toml")

    def test_bind_residual_releases_pending_hold_into_handoff_hold(self) -> None:
        board = _bind_residual(_board_with_return())
        validate_board(board, self.workstream)
        self.assertIsNone(pending_late_return(board))
        self.assertEqual(bound_handoff_hold(board), "M01-T02")

    def test_pending_forbids_residual_card_binding(self) -> None:
        board = _board_with_return(residual_card="M01-T03")
        with self.assertRaisesRegex(ValidationError, "residual_card"):
            validate_board(board, self.workstream)

    def test_bound_requires_residual_card_binding(self) -> None:
        board = _bind_residual(_board_with_return())
        board["late_oversize_returns"][0]["residual_card"] = ""
        with self.assertRaisesRegex(ValidationError, "residual_card"):
            validate_board(board, self.workstream)

    def test_unknown_return_state_is_rejected(self) -> None:
        board = _board_with_return(state="handed_off")
        with self.assertRaisesRegex(ValidationError, "unknown return state"):
            validate_board(board, self.workstream)

    def test_residual_must_not_be_the_original_card(self) -> None:
        board = _board_with_return(
            state="residual_bound", residual_card="M01-T02",
        )
        with self.assertRaisesRegex(ValidationError, "must name a different Card"):
            validate_board(board, self.workstream)

    def test_dangling_residual_card_is_rejected(self) -> None:
        board = _board_with_return(
            state="residual_bound", residual_card="M01-T99",
        )
        with self.assertRaisesRegex(ValidationError, "unknown residual Card"):
            validate_board(board, self.workstream)

    def test_done_with_bound_return_is_rejected(self) -> None:
        board = _bind_residual(_board_with_return(status="done"))
        for card in board["cards"]:
            if card["id"] == "M01-T02":
                card["result"] = {
                    "class": "result",
                    "path": "implementation/workstreams/sample-workstream/results/M01-T02.md",
                }
        with self.assertRaisesRegex(ValidationError, "reserved for accepted"):
            validate_board(board, self.workstream)

    def test_returned_with_pending_return_is_rejected(self) -> None:
        board = _board_with_return(status="returned")
        with self.assertRaisesRegex(ValidationError, "must be bound"):
            validate_board(board, self.workstream)

    def test_returned_without_return_is_rejected(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        for card in board["cards"]:
            if card["id"] == "M01-T02":
                card["status"] = "returned"
        with self.assertRaisesRegex(
            ValidationError, "requires a bound late-oversize return"
        ):
            validate_board(board, self.workstream)

    def test_returned_with_bound_return_is_non_green_terminal(self) -> None:
        board = _bind_residual(_board_with_return(status="returned"))
        for card in board["cards"]:
            if card["id"] == "M01-T02":
                card["result"] = {
                    "class": "result",
                    "path": "implementation/workstreams/sample-workstream/results/M01-T02.md",
                }
        validate_board(board, self.workstream)
        self.assertIsNone(pending_late_return(board))
        self.assertIsNone(bound_handoff_hold(board))
        record = board["late_oversize_returns"][0]
        self.assertEqual(record["state"], "residual_bound")
        self.assertFalse(record["claims_green"])

    def test_returned_terminal_needs_no_result(self) -> None:
        board = _bind_residual(_board_with_return(status="returned"))
        validate_board(board, self.workstream)
        for card in board["cards"]:
            if card["id"] == "M01-T02":
                self.assertNotIn("result", card)

    def test_trigger_advances_after_non_green_terminal(self) -> None:
        for trigger_state in ("satisfied", "consumed"):
            with self.subTest(trigger_state=trigger_state):
                board = _bind_residual(
                    _board_with_return(status="returned",
                                       trigger_state=trigger_state)
                )
                validate_board(board, self.workstream)
                record = board["late_oversize_returns"][0]
                self.assertEqual(record["residual_trigger"], "after-M01-T02")
                self.assertFalse(record["claims_green"])

    def test_forged_trigger_satisfaction_after_returned_is_rejected(self) -> None:
        board = _bind_residual(_board_with_return(status="returned"))
        board["jit_triggers"].append({
            "id": "after-M01-T02-forged", "after_card": "M01-T02",
            "state": "satisfied",
            "condition": "Forged satisfaction without a bound handoff.",
        })
        with self.assertRaisesRegex(
            ValidationError, "bound late-oversize handoff"
        ):
            validate_board(board, self.workstream)

    def test_done_predecessor_trigger_path_is_unchanged(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board.pop("late_oversize_returns", None)
        board["jit_triggers"] = [{
            "id": "after-M01-T01", "after_card": "M01-T01",
            "state": "satisfied",
            "condition": "Historical DONE predecessor result consumed.",
        }]
        validate_board(board, self.workstream)

    def test_trigger_cannot_advance_before_handoff_terminal(self) -> None:
        board = _bind_residual(
            _board_with_return(trigger_state="satisfied")
        )
        with self.assertRaisesRegex(ValidationError, "DONE predecessor result"):
            validate_board(board, self.workstream)

    def test_blocked_card_cannot_hold_a_return(self) -> None:
        board = _bind_residual(_board_with_return())
        for card in board["cards"]:
            if card["id"] == "M01-T02":
                card["status"] = "blocked"
                card["blocker"] = {
                    "class": "blocker",
                    "path": "implementation/workstreams/sample-workstream/blockers/M01-T02.toml",
                }
        with self.assertRaisesRegex(ValidationError, "in_progress"):
            validate_board(board, self.workstream)

    def test_bound_residual_requires_fresh_audits(self) -> None:
        board = _bind_residual(_board_with_return())
        board["sizing_audits"] = [a for a in board["sizing_audits"]
                                  if a["card_id"] != "M01-T03"]
        with self.assertRaisesRegex(
            ValidationError, "missing durable sizing audit for Card 'M01-T03'"
        ):
            validate_board(board, self.workstream)

    def test_history_survives_binding_and_terminal(self) -> None:
        attempts = [{
            "class": "review_attempt",
            "path": "implementation/workstreams/sample-workstream/reviews/M01-T02-R01.toml",
        }]
        board = _bind_residual(_board_with_return(
            attempts=attempts, status="returned", origin="review",
            origin_attempt="M01-T02-R01",
            origin_attempt_path="implementation/workstreams/sample-workstream/reviews/M01-T02-R01.toml",
        ))
        for card in board["cards"]:
            if card["id"] == "M01-T02":
                card["result"] = {
                    "class": "result",
                    "path": "implementation/workstreams/sample-workstream/results/M01-T02.md",
                }
        validate_board(board, self.workstream)
        for card in board["cards"]:
            if card["id"] == "M01-T02":
                self.assertEqual(card["review_attempts"], attempts)
                self.assertIn("result", card)


class TrajectoryTests(unittest.TestCase):
    """Full Board/router trajectory from pending return to residual launch."""

    def copy_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(ROUTER_FIXTURE, project)
        return temp, project

    def _audit_toml(self, card_id: str) -> str:
        if card_id == "M01-T05":
            outcome_id = "residual-retry"
            statement = "Bounded retry policy with its own contract."
            family = "retry-policy"
        else:
            outcome_id = "scope"
            statement = "Coherent single outcome."
            family = "scope"
        return (
            "[[sizing_audits]]\n"
            f"card_id = \"{card_id}\"\n"
            "decision = \"single\"\n"
            "rebuttal_class = \"\"\n"
            "rebuttal = \"\"\n"
            "[[sizing_audits.outcomes]]\n"
            f"id = \"{outcome_id}\"\n"
            "kind = \"invariant\"\n"
            f"statement = \"{statement}\"\n"
            f"family = \"{family}\"\n"
            "independently_verifiable = true\n"
            "independently_useful = true\n"
            "falsifiable = true\n"
            "substantial = true\n"
            "scaffolding_only = false\n"
            "independently_consumed = false\n"
            "[sizing_audits.dimensions]\n"
            "independent_implementability = \"Builds and passes alone.\"\n"
            "falsifiability_testability = \"Own failing check before GREEN.\"\n"
            "reviewability = \"One bounded Card review covers it.\"\n"
            "invariant_contract_family = \"Single family.\"\n"
            "dependency_ordering = \"Launches after the handoff trigger.\"\n"
            "atomic_mutation_migration = \"No joint atomic landing.\"\n"
            "cross_surface_coupling = \"No shared mutable surface.\"\n"
            "[[topology_audits]]\n"
            f"card_id = \"{card_id}\"\n"
            "risk = \"simple\"\n"
            "triggers = []\n"
            "risk_basis = \"Single coherent outcome in one invariant family.\"\n"
            "review_scope = \"card_local\"\n"
            "atomicity_rationale_class = \"\"\n"
            "atomicity_rationale = \"\"\n"
        )

    def _return_toml(self, *, state: str, residual_card: str,
                     origin: str = "execution",
                     origin_attempt: str = "",
                     origin_attempt_path: str = "") -> str:
        outcome = (
            "[[late_oversize_returns.residual_outcomes]]\n"
            "id = \"residual-retry\"\n"
            "kind = \"invariant\"\n"
            "statement = \"Bounded retry policy with its own contract.\"\n"
            "family = \"retry-policy\"\n"
            "independently_verifiable = true\n"
            "independently_useful = true\n"
            "falsifiable = true\n"
            "substantial = true\n"
            "scaffolding_only = false\n"
            "independently_consumed = false\n"
        )
        return (
            "[[late_oversize_returns]]\n"
            "card_id = \"M01-T04\"\n"
            f"origin = \"{origin}\"\n"
            f"origin_attempt = \"{origin_attempt}\"\n"
            f"origin_attempt_path = \"{origin_attempt_path}\"\n"
            f"state = \"{state}\"\n"
            f"residual_card = \"{residual_card}\"\n"
            "material_evidence = \"Load testing exposed a second separable review-worthy outcome.\"\n"
            "preserved_refs = [\"implementation/workstreams/sample-workstream/evidence/M01-T04-core.md\"]\n"
            "preserved_basis = \"Core routing validation passes alone while residual scope is RED.\"\n"
            "residual_scope = \"Remaining unaccepted scope returns for bounded re-decomposition.\"\n"
            "residual_trigger = \"after-M01-T04\"\n"
            "bounded_correction_applies = false\n"
            "not_bug_basis = \"Separable review-worthy outcome, not a core defect.\"\n"
            "merges_required_seam = false\n"
            "seam_basis = \"No required seam is merged by this return.\"\n"
            "preserves_history = true\n"
            "claims_green = false\n"
            f"{outcome}"
        )

    def write_board(self, project: Path, *, original_status: str,
                    return_state: str | None = "pending",
                    residual_card: str = "",
                    residual_status: str | None = None,
                    trigger_state: str = "waiting",
                    review_locator: str | None = None,
                    origin: str = "execution",
                    origin_attempt: str = "",
                    origin_attempt_path: str = "",
                    with_result: bool = False,
                    result_commit: str | None = None,
                    result_blob: str | None = None) -> None:
        cards = (
            "[[cards]]\n"
            "id = \"M01-T04\"\n"
            f"status = \"{original_status}\"\n"
            "[cards.contract]\n"
            "class = \"task_card\"\n"
            "path = \"implementation/workstreams/sample-workstream/cards/M01-T04.md\"\n"
        )
        if original_status == "done" or with_result:
            cards += (
                "[cards.result]\n"
                "class = \"result\"\n"
                "path = \"implementation/workstreams/sample-workstream/results/M01-T04.md\"\n"
            )
            if result_commit is not None and result_blob is not None:
                cards += (
                    f"commit = \"{result_commit}\"\n"
                    f"blob = \"{result_blob}\"\n"
                )
        if review_locator is not None:
            cards += (
                "[[cards.review_attempts]]\n"
                "class = \"review_attempt\"\n"
                f"path = \"{review_locator}\"\n"
            )
        if residual_status is not None:
            cards += (
                "[[cards]]\n"
                "id = \"M01-T05\"\n"
                f"status = \"{residual_status}\"\n"
                "[cards.contract]\n"
                "class = \"task_card\"\n"
                "path = \"implementation/workstreams/sample-workstream/cards/M01-T05.md\"\n"
            )
            if residual_status == "done":
                cards += (
                    "[cards.result]\n"
                    "class = \"result\"\n"
                    "path = \"implementation/workstreams/sample-workstream/results/M01-T05.md\"\n"
                )
        audits = self._audit_toml("M01-T04")
        if residual_status is not None:
            audits += self._audit_toml("M01-T05")
        trigger = (
            "[[jit_triggers]]\n"
            "id = \"after-M01-T04\"\n"
            "after_card = \"M01-T04\"\n"
            f"state = \"{trigger_state}\"\n"
            "condition = \"Residual late-oversize scope awaits re-decomposition.\"\n"
        )
        returns = ""
        if return_state is not None:
            returns = self._return_toml(
                state=return_state, residual_card=residual_card,
                origin=origin, origin_attempt=origin_attempt,
                origin_attempt_path=origin_attempt_path,
            )
        board = (
            "workstream_id = \"sample-workstream\"\n"
            "revision = 3\n"
            "[execution_ref]\n"
            "branch = \"feat/sample-workstream\"\n"
            f"{cards}{audits}{trigger}{returns}"
        )
        (project / ROUTER_BOARD).write_text(board)

    def write_supporting_files(self, project: Path, *,
                               with_residual_card: bool = False,
                               residual_dependencies: str = "none",
                               attempt_id: str | None = None) -> None:
        base = project / "implementation" / "workstreams" / "sample-workstream"
        evidence = base / "evidence" / "M01-T04-core.md"
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text("# Preserved core evidence\n")
        result = base / "results" / "M01-T04.md"
        result.parent.mkdir(parents=True, exist_ok=True)
        result.write_text(
            "# Card Result\n"
            "- Card ID: M01-T04\n"
            "- Implementation subject: preserved core routing scope only\n"
            "- Evidence refs: implementation/workstreams/sample-workstream/evidence/M01-T04-core.md\n"
            "- Tests/readback summary: core checks pass; residual retry scope handed to M01-T05\n"
        )
        if with_residual_card:
            (base / "cards" / "M01-T05.md").write_text(
                "# Fixture Card\n"
                "- Card ID: M01-T05\n"
                "- Included scope: residual retry policy\n"
                "- Excluded scope: runtime-specific orchestration\n"
                "- Authority refs: requirements/REQUIREMENTS.md\n"
                f"- Dependencies: {residual_dependencies}\n"
                "- Acceptance: bounded retry policy with its own contract\n"
                "- Required tests/readback: residual contract fixtures\n"
                "- Review requirement: none\n"
                "- Technical contract: none\n"
            )
            authority = project / "requirements" / "REQUIREMENTS.md"
            authority.parent.mkdir(parents=True, exist_ok=True)
            authority.write_text("# Accepted authority\n")
        if attempt_id is not None:
            reviews = base / "reviews"
            reviews.mkdir(parents=True, exist_ok=True)
            (reviews / "M01-T04-R01.toml").write_text(
                f"attempt = \"{attempt_id}\"\n"
                "verdict = \"red\"\n"
                "evidence_path = \"evidence/review-R01.md\"\n"
                "[subject]\n"
                "class = \"git_blob\"\n"
                "repository = \"owner/fixture-project\"\n"
                "commit = \"2222222222222222222222222222222222222222\"\n"
                "path = \"workflow/STATE.md\"\n"
                "blob = \"3333333333333333333333333333333333333333\"\n"
                "[acceptance]\n"
                "class = \"authority\"\n"
                "path = \"requirements/PROJECT_WORKFLOW_V2.md\"\n"
                "[independence]\n"
                "materially_produced_or_repaired_subject = false\n"
                "basis = \"Independent review context.\"\n"
            )

    def test_full_execution_origin_trajectory_to_residual_launch(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.write_supporting_files(project, with_residual_card=True)
            # Phase A: pending return holds the active Card in Execution Prep.
            self.write_board(project, original_status="in_progress")
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution_prep", "M01-T04"),
            )
            self.assertIn("late-oversize", routed.reason)
            self.assertIn("pending", routed.reason)
            # Phase B: bound residual holds for non-GREEN handoff finalization.
            self.write_board(
                project, original_status="in_progress",
                return_state="residual_bound", residual_card="M01-T05",
                residual_status="planned",
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution_prep", "M01-T04"),
            )
            self.assertIn("handoff", routed.reason)
            # Phase C: returned terminal original releases the residual.
            self.write_board(
                project, original_status="returned",
                return_state="residual_bound", residual_card="M01-T05",
                residual_status="planned", trigger_state="consumed",
                with_result=True,
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "execution_prep"),
            )
            # Phase D: residual launches through the ordinary gates.
            self.write_board(
                project, original_status="returned",
                return_state="residual_bound", residual_card="M01-T05",
                residual_status="ready", trigger_state="consumed",
                with_result=True,
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution_prep", "M01-T05"),
            )
            self.write_board(
                project, original_status="returned",
                return_state="residual_bound", residual_card="M01-T05",
                residual_status="in_progress", trigger_state="consumed",
                with_result=True,
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution", "M01-T05"),
            )
            # Phase E: all terminal routes Close without a Prep loop, and
            # Close is told the returned Card is not accepted completion.
            self.write_board(
                project, original_status="returned",
                return_state="residual_bound", residual_card="M01-T05",
                residual_status="done", trigger_state="consumed",
                with_result=True,
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "close"),
            )
            self.assertEqual(routed.owner_module, "workflow/CLOSE.md")
            self.assertIn("returned", routed.reason)
        finally:
            temp.cleanup()

    def test_review_origin_trajectory_verifies_exact_attempt(self) -> None:
        temp, project = self.copy_fixture()
        try:
            locator = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
            self.write_supporting_files(project, with_residual_card=True,
                                        attempt_id="M01-T04-R01")
            self.write_board(
                project, original_status="in_progress",
                review_locator=locator, origin="review",
                origin_attempt="M01-T04-R01", origin_attempt_path=locator,
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution_prep", "M01-T04"),
            )
            self.assertIn(locator, "\n".join(routed.read_set))
            # Bound review-origin handoff finalizes to returned, keeping history.
            self.write_board(
                project, original_status="in_progress",
                return_state="residual_bound", residual_card="M01-T05",
                residual_status="planned",
                review_locator=locator, origin="review",
                origin_attempt="M01-T04-R01", origin_attempt_path=locator,
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution_prep", "M01-T04"),
            )
            self.assertIn("handoff", routed.reason)
            self.write_board(
                project, original_status="returned",
                return_state="residual_bound", residual_card="M01-T05",
                residual_status="planned", trigger_state="consumed",
                review_locator=locator, origin="review",
                origin_attempt="M01-T04-R01", origin_attempt_path=locator,
                with_result=True,
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "execution_prep"),
            )
            self.write_board(
                project, original_status="returned",
                return_state="residual_bound", residual_card="M01-T05",
                residual_status="done", trigger_state="consumed",
                review_locator=locator, origin="review",
                origin_attempt="M01-T04-R01", origin_attempt_path=locator,
                with_result=True,
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "close"),
            )
        finally:
            temp.cleanup()

    def test_review_attempt_id_mismatch_recovers(self) -> None:
        temp, project = self.copy_fixture()
        try:
            locator = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
            self.write_supporting_files(project, attempt_id="M01-T04-R99")
            self.write_board(
                project, original_status="in_progress",
                review_locator=locator, origin="review",
                origin_attempt="M01-T04-R01", origin_attempt_path=locator,
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("review attempt", routed.reason)
        finally:
            temp.cleanup()

    def test_missing_review_attempt_file_recovers(self) -> None:
        temp, project = self.copy_fixture()
        try:
            locator = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
            self.write_supporting_files(project, attempt_id=None)
            self.write_board(
                project, original_status="in_progress",
                review_locator=locator, origin="review",
                origin_attempt="M01-T04-R01", origin_attempt_path=locator,
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
        finally:
            temp.cleanup()

    def test_done_with_return_recovers(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.write_supporting_files(project)
            self.write_board(project, original_status="done")
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("reserved for accepted", routed.reason)
        finally:
            temp.cleanup()

    def test_bound_hold_wins_over_result_finalization(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.write_supporting_files(project, with_residual_card=True)
            self.write_board(
                project, original_status="in_progress",
                return_state="residual_bound", residual_card="M01-T05",
                residual_status="planned", with_result=True,
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution_prep", "M01-T04"),
            )
            self.assertIn("handoff", routed.reason)
        finally:
            temp.cleanup()

    def test_returned_result_is_not_a_done_predecessor(self) -> None:
        temp, project = self.copy_fixture()
        try:
            commit, blob = "a" * 40, "b" * 40
            dependency = (
                "implementation/workstreams/sample-workstream/results/M01-T04.md"
                f"@{commit}:{blob}"
            )
            self.write_supporting_files(
                project, with_residual_card=True,
                residual_dependencies=dependency,
            )
            self.write_board(
                project, original_status="returned",
                return_state="residual_bound", residual_card="M01-T05",
                residual_status="ready", trigger_state="consumed",
                with_result=True, result_commit=commit, result_blob=blob,
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("DONE predecessor result", routed.reason)
        finally:
            temp.cleanup()

    def test_dangling_residual_binding_recovers(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.write_supporting_files(project)
            self.write_board(
                project, original_status="in_progress",
                return_state="residual_bound", residual_card="M01-T99",
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("unknown residual Card", routed.reason)
        finally:
            temp.cleanup()

    def test_coverage_mismatch_recovers(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.write_supporting_files(project, with_residual_card=True)
            self.write_board(
                project, original_status="in_progress",
                return_state="residual_bound", residual_card="M01-T05",
                residual_status="planned",
            )
            board_path = project / ROUTER_BOARD
            text = board_path.read_text()
            board_path.write_text(
                text.replace('id = "residual-retry"', 'id = "unrelated"', 1)
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("no covering outcome", routed.reason)
        finally:
            temp.cleanup()


class SplitTrajectoryTests(unittest.TestCase):
    """Two residual outcomes across Card/JIT boundaries to Close."""

    OUTCOMES = (
        {"id": "retry-core", "kind": "invariant",
         "statement": "Core retry state machine with its own contract.",
         "family": "retry-core"},
        {"id": "retry-backoff", "kind": "invariant",
         "statement": "Backoff schedule with its own contract.",
         "family": "retry-backoff"},
    )

    def copy_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(ROUTER_FIXTURE, project)
        return temp, project

    def _write_card_file(self, project: Path, card_id: str,
                         scope: str) -> None:
        base = project / "implementation" / "workstreams" / "sample-workstream"
        (base / "cards" / f"{card_id}.md").write_text(
            "# Fixture Card\n"
            f"- Card ID: {card_id}\n"
            f"- Included scope: {scope}\n"
            "- Excluded scope: runtime-specific orchestration\n"
            "- Authority refs: requirements/REQUIREMENTS.md\n"
            "- Dependencies: none\n"
            "- Acceptance: residual scope acceptance\n"
            "- Required tests/readback: residual fixtures\n"
            "- Review requirement: none\n"
            "- Technical contract: none\n"
        )
        authority = project / "requirements" / "REQUIREMENTS.md"
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text("# Accepted authority\n")

    def _outcome_toml(self, outcome: dict, allocated_to: str | None = None,
                      table: str = "sizing_audits.outcomes") -> str:
        text = (
            f"[[{table}]]\n"
            f"id = \"{outcome['id']}\"\n"
            f"kind = \"{outcome['kind']}\"\n"
            f"statement = \"{outcome['statement']}\"\n"
            f"family = \"{outcome['family']}\"\n"
            "independently_verifiable = true\n"
            "independently_useful = true\n"
            "falsifiable = true\n"
            "substantial = true\n"
            "scaffolding_only = false\n"
            "independently_consumed = false\n"
        )
        if allocated_to is not None:
            text += f"allocated_to = \"{allocated_to}\"\n"
        return text

    def _dims_toml(self) -> str:
        return (
            "[sizing_audits.dimensions]\n"
            "independent_implementability = \"Builds and passes alone.\"\n"
            "falsifiability_testability = \"Own failing check before GREEN.\"\n"
            "reviewability = \"One bounded Card review covers it.\"\n"
            "invariant_contract_family = \"Single family.\"\n"
            "dependency_ordering = \"Launches after the handoff trigger.\"\n"
            "atomic_mutation_migration = \"No joint atomic landing.\"\n"
            "cross_surface_coupling = \"No shared mutable surface.\"\n"
        )

    def _topology_toml(self, card_id: str) -> str:
        return (
            "[[topology_audits]]\n"
            f"card_id = \"{card_id}\"\n"
            "risk = \"simple\"\n"
            "triggers = []\n"
            "risk_basis = \"Single coherent outcome in one invariant family.\"\n"
            "review_scope = \"card_local\"\n"
            "atomicity_rationale_class = \"\"\n"
            "atomicity_rationale = \"\"\n"
        )

    def _card_toml(self, card_id: str, status: str,
                   with_result: bool = False) -> str:
        text = (
            "[[cards]]\n"
            f"id = \"{card_id}\"\n"
            f"status = \"{status}\"\n"
            "[cards.contract]\n"
            "class = \"task_card\"\n"
            f"path = \"implementation/workstreams/sample-workstream/cards/{card_id}.md\"\n"
        )
        if with_result or status == "done":
            text += (
                "[cards.result]\n"
                "class = \"result\"\n"
                f"path = \"implementation/workstreams/sample-workstream/results/{card_id}.md\"\n"
            )
        return text

    def write_board(self, project: Path, *, original_status: str,
                    return_state: str = "pending",
                    anchor_status: str | None = None,
                    r3_status: str | None = None,
                    handoff_trigger_state: str = "waiting",
                    jit_trigger_state: str = "waiting",
                    resolutions: list[tuple[str, str]] | None = None) -> None:
        cards = self._card_toml("M01-T04", original_status,
                                with_result=(original_status == "returned"))
        if anchor_status is not None:
            cards += self._card_toml("M01-T05", anchor_status)
        if r3_status is not None:
            cards += self._card_toml("M01-T07", r3_status)
        audits = (
            "[[sizing_audits]]\n"
            "card_id = \"M01-T04\"\n"
            "decision = \"single\"\n"
            "rebuttal_class = \"\"\n"
            "rebuttal = \"\"\n"
            + self._outcome_toml({"id": "scope", "kind": "invariant",
                                  "statement": "Coherent single outcome.",
                                  "family": "scope"})
            + self._dims_toml()
            + self._topology_toml("M01-T04")
        )
        if anchor_status is not None:
            audits += (
                "[[sizing_audits]]\n"
                "card_id = \"M01-T05\"\n"
                "decision = \"split\"\n"
                "rebuttal_class = \"\"\n"
                "rebuttal = \"\"\n"
                + self._outcome_toml(self.OUTCOMES[0],
                                     allocated_to="card:M01-T05")
                + self._outcome_toml(self.OUTCOMES[1],
                                     allocated_to="jit:after-M01-T05")
                + self._dims_toml()
                + self._topology_toml("M01-T05")
            )
        if r3_status in ("planned", "ready", "in_progress"):
            audits += (
                "[[sizing_audits]]\n"
                "card_id = \"M01-T07\"\n"
                "decision = \"single\"\n"
                "rebuttal_class = \"\"\n"
                "rebuttal = \"\"\n"
                + self._outcome_toml(self.OUTCOMES[1])
                + self._dims_toml()
                + self._topology_toml("M01-T07")
            )
        triggers = (
            "[[jit_triggers]]\n"
            "id = \"after-M01-T04\"\n"
            "after_card = \"M01-T04\"\n"
            f"state = \"{handoff_trigger_state}\"\n"
            "condition = \"Residual late-oversize scope awaits re-decomposition.\"\n"
        )
        if anchor_status is not None:
            triggers += (
                "[[jit_triggers]]\n"
                "id = \"after-M01-T05\"\n"
                "after_card = \"M01-T05\"\n"
                f"state = \"{jit_trigger_state}\"\n"
                "condition = \"Backoff outcome awaits its own Card.\"\n"
            )
        outcomes = "".join(
            self._outcome_toml(outcome,
                               table="late_oversize_returns.residual_outcomes")
            for outcome in self.OUTCOMES
        )
        resolutions_toml = "".join(
            "[[late_oversize_returns.jit_resolutions]]\n"
            f"trigger = \"{trigger}\"\n"
            f"card = \"{card}\"\n"
            for trigger, card in (resolutions or [])
        )
        returns = (
            "[[late_oversize_returns]]\n"
            "card_id = \"M01-T04\"\n"
            "origin = \"execution\"\n"
            "origin_attempt = \"\"\n"
            "origin_attempt_path = \"\"\n"
            f"state = \"{return_state}\"\n"
            f"residual_card = \"{'M01-T05' if return_state == 'residual_bound' else ''}\"\n"
            "material_evidence = \"Load testing exposed two separable review-worthy outcomes.\"\n"
            "preserved_refs = [\"implementation/workstreams/sample-workstream/evidence/M01-T04-core.md\"]\n"
            "preserved_basis = \"Core routing validation passes alone while residual scope is RED.\"\n"
            "residual_scope = \"Remaining unaccepted scope returns for bounded re-decomposition.\"\n"
            "residual_trigger = \"after-M01-T04\"\n"
            "bounded_correction_applies = false\n"
            "not_bug_basis = \"Separable review-worthy outcomes, not core defects.\"\n"
            "merges_required_seam = false\n"
            "seam_basis = \"No required seam is merged by this return.\"\n"
            "preserves_history = true\n"
            "claims_green = false\n"
            f"{outcomes}{resolutions_toml}"
        )
        board = (
            "workstream_id = \"sample-workstream\"\n"
            "revision = 3\n"
            "[execution_ref]\n"
            "branch = \"feat/sample-workstream\"\n"
            f"{cards}{audits}{triggers}{returns}"
        )
        (project / ROUTER_BOARD).write_text(board)

    def test_split_two_outcome_trajectory_to_close(self) -> None:
        temp, project = self.copy_fixture()
        try:
            base = (project / "implementation" / "workstreams"
                    / "sample-workstream")
            evidence = base / "evidence" / "M01-T04-core.md"
            evidence.parent.mkdir(parents=True, exist_ok=True)
            evidence.write_text("# Preserved core evidence\n")
            self._write_card_file(project, "M01-T05", "residual retry core")
            self._write_card_file(project, "M01-T07", "residual backoff")
            self.write_board(project, original_status="in_progress")
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution_prep", "M01-T04"),
            )
            self.assertIn("pending", routed.reason)
            self.write_board(project, original_status="in_progress",
                             return_state="residual_bound",
                             anchor_status="planned")
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution_prep", "M01-T04"),
            )
            self.assertIn("handoff", routed.reason)
            self.write_board(project, original_status="returned",
                             return_state="residual_bound",
                             anchor_status="planned",
                             handoff_trigger_state="consumed")
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "execution_prep"),
            )
            self.write_board(project, original_status="returned",
                             return_state="residual_bound",
                             anchor_status="ready",
                             handoff_trigger_state="consumed")
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution_prep", "M01-T05"),
            )
            self.write_board(project, original_status="returned",
                             return_state="residual_bound",
                             anchor_status="in_progress",
                             handoff_trigger_state="consumed")
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution", "M01-T05"),
            )
            self.write_board(project, original_status="returned",
                             return_state="residual_bound",
                             anchor_status="done",
                             handoff_trigger_state="consumed")
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "execution_prep"),
            )
            self.assertIn("retry-backoff", routed.reason)
            self.assertIn("after-M01-T05", routed.reason)
            self.write_board(project, original_status="returned",
                             return_state="residual_bound",
                             anchor_status="done",
                             handoff_trigger_state="consumed",
                             jit_trigger_state="consumed")
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "execution_prep"),
            )
            self.assertIn("bind the trigger", routed.reason)
            self.write_board(project, original_status="returned",
                             return_state="residual_bound",
                             anchor_status="done",
                             r3_status="planned",
                             handoff_trigger_state="consumed",
                             jit_trigger_state="consumed",
                             resolutions=[("after-M01-T05", "M01-T07")])
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "execution_prep"),
            )
            self.write_board(project, original_status="returned",
                             return_state="residual_bound",
                             anchor_status="done",
                             r3_status="ready",
                             handoff_trigger_state="consumed",
                             jit_trigger_state="consumed",
                             resolutions=[("after-M01-T05", "M01-T07")])
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution_prep", "M01-T07"),
            )
            self.write_board(project, original_status="returned",
                             return_state="residual_bound",
                             anchor_status="done",
                             r3_status="in_progress",
                             handoff_trigger_state="consumed",
                             jit_trigger_state="consumed",
                             resolutions=[("after-M01-T05", "M01-T07")])
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution", "M01-T07"),
            )
            self.write_board(project, original_status="returned",
                             return_state="residual_bound",
                             anchor_status="done",
                             r3_status="done",
                             handoff_trigger_state="consumed",
                             jit_trigger_state="consumed",
                             resolutions=[("after-M01-T05", "M01-T07")])
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "close"),
            )
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
