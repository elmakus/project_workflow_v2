from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.live_consumer_contract import (
    ADMISSION_DECISION_FIELDS,
    LIVE_CONSUMER_READINESS_STATES,
    LiveConsumerError,
    parse_admission_decision,
    require_admitted_trigger_consumption,
    validate_live_consumer_declaration,
    validate_live_consumer_gates,
    verify_admission_decision,
    verify_live_consumer_records,
)
from tools.router import select_route
from tools.state_contract import ValidationError, read_toml, validate_board

ROOT = Path(__file__).resolve().parents[1]
VALID = ROOT / "tests" / "fixtures" / "state" / "valid"
ROUTER_FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
ROUTER_MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"

WORKSTREAM_ID = "sample-workstream"
TRIGGER_ID = "after-M01-T01"
AFTER_CARD = "M01-T01"

AUTHORITY_REPOSITORY = "elmakus/project_workflow_v2"
PLANNING_SUBJECT_COMMIT = "e" * 40
PLANNING_SUBJECT_BLOB = "f" * 40
PLANNING_SUBJECT_PATH = "planning/PWV21_POLICY_KERNEL_MASTER_PLAN_P6.md"
# The corrected-authority selection must be the exact current accepted
# Planning subject; fixtures align the pin/admission authority triple with it.
AUTHORITY_COMMIT = PLANNING_SUBJECT_COMMIT
AUTHORITY_BLOB = PLANNING_SUBJECT_BLOB
AUTHORITY_PATH = PLANNING_SUBJECT_PATH

DEFINITION_PATH = f"implementation/workstreams/{WORKSTREAM_ID}/DEFINITION.toml"
DEFINITION_REVISION = "R3"
PLANNING_PATH = f"implementation/workstreams/{WORKSTREAM_ID}/PLANNING.toml"
PLANNING_REVISION = "P6"
PLANNING_CYCLE = 1
PLAN_REVIEW_PATH = f"implementation/workstreams/{WORKSTREAM_ID}/PLAN_REVIEW.toml"
PLAN_REVIEW_ATTEMPT = "PLAN-R01"

PREDECESSOR_PATH = f"implementation/workstreams/{WORKSTREAM_ID}/results/M01-T01.md"
PREDECESSOR_COMMIT = "c" * 40
PREDECESSOR_BLOB = "d" * 40

REVIEW_PATH = f"implementation/workstreams/{WORKSTREAM_ID}/reviews/M01-T01-R02.toml"
REVIEW_ATTEMPT = "M01-T01-R02"
MILESTONE_PATH = f"implementation/workstreams/{WORKSTREAM_ID}/reviews/M01-MILESTONE-R02.toml"
MILESTONE_ATTEMPT = "M01-MILESTONE-R02"

ADMISSION_PATH = f"implementation/workstreams/{WORKSTREAM_ID}/readiness/after-M01-T01.toml"


def _admission_citation(
    stage: str = "execution_prep",
    path: str | None = None,
    record_class: str = "live_consumer_admission",
) -> dict:
    return {
        "stage": stage,
        "record": {
            "class": record_class,
            "path": path or ADMISSION_PATH,
        },
    }


def _authority_pin(
    repository: str = AUTHORITY_REPOSITORY,
    commit: str = AUTHORITY_COMMIT,
    path: str = AUTHORITY_PATH,
    blob: str = AUTHORITY_BLOB,
) -> dict:
    return {
        "repository": repository,
        "commit": commit,
        "path": path,
        "blob": blob,
    }


def _live_consumer(
    intended: bool = True,
    readiness: str = "pending",
    admission: dict | None = None,
    authority: dict | None | bool = None,
) -> dict:
    table: dict = {"intended": intended}
    if intended is False:
        return table
    table["readiness"] = readiness
    if authority is None:
        table["authority"] = _authority_pin()
    elif authority is not False:
        table["authority"] = authority
    if admission is not None:
        table["admission"] = admission
    return table


def _trigger(
    trigger_id: str = TRIGGER_ID,
    after_card: str = AFTER_CARD,
    state: str = "satisfied",
    live_consumer: dict | None = None,
) -> dict:
    record: dict = {
        "id": trigger_id,
        "after_card": after_card,
        "state": state,
        "condition": "Downstream live-consumer test depends on the predecessor result.",
    }
    if live_consumer is not None:
        record["live_consumer"] = live_consumer
    return record


def _admission_text(**overrides: str) -> str:
    fields = {
        "trigger_id": TRIGGER_ID,
        "authority_repository": AUTHORITY_REPOSITORY,
        "authority_commit": AUTHORITY_COMMIT,
        "authority_path": AUTHORITY_PATH,
        "authority_blob": AUTHORITY_BLOB,
        "definition_path": DEFINITION_PATH,
        "definition_revision": DEFINITION_REVISION,
        "planning_path": PLANNING_PATH,
        "planning_revision": PLANNING_REVISION,
        "plan_review_path": PLAN_REVIEW_PATH,
        "plan_review_attempt": PLAN_REVIEW_ATTEMPT,
        "review_path": REVIEW_PATH,
        "review_attempt": REVIEW_ATTEMPT,
        "predecessor_path": PREDECESSOR_PATH,
        "predecessor_commit": PREDECESSOR_COMMIT,
        "predecessor_blob": PREDECESSOR_BLOB,
        "milestone_path": MILESTONE_PATH,
        "milestone_attempt": MILESTONE_ATTEMPT,
        "decision": "admitted",
    }
    fields.update(overrides)
    lines = [f'{key} = "{value}"' for key, value in sorted(fields.items())]
    return "\n".join(lines) + "\n"


def _definition_toml(revision: str = DEFINITION_REVISION, state: str = "green") -> str:
    return (
        f'workstream_id = "{WORKSTREAM_ID}"\n'
        f'revision = "{revision}"\n'
        f'state = "{state}"\n'
    )


def _planning_toml(
    revision: str = PLANNING_REVISION,
    state: str = "approved",
    subject_commit: str = PLANNING_SUBJECT_COMMIT,
    subject_blob: str = PLANNING_SUBJECT_BLOB,
    subject_path: str = PLANNING_SUBJECT_PATH,
) -> str:
    return (
        f'workstream_id = "{WORKSTREAM_ID}"\n'
        f'revision = "{revision}"\n'
        f'cycle = {PLANNING_CYCLE}\n'
        f'state = "{state}"\n'
        "[subject]\n"
        f'repository = "{AUTHORITY_REPOSITORY}"\n'
        f'commit = "{subject_commit}"\n'
        f'path = "{subject_path}"\n'
        f'blob = "{subject_blob}"\n'
    )


def _plan_review_toml(
    attempt: str = PLAN_REVIEW_ATTEMPT,
    verdict: str = "green",
    plan_revision: str = PLANNING_REVISION,
    planning_cycle: int = PLANNING_CYCLE,
    subject_commit: str = PLANNING_SUBJECT_COMMIT,
    subject_blob: str = PLANNING_SUBJECT_BLOB,
    subject_path: str = PLANNING_SUBJECT_PATH,
) -> str:
    return (
        f'workstream_id = "{WORKSTREAM_ID}"\n'
        f'attempt = "{attempt}"\n'
        f'verdict = "{verdict}"\n'
        f'plan_revision = "{plan_revision}"\n'
        f'planning_cycle = {planning_cycle}\n'
        "[subject]\n"
        f'repository = "{AUTHORITY_REPOSITORY}"\n'
        f'commit = "{subject_commit}"\n'
        f'path = "{subject_path}"\n'
        f'blob = "{subject_blob}"\n'
    )


def _review_toml(
    attempt: str = REVIEW_ATTEMPT,
    verdict: str = "green",
    card_id: str = AFTER_CARD,
) -> str:
    return (
        f'workstream_id = "{WORKSTREAM_ID}"\n'
        f'card_id = "{card_id}"\n'
        f'attempt = "{attempt}"\n'
        f'verdict = "{verdict}"\n'
        "[subject]\n"
        f'repository = "{AUTHORITY_REPOSITORY}"\n'
        f'commit = "{PREDECESSOR_COMMIT}"\n'
        f'path = "{PREDECESSOR_PATH}"\n'
        f'blob = "{PREDECESSOR_BLOB}"\n'
        "[acceptance]\n"
        'class = "task_card"\n'
        f'path = "implementation/workstreams/{WORKSTREAM_ID}/cards/{card_id}.md"\n'
    )


def _milestone_toml(
    attempt: str = MILESTONE_ATTEMPT,
    verdict: str = "green",
    scope: str | None = "milestone",
    acceptance_class: str | None = "authority",
    acceptance_path: str | None = None,
    card_id: str | None = None,
) -> str:
    scope_line = f'review_scope = "{scope}"\n' if scope is not None else ""
    card_line = f'card_id = "{card_id}"\n' if card_id is not None else ""
    if acceptance_class is None:
        acceptance_block = ""
    else:
        acceptance_block = (
            "[acceptance]\n"
            f'class = "{acceptance_class}"\n'
            f'path = "{acceptance_path or PLANNING_SUBJECT_PATH}"\n'
        )
    return (
        f'workstream_id = "{WORKSTREAM_ID}"\n'
        f"{card_line}"
        f'attempt = "{attempt}"\n'
        f'verdict = "{verdict}"\n'
        f"{scope_line}"
        "[subject]\n"
        f'repository = "{AUTHORITY_REPOSITORY}"\n'
        f'commit = "{PREDECESSOR_COMMIT}"\n'
        f'path = "{PREDECESSOR_PATH}"\n'
        f'blob = "{PREDECESSOR_BLOB}"\n'
        f"{acceptance_block}"
    )


def _bare_green_toml() -> str:
    """Markerless hand-forged GREEN record: attempt/verdict/subject only."""
    return (
        f'workstream_id = "{WORKSTREAM_ID}"\n'
        f'attempt = "{MILESTONE_ATTEMPT}"\n'
        'verdict = "green"\n'
        "[subject]\n"
        f'repository = "{AUTHORITY_REPOSITORY}"\n'
        f'commit = "{PREDECESSOR_COMMIT}"\n'
        f'path = "{PREDECESSOR_PATH}"\n'
        f'blob = "{PREDECESSOR_BLOB}"\n'
    )


def _m02_shaped_milestone_toml() -> str:
    """Milestone record with the exact historical M02 terminal shape.

    Mirrors ``M02-MILESTONE-R02.toml`` at the pinned corpus commit: no
    ``review_scope``/``review_kind`` markers, no ``card_id``, authority
    acceptance bound to the accepted plan, plus evidence and independence
    provenance. Adapted only in workstream/attempt/subject identity.
    """
    return (
        f'workstream_id = "{WORKSTREAM_ID}"\n'
        f'attempt = "{MILESTONE_ATTEMPT}"\n'
        'verdict = "green"\n'
        f'evidence_path = "implementation/workstreams/{WORKSTREAM_ID}/evidence/MS-R02.md"\n'
        "\n"
        "[subject]\n"
        'class = "git_blob"\n'
        f'repository = "{AUTHORITY_REPOSITORY}"\n'
        f'commit = "{PREDECESSOR_COMMIT}"\n'
        f'path = "{PREDECESSOR_PATH}"\n'
        f'blob = "{PREDECESSOR_BLOB}"\n'
        "\n"
        "[acceptance]\n"
        'class = "authority"\n'
        f'path = "{PLANNING_SUBJECT_PATH}"\n'
        "\n"
        "[independence]\n"
        "materially_produced_or_repaired_subject = false\n"
        'basis = "Fresh independent Milestone re-review from exact authority."\n'
    )


def _board_with_triggers(triggers: list[dict]) -> dict:
    return {
        "workstream_id": WORKSTREAM_ID,
        "cards": [
            {
                "id": AFTER_CARD,
                "status": "done",
                "contract": {
                    "class": "task_card",
                    "path": f"implementation/workstreams/{WORKSTREAM_ID}/cards/{AFTER_CARD}.md",
                },
                "result": {
                    "class": "result",
                    "path": PREDECESSOR_PATH,
                    "commit": PREDECESSOR_COMMIT,
                    "blob": PREDECESSOR_BLOB,
                },
            }
        ],
        "jit_triggers": triggers,
    }


def _readers(
    admission: str | None = None,
    definition: str | None = None,
    planning: str | None = None,
    plan_review: str | None = None,
    review: str | None = None,
    milestone: str | None = None,
    predecessor: str | None = "# result\n",
    git_blob: str | None = AUTHORITY_BLOB,
):
    files = {
        ADMISSION_PATH: _admission_text() if admission is None else admission,
        DEFINITION_PATH: _definition_toml() if definition is None else definition,
        PLANNING_PATH: _planning_toml() if planning is None else planning,
        PLAN_REVIEW_PATH: _plan_review_toml() if plan_review is None else plan_review,
        REVIEW_PATH: _review_toml() if review is None else review,
        MILESTONE_PATH: _milestone_toml() if milestone is None else milestone,
        PREDECESSOR_PATH: predecessor,
    }

    def record_reader(path: str) -> str | None:
        return files.get(path)

    def git_reader(repository: str, commit: str, path: str) -> str | None:
        if (
            repository == AUTHORITY_REPOSITORY
            and commit == AUTHORITY_COMMIT
            and path == AUTHORITY_PATH
        ):
            return git_blob
        return None

    return record_reader, git_reader


class DeclarationTests(unittest.TestCase):
    def test_readiness_vocabulary_is_exact(self) -> None:
        self.assertEqual(
            LIVE_CONSUMER_READINESS_STATES, frozenset({"pending", "admitted"})
        )
        self.assertEqual(len(ADMISSION_DECISION_FIELDS), 19)

    def test_absent_declaration_is_ordinary_and_never_blocks(self) -> None:
        trigger = _trigger()
        self.assertIsNone(
            validate_live_consumer_declaration(
                trigger, WORKSTREAM_ID, "task_board.jit_triggers[0].live_consumer"
            )
        )
        self.assertEqual(validate_live_consumer_gates([trigger], WORKSTREAM_ID), {})

    def test_explicit_ordinary_never_blocks(self) -> None:
        trigger = _trigger(live_consumer={"intended": False})
        validated = validate_live_consumer_declaration(
            trigger, WORKSTREAM_ID, "task_board.jit_triggers[0].live_consumer"
        )
        self.assertEqual(validated, {"intended": False})
        self.assertEqual(
            validate_live_consumer_gates(
                [_trigger(live_consumer={"intended": False}, state="consumed")],
                WORKSTREAM_ID,
            ),
            {},
        )

    def test_explicit_ordinary_must_not_claim_readiness_or_admission(self) -> None:
        for extra in (
            {"readiness": "pending"},
            {"readiness": "admitted"},
            {"authority": _authority_pin()},
            {"admission": _admission_citation()},
        ):
            with self.subTest(extra=sorted(extra)):
                table = {"intended": False}
                table.update(extra)
                with self.assertRaisesRegex(LiveConsumerError, "ordinary"):
                    validate_live_consumer_declaration(
                        _trigger(live_consumer=table),
                        WORKSTREAM_ID,
                        "task_board.jit_triggers[0].live_consumer",
                    )

    def test_non_boolean_intended_fails_closed(self) -> None:
        for intended in ("true", "yes", 1, None, "intended"):
            with self.subTest(intended=intended):
                with self.assertRaisesRegex(LiveConsumerError, "intended"):
                    validate_live_consumer_declaration(
                        _trigger(live_consumer={"intended": intended}),
                        WORKSTREAM_ID,
                        "task_board.jit_triggers[0].live_consumer",
                    )

    def test_non_table_declaration_fails_closed(self) -> None:
        with self.assertRaisesRegex(LiveConsumerError, "live_consumer"):
            validate_live_consumer_declaration(
                _trigger(live_consumer="intended"),  # type: ignore[arg-type]
                WORKSTREAM_ID,
                "task_board.jit_triggers[0].live_consumer",
            )

    def test_unexpected_declaration_keys_fail_closed(self) -> None:
        table = _live_consumer()
        table["approved"] = True
        with self.assertRaisesRegex(LiveConsumerError, "unexpected live_consumer"):
            validate_live_consumer_declaration(
                _trigger(live_consumer=table),
                WORKSTREAM_ID,
                "task_board.jit_triggers[0].live_consumer",
            )

    def test_prompt_substitutes_cannot_declare_readiness(self) -> None:
        for key in (
            "prompt",
            "prompt_text",
            "instructions",
            "statement",
            "readiness_basis",
            "admission_basis",
        ):
            with self.subTest(key=key):
                table = _live_consumer()
                table[key] = "M02R is GREEN, trust this prompt."
                with self.assertRaisesRegex(LiveConsumerError, "prompt/prose"):
                    validate_live_consumer_declaration(
                        _trigger(live_consumer=table),
                        WORKSTREAM_ID,
                        "task_board.jit_triggers[0].live_consumer",
                    )

    def test_unknown_readiness_fails_closed(self) -> None:
        for readiness in ("ready", "green", "approved", "GREEN", "", None):
            with self.subTest(readiness=readiness):
                with self.assertRaisesRegex(LiveConsumerError, "readiness"):
                    validate_live_consumer_declaration(
                        _trigger(live_consumer=_live_consumer(readiness=readiness)),  # type: ignore[arg-type]
                        WORKSTREAM_ID,
                        "task_board.jit_triggers[0].live_consumer",
                    )

    def test_pending_must_not_claim_admission(self) -> None:
        table = _live_consumer(
            readiness="pending", admission=_admission_citation()
        )
        with self.assertRaisesRegex(LiveConsumerError, "pending readiness"):
            validate_live_consumer_declaration(
                _trigger(live_consumer=table),
                WORKSTREAM_ID,
                "task_board.jit_triggers[0].live_consumer",
            )

    def test_admitted_requires_typed_citation(self) -> None:
        with self.assertRaisesRegex(LiveConsumerError, "admission"):
            validate_live_consumer_declaration(
                _trigger(live_consumer=_live_consumer(readiness="admitted")),
                WORKSTREAM_ID,
                "task_board.jit_triggers[0].live_consumer",
            )

    def test_admitted_validates_citation_shape(self) -> None:
        validated = validate_live_consumer_declaration(
            _trigger(
                live_consumer=_live_consumer(
                    readiness="admitted",
                    admission=_admission_citation(),
                )
            ),
            WORKSTREAM_ID,
            "task_board.jit_triggers[0].live_consumer",
        )
        assert validated is not None
        self.assertEqual(validated["readiness"], "admitted")
        self.assertEqual(
            validated["admission"]["record"],
            {"class": "live_consumer_admission", "path": ADMISSION_PATH},
        )
        self.assertEqual(
            validated["authority"],
            {
                "repository": AUTHORITY_REPOSITORY,
                "commit": AUTHORITY_COMMIT,
                "path": AUTHORITY_PATH,
                "blob": AUTHORITY_BLOB,
            },
        )

    def test_worker_stage_cannot_admit(self) -> None:
        for stage in ("worker", "worker_1", "Worker"):
            with self.subTest(stage=stage):
                table = _live_consumer(
                    readiness="admitted",
                    admission=_admission_citation(stage=stage),
                )
                with self.assertRaisesRegex(LiveConsumerError, "Worker"):
                    validate_live_consumer_declaration(
                        _trigger(live_consumer=table),
                        WORKSTREAM_ID,
                        "task_board.jit_triggers[0].live_consumer",
                    )

    def test_unknown_admitting_stage_fails_closed(self) -> None:
        table = _live_consumer(
            readiness="admitted",
            admission=_admission_citation(stage="planning"),
        )
        with self.assertRaisesRegex(LiveConsumerError, "admitting stage"):
            validate_live_consumer_declaration(
                _trigger(live_consumer=table),
                WORKSTREAM_ID,
                "task_board.jit_triggers[0].live_consumer",
            )

    def test_unknown_record_class_fails_closed(self) -> None:
        for record_class in (
            "finding_reconciliation",
            "finding_acceptance",
            "evidence",
            "review_attempt",
        ):
            with self.subTest(record_class=record_class):
                table = _live_consumer(
                    readiness="admitted",
                    admission=_admission_citation(record_class=record_class),
                )
                with self.assertRaisesRegex(LiveConsumerError, "record class"):
                    validate_live_consumer_declaration(
                        _trigger(live_consumer=table),
                        WORKSTREAM_ID,
                        "task_board.jit_triggers[0].live_consumer",
                    )

    def test_tracker_record_path_fails_closed(self) -> None:
        for path in ("owner/repo#12", "https://github.com/owner/repo/issues/12"):
            with self.subTest(path=path):
                table = _live_consumer(
                    readiness="admitted",
                    admission=_admission_citation(path=path),
                )
                with self.assertRaisesRegex(LiveConsumerError, "tracker"):
                    validate_live_consumer_declaration(
                        _trigger(live_consumer=table),
                        WORKSTREAM_ID,
                        "task_board.jit_triggers[0].live_consumer",
                    )

    def test_wrong_source_record_path_fails_closed(self) -> None:
        table = _live_consumer(
            readiness="admitted",
            admission=_admission_citation(
                path=f"implementation/workstreams/{WORKSTREAM_ID}/findings/x.toml"
            ),
        )
        with self.assertRaisesRegex(LiveConsumerError, "readiness"):
            validate_live_consumer_declaration(
                _trigger(live_consumer=table),
                WORKSTREAM_ID,
                "task_board.jit_triggers[0].live_consumer",
            )

    def test_admission_prompt_keys_fail_closed(self) -> None:
        citation = _admission_citation()
        citation["statement"] = "Execution Prep admits per prompt."
        table = _live_consumer(readiness="admitted", admission=citation)
        with self.assertRaisesRegex(LiveConsumerError, "prompt/prose"):
            validate_live_consumer_declaration(
                _trigger(live_consumer=table),
                WORKSTREAM_ID,
                "task_board.jit_triggers[0].live_consumer",
            )

    def test_intended_requires_authority_pin(self) -> None:
        for readiness in ("pending", "admitted"):
            with self.subTest(readiness=readiness):
                table = _live_consumer(readiness=readiness, authority=False)
                if readiness == "admitted":
                    table["admission"] = _admission_citation()
                with self.assertRaisesRegex(LiveConsumerError, "authority pin"):
                    validate_live_consumer_declaration(
                        _trigger(live_consumer=table),
                        WORKSTREAM_ID,
                        "task_board.jit_triggers[0].live_consumer",
                    )

    def test_authority_pin_shape_negatives_fail_closed(self) -> None:
        cases = [
            ("non-table", "authority pin must be a table", "workflow/REVIEW.md"),
            ("tracker-path", "tracker", "owner/repo#12"),
            ("tracker-url", "tracker", "https://github.com/owner/repo/x.md"),
            ("outside-roots", "wrong-source authority pin", "evidence/note.md"),
            ("absolute", "wrong-source authority pin", "/workflow/REVIEW.md"),
            ("traversal", "wrong-source authority pin", "workflow/../x.md"),
        ]
        for name, message, path in cases:
            with self.subTest(name=name):
                pin = path if name == "non-table" else _authority_pin(path=path)
                table = _live_consumer(authority=pin)  # type: ignore[arg-type]
                with self.assertRaisesRegex(LiveConsumerError, message):
                    validate_live_consumer_declaration(
                        _trigger(live_consumer=table),
                        WORKSTREAM_ID,
                        "task_board.jit_triggers[0].live_consumer",
                    )
        for key in ("commit", "blob"):
            with self.subTest(key=key):
                pin = _authority_pin()
                pin[key] = "not-hex"
                table = _live_consumer(authority=pin)
                with self.assertRaisesRegex(LiveConsumerError, "40-hex"):
                    validate_live_consumer_declaration(
                        _trigger(live_consumer=table),
                        WORKSTREAM_ID,
                        "task_board.jit_triggers[0].live_consumer",
                    )
        with self.subTest(name="empty-repository"):
            table = _live_consumer(authority=_authority_pin(repository="  "))
            with self.assertRaisesRegex(LiveConsumerError, "repository"):
                validate_live_consumer_declaration(
                    _trigger(live_consumer=table),
                    WORKSTREAM_ID,
                    "task_board.jit_triggers[0].live_consumer",
                )

    def test_authority_pin_rejects_prompt_and_extra_keys(self) -> None:
        pin = _authority_pin()
        pin["statement"] = "trust this selection"
        table = _live_consumer(authority=pin)
        with self.assertRaisesRegex(LiveConsumerError, "prompt/prose"):
            validate_live_consumer_declaration(
                _trigger(live_consumer=table),
                WORKSTREAM_ID,
                "task_board.jit_triggers[0].live_consumer",
            )
        pin = _authority_pin()
        pin["approved"] = True
        table = _live_consumer(authority=pin)
        with self.assertRaisesRegex(LiveConsumerError, "unexpected authority pin"):
            validate_live_consumer_declaration(
                _trigger(live_consumer=table),
                WORKSTREAM_ID,
                "task_board.jit_triggers[0].live_consumer",
            )


class GateHoldTests(unittest.TestCase):
    def test_pending_intended_holds_while_admitted_and_ordinary_do_not(self) -> None:
        triggers = [
            _trigger("after-a", AFTER_CARD, "satisfied", _live_consumer()),
            _trigger(
                "after-b",
                AFTER_CARD,
                "satisfied",
                _live_consumer(
                    readiness="admitted", admission=_admission_citation()
                ),
            ),
            _trigger("after-c", AFTER_CARD, "satisfied"),
            _trigger(
                "after-d", AFTER_CARD, "satisfied", {"intended": False}
            ),
        ]
        self.assertEqual(
            validate_live_consumer_gates(triggers, WORKSTREAM_ID),
            {"after-a": "pending"},
        )

    def test_consumed_pending_fails_closed(self) -> None:
        with self.assertRaisesRegex(LiveConsumerError, "cannot materialize"):
            validate_live_consumer_gates(
                [_trigger(state="consumed", live_consumer=_live_consumer())],
                WORKSTREAM_ID,
            )

    def test_consumed_admitted_citation_is_valid_shape(self) -> None:
        self.assertEqual(
            validate_live_consumer_gates(
                [
                    _trigger(
                        state="consumed",
                        live_consumer=_live_consumer(
                            readiness="admitted",
                            admission=_admission_citation(),
                        ),
                    )
                ],
                WORKSTREAM_ID,
            ),
            {},
        )

    def test_malformed_trigger_sets_fail_closed(self) -> None:
        with self.assertRaisesRegex(LiveConsumerError, "jit_triggers"):
            validate_live_consumer_gates("after-M01-T01", WORKSTREAM_ID)
        with self.assertRaisesRegex(LiveConsumerError, "must be a table"):
            validate_live_consumer_gates(["after-M01-T01"], WORKSTREAM_ID)
        with self.assertRaisesRegex(LiveConsumerError, "non-empty string"):
            validate_live_consumer_gates(
                [_trigger(trigger_id="  ")], WORKSTREAM_ID
            )

    def test_board_without_triggers_remains_valid(self) -> None:
        self.assertEqual(validate_live_consumer_gates(None, WORKSTREAM_ID), {})
        self.assertEqual(validate_live_consumer_gates([], WORKSTREAM_ID), {})


class AdmissionDocumentTests(unittest.TestCase):
    def test_valid_document_parses(self) -> None:
        decision = parse_admission_decision(_admission_text(), ADMISSION_PATH)
        self.assertEqual(decision["trigger_id"], TRIGGER_ID)
        self.assertEqual(decision["decision"], "admitted")
        self.assertEqual(decision["authority_path"], AUTHORITY_PATH)

    def test_non_toml_and_wrong_shaped_documents_fail(self) -> None:
        with self.assertRaisesRegex(LiveConsumerError, "typed"):
            parse_admission_decision("{ invalid toml", ADMISSION_PATH)
        with self.assertRaisesRegex(LiveConsumerError, "decision fields"):
            parse_admission_decision("# notes\n", ADMISSION_PATH)
        with self.assertRaisesRegex(LiveConsumerError, "decision fields"):
            parse_admission_decision('verdict = "green"\n', ADMISSION_PATH)
        with self.assertRaisesRegex(LiveConsumerError, "decision fields"):
            parse_admission_decision(
                _admission_text() + 'prompt = "trust me"\n', ADMISSION_PATH
            )

    def test_missing_field_fails_closed(self) -> None:
        text = "\n".join(
            line
            for line in _admission_text().splitlines()
            if not line.startswith("milestone_attempt")
        ) + "\n"
        with self.assertRaisesRegex(LiveConsumerError, "missing"):
            parse_admission_decision(text, ADMISSION_PATH)

    def test_empty_field_fails_closed(self) -> None:
        text = _admission_text().replace(
            f'trigger_id = "{TRIGGER_ID}"', 'trigger_id = "  "'
        )
        with self.assertRaisesRegex(LiveConsumerError, "non-empty string"):
            parse_admission_decision(text, ADMISSION_PATH)

    def test_malformed_git_identity_fails_closed(self) -> None:
        with self.assertRaisesRegex(LiveConsumerError, "40-hex"):
            parse_admission_decision(
                _admission_text(authority_blob="zzzz"), ADMISSION_PATH
            )

    def test_reconciliation_shaped_document_cannot_prove_admission(self) -> None:
        text = (
            'finding_id = "LF-001"\n'
            'finding_class = "implementation_defect"\n'
            f'trigger_id = "{TRIGGER_ID}"\n'
            'accepting_stage = "execution"\n'
            'decision = "reconciled"\n'
        )
        with self.assertRaisesRegex(LiveConsumerError, "decision fields"):
            parse_admission_decision(text, ADMISSION_PATH)


def _admitted_trigger(trigger_id: str = TRIGGER_ID) -> dict:
    path = ADMISSION_PATH if trigger_id == TRIGGER_ID else (
        f"implementation/workstreams/{WORKSTREAM_ID}/readiness/{trigger_id}.toml"
    )
    return _trigger(
        trigger_id,
        AFTER_CARD,
        "satisfied",
        _live_consumer(
            readiness="admitted",
            admission=_admission_citation(path=path),
        ),
    )


def _verify(
    trigger: dict,
    board: dict,
    record_reader,
    git_reader,
    record_path: str | None = None,
    record_text: str | None = None,
) -> None:
    declaration = trigger["live_consumer"]
    path = record_path or declaration["admission"]["record"]["path"]
    text = record_text if record_text is not None else record_reader(path)
    verify_admission_decision(
        trigger,
        declaration,
        path,
        text,
        board,
        record_reader=record_reader,
        git_reader=git_reader,
    )


class AdmissionVerificationTests(unittest.TestCase):
    def test_exact_complete_gates_verify(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        record_reader, git_reader = _readers()
        _verify(trigger, board, record_reader, git_reader)
        verify_live_consumer_records(
            board, record_reader=record_reader, git_reader=git_reader
        )
        self.assertEqual(
            require_admitted_trigger_consumption(
                board, TRIGGER_ID,
                record_reader=record_reader, git_reader=git_reader,
            ),
            TRIGGER_ID,
        )

    def test_unreadable_admission_fails_closed(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        _, git_reader = _readers()

        def missing_reader(path: str) -> str | None:
            return None

        with self.assertRaisesRegex(LiveConsumerError, "cannot be read back"):
            verify_admission_decision(
                trigger,
                trigger["live_consumer"],
                ADMISSION_PATH,
                None,
                board,
                record_reader=missing_reader,
                git_reader=git_reader,
            )

    def test_decision_for_another_trigger_fails(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        record_reader, git_reader = _readers(
            admission=_admission_text(trigger_id="after-other")
        )
        with self.assertRaisesRegex(LiveConsumerError, "unrelated decisions"):
            _verify(trigger, board, record_reader, git_reader)

    def test_non_admitted_decision_cannot_release(self) -> None:
        for decision in ("green", "accepted", "approved", "reconciled"):
            with self.subTest(decision=decision):
                trigger = _admitted_trigger()
                board = _board_with_triggers([trigger])
                record_reader, git_reader = _readers(
                    admission=_admission_text(decision=decision)
                )
                with self.assertRaisesRegex(LiveConsumerError, "explicit admitted"):
                    _verify(trigger, board, record_reader, git_reader)

    def test_authority_outside_accepted_roots_fails(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        record_reader, git_reader = _readers(
            admission=_admission_text(authority_path="evidence/note.md")
        )
        with self.assertRaisesRegex(LiveConsumerError, "wrong-source authority"):
            _verify(trigger, board, record_reader, git_reader)

    def test_authority_tracker_pointer_fails(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        record_reader, git_reader = _readers(
            admission=_admission_text(
                authority_path="https://github.com/owner/repo/issues/12"
            )
        )
        with self.assertRaisesRegex(LiveConsumerError, "tracker"):
            _verify(trigger, board, record_reader, git_reader)

    def test_authority_pin_must_resolve_in_git(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        record_reader, git_reader = _readers(git_blob="0" * 40)
        with self.assertRaisesRegex(LiveConsumerError, "pinned blob"):
            _verify(trigger, board, record_reader, git_reader)
        record_reader, git_reader = _readers(git_blob=None)
        with self.assertRaisesRegex(LiveConsumerError, "pinned blob"):
            _verify(trigger, board, record_reader, git_reader)

    def test_admission_must_reproduce_board_pin_exactly(self) -> None:
        for field, stale in (
            ("authority_repository", "other/repo"),
            ("authority_commit", "0" * 40),
            ("authority_path", "workflow/ROUTER.md"),
            ("authority_blob", "0" * 40),
        ):
            with self.subTest(field=field):
                trigger = _admitted_trigger()
                board = _board_with_triggers([trigger])
                record_reader, git_reader = _readers(
                    admission=_admission_text(**{field: stale})
                )
                with self.assertRaisesRegex(LiveConsumerError, "stale authority"):
                    _verify(trigger, board, record_reader, git_reader)

    def test_unrelated_in_roots_selection_fails_despite_agreement(self) -> None:
        # BOUNDARY class: board pin and admission agree on a readable
        # in-roots file that is not the accepted Planning subject.
        unrelated = _authority_pin(
            commit="9" * 40, path="workflow/UNRELATED.md", blob="8" * 40
        )
        trigger = _trigger(
            live_consumer=_live_consumer(
                readiness="admitted",
                admission=_admission_citation(),
                authority=unrelated,
            ),
        )
        board = _board_with_triggers([trigger])
        base_reader, _ = _readers()

        def record_reader(path: str) -> str | None:
            if path == ADMISSION_PATH:
                return _admission_text(
                    authority_commit="9" * 40,
                    authority_path="workflow/UNRELATED.md",
                    authority_blob="8" * 40,
                )
            return base_reader(path)

        def git_reader(repository: str, commit: str, path: str) -> str | None:
            if (
                repository == AUTHORITY_REPOSITORY
                and commit == "9" * 40
                and path == "workflow/UNRELATED.md"
            ):
                return "8" * 40
            return None

        with self.assertRaisesRegex(LiveConsumerError, "accepted Planning subject"):
            _verify(trigger, board, record_reader, git_reader)

    def test_pin_must_match_subject_repository_commit_path_blob(self) -> None:
        for field, rogue in (
            ("repository", "other/repo"),
            ("commit", "0" * 40),
            ("path", "workflow/REVIEW.md"),
            ("blob", "0" * 40),
        ):
            with self.subTest(field=field):
                pin = _authority_pin()
                pin[field] = rogue
                trigger = _trigger(
                    live_consumer=_live_consumer(
                        readiness="admitted",
                        admission=_admission_citation(),
                        authority=pin,
                    ),
                )
                board = _board_with_triggers([trigger])
                base_reader, _ = _readers()
                admission = _admission_text(
                    **{f"authority_{field}": rogue}
                )

                def record_reader(path: str, _a: str = admission) -> str | None:
                    if path == ADMISSION_PATH:
                        return _a
                    return base_reader(path)

                def git_reader(
                    repository: str, commit: str, path: str
                ) -> str | None:
                    if (
                        repository == pin["repository"]
                        and commit == pin["commit"]
                        and path == pin["path"]
                    ):
                        return pin["blob"]
                    return None

                with self.assertRaisesRegex(
                    LiveConsumerError, "accepted Planning subject"
                ):
                    _verify(trigger, board, record_reader, git_reader)

    def test_malformed_planning_subject_fails_closed(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        forged_planning = (
            f'workstream_id = "{WORKSTREAM_ID}"\n'
            f'revision = "{PLANNING_REVISION}"\n'
            f'cycle = {PLANNING_CYCLE}\n'
            'state = "approved"\n'
            "[subject]\n"
        )
        forged_review = (
            f'workstream_id = "{WORKSTREAM_ID}"\n'
            f'attempt = "{PLAN_REVIEW_ATTEMPT}"\n'
            'verdict = "green"\n'
            f'plan_revision = "{PLANNING_REVISION}"\n'
            f'planning_cycle = {PLANNING_CYCLE}\n'
            "[subject]\n"
        )
        record_reader, git_reader = _readers(
            planning=forged_planning, plan_review=forged_review
        )
        with self.assertRaisesRegex(LiveConsumerError, "subject is malformed"):
            _verify(trigger, board, record_reader, git_reader)

    def test_moved_selection_stales_old_admission_until_refreshed(self) -> None:
        # Replan P6 -> P7 advances the accepted subject; the old subject blob
        # remains readable in git.
        new_commit, new_blob = "1" * 40, "2" * 40
        replanned = _planning_toml(
            revision="P7", subject_commit=new_commit, subject_blob=new_blob
        )
        re_reviewed = _plan_review_toml(
            plan_revision="P7", subject_commit=new_commit, subject_blob=new_blob
        )

        def git_reader(repository: str, commit: str, path: str) -> str | None:
            if repository != AUTHORITY_REPOSITORY or path != AUTHORITY_PATH:
                return None
            return {
                AUTHORITY_COMMIT: AUTHORITY_BLOB,
                new_commit: new_blob,
            }.get(commit)

        def reader_for(admission: str):
            base, _ = _readers(
                planning=replanned,
                plan_review=re_reviewed,
                admission=admission,
            )
            return base

        # Phase 1: pin still cites the superseded subject -> wrong-source.
        stale_pin = _trigger(
            live_consumer=_live_consumer(
                readiness="admitted",
                admission=_admission_citation(),
                authority=_authority_pin(),
            ),
        )
        board = _board_with_triggers([stale_pin])
        with self.assertRaisesRegex(
            LiveConsumerError, "accepted Planning subject"
        ):
            _verify(
                stale_pin,
                board,
                reader_for(_admission_text(planning_revision="P7")),
                git_reader,
            )

        # Phase 2: pin moved to the new subject but the admission still cites
        # the old authority -> stale.
        moved_pin = _trigger(
            live_consumer=_live_consumer(
                readiness="admitted",
                admission=_admission_citation(),
                authority=_authority_pin(commit=new_commit, blob=new_blob),
            ),
        )
        board = _board_with_triggers([moved_pin])
        with self.assertRaisesRegex(LiveConsumerError, "stale authority"):
            _verify(
                moved_pin,
                board,
                reader_for(_admission_text(planning_revision="P7")),
                git_reader,
            )

        # Phase 3: refreshed admission citing the current subject releases.
        verify_admission_decision(
            moved_pin,
            moved_pin["live_consumer"],
            ADMISSION_PATH,
            _admission_text(
                planning_revision="P7",
                authority_commit=new_commit,
                authority_blob=new_blob,
            ),
            board,
            record_reader=reader_for(
                _admission_text(
                    planning_revision="P7",
                    authority_commit=new_commit,
                    authority_blob=new_blob,
                )
            ),
            git_reader=git_reader,
        )

    def test_definition_stale_not_green_or_unreadable_fails(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        record_reader, git_reader = _readers(
            definition=_definition_toml(revision="R2")
        )
        with self.assertRaisesRegex(LiveConsumerError, "stale Definition"):
            _verify(trigger, board, record_reader, git_reader)
        record_reader, git_reader = _readers(
            definition=_definition_toml(state="active")
        )
        with self.assertRaisesRegex(LiveConsumerError, "not GREEN"):
            _verify(trigger, board, record_reader, git_reader)
        files = {ADMISSION_PATH: _admission_text()}

        def missing_reader(path: str) -> str | None:
            return files.get(path)

        _, git_reader = _readers()
        with self.assertRaisesRegex(LiveConsumerError, "cannot be read back"):
            _verify(trigger, board, missing_reader, git_reader)

    def test_definition_wrong_source_fails(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        record_reader, git_reader = _readers(
            admission=_admission_text(
                definition_path="implementation/workstreams/other/DEFINITION.toml"
            )
        )
        with self.assertRaisesRegex(LiveConsumerError, "wrong-source"):
            _verify(trigger, board, record_reader, git_reader)

    def test_planning_stale_or_not_approved_fails(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        record_reader, git_reader = _readers(
            planning=_planning_toml(revision="P5")
        )
        with self.assertRaisesRegex(LiveConsumerError, "stale Planning"):
            _verify(trigger, board, record_reader, git_reader)
        record_reader, git_reader = _readers(
            planning=_planning_toml(state="frozen")
        )
        with self.assertRaisesRegex(LiveConsumerError, "not approved"):
            _verify(trigger, board, record_reader, git_reader)

    def test_plan_review_must_be_green_and_bind_exact_subject(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        record_reader, git_reader = _readers(
            plan_review=_plan_review_toml(verdict="red")
        )
        with self.assertRaisesRegex(LiveConsumerError, "not GREEN"):
            _verify(trigger, board, record_reader, git_reader)
        record_reader, git_reader = _readers(
            plan_review=_plan_review_toml(plan_revision="P5")
        )
        with self.assertRaisesRegex(LiveConsumerError, "another plan"):
            _verify(trigger, board, record_reader, git_reader)
        record_reader, git_reader = _readers(
            plan_review=_plan_review_toml(planning_cycle=2)
        )
        with self.assertRaisesRegex(LiveConsumerError, "another planning"):
            _verify(trigger, board, record_reader, git_reader)

    def test_predecessor_must_match_exact_done_result(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        record_reader, git_reader = _readers(
            admission=_admission_text(predecessor_blob="0" * 40)
        )
        with self.assertRaisesRegex(LiveConsumerError, "predecessor"):
            _verify(trigger, board, record_reader, git_reader)
        board["cards"][0]["result"]["blob"] = "0" * 40
        record_reader, git_reader = _readers()
        with self.assertRaisesRegex(LiveConsumerError, "predecessor"):
            _verify(trigger, board, record_reader, git_reader)

    def test_review_must_be_green_for_predecessor_subject(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        record_reader, git_reader = _readers(review=_review_toml(verdict="red"))
        with self.assertRaisesRegex(LiveConsumerError, "not GREEN"):
            _verify(trigger, board, record_reader, git_reader)
        record_reader, git_reader = _readers(
            review=_review_toml(card_id="M01-T02")
        )
        with self.assertRaisesRegex(LiveConsumerError, "another Card"):
            _verify(trigger, board, record_reader, git_reader)
        record_reader, git_reader = _readers(
            review=_review_toml(attempt="M01-T01-R01")
        )
        with self.assertRaisesRegex(LiveConsumerError, "stale review"):
            _verify(trigger, board, record_reader, git_reader)

    def test_milestone_must_be_green_milestone_scope_for_subject(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        record_reader, git_reader = _readers(
            milestone=_milestone_toml(verdict="red")
        )
        with self.assertRaisesRegex(LiveConsumerError, "Milestone.*not GREEN"):
            _verify(trigger, board, record_reader, git_reader)
        record_reader, git_reader = _readers(
            milestone=_milestone_toml(scope="card")
        )
        with self.assertRaisesRegex(LiveConsumerError, "review scope"):
            _verify(trigger, board, record_reader, git_reader)

    def test_milestone_cannot_reuse_card_review(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        record_reader, git_reader = _readers(
            admission=_admission_text(
                milestone_path=REVIEW_PATH, milestone_attempt=REVIEW_ATTEMPT
            )
        )
        with self.assertRaisesRegex(LiveConsumerError, "reuses the Card review"):
            _verify(trigger, board, record_reader, git_reader)

    def test_bare_green_record_cannot_satisfy_milestone_gate(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        record_reader, git_reader = _readers(milestone=_bare_green_toml())
        with self.assertRaisesRegex(LiveConsumerError, "typed acceptance"):
            _verify(trigger, board, record_reader, git_reader)

    def test_milestone_requires_authority_acceptance(self) -> None:
        for acceptance_class, message in (
            ("task_card", "acceptance class"),
            ("evidence", "acceptance class"),
            ("result", "acceptance class"),
        ):
            with self.subTest(acceptance_class=acceptance_class):
                trigger = _admitted_trigger()
                board = _board_with_triggers([trigger])
                record_reader, git_reader = _readers(
                    milestone=_milestone_toml(acceptance_class=acceptance_class)
                )
                with self.assertRaisesRegex(LiveConsumerError, message):
                    _verify(trigger, board, record_reader, git_reader)
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        record_reader, git_reader = _readers(
            milestone=_milestone_toml(acceptance_class=None)
        )
        with self.assertRaisesRegex(LiveConsumerError, "typed acceptance"):
            _verify(trigger, board, record_reader, git_reader)

    def test_milestone_acceptance_must_bind_accepted_plan_scope(self) -> None:
        for acceptance_path, message in (
            ("planning/PWV21_POLICY_KERNEL_MASTER_PLAN_P5.md", "accepted plan scope"),
            ("decisions/ADR_PWV21_LIVE_VALIDATION.md", "accepted plan scope"),
            ("evidence/note.md", "wrong-source Milestone acceptance"),
            ("owner/repo#12", "tracker"),
        ):
            with self.subTest(acceptance_path=acceptance_path):
                trigger = _admitted_trigger()
                board = _board_with_triggers([trigger])
                record_reader, git_reader = _readers(
                    milestone=_milestone_toml(acceptance_path=acceptance_path)
                )
                with self.assertRaisesRegex(LiveConsumerError, message):
                    _verify(trigger, board, record_reader, git_reader)

    def test_milestone_proof_must_not_name_a_card(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        record_reader, git_reader = _readers(
            milestone=_milestone_toml(card_id=AFTER_CARD)
        )
        with self.assertRaisesRegex(LiveConsumerError, "Card-scoped"):
            _verify(trigger, board, record_reader, git_reader)

    def test_legacy_markerless_milestone_with_acceptance_still_releases(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        record_reader, git_reader = _readers(
            milestone=_milestone_toml(scope=None)
        )
        _verify(trigger, board, record_reader, git_reader)

    def test_m02_shaped_milestone_still_releases(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        record_reader, git_reader = _readers(
            milestone=_m02_shaped_milestone_toml()
        )
        _verify(trigger, board, record_reader, git_reader)
        verify_live_consumer_records(
            board, record_reader=record_reader, git_reader=git_reader
        )

    def test_tracker_gate_path_cannot_substitute(self) -> None:
        trigger = _admitted_trigger()
        board = _board_with_triggers([trigger])
        record_reader, git_reader = _readers(
            admission=_admission_text(review_path="owner/repo#12")
        )
        with self.assertRaisesRegex(LiveConsumerError, "tracker"):
            _verify(trigger, board, record_reader, git_reader)

    def test_verification_requires_workstream_board(self) -> None:
        record_reader, git_reader = _readers()
        with self.assertRaisesRegex(LiveConsumerError, "Task Board table"):
            verify_live_consumer_records(
                [], record_reader=record_reader, git_reader=git_reader
            )
        with self.assertRaisesRegex(LiveConsumerError, "workstream-bound"):
            verify_live_consumer_records(
                {"jit_triggers": []},
                record_reader=record_reader,
                git_reader=git_reader,
            )

    def test_board_without_admitted_verifies_trivially(self) -> None:
        board = _board_with_triggers(
            [_trigger(live_consumer=_live_consumer()), _trigger("after-b")]
        )

        def _reader(path: str) -> str | None:
            raise AssertionError("reader must not be called")

        def _git(repository: str, commit: str, path: str) -> str | None:
            raise AssertionError("git reader must not be called")

        verify_live_consumer_records(
            board, record_reader=_reader, git_reader=_git
        )


class ConsumptionGuardTests(unittest.TestCase):
    def test_ordinary_trigger_consumes_normally(self) -> None:
        board = _board_with_triggers([_trigger()])
        self.assertEqual(
            require_admitted_trigger_consumption(board, TRIGGER_ID), TRIGGER_ID
        )
        board = _board_with_triggers(
            [_trigger(live_consumer={"intended": False})]
        )
        self.assertEqual(
            require_admitted_trigger_consumption(board, TRIGGER_ID), TRIGGER_ID
        )

    def test_pending_blocks_consumption(self) -> None:
        board = _board_with_triggers(
            [_trigger(live_consumer=_live_consumer())]
        )
        with self.assertRaisesRegex(LiveConsumerError, "pending"):
            require_admitted_trigger_consumption(board, TRIGGER_ID)

    def test_admitted_shape_permits_without_readers(self) -> None:
        board = _board_with_triggers([_admitted_trigger()])
        self.assertEqual(
            require_admitted_trigger_consumption(board, TRIGGER_ID), TRIGGER_ID
        )

    def test_admitted_with_readers_verifies_gates(self) -> None:
        board = _board_with_triggers([_admitted_trigger()])
        record_reader, git_reader = _readers(
            milestone=_milestone_toml(verdict="red")
        )
        with self.assertRaisesRegex(LiveConsumerError, "Milestone"):
            require_admitted_trigger_consumption(
                board, TRIGGER_ID,
                record_reader=record_reader, git_reader=git_reader,
            )

    def test_partial_readers_fail_closed(self) -> None:
        board = _board_with_triggers([_admitted_trigger()])
        record_reader, _ = _readers()
        with self.assertRaisesRegex(LiveConsumerError, "both"):
            require_admitted_trigger_consumption(
                board, TRIGGER_ID, record_reader=record_reader
            )

    def test_unknown_trigger_fails_closed(self) -> None:
        board = _board_with_triggers([_trigger()])
        with self.assertRaisesRegex(LiveConsumerError, "does not exist"):
            require_admitted_trigger_consumption(board, "after-unknown")

    def test_consumption_requires_workstream_board(self) -> None:
        with self.assertRaisesRegex(LiveConsumerError, "Task Board table"):
            require_admitted_trigger_consumption([], TRIGGER_ID)
        with self.assertRaisesRegex(LiveConsumerError, "workstream-bound"):
            require_admitted_trigger_consumption({"jit_triggers": []}, TRIGGER_ID)


class BoardValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workstream = read_toml(VALID / "WORKSTREAM.toml")

    def _board(self, triggers: list[dict] | None) -> dict:
        board = read_toml(VALID / "TASK_BOARD.toml")
        if triggers is None:
            board.pop("jit_triggers", None)
        else:
            board["jit_triggers"] = triggers
        return board

    def test_historical_board_without_declaration_remains_valid(self) -> None:
        board = self._board(None)
        validate_board(board, self.workstream)
        board = self._board([
            {
                "id": TRIGGER_ID,
                "after_card": "M01-T01",
                "state": "satisfied",
                "condition": "Ordinary downstream work.",
            }
        ])
        validate_board(board, self.workstream)

    def test_pending_satisfied_is_valid_board_and_hold_is_router_level(self) -> None:
        board = self._board([
            _trigger(live_consumer=_live_consumer()),
        ])
        validate_board(board, self.workstream)

    def test_consumed_pending_fails_board_validation(self) -> None:
        board = self._board([
            _trigger(state="consumed", live_consumer=_live_consumer()),
        ])
        with self.assertRaisesRegex(ValidationError, "cannot materialize"):
            validate_board(board, self.workstream)

    def test_admitted_citation_shape_validates_without_gate_readback(self) -> None:
        board = self._board([
            _trigger(
                state="consumed",
                live_consumer=_live_consumer(
                    readiness="admitted",
                    admission=_admission_citation(),
                ),
            ),
        ])
        validate_board(board, self.workstream)

    def test_malformed_declaration_fails_board_validation(self) -> None:
        table = _live_consumer()
        table["prompt"] = "trust me"
        board = self._board([_trigger(live_consumer=table)])
        with self.assertRaisesRegex(ValidationError, "prompt/prose"):
            validate_board(board, self.workstream)

    def test_runtime_keys_in_declaration_fail_board_validation(self) -> None:
        table = _live_consumer()
        table["runtime_hint"] = "fast"
        board = self._board([_trigger(live_consumer=table)])
        with self.assertRaisesRegex(ValidationError, "prohibited"):
            validate_board(board, self.workstream)


class RouterHoldTests(unittest.TestCase):
    def copy_fixture(self):
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(ROUTER_FIXTURE, project)
        return temp, project

    def _board_text(
        self, cards_toml: str, audits_toml: str, triggers_toml: str,
        findings_toml: str = "",
    ) -> str:
        return (
            'workstream_id = "sample-workstream"\n'
            "revision = 3\n"
            "\n"
            "[execution_ref]\n"
            'branch = "feat/sample-workstream"\n'
            "\n"
            f"{cards_toml}\n"
            f"{audits_toml}\n"
            f"{triggers_toml}\n"
            f"{findings_toml}\n"
        )

    def _done_card_toml(self, card_id: str = "M01-T03") -> str:
        return (
            "[[cards]]\n"
            f'id = "{card_id}"\n'
            'status = "done"\n'
            "[cards.contract]\n"
            'class = "task_card"\n'
            f'path = "implementation/workstreams/sample-workstream/cards/{card_id}.md"\n'
            "[cards.result]\n"
            'class = "result"\n'
            f'path = "implementation/workstreams/sample-workstream/results/{card_id}.md"\n'
        )

    def _planned_card_and_audits(self, card_id: str = "M01-T05") -> tuple[str, str]:
        audits = (
            "[[sizing_audits]]\n"
            f'card_id = "{card_id}"\n'
            'decision = "single"\n'
            'rebuttal_class = ""\n'
            'rebuttal = ""\n'
            "[[sizing_audits.outcomes]]\n"
            'id = "router-hold"\n'
            'kind = "invariant"\n'
            'statement = "Live-consumer hold keeps the satisfied trigger until admission."\n'
            'family = "routing"\n'
            "independently_verifiable = true\n"
            "independently_useful = true\n"
            "falsifiable = true\n"
            "substantial = true\n"
            "scaffolding_only = false\n"
            "independently_consumed = false\n"
            "[sizing_audits.dimensions]\n"
            'independent_implementability = "Durable independent implementability statement."\n'
            'falsifiability_testability = "Durable falsifiability testability statement."\n'
            'reviewability = "Durable reviewability statement."\n'
            'invariant_contract_family = "Durable invariant contract family statement."\n'
            'dependency_ordering = "Durable dependency ordering statement."\n'
            'atomic_mutation_migration = "Durable atomic mutation migration statement."\n'
            'cross_surface_coupling = "Durable cross surface coupling statement."\n'
            "\n"
            "[[topology_audits]]\n"
            f'card_id = "{card_id}"\n'
            'risk = "simple"\n'
            "triggers = []\n"
            'risk_basis = "Single coherent outcome in one invariant family."\n'
            'review_scope = "card_local"\n'
            'atomicity_rationale_class = ""\n'
            'atomicity_rationale = ""\n'
        )
        card = (
            "[[cards]]\n"
            f'id = "{card_id}"\n'
            'status = "planned"\n'
            "[cards.contract]\n"
            'class = "task_card"\n'
            f'path = "implementation/workstreams/sample-workstream/cards/{card_id}.md"\n'
        )
        return card, audits

    def _pin_toml(
        self,
        repository: str = "owner/router-fixture",
        commit: str = AUTHORITY_COMMIT,
        path: str = AUTHORITY_PATH,
        blob: str = AUTHORITY_BLOB,
    ) -> str:
        return (
            "[jit_triggers.live_consumer.authority]\n"
            f'repository = "{repository}"\n'
            f'commit = "{commit}"\n'
            f'path = "{path}"\n'
            f'blob = "{blob}"\n'
        )

    def _write_card_contract(self, project: Path, card_id: str) -> None:
        card_path = (
            project / "implementation" / "workstreams" / "sample-workstream"
            / "cards" / f"{card_id}.md"
        )
        card_path.parent.mkdir(parents=True, exist_ok=True)
        card_path.write_text(
            f"- Card ID: {card_id}\n"
            "- Included scope: bounded test scope\n"
            "- Excluded scope: nothing else\n"
            "- Authority refs: requirements/PROJECT_WORKFLOW_V2.md\n"
            "- Dependencies: none\n"
            "- Acceptance: observable test acceptance\n"
            "- Required tests/readback: unit tests\n"
            "- Review requirement: none\n"
            "- Technical contract: none\n",
            encoding="utf-8",
        )

    def test_ordinary_satisfied_trigger_routes_normally(self) -> None:
        temp, project = self.copy_fixture()
        try:
            done = self._done_card_toml()
            planned, audits = self._planned_card_and_audits()
            triggers = (
                "[[jit_triggers]]\n"
                'id = "after-M01-T03"\n'
                'after_card = "M01-T03"\n'
                'state = "satisfied"\n'
                'condition = "Ordinary downstream work."\n'
            )
            board_path = (
                project / "implementation" / "workstreams"
                / "sample-workstream" / "TASK_BOARD.toml"
            )
            board_path.write_text(
                self._board_text(done + planned, audits, triggers),
                encoding="utf-8",
            )
            self._write_card_contract(project, "M01-T05")
            routed = select_route(project, [ROUTER_MANIFEST])
            self.assertEqual(routed.disposition, "route")
            self.assertEqual(routed.obligation, "execution_prep")
        finally:
            temp.cleanup()

    def test_pending_live_consumer_holds_at_router(self) -> None:
        temp, project = self.copy_fixture()
        try:
            done = self._done_card_toml()
            planned, audits = self._planned_card_and_audits()
            triggers = (
                "[[jit_triggers]]\n"
                'id = "after-M01-T03"\n'
                'after_card = "M01-T03"\n'
                'state = "satisfied"\n'
                'condition = "Intended live-consumer test."\n'
                "[jit_triggers.live_consumer]\n"
                "intended = true\n"
                'readiness = "pending"\n'
                "[jit_triggers.live_consumer.authority]\n"
                'repository = "owner/router-fixture"\n'
                'commit = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\n'
                'path = "workflow/REVIEW.md"\n'
                'blob = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"\n'
            )
            board_path = (
                project / "implementation" / "workstreams"
                / "sample-workstream" / "TASK_BOARD.toml"
            )
            board_path.write_text(
                self._board_text(done + planned, audits, triggers),
                encoding="utf-8",
            )
            self._write_card_contract(project, "M01-T05")
            routed = select_route(project, [ROUTER_MANIFEST])
            self.assertEqual(routed.disposition, "route")
            self.assertEqual(routed.obligation, "live_consumer_readiness")
            self.assertEqual(routed.subject, "after-M01-T03")
            self.assertEqual(
                routed.owner_module, "workflow/EXECUTION_PREP.md"
            )
        finally:
            temp.cleanup()

    def test_waiting_live_consumer_does_not_hold(self) -> None:
        temp, project = self.copy_fixture()
        try:
            done = self._done_card_toml()
            planned, audits = self._planned_card_and_audits()
            triggers = (
                "[[jit_triggers]]\n"
                'id = "after-M01-T03"\n'
                'after_card = "M01-T03"\n'
                'state = "waiting"\n'
                'condition = "Intended live-consumer test."\n'
                "[jit_triggers.live_consumer]\n"
                "intended = true\n"
                'readiness = "pending"\n'
                "[jit_triggers.live_consumer.authority]\n"
                'repository = "owner/router-fixture"\n'
                'commit = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\n'
                'path = "workflow/REVIEW.md"\n'
                'blob = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"\n'
            )
            board_path = (
                project / "implementation" / "workstreams"
                / "sample-workstream" / "TASK_BOARD.toml"
            )
            board_path.write_text(
                self._board_text(done + planned, audits, triggers),
                encoding="utf-8",
            )
            self._write_card_contract(project, "M01-T05")
            routed = select_route(project, [ROUTER_MANIFEST])
            self.assertEqual(routed.disposition, "route")
            self.assertEqual(routed.obligation, "execution_prep")
        finally:
            temp.cleanup()

    def test_admitted_with_unreadable_record_fails_closed_to_recovery(self) -> None:
        temp, project = self.copy_fixture()
        try:
            done = self._done_card_toml()
            planned, audits = self._planned_card_and_audits()
            triggers = (
                "[[jit_triggers]]\n"
                'id = "after-M01-T03"\n'
                'after_card = "M01-T03"\n'
                'state = "satisfied"\n'
                'condition = "Intended live-consumer test."\n'
                "[jit_triggers.live_consumer]\n"
                "intended = true\n"
                'readiness = "admitted"\n'
                "[jit_triggers.live_consumer.authority]\n"
                'repository = "owner/router-fixture"\n'
                'commit = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\n'
                'path = "workflow/REVIEW.md"\n'
                'blob = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"\n'
                "[jit_triggers.live_consumer.admission]\n"
                'stage = "execution_prep"\n'
                "[jit_triggers.live_consumer.admission.record]\n"
                'class = "live_consumer_admission"\n'
                'path = "implementation/workstreams/sample-workstream/readiness/after-M01-T03.toml"\n'
            )
            board_path = (
                project / "implementation" / "workstreams"
                / "sample-workstream" / "TASK_BOARD.toml"
            )
            board_path.write_text(
                self._board_text(done + planned, audits, triggers),
                encoding="utf-8",
            )
            self._write_card_contract(project, "M01-T05")
            routed = select_route(project, [ROUTER_MANIFEST])
            self.assertEqual(routed.disposition, "recovery")
            self.assertIn("live-consumer", routed.reason)
        finally:
            temp.cleanup()


class FindingInteractionTests(unittest.TestCase):
    """T09 affected-finding holds compose with T11 readiness holds."""

    def test_both_guards_must_release_before_consumption(self) -> None:
        from tools.live_finding_contract import (
            require_reconciled_trigger_consumption,
        )

        trigger = _trigger(
            live_consumer=_live_consumer(),
        )
        board = _board_with_triggers([trigger])
        board["live_findings"] = [
            {
                "id": "LF-001",
                "finding_class": "implementation_defect",
                "observed": "Live execution showed a stale retry helper.",
                "evidence_refs": [
                    f"implementation/workstreams/{WORKSTREAM_ID}/evidence/LF-001.md"
                ],
                "owner_stage": "execution",
                "authorization": "none",
                "tracker_locators": [],
                "downstream": {
                    "disposition": "material",
                    "trigger": TRIGGER_ID,
                    "aspect": "semantics",
                    "material_evidence_refs": [
                        f"implementation/workstreams/{WORKSTREAM_ID}/evidence/LF-001-material.md"
                    ],
                    "reconciliation": "pending",
                },
            }
        ]
        with self.assertRaisesRegex(LiveConsumerError, "pending"):
            require_admitted_trigger_consumption(board, TRIGGER_ID)
        from tools.live_finding_contract import LiveFindingError

        with self.assertRaisesRegex(LiveFindingError, "held by pending"):
            require_reconciled_trigger_consumption(board, TRIGGER_ID)

    def test_router_prefers_finding_hold_when_both_apply(self) -> None:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(ROUTER_FIXTURE, project)
        try:
            router_case = RouterHoldTests()
            done = router_case._done_card_toml()
            planned, audits = router_case._planned_card_and_audits()
            triggers = (
                "[[jit_triggers]]\n"
                'id = "after-M01-T03"\n'
                'after_card = "M01-T03"\n'
                'state = "satisfied"\n'
                'condition = "Held by both gates."\n'
                "[jit_triggers.live_consumer]\n"
                "intended = true\n"
                'readiness = "pending"\n'
                "[jit_triggers.live_consumer.authority]\n"
                'repository = "owner/router-fixture"\n'
                'commit = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\n'
                'path = "workflow/REVIEW.md"\n'
                'blob = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"\n'
            )
            findings = (
                "[[live_findings]]\n"
                'id = "LF-001"\n'
                'finding_class = "implementation_defect"\n'
                'observed = "Live execution showed a stale retry helper."\n'
                'evidence_refs = ["implementation/workstreams/sample-workstream/evidence/LF-001.md"]\n'
                'owner_stage = "execution"\n'
                'authorization = "none"\n'
                "tracker_locators = []\n"
                "[live_findings.downstream]\n"
                'disposition = "material"\n'
                'trigger = "after-M01-T03"\n'
                'aspect = "semantics"\n'
                'material_evidence_refs = ["implementation/workstreams/sample-workstream/evidence/LF-001-material.md"]\n'
                'reconciliation = "pending"\n'
            )
            board_path = (
                project / "implementation" / "workstreams"
                / "sample-workstream" / "TASK_BOARD.toml"
            )
            board_path.write_text(
                router_case._board_text(done + planned, audits, triggers, findings),
                encoding="utf-8",
            )
            router_case._write_card_contract(project, "M01-T05")
            evidence_dir = (
                project / "implementation" / "workstreams"
                / "sample-workstream" / "evidence"
            )
            evidence_dir.mkdir(parents=True, exist_ok=True)
            (evidence_dir / "LF-001.md").write_text("# evidence\n")
            (evidence_dir / "LF-001-material.md").write_text("# material\n")
            routed = select_route(project, [ROUTER_MANIFEST])
            self.assertEqual(routed.disposition, "route")
            self.assertEqual(routed.obligation, "finding_reconciliation")
        finally:
            temp.cleanup()


class M03ProspectiveFixtureTests(unittest.TestCase):
    """M03-style consumer stays held before Milestone GREEN, releases after."""

    WORKSTREAM = "sample-workstream"
    CARD = "M02R-T10"
    TRIGGER = "after-M02R-T10"
    MILESTONE_ATTEMPT = "M02R-MILESTONE-R01"

    def _m03_board(
        self,
        readiness: str,
        admission: dict | None = None,
        authority: dict | None = None,
    ) -> dict:
        live: dict | None = None
        if readiness != "ordinary":
            live = {"intended": True, "readiness": readiness}
            live["authority"] = (
                authority
                if authority is not None
                else {
                    "repository": AUTHORITY_REPOSITORY,
                    "commit": AUTHORITY_COMMIT,
                    "path": AUTHORITY_PATH,
                    "blob": AUTHORITY_BLOB,
                }
            )
            if admission is not None:
                live["admission"] = admission
        trigger: dict = {
            "id": self.TRIGGER,
            "after_card": self.CARD,
            "state": "satisfied",
            "condition": "First M03-style live-consumer test of corrected rules.",
        }
        if live is not None:
            trigger["live_consumer"] = live
        return {
            "workstream_id": self.WORKSTREAM,
            "cards": [
                {
                    "id": self.CARD,
                    "status": "done",
                    "contract": {
                        "class": "task_card",
                        "path": f"implementation/workstreams/{self.WORKSTREAM}/cards/{self.CARD}.md",
                    },
                    "result": {
                        "class": "result",
                        "path": f"implementation/workstreams/{self.WORKSTREAM}/results/{self.CARD}.md",
                        "commit": "c" * 40,
                        "blob": "d" * 40,
                    },
                }
            ],
            "jit_triggers": [trigger],
        }

    def _m03_files(self, milestone_verdict: str) -> dict[str, str]:
        ws = self.WORKSTREAM
        predecessor_path = f"implementation/workstreams/{ws}/results/{self.CARD}.md"
        review_path = f"implementation/workstreams/{ws}/reviews/{self.CARD}-R02.toml"
        milestone_path = f"implementation/workstreams/{ws}/reviews/M02R-MILESTONE-R01.toml"
        admission_path = f"implementation/workstreams/{ws}/readiness/{self.TRIGGER}.toml"
        planning_subject = (
            "[subject]\n"
            f'repository = "{AUTHORITY_REPOSITORY}"\n'
            f'commit = "{PLANNING_SUBJECT_COMMIT}"\n'
            f'path = "{PLANNING_SUBJECT_PATH}"\n'
            f'blob = "{PLANNING_SUBJECT_BLOB}"\n'
        )
        files = {
            f"implementation/workstreams/{ws}/DEFINITION.toml": (
                f'workstream_id = "{ws}"\nrevision = "R3"\nstate = "green"\n'
            ),
            f"implementation/workstreams/{ws}/PLANNING.toml": (
                f'workstream_id = "{ws}"\nrevision = "P6"\ncycle = 1\n'
                'state = "approved"\n' + planning_subject
            ),
            f"implementation/workstreams/{ws}/PLAN_REVIEW.toml": (
                f'workstream_id = "{ws}"\nattempt = "PLAN-R01"\nverdict = "green"\n'
                'plan_revision = "P6"\nplanning_cycle = 1\n' + planning_subject
            ),
            review_path: (
                f'workstream_id = "{ws}"\ncard_id = "{self.CARD}"\n'
                f'attempt = "{self.CARD}-R02"\nverdict = "green"\n'
                "[subject]\n"
                f'repository = "{AUTHORITY_REPOSITORY}"\ncommit = "{"c" * 40}"\n'
                f'path = "{predecessor_path}"\nblob = "{"d" * 40}"\n'
                "[acceptance]\nclass = \"task_card\"\n"
                f'path = "implementation/workstreams/{ws}/cards/{self.CARD}.md"\n'
            ),
            milestone_path: (
                f'workstream_id = "{ws}"\nattempt = "{self.MILESTONE_ATTEMPT}"\n'
                f'verdict = "{milestone_verdict}"\nreview_scope = "milestone"\n'
                "[subject]\n"
                f'repository = "{AUTHORITY_REPOSITORY}"\ncommit = "{"c" * 40}"\n'
                f'path = "{predecessor_path}"\nblob = "{"d" * 40}"\n'
                "[acceptance]\nclass = \"authority\"\n"
                f'path = "{PLANNING_SUBJECT_PATH}"\n'
            ),
            predecessor_path: "# M02R-T10 result\n",
        }
        admission_fields = {
            "trigger_id": self.TRIGGER,
            "authority_repository": AUTHORITY_REPOSITORY,
            "authority_commit": AUTHORITY_COMMIT,
            "authority_path": AUTHORITY_PATH,
            "authority_blob": AUTHORITY_BLOB,
            "definition_path": f"implementation/workstreams/{ws}/DEFINITION.toml",
            "definition_revision": "R3",
            "planning_path": f"implementation/workstreams/{ws}/PLANNING.toml",
            "planning_revision": "P6",
            "plan_review_path": f"implementation/workstreams/{ws}/PLAN_REVIEW.toml",
            "plan_review_attempt": "PLAN-R01",
            "review_path": review_path,
            "review_attempt": f"{self.CARD}-R02",
            "predecessor_path": predecessor_path,
            "predecessor_commit": "c" * 40,
            "predecessor_blob": "d" * 40,
            "milestone_path": milestone_path,
            "milestone_attempt": self.MILESTONE_ATTEMPT,
            "decision": "admitted",
        }
        files[admission_path] = "\n".join(
            f'{key} = "{value}"' for key, value in sorted(admission_fields.items())
        ) + "\n"
        return files

    def test_hold_before_milestone_green_and_release_after(self) -> None:
        admission_path = (
            f"implementation/workstreams/{self.WORKSTREAM}/readiness/{self.TRIGGER}.toml"
        )
        pending_board = self._m03_board("pending")
        self.assertEqual(
            validate_live_consumer_gates(
                pending_board["jit_triggers"], self.WORKSTREAM
            ),
            {self.TRIGGER: "pending"},
        )
        with self.assertRaisesRegex(LiveConsumerError, "pending"):
            require_admitted_trigger_consumption(pending_board, self.TRIGGER)
        admitted_board = self._m03_board(
            "admitted",
            {
                "stage": "execution_prep",
                "record": {
                    "class": "live_consumer_admission",
                    "path": admission_path,
                },
            },
        )
        red_files = self._m03_files("red")

        def red_reader(path: str) -> str | None:
            return red_files.get(path)

        def git_reader(repository: str, commit: str, path: str) -> str | None:
            if (
                repository == AUTHORITY_REPOSITORY
                and commit == AUTHORITY_COMMIT
                and path == AUTHORITY_PATH
            ):
                return AUTHORITY_BLOB
            return None

        with self.assertRaisesRegex(LiveConsumerError, "Milestone.*not GREEN"):
            verify_live_consumer_records(
                admitted_board, record_reader=red_reader, git_reader=git_reader
            )
        green_files = self._m03_files("green")

        def green_reader(path: str) -> str | None:
            return green_files.get(path)

        verify_live_consumer_records(
            admitted_board, record_reader=green_reader, git_reader=git_reader
        )
        self.assertEqual(
            require_admitted_trigger_consumption(
                admitted_board, self.TRIGGER,
                record_reader=green_reader, git_reader=git_reader,
            ),
            self.TRIGGER,
        )
        card_ids = [card["id"] for card in admitted_board["cards"]]
        self.assertNotIn("M03-T01", card_ids)
        self.assertNotIn("M03", "".join(card_ids))

    def test_router_holds_m03_style_pending_without_materializing_m03(self) -> None:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(ROUTER_FIXTURE, project)
        try:
            router_case = RouterHoldTests()
            done = router_case._done_card_toml("M02R-T10")
            planned, audits = router_case._planned_card_and_audits("M02R-T11")
            triggers = (
                "[[jit_triggers]]\n"
                'id = "after-M02R-T10"\n'
                'after_card = "M02R-T10"\n'
                'state = "satisfied"\n'
                'condition = "First M03-style live-consumer test."\n'
                "[jit_triggers.live_consumer]\n"
                "intended = true\n"
                'readiness = "pending"\n'
                "[jit_triggers.live_consumer.authority]\n"
                'repository = "owner/router-fixture"\n'
                'commit = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\n'
                'path = "workflow/REVIEW.md"\n'
                'blob = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"\n'
            )
            board_path = (
                project / "implementation" / "workstreams"
                / "sample-workstream" / "TASK_BOARD.toml"
            )
            board_path.write_text(
                router_case._board_text(done + planned, audits, triggers),
                encoding="utf-8",
            )
            router_case._write_card_contract(project, "M02R-T11")
            routed = select_route(project, [ROUTER_MANIFEST])
            self.assertEqual(routed.disposition, "route")
            self.assertEqual(routed.obligation, "live_consumer_readiness")
            self.assertEqual(routed.subject, "after-M02R-T10")
            m03_card = (
                project / "implementation" / "workstreams"
                / "sample-workstream" / "cards" / "M03-T01.md"
            )
            self.assertFalse(m03_card.exists())
        finally:
            temp.cleanup()

    @staticmethod
    def _git(project: Path, *args: str) -> str:
        return subprocess.run(
            ["git", *args],
            cwd=project, check=True, capture_output=True, text=True,
        ).stdout.strip()

    def _init_router_git(self, project: Path) -> None:
        subprocess.run(
            ["git", "init"], cwd=project, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=project, check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=project, check=True,
        )

    def _write_m03_router_gates(
        self,
        ws_dir: Path,
        *,
        planning_commit: str,
        planning_blob: str,
        planning_subject_path: str,
        predecessor_commit: str,
        predecessor_blob: str,
        predecessor_path: str,
        planning_revision: str = "P6",
    ) -> None:
        (ws_dir / "results").mkdir(parents=True, exist_ok=True)
        (ws_dir / "results" / "M02R-T10.md").write_text(
            "# M02R-T10 result\n", encoding="utf-8"
        )
        (ws_dir / "DEFINITION.toml").write_text(
            'workstream_id = "sample-workstream"\nrevision = "R3"\nstate = "green"\n',
            encoding="utf-8",
        )
        (ws_dir / "PLANNING.toml").write_text(
            f'workstream_id = "sample-workstream"\nrevision = "{planning_revision}"\n'
            'cycle = 1\n'
            'state = "approved"\n[subject]\n'
            'repository = "owner/router-fixture"\n'
            f'commit = "{planning_commit}"\n'
            f'path = "{planning_subject_path}"\n'
            f'blob = "{planning_blob}"\n',
            encoding="utf-8",
        )
        (ws_dir / "PLAN_REVIEW.toml").write_text(
            'workstream_id = "sample-workstream"\nattempt = "PLAN-R01"\n'
            f'verdict = "green"\nplan_revision = "{planning_revision}"\n'
            'planning_cycle = 1\n'
            "[subject]\n"
            'repository = "owner/router-fixture"\n'
            f'commit = "{planning_commit}"\n'
            f'path = "{planning_subject_path}"\n'
            f'blob = "{planning_blob}"\n',
            encoding="utf-8",
        )
        (ws_dir / "reviews").mkdir(parents=True, exist_ok=True)
        (ws_dir / "reviews" / "M02R-T10-R02.toml").write_text(
            'workstream_id = "sample-workstream"\ncard_id = "M02R-T10"\n'
            'attempt = "M02R-T10-R02"\nverdict = "green"\n[subject]\n'
            'repository = "owner/router-fixture"\n'
            f'commit = "{predecessor_commit}"\n'
            f'path = "{predecessor_path}"\n'
            f'blob = "{predecessor_blob}"\n[acceptance]\nclass = "task_card"\n'
            'path = "implementation/workstreams/sample-workstream/cards/M02R-T10.md"\n',
            encoding="utf-8",
        )
        (ws_dir / "reviews" / "M02R-MILESTONE-R02.toml").write_text(
            'workstream_id = "sample-workstream"\n'
            'attempt = "M02R-MILESTONE-R02"\nverdict = "green"\n'
            'review_scope = "milestone"\n[subject]\n'
            'repository = "owner/router-fixture"\n'
            f'commit = "{predecessor_commit}"\n'
            f'path = "{predecessor_path}"\n'
            f'blob = "{predecessor_blob}"\n[acceptance]\nclass = "authority"\n'
            f'path = "{planning_subject_path}"\n',
            encoding="utf-8",
        )

    def _write_m03_router_admission(
        self,
        ws_dir: Path,
        *,
        authority_commit: str,
        authority_rel: str,
        authority_blob: str,
        predecessor_commit: str,
        predecessor_blob: str,
        predecessor_path: str,
        planning_revision: str = "P6",
    ) -> None:
        (ws_dir / "readiness").mkdir(parents=True, exist_ok=True)
        admission_fields = {
            "trigger_id": "after-M02R-T10",
            "authority_repository": "owner/router-fixture",
            "authority_commit": authority_commit,
            "authority_path": authority_rel,
            "authority_blob": authority_blob,
            "definition_path": "implementation/workstreams/sample-workstream/DEFINITION.toml",
            "definition_revision": "R3",
            "planning_path": "implementation/workstreams/sample-workstream/PLANNING.toml",
            "planning_revision": planning_revision,
            "plan_review_path": "implementation/workstreams/sample-workstream/PLAN_REVIEW.toml",
            "plan_review_attempt": "PLAN-R01",
            "review_path": "implementation/workstreams/sample-workstream/reviews/M02R-T10-R02.toml",
            "review_attempt": "M02R-T10-R02",
            "predecessor_path": predecessor_path,
            "predecessor_commit": predecessor_commit,
            "predecessor_blob": predecessor_blob,
            "milestone_path": "implementation/workstreams/sample-workstream/reviews/M02R-MILESTONE-R02.toml",
            "milestone_attempt": "M02R-MILESTONE-R02",
            "decision": "admitted",
        }
        (ws_dir / "readiness" / "after-M02R-T10.toml").write_text(
            "\n".join(
                f'{key} = "{value}"'
                for key, value in sorted(admission_fields.items())
            ) + "\n",
            encoding="utf-8",
        )

    def _write_m03_router_board(
        self,
        project: Path,
        ws_dir: Path,
        router_case: "RouterHoldTests",
        *,
        pin_commit: str,
        pin_blob: str,
        authority_rel: str,
        predecessor_commit: str,
        predecessor_blob: str,
        predecessor_path: str,
    ) -> None:
        done = (
            "[[cards]]\n"
            'id = "M02R-T10"\n'
            'status = "done"\n'
            "[cards.contract]\n"
            'class = "task_card"\n'
            'path = "implementation/workstreams/sample-workstream/cards/M02R-T10.md"\n'
            "[cards.result]\n"
            'class = "result"\n'
            f'path = "{predecessor_path}"\n'
            f'commit = "{predecessor_commit}"\n'
            f'blob = "{predecessor_blob}"\n'
        )
        planned, audits = router_case._planned_card_and_audits("M02R-T11")
        triggers = (
            "[[jit_triggers]]\n"
            'id = "after-M02R-T10"\n'
            'after_card = "M02R-T10"\n'
            'state = "satisfied"\n'
            'condition = "First M03-style live-consumer test."\n'
            "[jit_triggers.live_consumer]\n"
            "intended = true\n"
            'readiness = "admitted"\n'
            "[jit_triggers.live_consumer.authority]\n"
            'repository = "owner/router-fixture"\n'
            f'commit = "{pin_commit}"\n'
            f'path = "{authority_rel}"\n'
            f'blob = "{pin_blob}"\n'
            "[jit_triggers.live_consumer.admission]\n"
            'stage = "execution_prep"\n'
            "[jit_triggers.live_consumer.admission.record]\n"
            'class = "live_consumer_admission"\n'
            'path = "implementation/workstreams/sample-workstream/readiness/after-M02R-T10.toml"\n'
        )
        (ws_dir / "TASK_BOARD.toml").write_text(
            router_case._board_text(done + planned, audits, triggers),
            encoding="utf-8",
        )
        router_case._write_card_contract(project, "M02R-T11")

    def test_router_releases_verified_m03_style_without_special_prompt(self) -> None:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(ROUTER_FIXTURE, project)
        try:
            self._init_router_git(project)
            ws_dir = project / "implementation" / "workstreams" / "sample-workstream"
            planning_subject_path = "planning/PWV21_POLICY_KERNEL_MASTER_PLAN_P6.md"
            (project / "planning").mkdir(parents=True, exist_ok=True)
            (project / planning_subject_path).write_text("# P6\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "."], cwd=project, check=True, capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", "gates"],
                cwd=project, check=True, capture_output=True,
            )
            # The corrected-authority selection is the accepted Planning subject.
            authority_rel = planning_subject_path
            authority_commit = self._git(project, "rev-parse", "HEAD")
            authority_blob = self._git(project, "rev-parse", f"HEAD:{authority_rel}")
            planning_blob = authority_blob
            predecessor_commit, predecessor_blob = "c" * 40, "d" * 40
            predecessor_path = (
                "implementation/workstreams/sample-workstream/results/M02R-T10.md"
            )
            self._write_m03_router_gates(
                ws_dir,
                planning_commit=authority_commit,
                planning_blob=planning_blob,
                planning_subject_path=planning_subject_path,
                predecessor_commit=predecessor_commit,
                predecessor_blob=predecessor_blob,
                predecessor_path=predecessor_path,
            )
            self._write_m03_router_admission(
                ws_dir,
                authority_commit=authority_commit,
                authority_rel=authority_rel,
                authority_blob=authority_blob,
                predecessor_commit=predecessor_commit,
                predecessor_blob=predecessor_blob,
                predecessor_path=predecessor_path,
            )
            router_case = RouterHoldTests()
            self._write_m03_router_board(
                project, ws_dir, router_case,
                pin_commit=authority_commit,
                pin_blob=authority_blob,
                authority_rel=authority_rel,
                predecessor_commit=predecessor_commit,
                predecessor_blob=predecessor_blob,
                predecessor_path=predecessor_path,
            )
            routed = select_route(project, [ROUTER_MANIFEST])
            self.assertEqual(routed.disposition, "route")
            self.assertEqual(routed.obligation, "execution_prep")
            self.assertNotIn("prompt", routed.reason.lower())
            m03_card = ws_dir / "cards" / "M03-T01.md"
            self.assertFalse(m03_card.exists())
        finally:
            temp.cleanup()

    def test_router_stale_pin_move_fails_then_refreshed_releases(self) -> None:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(ROUTER_FIXTURE, project)
        try:
            self._init_router_git(project)
            ws_dir = project / "implementation" / "workstreams" / "sample-workstream"
            planning_subject_path = "planning/PWV21_POLICY_KERNEL_MASTER_PLAN_P6.md"
            authority_rel = planning_subject_path
            (project / "planning").mkdir(parents=True, exist_ok=True)
            # First accepted subject generation (P6).
            (project / planning_subject_path).write_text("# P6\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "."], cwd=project, check=True, capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", "plan v1"],
                cwd=project, check=True, capture_output=True,
            )
            old_commit = self._git(project, "rev-parse", "HEAD")
            old_blob = self._git(project, "rev-parse", f"HEAD:{authority_rel}")
            # Replan advances the accepted subject; the old blob stays readable.
            (project / planning_subject_path).write_text(
                "# P6 revised\n", encoding="utf-8"
            )
            subprocess.run(
                ["git", "add", "."], cwd=project, check=True, capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", "plan v2"],
                cwd=project, check=True, capture_output=True,
            )
            new_commit = self._git(project, "rev-parse", "HEAD")
            new_blob = self._git(project, "rev-parse", f"HEAD:{authority_rel}")
            self.assertNotEqual(old_blob, new_blob)
            self.assertEqual(
                self._git(project, "rev-parse", f"{old_commit}:{authority_rel}"),
                old_blob,
            )
            predecessor_commit, predecessor_blob = "c" * 40, "d" * 40
            predecessor_path = (
                "implementation/workstreams/sample-workstream/results/M02R-T10.md"
            )
            self._write_m03_router_gates(
                ws_dir,
                planning_commit=new_commit,
                planning_blob=new_blob,
                planning_subject_path=planning_subject_path,
                predecessor_commit=predecessor_commit,
                predecessor_blob=predecessor_blob,
                predecessor_path=predecessor_path,
                planning_revision="P7",
            )
            router_case = RouterHoldTests()
            # Phase 1: pin still cites the superseded subject -> wrong-source.
            self._write_m03_router_admission(
                ws_dir,
                authority_commit=old_commit,
                authority_rel=authority_rel,
                authority_blob=old_blob,
                predecessor_commit=predecessor_commit,
                predecessor_blob=predecessor_blob,
                predecessor_path=predecessor_path,
                planning_revision="P7",
            )
            self._write_m03_router_board(
                project, ws_dir, router_case,
                pin_commit=old_commit,
                pin_blob=old_blob,
                authority_rel=authority_rel,
                predecessor_commit=predecessor_commit,
                predecessor_blob=predecessor_blob,
                predecessor_path=predecessor_path,
            )
            routed = select_route(project, [ROUTER_MANIFEST])
            self.assertEqual(routed.disposition, "recovery")
            self.assertIn("accepted Planning subject", routed.reason)
            # Phase 2: pin moved but the admission still cites v1 -> stale.
            self._write_m03_router_board(
                project, ws_dir, router_case,
                pin_commit=new_commit,
                pin_blob=new_blob,
                authority_rel=authority_rel,
                predecessor_commit=predecessor_commit,
                predecessor_blob=predecessor_blob,
                predecessor_path=predecessor_path,
            )
            routed = select_route(project, [ROUTER_MANIFEST])
            self.assertEqual(routed.disposition, "recovery")
            self.assertIn("stale authority", routed.reason)
            # Phase 3: refreshed admission citing the current subject releases.
            self._write_m03_router_admission(
                ws_dir,
                authority_commit=new_commit,
                authority_rel=authority_rel,
                authority_blob=new_blob,
                predecessor_commit=predecessor_commit,
                predecessor_blob=predecessor_blob,
                predecessor_path=predecessor_path,
                planning_revision="P7",
            )
            routed = select_route(project, [ROUTER_MANIFEST])
            self.assertEqual(routed.disposition, "route")
            self.assertEqual(routed.obligation, "execution_prep")
            m03_card = ws_dir / "cards" / "M03-T01.md"
            self.assertFalse(m03_card.exists())
        finally:
            temp.cleanup()

    def test_router_unrelated_in_roots_selection_fails(self) -> None:
        # BOUNDARY class at the router: pin and admission agree on a readable
        # in-roots file that is not the accepted Planning subject.
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(ROUTER_FIXTURE, project)
        try:
            self._init_router_git(project)
            ws_dir = project / "implementation" / "workstreams" / "sample-workstream"
            planning_subject_path = "planning/PWV21_POLICY_KERNEL_MASTER_PLAN_P6.md"
            (project / "planning").mkdir(parents=True, exist_ok=True)
            (project / planning_subject_path).write_text("# P6\n", encoding="utf-8")
            unrelated_rel = "workflow/UNRELATED.md"
            (project / "workflow").mkdir(parents=True, exist_ok=True)
            (project / unrelated_rel).write_text("# unrelated\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "."], cwd=project, check=True, capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", "gates"],
                cwd=project, check=True, capture_output=True,
            )
            head = self._git(project, "rev-parse", "HEAD")
            planning_blob = self._git(
                project, "rev-parse", f"HEAD:{planning_subject_path}"
            )
            unrelated_blob = self._git(
                project, "rev-parse", f"HEAD:{unrelated_rel}"
            )
            predecessor_commit, predecessor_blob = "c" * 40, "d" * 40
            predecessor_path = (
                "implementation/workstreams/sample-workstream/results/M02R-T10.md"
            )
            self._write_m03_router_gates(
                ws_dir,
                planning_commit=head,
                planning_blob=planning_blob,
                planning_subject_path=planning_subject_path,
                predecessor_commit=predecessor_commit,
                predecessor_blob=predecessor_blob,
                predecessor_path=predecessor_path,
            )
            self._write_m03_router_admission(
                ws_dir,
                authority_commit=head,
                authority_rel=unrelated_rel,
                authority_blob=unrelated_blob,
                predecessor_commit=predecessor_commit,
                predecessor_blob=predecessor_blob,
                predecessor_path=predecessor_path,
            )
            router_case = RouterHoldTests()
            self._write_m03_router_board(
                project, ws_dir, router_case,
                pin_commit=head,
                pin_blob=unrelated_blob,
                authority_rel=unrelated_rel,
                predecessor_commit=predecessor_commit,
                predecessor_blob=predecessor_blob,
                predecessor_path=predecessor_path,
            )
            routed = select_route(project, [ROUTER_MANIFEST])
            self.assertEqual(routed.disposition, "recovery")
            self.assertIn("accepted Planning subject", routed.reason)
            m03_card = ws_dir / "cards" / "M03-T01.md"
            self.assertFalse(m03_card.exists())
        finally:
            temp.cleanup()
