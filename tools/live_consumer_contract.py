#!/usr/bin/env python3
"""Bounded prospective intentional live-consumer readiness/admission contract (REQ-127).

A downstream JIT trigger explicitly declared as an intentional live-consumer
test of corrected PWv2.1 rules cannot be consumed — and its Card cannot be
materialized — before verified complete evidence proves the corrected
authority and the required Definition, Planning, review, predecessor and
Milestone gates for that consumer. Exact complete evidence releases the
trigger through the normal JIT state lifecycle; no special prompt or
bookkeeping substitutes for missing workflow semantics.

Scope is deliberately narrow. Only triggers carrying an explicit
``live_consumer`` table with ``intended = true`` are gated. Triggers without
the table, triggers explicitly marked ``intended = false``, and historical
Boards without the declaration remain ordinary and valid. This module never
creates a broad speculative gate for every Card.

Declaration shape (per ``jit_triggers[]`` entry)::

    [jit_triggers.live_consumer]
    intended = true
    readiness = "pending" | "admitted"
    [jit_triggers.live_consumer.authority]          # required iff intended
    repository = "<accepted plan repository>"
    commit = "<accepted plan subject commit>"
    path = "planning/<accepted plan file>"
    blob = "<accepted plan subject blob>"
    [jit_triggers.live_consumer.admission]          # required iff admitted
    stage = "execution_prep"
    [jit_triggers.live_consumer.admission.record]
    class = "live_consumer_admission"
    path = "implementation/workstreams/<id>/readiness/<trigger>.toml"

``pending`` holds a ``satisfied`` trigger at the router; ``consumed`` while
``pending`` is invalid and fails closed. ``admitted`` cites exactly one typed
admission-decision record verified by readback. The admitting stage is the
JIT materialization boundary (``execution_prep``); Worker identity can never
admit.

The board-co-bound ``authority`` pin is the durable currency selector for
the corrected-authority gate, and it must be the exact current accepted
Planning subject — the only versioned, Plan-Review-bound, approved-state
authority artifact in the workstream (Definition and workstream authority
refs carry unversioned paths only). The pin itself must resolve in Git and
the admission must reproduce the pinned repository/commit/path/blob exactly.
An arbitrary in-roots file is never eligible even when the Board and
admission agree, and an old-but-still-readable git object never suffices on
its own: replanning to a new accepted subject stales every previous
pin/admission until refreshed. Refreshing the pin on replan is Execution
Prep discipline at the JIT boundary, like launch refresh; currency tracks
the accepted subject, so a still-current selection keeps releasing while a
superseded one stales old proofs.

The admission record is TOML with exactly 19 non-empty string fields:
``trigger_id``, the corrected-authority git-blob subject
(``authority_repository``/``authority_commit``/``authority_path``/
``authority_blob``), ``definition_path``/``definition_revision``,
``planning_path``/``planning_revision``, ``plan_review_path``/
``plan_review_attempt``, ``review_path``/``review_attempt``,
``predecessor_path``/``predecessor_commit``/``predecessor_blob``,
``milestone_path``/``milestone_attempt`` and ``decision = "admitted"``.
There is no free-prose field: prompt text, tracker shorthand, generic
GREEN/status strings and Worker claims can never satisfy the proof.

Verification (router-level, with readers) checks every gate by content:
the board-selected authority pin equals the exact current accepted Planning
subject, resolves exactly via Git, and the admission reproduces the pin;
the Definition record matches revision and is GREEN;
the Planning record matches revision and is approved; the Plan Review
record matches attempt, is GREEN and binds the exact Planning
subject/revision/cycle; the predecessor identity matches the board's DONE
predecessor result and reads back; the Card review record matches attempt,
is GREEN, names the predecessor Card and covers the exact predecessor
subject; the Milestone record matches attempt, is GREEN, carries no Card
marker, binds authority acceptance to the exact accepted plan subject and
covers the exact predecessor subject. Missing, partial, stale,
contradictory, forged, wrong-source or unreadable evidence fails closed to
Recovery. This gate checks terminal completion plus exact identity;
internal gate validity (premium arithmetic, independence, review history)
remains owned by the Definition/Planning/Review validators that produced
those records.

Runtime-neutral: no runtime/model/session/worker identity is canonical
state. Releasing the hold permits normal JIT consumption without erasing
the declaration or its decision history.
"""

from __future__ import annotations

import re
import tomllib
from collections.abc import Callable, Mapping
from typing import Any

try:
    from tools.exact_locator import ExactLocatorError, normalize_locator_path
except ModuleNotFoundError:  # direct script execution from tools/
    from exact_locator import ExactLocatorError, normalize_locator_path

LIVE_CONSUMER_READINESS_STATES = frozenset({"pending", "admitted"})

ADMISSION_RECORD_CLASSES = frozenset({"live_consumer_admission"})

ADMISSION_DECISION_ADMITTED = "admitted"

ADMISSION_DECISION_FIELDS = frozenset({
    "trigger_id",
    "authority_repository",
    "authority_commit",
    "authority_path",
    "authority_blob",
    "definition_path",
    "definition_revision",
    "planning_path",
    "planning_revision",
    "plan_review_path",
    "plan_review_attempt",
    "review_path",
    "review_attempt",
    "predecessor_path",
    "predecessor_commit",
    "predecessor_blob",
    "milestone_path",
    "milestone_attempt",
    "decision",
})

LIVE_CONSUMER_ALLOWED_KEYS = frozenset({"intended", "readiness", "authority", "admission"})

AUTHORITY_PIN_KEYS = frozenset({"repository", "commit", "path", "blob"})

ADMISSION_ALLOWED_KEYS = frozenset({"stage", "record"})

ADMISSION_RECORD_KEYS = frozenset({"class", "path"})

ADMITTING_STAGES = frozenset({"execution_prep"})

AUTHORITY_ROOTS = ("requirements/", "decisions/", "planning/", "workflow/")

TRACKER_PROVENANCE_MARKERS = (
    "tracker.toml",
    "tracker/",
    "issue#",
    "issue #",
    "github.com",
    "http://",
    "https://",
)

PROMPT_SUBSTITUTE_KEYS = frozenset({
    "prompt",
    "prompt_text",
    "instructions",
    "instruction",
    "special_instructions",
    "special_prompt",
    "statement",
    "basis",
    "readiness_basis",
    "admission_basis",
    "justification",
    "rationale_note",
})

_SHA40 = re.compile(r"^[0-9a-f]{40}$")


class LiveConsumerError(ValueError):
    """Raised when intentional live-consumer readiness/admission is invalid."""


def is_tracker_provenance(value: str) -> bool:
    """Return whether a cited record path is a tracker/issue pointer."""
    if "#" in value:
        return True
    lowered = value.lower()
    return any(marker in lowered for marker in TRACKER_PROVENANCE_MARKERS)


def _is_worker_identity(stage: Any) -> bool:
    """Return whether a stage value claims Worker identity."""
    if not isinstance(stage, str):
        return False
    head = stage.strip().lower().replace("-", "_").replace(":", "_").replace(" ", "_")
    return head == "worker" or head.startswith("worker_")


def _validate_record_path(path: Any, label: str, workstream_id: str) -> str:
    """Validate one workstream-local readiness record path."""
    if not isinstance(path, str) or not path:
        raise LiveConsumerError(f"{label}: record path must be a non-empty string")
    if is_tracker_provenance(path):
        raise LiveConsumerError(
            f"{label}: tracker/issue pointers are untrusted bookkeeping and cannot "
            "serve as durable readiness records"
        )
    prefix = f"implementation/workstreams/{workstream_id}/readiness/"
    try:
        normalize_locator_path(path, label)
    except ExactLocatorError as exc:
        raise LiveConsumerError(
            f"{label}: invalid live_consumer_admission record path {path!r}; "
            f"expected {prefix}*.toml: {exc}"
        ) from exc
    if not path.startswith(prefix) or not path.endswith(".toml"):
        raise LiveConsumerError(
            f"{label}: invalid live_consumer_admission record path {path!r}; "
            f"expected {prefix}*.toml"
        )
    return path


def _validate_authority_pin(pin: Any, label: str) -> dict[str, str]:
    """Validate the board-co-bound selected-authority pin shape.

    The pin names the exact corrected-authority git-blob subject
    (``repository``/``commit``/``path``/``blob``) the intended consumer is
    selected to exercise. It lives on the durable board declaration, external
    to any admission claim, so moving the selection stales old admissions.
    Content (git resolution) is verified by readback at the serving boundary.
    """
    if not isinstance(pin, Mapping):
        raise LiveConsumerError(
            f"{label}: authority pin must be a table naming the exact selected "
            "corrected-authority subject"
        )
    prompt_keys = PROMPT_SUBSTITUTE_KEYS & set(pin)
    if prompt_keys:
        raise LiveConsumerError(
            f"{label}: prompt/prose substitutes ({', '.join(sorted(prompt_keys))}) "
            "cannot select corrected authority; record the exact "
            "repository/commit/path/blob pin"
        )
    unexpected = set(pin) - AUTHORITY_PIN_KEYS
    if unexpected:
        raise LiveConsumerError(
            f"{label}: unexpected authority pin keys "
            f"({', '.join(sorted(str(key) for key in unexpected))}); expected "
            "exactly repository, commit, path and blob"
        )
    repository = pin.get("repository")
    if not isinstance(repository, str) or not repository.strip():
        raise LiveConsumerError(
            f"{label}: authority pin repository must be a non-empty string"
        )
    if is_tracker_provenance(repository):
        raise LiveConsumerError(
            f"{label}: tracker/issue pointers cannot select corrected authority"
        )
    for key in ("commit", "blob"):
        value = pin.get(key)
        if not isinstance(value, str) or _SHA40.fullmatch(value) is None:
            raise LiveConsumerError(
                f"{label}: authority pin {key} must be exact 40-hex Git identity"
            )
    path = pin.get("path")
    if not isinstance(path, str) or not path:
        raise LiveConsumerError(
            f"{label}: authority pin path must be a non-empty string"
        )
    if is_tracker_provenance(path):
        raise LiveConsumerError(
            f"{label}: tracker/issue pointers cannot select corrected authority"
        )
    try:
        normalize_locator_path(path, label)
    except ExactLocatorError as exc:
        raise LiveConsumerError(
            f"{label}: wrong-source authority pin {path!r}; expected one of "
            f"requirements/, decisions/, planning/, workflow/: {exc}"
        ) from exc
    if not path.startswith(AUTHORITY_ROOTS):
        raise LiveConsumerError(
            f"{label}: wrong-source authority pin {path!r}; expected one of "
            "requirements/, decisions/, planning/, workflow/"
        )
    return {
        "repository": repository,
        "commit": str(pin.get("commit")),
        "path": path,
        "blob": str(pin.get("blob")),
    }


def _validate_admission_citation(
    admission: Any, label: str, *, workstream_id: str
) -> dict[str, Any]:
    """Validate the Execution Prep admission citation shape (content verified later)."""
    if not isinstance(admission, Mapping):
        raise LiveConsumerError(
            f"{label}: admission must bind the admitting stage to one typed "
            "admission-decision record"
        )
    prompt_keys = PROMPT_SUBSTITUTE_KEYS & set(admission)
    if prompt_keys:
        raise LiveConsumerError(
            f"{label}: prompt/prose substitutes ({', '.join(sorted(prompt_keys))}) "
            "cannot prove readiness; the typed decision record carries the proof"
        )
    unexpected = set(admission) - ADMISSION_ALLOWED_KEYS
    if unexpected:
        raise LiveConsumerError(
            f"{label}: unexpected admission keys "
            f"({', '.join(sorted(str(key) for key in unexpected))}); expected "
            "exactly stage and record"
        )
    stage = admission.get("stage")
    if _is_worker_identity(stage):
        raise LiveConsumerError(
            f"{label}: Worker self-certification cannot admit an intentional "
            "live-consumer trigger; only execution_prep verifies the gates"
        )
    if stage not in ADMITTING_STAGES:
        raise LiveConsumerError(
            f"{label}: unknown admitting stage {stage!r}; expected exactly one of "
            + ", ".join(sorted(ADMITTING_STAGES))
        )
    cited = admission.get("record")
    if not isinstance(cited, Mapping):
        raise LiveConsumerError(
            f"{label}: admission must cite one admission-decision record table"
        )
    prompt_record = PROMPT_SUBSTITUTE_KEYS & set(cited)
    if prompt_record:
        raise LiveConsumerError(
            f"{label}: prompt/prose substitutes cannot prove readiness; the typed "
            "decision record carries the proof"
        )
    unexpected_record = set(cited) - ADMISSION_RECORD_KEYS
    if unexpected_record:
        raise LiveConsumerError(
            f"{label}: unexpected admission record keys "
            f"({', '.join(sorted(str(key) for key in unexpected_record))}); "
            "expected exactly class and path"
        )
    record_class = cited.get("class")
    if record_class not in ADMISSION_RECORD_CLASSES:
        raise LiveConsumerError(
            f"{label}: unknown admission record class {record_class!r}; expected one "
            "of " + ", ".join(sorted(ADMISSION_RECORD_CLASSES))
        )
    record_path = _validate_record_path(
        cited.get("path"), f"{label}: record", workstream_id
    )
    return {
        "stage": str(stage),
        "record": {"class": str(record_class), "path": record_path},
    }


def validate_live_consumer_declaration(
    trigger: Mapping[str, Any], workstream_id: str, label: str
) -> dict[str, Any] | None:
    """Validate one trigger's optional intentional live-consumer declaration.

    Returns ``None`` for ordinary triggers without the table. An explicit
    ``intended = false`` table records an ordinary path and must not claim
    readiness, an authority pin or admission. An ``intended = true`` table
    requires an exact co-bound ``authority`` pin selecting the
    corrected-authority subject plus ``readiness`` in
    ``pending``/``admitted``; ``admitted`` additionally binds the Execution
    Prep admission citation while ``pending`` must not claim one.
    Prompt/prose substitutes, tracker records, Worker stages and generic
    readiness strings fail closed here; gate content is verified by readback
    at the serving boundary.
    """
    if not isinstance(trigger, Mapping):
        raise LiveConsumerError(f"{label}: trigger must be a table")
    declaration = trigger.get("live_consumer")
    if declaration is None:
        return None
    if not isinstance(declaration, Mapping):
        raise LiveConsumerError(
            f"{label}: live_consumer must be a table carrying the intentional "
            "declaration"
        )
    prompt_keys = PROMPT_SUBSTITUTE_KEYS & set(declaration)
    if prompt_keys:
        raise LiveConsumerError(
            f"{label}: prompt/prose substitutes ({', '.join(sorted(prompt_keys))}) "
            "cannot declare or prove live-consumer readiness; record the exact "
            "intended/readiness bindings plus the typed decision record"
        )
    unexpected = set(declaration) - LIVE_CONSUMER_ALLOWED_KEYS
    if unexpected:
        raise LiveConsumerError(
            f"{label}: unexpected live_consumer keys "
            f"({', '.join(sorted(str(key) for key in unexpected))}); live_consumer "
            "carries only intended, readiness, authority and admission"
        )
    intended = declaration.get("intended")
    if not isinstance(intended, bool):
        raise LiveConsumerError(
            f"{label}: missing or ambiguous intended flag {intended!r}; expected an "
            "explicit boolean"
        )
    if intended is False:
        if set(declaration) != {"intended"}:
            raise LiveConsumerError(
                f"{label}: explicitly ordinary triggers must not claim readiness, "
                "an authority pin or admission"
            )
        return {"intended": False}
    readiness = declaration.get("readiness")
    if readiness not in LIVE_CONSUMER_READINESS_STATES:
        raise LiveConsumerError(
            f"{label}: missing or ambiguous readiness {readiness!r}; expected "
            "exactly one of " + ", ".join(sorted(LIVE_CONSUMER_READINESS_STATES))
        )
    if "authority" not in declaration:
        raise LiveConsumerError(
            f"{label}: an intended live-consumer trigger requires an exact "
            "co-bound authority pin selecting the corrected-authority subject; "
            "the admission must reproduce this board selection exactly"
        )
    pin = _validate_authority_pin(
        declaration.get("authority"), f"{label}: authority"
    )
    admission = declaration.get("admission")
    if readiness == "admitted":
        validated = _validate_admission_citation(
            admission, f"{label}: admission", workstream_id=workstream_id
        )
    elif admission is not None:
        raise LiveConsumerError(
            f"{label}: pending readiness must not claim admission; the intended "
            "trigger stays held until every required gate is verified complete"
        )
    else:
        validated = None
    return {
        "intended": True,
        "readiness": str(readiness),
        "authority": pin,
        "admission": validated,
    }


def validate_live_consumer_gates(
    triggers: Any, workstream_id: str
) -> dict[str, str]:
    """Enforce the intentional live-consumer hold across board triggers.

    Returns the pending hold set: intended trigger ids mapped to ``"pending"``.
    Ordinary triggers, explicitly ordinary declarations and admitted triggers
    impose no hold. A ``consumed`` trigger with ``pending`` readiness fails
    closed since the intended consumer cannot materialize before verified
    admission. Admission content is verified by readback at the serving
    boundary.
    """
    if triggers is None:
        triggers = []
    if not isinstance(triggers, list):
        raise LiveConsumerError(
            "task_board jit_triggers must be an array of trigger records"
        )
    if not isinstance(workstream_id, str) or not workstream_id.strip():
        raise LiveConsumerError(
            "live-consumer validation requires a workstream-bound Task Board"
        )
    holds: dict[str, str] = {}
    for index, trigger in enumerate(triggers):
        label = f"task_board.jit_triggers[{index}]"
        if not isinstance(trigger, Mapping):
            raise LiveConsumerError(f"{label}: trigger must be a table")
        trigger_id = trigger.get("id")
        if not isinstance(trigger_id, str) or not trigger_id.strip():
            raise LiveConsumerError(
                f"{label}: trigger id must be a non-empty string"
            )
        declaration = validate_live_consumer_declaration(
            trigger, workstream_id, f"{label}.live_consumer"
        )
        if declaration is None or declaration.get("intended") is False:
            continue
        if declaration.get("readiness") == "admitted":
            continue
        if trigger.get("state") == "consumed":
            raise LiveConsumerError(
                f"JIT trigger {trigger_id!r} is consumed while intentional "
                "live-consumer readiness is still pending; the intended consumer "
                "cannot materialize before verified corrected authority and every "
                "required Definition, Planning, review, predecessor and Milestone "
                "gate is complete"
            )
        holds[str(trigger_id)] = "pending"
    return dict(sorted(holds.items()))


def parse_admission_decision(text: str, record_path: str) -> dict[str, str]:
    """Parse one typed live-consumer admission-decision document.

    The document must be TOML carrying exactly the 19 admission fields as
    non-empty strings. Anything else — Markdown notes, result prose, review
    attempts, tracker exports, generic GREEN/status claims — fails here so
    unrelated records can never satisfy the proof.
    """
    try:
        document = tomllib.loads(text)
    except (tomllib.TOMLDecodeError, ValueError) as exc:
        raise LiveConsumerError(
            f"admission record {record_path!r} is not a typed "
            f"admission-decision document: {exc}"
        ) from exc
    if not isinstance(document, dict):
        raise LiveConsumerError(
            f"admission record {record_path!r} must be a TOML table"
        )
    keys = set(document)
    if keys != ADMISSION_DECISION_FIELDS:
        missing = sorted(ADMISSION_DECISION_FIELDS - keys)
        extra = sorted(keys - ADMISSION_DECISION_FIELDS)
        raise LiveConsumerError(
            f"admission record {record_path!r} has wrong decision fields "
            f"missing={missing} extra={extra}; expected exactly "
            + ", ".join(sorted(ADMISSION_DECISION_FIELDS))
        )
    decision: dict[str, str] = {}
    for key in sorted(ADMISSION_DECISION_FIELDS):
        value = document[key]
        if not isinstance(value, str) or not value.strip():
            raise LiveConsumerError(
                f"admission record {record_path!r}: decision field {key!r} must be "
                "a non-empty string"
            )
        decision[key] = value
    for key in (
        "authority_commit",
        "authority_blob",
        "predecessor_commit",
        "predecessor_blob",
    ):
        if _SHA40.fullmatch(decision[key]) is None:
            raise LiveConsumerError(
                f"admission record {record_path!r}: decision field {key!r} must be "
                "exact 40-hex Git identity"
            )
    return decision


def _require_safe_workstream_path(
    raw: Any, label: str, workstream_id: str, subdir: str, suffix: str
) -> str:
    """Require an exact workstream-local path, rejecting tracker provenance."""
    if not isinstance(raw, str) or not raw:
        raise LiveConsumerError(f"{label} must be a non-empty string")
    if is_tracker_provenance(raw):
        raise LiveConsumerError(
            f"{label} cites tracker/issue pointer {raw!r}; tracker bookkeeping "
            "cannot satisfy a live-consumer gate"
        )
    prefix = f"implementation/workstreams/{workstream_id}/{subdir}"
    try:
        normalize_locator_path(raw, label)
    except ExactLocatorError as exc:
        raise LiveConsumerError(
            f"{label} cites wrong-source path {raw!r}; expected {prefix}*{suffix}: {exc}"
        ) from exc
    if not raw.startswith(prefix) or not raw.endswith(suffix):
        raise LiveConsumerError(
            f"{label} cites wrong-source path {raw!r}; expected {prefix}*{suffix}"
        )
    return raw


def _load_gate_toml(
    raw_text: str | None, cited_path: str, gate: str
) -> dict[str, Any]:
    """Parse one cited gate record, failing closed on unreadable/malformed."""
    if raw_text is None:
        raise LiveConsumerError(
            f"live-consumer {gate} gate cites {cited_path!r} that cannot be read "
            "back; unverifiable gates fail closed to Recovery"
        )
    try:
        document = tomllib.loads(raw_text)
    except (tomllib.TOMLDecodeError, ValueError) as exc:
        raise LiveConsumerError(
            f"live-consumer {gate} gate record {cited_path!r} is not valid TOML: "
            f"{exc}"
        ) from exc
    if not isinstance(document, dict):
        raise LiveConsumerError(
            f"live-consumer {gate} gate record {cited_path!r} must be a TOML table"
        )
    return document


def verify_admission_decision(
    trigger: Mapping[str, Any],
    live_consumer: Mapping[str, Any],
    record_path: str,
    record_text: str | None,
    board: Mapping[str, Any],
    *,
    record_reader: Callable[[str], str | None],
    git_reader: Callable[[str, str, str], str | None],
) -> None:
    """Verify one admitted trigger's admission record plus every required gate.

    ``record_text`` is the admission file content or ``None`` when unreadable.
    ``record_reader`` returns workstream-local file text or ``None``;
    ``git_reader`` returns the exact blob id for ``(repository, commit, path)``
    or ``None``. The admission must name this exact trigger id with an
    explicit ``admitted`` decision, and every gate — corrected authority
    equal to the exact current accepted Planning subject, Definition GREEN,
    Planning approved, Plan Review GREEN bound to the exact Planning
    subject, predecessor DONE identity, Card review GREEN covering the exact
    predecessor subject, Milestone GREEN covering the exact predecessor
    subject — must read back and match by content. Anything else fails
    closed.
    """
    trigger_id = trigger.get("id")
    workstream_id = board.get("workstream_id")
    if not isinstance(workstream_id, str) or not workstream_id.strip():
        raise LiveConsumerError(
            "live-consumer verification requires a workstream-bound Task Board"
        )
    if record_text is None:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites admission record {record_path!r} "
            "that cannot be read back; unverifiable admission fails closed to "
            "Recovery"
        )
    decision = parse_admission_decision(record_text, record_path)
    if decision["trigger_id"] != trigger_id:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites admission record {record_path!r} "
            f"decided for trigger {decision['trigger_id']!r}; unrelated decisions "
            "cannot admit this consumer"
        )
    if decision["decision"] != ADMISSION_DECISION_ADMITTED:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites admission record {record_path!r} "
            f"with decision {decision['decision']!r}; only an explicit admitted "
            "decision releases the hold"
        )
    admission = live_consumer.get("admission")
    if not isinstance(admission, Mapping):
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} claims admitted readiness without a "
            "typed admission citation"
        )
    # Definition gate: exact revision plus GREEN state.
    definition_path = _require_safe_workstream_path(
        decision["definition_path"],
        f"JIT trigger {trigger_id!r} definition gate",
        workstream_id,
        "DEFINITION.toml",
        ".toml",
    )
    if definition_path != f"implementation/workstreams/{workstream_id}/DEFINITION.toml":
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites wrong-source Definition "
            f"{definition_path!r}"
        )
    definition = _load_gate_toml(
        record_reader(definition_path), definition_path, "definition"
    )
    if definition.get("workstream_id") != workstream_id:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites Definition from another workstream"
        )
    if definition.get("revision") != decision["definition_revision"]:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites stale Definition revision "
            f"{decision['definition_revision']!r}; current is "
            f"{definition.get('revision')!r}"
        )
    if definition.get("state") != "green":
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites Definition that is not GREEN; "
            "generic status cannot substitute for the exact GREEN gate"
        )
    # Planning gate: exact revision plus approved state.
    planning_path = _require_safe_workstream_path(
        decision["planning_path"],
        f"JIT trigger {trigger_id!r} planning gate",
        workstream_id,
        "PLANNING.toml",
        ".toml",
    )
    if planning_path != f"implementation/workstreams/{workstream_id}/PLANNING.toml":
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites wrong-source Planning "
            f"{planning_path!r}"
        )
    planning = _load_gate_toml(
        record_reader(planning_path), planning_path, "planning"
    )
    if planning.get("workstream_id") != workstream_id:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites Planning from another workstream"
        )
    if planning.get("revision") != decision["planning_revision"]:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites stale Planning revision "
            f"{decision['planning_revision']!r}; current is "
            f"{planning.get('revision')!r}"
        )
    if planning.get("state") != "approved":
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites Planning that is not approved; "
            "the consumer requires the exact approved gate"
        )
    # Plan Review gate: GREEN attempt bound to the exact Planning subject.
    plan_review_path = _require_safe_workstream_path(
        decision["plan_review_path"],
        f"JIT trigger {trigger_id!r} plan-review gate",
        workstream_id,
        "PLAN_REVIEW.toml",
        ".toml",
    )
    if plan_review_path != f"implementation/workstreams/{workstream_id}/PLAN_REVIEW.toml":
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites wrong-source Plan Review "
            f"{plan_review_path!r}"
        )
    plan_review = _load_gate_toml(
        record_reader(plan_review_path), plan_review_path, "plan-review"
    )
    if plan_review.get("workstream_id") != workstream_id:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites Plan Review from another workstream"
        )
    if plan_review.get("attempt") != decision["plan_review_attempt"]:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites stale Plan Review attempt "
            f"{decision['plan_review_attempt']!r}; current is "
            f"{plan_review.get('attempt')!r}"
        )
    if plan_review.get("verdict") != "green":
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites Plan Review that is not GREEN"
        )
    if plan_review.get("plan_revision") != planning.get("revision"):
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites Plan Review for another plan "
            "revision; the review must bind the exact current Planning subject"
        )
    if plan_review.get("planning_cycle") != planning.get("cycle"):
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites Plan Review for another planning "
            "cycle; the review must bind the exact current Planning subject"
        )
    planning_subject = planning.get("subject")
    review_subject = plan_review.get("subject")
    if (
        not isinstance(planning_subject, Mapping)
        or not isinstance(review_subject, Mapping)
        or any(
            planning_subject.get(key) != review_subject.get(key)
            for key in ("repository", "commit", "path", "blob")
        )
    ):
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites Plan Review whose subject does not "
            "match the exact approved Planning subject"
        )
    for key in ("repository", "commit", "path", "blob"):
        value = planning_subject.get(key)
        if not isinstance(value, str) or not value:
            raise LiveConsumerError(
                f"JIT trigger {trigger_id!r} cannot bind corrected authority: "
                "the approved Planning subject is malformed"
            )
    # Corrected-authority gate: the board selection must be the exact
    # current accepted Planning subject, which itself must resolve in Git;
    # the admission must reproduce the pin. Arbitrary in-roots files are
    # never eligible even when the Board and admission agree, and replanning
    # stales every previous pin/admission until refreshed to the new subject.
    pin = _validate_authority_pin(
        live_consumer.get("authority"),
        f"JIT trigger {trigger_id!r} board-selected authority",
    )
    authority_path = decision["authority_path"]
    if is_tracker_provenance(authority_path):
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites tracker authority "
            f"{authority_path!r}; tracker bookkeeping cannot satisfy corrected "
            "authority"
        )
    try:
        normalize_locator_path(authority_path, f"JIT trigger {trigger_id!r} authority")
    except ExactLocatorError as exc:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites wrong-source authority "
            f"{authority_path!r}; expected one of requirements/, decisions/, "
            f"planning/, workflow/: {exc}"
        ) from exc
    if not authority_path.startswith(AUTHORITY_ROOTS):
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites wrong-source authority "
            f"{authority_path!r}; expected one of requirements/, decisions/, "
            "planning/, workflow/"
        )
    resolved = git_reader(
        pin["repository"],
        pin["commit"],
        pin["path"],
    )
    if resolved != pin["blob"]:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} board-selected authority "
            f"{pin['path']!r} does not resolve to the pinned blob in Git; a "
            "forged or moved selection fails closed"
        )
    for field in ("repository", "commit", "path", "blob"):
        if pin[field] != planning_subject[field]:
            raise LiveConsumerError(
                f"JIT trigger {trigger_id!r} selects wrong-source authority_{field} "
                f"{pin[field]!r}; the exact current accepted Planning subject is "
                f"{planning_subject[field]!r}. Only the accepted subject is "
                "eligible — Board/admission agreement alone cannot authorize an "
                "arbitrary source."
            )
    for field in ("repository", "commit", "path", "blob"):
        if decision[f"authority_{field}"] != pin[field]:
            raise LiveConsumerError(
                f"JIT trigger {trigger_id!r} cites stale authority_{field} "
                f"{decision[f'authority_{field}']!r}; the board-selected authority "
                f"is {pin[field]!r}. The selection has moved — refresh the "
                "admission to the current selection."
            )
    # Predecessor gate: exact DONE predecessor result identity plus readback.
    predecessor_path = _require_safe_workstream_path(
        decision["predecessor_path"],
        f"JIT trigger {trigger_id!r} predecessor gate",
        workstream_id,
        "results/",
        ".md",
    )
    after_card = trigger.get("after_card")
    cards = board.get("cards", [])
    predecessor: Mapping[str, Any] | None = None
    if isinstance(cards, list):
        for card in cards:
            if isinstance(card, Mapping) and card.get("id") == after_card:
                predecessor = card
                break
    if predecessor is None:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} names unknown predecessor Card "
            f"{after_card!r}"
        )
    result = predecessor.get("result") if isinstance(predecessor, Mapping) else None
    if (
        not isinstance(result, Mapping)
        or result.get("path") != decision["predecessor_path"]
        or result.get("commit") != decision["predecessor_commit"]
        or result.get("blob") != decision["predecessor_blob"]
    ):
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites stale or forged predecessor "
            "result identity; the admission must bind the exact current DONE "
            "predecessor result"
        )
    if record_reader(predecessor_path) is None:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites predecessor result "
            f"{predecessor_path!r} that cannot be read back"
        )
    expected_subject = {
        "repository": decision["authority_repository"],
        "commit": decision["predecessor_commit"],
        "path": decision["predecessor_path"],
        "blob": decision["predecessor_blob"],
    }
    # Card review gate: GREEN attempt for the predecessor covering its subject.
    review_path = _require_safe_workstream_path(
        decision["review_path"],
        f"JIT trigger {trigger_id!r} review gate",
        workstream_id,
        "reviews/",
        ".toml",
    )
    review = _load_gate_toml(record_reader(review_path), review_path, "review")
    if review.get("workstream_id") != workstream_id:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites review from another workstream"
        )
    if review.get("attempt") != decision["review_attempt"]:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites stale review attempt "
            f"{decision['review_attempt']!r}; current is "
            f"{review.get('attempt')!r}"
        )
    if review.get("verdict") != "green":
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites review that is not GREEN"
        )
    if review.get("card_id") != after_card:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites review for another Card "
            f"{review.get('card_id')!r}; the review must cover the exact "
            "predecessor Card"
        )
    subject = review.get("subject")
    if (
        not isinstance(subject, Mapping)
        or any(subject.get(key) != expected_subject[key] for key in expected_subject)
    ):
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites review whose subject does not match "
            "the exact predecessor result; unrelated GREEN reviews cannot satisfy "
            "the gate"
        )
    # Milestone gate: GREEN milestone review covering the predecessor subject.
    milestone_path = _require_safe_workstream_path(
        decision["milestone_path"],
        f"JIT trigger {trigger_id!r} milestone gate",
        workstream_id,
        "reviews/",
        ".toml",
    )
    if milestone_path == review_path:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} reuses the Card review as its Milestone "
            "proof; the Milestone gate requires its own GREEN milestone review"
        )
    milestone = _load_gate_toml(
        record_reader(milestone_path), milestone_path, "milestone"
    )
    if milestone.get("workstream_id") != workstream_id:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites Milestone review from another "
            "workstream"
        )
    if milestone.get("attempt") != decision["milestone_attempt"]:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites stale Milestone attempt "
            f"{decision['milestone_attempt']!r}; current is "
            f"{milestone.get('attempt')!r}"
        )
    if milestone.get("verdict") != "green":
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites Milestone review that is not GREEN; "
            "the M03-style consumer stays held before Milestone GREEN"
        )
    if "card_id" in milestone:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites a Card-scoped review "
            f"(card_id {milestone.get('card_id')!r}) as Milestone proof; the "
            "Milestone gate requires milestone scope"
        )
    if "review_scope" in milestone and milestone.get("review_scope") != "milestone":
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites Milestone proof with review scope "
            f"{milestone.get('review_scope')!r}; expected milestone scope"
        )
    acceptance = milestone.get("acceptance")
    if not isinstance(acceptance, Mapping):
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites Milestone proof without a typed "
            "acceptance record; the Milestone gate requires authority acceptance "
            "bound to the accepted plan"
        )
    if acceptance.get("class") != "authority":
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites Milestone proof with acceptance "
            f"class {acceptance.get('class')!r}; expected authority acceptance "
            "bound to the accepted plan"
        )
    acceptance_path = acceptance.get("path")
    if not isinstance(acceptance_path, str) or not acceptance_path:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites Milestone proof without an "
            "acceptance path; the Milestone gate requires authority acceptance "
            "bound to the accepted plan"
        )
    if is_tracker_provenance(acceptance_path):
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites Milestone acceptance tracker "
            "pointer; tracker bookkeeping cannot satisfy the Milestone gate"
        )
    if not acceptance_path.startswith(AUTHORITY_ROOTS):
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites wrong-source Milestone acceptance "
            f"{acceptance_path!r}; expected accepted authority scope"
        )
    plan_subject_path = (
        planning_subject.get("path")
        if isinstance(planning_subject, Mapping)
        else None
    )
    if not plan_subject_path:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cannot bind Milestone scope: the approved "
            "Planning subject is missing"
        )
    if acceptance_path != plan_subject_path:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites Milestone acceptance "
            f"{acceptance_path!r} but the accepted plan subject is "
            f"{plan_subject_path!r}; wrong accepted plan scope fails closed"
        )
    milestone_subject = milestone.get("subject")
    if (
        not isinstance(milestone_subject, Mapping)
        or any(
            milestone_subject.get(key) != expected_subject[key]
            for key in expected_subject
        )
    ):
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} cites Milestone review whose subject does "
            "not match the exact predecessor result; unrelated GREEN reviews "
            "cannot satisfy the gate"
        )


def verify_live_consumer_records(
    board: Mapping[str, Any],
    *,
    record_reader: Callable[[str], str | None],
    git_reader: Callable[[str, str, str], str | None],
) -> None:
    """Verify cited live-consumer admission records plus gates by readback.

    Every ``admitted`` intended trigger's admission record must read back and
    prove this trigger's admission by content, and every cited gate record
    must read back and match by content as terminal. Boards without admitted
    triggers verify trivially, preserving ordinary and historical boards.
    """
    if not isinstance(board, Mapping):
        raise LiveConsumerError(
            "live-consumer verification requires a Task Board table"
        )
    workstream_id = board.get("workstream_id")
    if not isinstance(workstream_id, str) or not workstream_id.strip():
        raise LiveConsumerError(
            "live-consumer verification requires a workstream-bound Task Board"
        )
    triggers = board.get("jit_triggers", [])
    validate_live_consumer_gates(triggers, workstream_id)
    if not isinstance(triggers, list):
        return
    for index, trigger in enumerate(triggers):
        if not isinstance(trigger, Mapping):
            continue
        declaration = validate_live_consumer_declaration(
            trigger, workstream_id, f"task_board.jit_triggers[{index}].live_consumer"
        )
        if declaration is None or declaration.get("intended") is False:
            continue
        if declaration.get("readiness") != "admitted":
            continue
        admission = declaration.get("admission")
        assert isinstance(admission, Mapping)
        cited = admission["record"]
        verify_admission_decision(
            trigger,
            declaration,
            cited["path"],
            record_reader(cited["path"]),
            board,
            record_reader=record_reader,
            git_reader=git_reader,
        )


def require_admitted_trigger_consumption(
    board: Mapping[str, Any],
    trigger_id: str,
    *,
    record_reader: Callable[[str], str | None] | None = None,
    git_reader: Callable[[str, str, str], str | None] | None = None,
) -> str:
    """Require verified live-consumer admission before one trigger is consumed.

    ``board`` is the Task Board table and ``trigger_id`` names the JIT
    trigger Execution Prep is about to consume. Ordinary triggers without an
    intentional declaration consume normally. An intended trigger with
    ``pending`` readiness fails closed. An ``admitted`` trigger consumes when
    its citation shape validates; when both readers are given, the admission
    record plus every gate must additionally read back and verify by content.
    Returns the trigger id.
    """
    if not isinstance(board, Mapping):
        raise LiveConsumerError("trigger consumption requires a Task Board table")
    workstream_id = board.get("workstream_id")
    if not isinstance(workstream_id, str) or not workstream_id.strip():
        raise LiveConsumerError(
            "trigger consumption requires a workstream-bound Task Board"
        )
    triggers = board.get("jit_triggers", [])
    if not isinstance(triggers, list):
        raise LiveConsumerError(
            "task_board jit_triggers must be an array of trigger records"
        )
    target: Mapping[str, Any] | None = None
    for trigger in triggers:
        if isinstance(trigger, Mapping) and trigger.get("id") == trigger_id:
            target = trigger
            break
    if target is None:
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} does not exist on this Task Board; "
            "consuming an unknown trigger fails closed"
        )
    declaration = validate_live_consumer_declaration(
        target, workstream_id, "task_board.live_consumer"
    )
    if declaration is None or declaration.get("intended") is False:
        return trigger_id
    if declaration.get("readiness") == "pending":
        raise LiveConsumerError(
            f"JIT trigger {trigger_id!r} is an intended live consumer with pending "
            "readiness; verified corrected authority and every required "
            "Definition, Planning, review, predecessor and Milestone gate must be "
            "complete before the consumer materializes"
        )
    if record_reader is not None or git_reader is not None:
        if record_reader is None or git_reader is None:
            raise LiveConsumerError(
                f"JIT trigger {trigger_id!r} admission verification requires both "
                "a record reader and a Git reader; partial verification fails closed"
            )
        admission = declaration.get("admission")
        assert isinstance(admission, Mapping)
        cited = admission["record"]
        verify_admission_decision(
            target,
            declaration,
            cited["path"],
            record_reader(cited["path"]),
            board,
            record_reader=record_reader,
            git_reader=git_reader,
        )
    return trigger_id
