#!/usr/bin/env python3
"""Runtime-neutral review-context, pass and convergence semantic helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass


REVIEW_KINDS = frozenset({"discovery", "closure_verification"})
REVIEW_SCOPE_DISCOVERY_CEILINGS = {
    "card": 5,
    "milestone": 4,
    "final": 3,
}
PER_CLASS_CLOSURE_FAILURE_CEILING = 3
CAUSAL_SCOPE_KEYS = (
    "known_findings",
    "defect_classes",
    "root_cause_evidence",
    "repair_diff",
    "regression_evidence",
    "reachable_callers",
    "consumers",
    "providers",
    "contracts",
    "sibling_representations",
    "negative_space",
)
CONVERGENCE_FIELDS = frozenset({
    "review_scope",
    "review_epoch",
    "epoch_reset_basis",
    "epoch_reset_subject",
    "material_defect_class_ids",
    "failed_material_defect_class_ids",
    "post_convergence_validation",
    "convergence_basis",
})
LOAD_BEARING_SURFACES = frozenset({
    "acceptance",
    "correctness",
    "safety",
    "security",
    "data_integrity",
    "dependency",
    "compatibility",
    "invariant",
    "contract",
    "required_evidence",
})
ADVISORY_CATEGORIES = frozenset({
    "advisory",
    "stylistic",
    "optional_cleanup",
    "preference",
    "speculative_hardening",
})
OPEN_OBSERVATION_DISPOSITION = "open"
OBSERVATION_DISPOSITIONS = frozenset({
    "resolved",
    "cleanup_candidate",
    "deferred",
    "promoted",
    "tracked",
})
FORBIDDEN_DOWNGRADE_BASES = frozenset({
    "convenience",
    "repair_cost",
    "reviewer_fatigue",
    "desire_to_finish",
})
TRACKER_PROVENANCE_MARKERS = (
    "tracker.toml",
    "issue#",
    "issue #",
    "github.com",
)
OBSERVATION_AWARENESS_KEYS = (
    "finding_severity",
    "observations",
    "observation_updates",
)


class ReviewContractError(ValueError):
    """Raised when review-pass semantic evidence is incomplete or contradictory."""


@dataclass(frozen=True)
class ReviewConvergenceState:
    """Derived convergence state for the latest stable authority/acceptance epoch."""

    review_scope: str | None
    review_epoch: str | None
    discovery_epochs: int
    discovery_ceiling: int | None
    seen_defect_classes: frozenset[str]
    failed_closure_rounds: Mapping[str, int]
    convergence_required: bool
    post_convergence_attempt: str | None
    post_convergence_verdict: str | None


def select_review_realization(
    *,
    current_context_produced_subject: bool,
    independent_context_available: bool,
) -> str:
    """Choose transient review realization without persisting runtime identity."""
    if not current_context_produced_subject:
        return "current_context"
    if independent_context_available:
        return "internal_independent"
    return "fresh_context"


def review_kind(attempt: Mapping[str, object]) -> str:
    """Return explicit PWv2.1 review kind, treating historical attempts as discovery."""
    kind = attempt.get("review_kind", "discovery")
    if kind not in REVIEW_KINDS:
        raise ReviewContractError(f"unsupported review kind {kind!r}")
    return str(kind)


def convergence_fields_present(attempt: Mapping[str, object]) -> bool:
    """Return whether an attempt uses the PWv2.1 convergence-aware shape."""
    return "review_epoch" in attempt


def material_defect_classes(attempt: Mapping[str, object]) -> frozenset[str]:
    """Read the durable material defect-class identity set from an aware attempt."""
    raw = attempt.get("material_defect_class_ids")
    if not isinstance(raw, list) or not all(
        isinstance(item, str) and item.strip() for item in raw
    ):
        raise ReviewContractError(
            "convergence-aware review attempt must record material_defect_class_ids"
        )
    if len(set(raw)) != len(raw):
        raise ReviewContractError("material_defect_class_ids must be unique")
    return frozenset(raw)


def failed_material_defect_classes(attempt: Mapping[str, object]) -> frozenset[str]:
    """Read the material defect classes that actually failed a RED closure pass."""
    raw = attempt.get("failed_material_defect_class_ids", [])
    if not isinstance(raw, list) or not all(
        isinstance(item, str) and item.strip() for item in raw
    ):
        raise ReviewContractError(
            "failed_material_defect_class_ids must contain non-empty strings"
        )
    if len(set(raw)) != len(raw):
        raise ReviewContractError("failed_material_defect_class_ids must be unique")
    return frozenset(raw)


def _review_subject_content_identity(attempt: Mapping[str, object]) -> tuple[str, str, str]:
    """Return reviewed content identity for repair-round accounting.

    Commit-only movement of the same repository/path/blob is not a new repaired
    content state and therefore must not consume another repair/closure round.
    """
    subject = attempt.get("subject")
    if not isinstance(subject, Mapping):
        raise ReviewContractError("RED closure verification requires exact reviewed subject")
    values = tuple(subject.get(key) for key in ("repository", "path", "blob"))
    if not all(isinstance(value, str) and value for value in values):
        raise ReviewContractError("RED closure verification requires exact reviewed subject")
    return values  # type: ignore[return-value]


def review_convergence_state(
    attempts: Iterable[Mapping[str, object]],
    *,
    expected_review_scope: str | None = None,
) -> ReviewConvergenceState:
    """Derive review-loop accounting from durable attempt history.

    Pre-convergence terminal history is intentionally ignored. A changed
    review_epoch resets derived counters; state-contract validation owns the
    requirement that such a reset has an accepted durable redesign basis.
    When expected_review_scope is set, every convergence-aware attempt must
    bind to that review obligation owner instead of a self-declared scope.
    """
    if expected_review_scope is not None and expected_review_scope not in REVIEW_SCOPE_DISCOVERY_CEILINGS:
        raise ReviewContractError(f"unsupported expected review scope {expected_review_scope!r}")
    scope: str | None = None
    epoch: str | None = None
    discovery_epochs = 0
    seen_classes: set[str] = set()
    failed_rounds: dict[str, int] = {}
    last_failed_round_content: dict[tuple[str, str], tuple[str, str, str]] = {}
    attempts_by_id: dict[str, Mapping[str, object]] = {}
    post_attempt: str | None = None
    post_verdict: str | None = None

    for attempt in attempts:
        attempt_id = attempt.get("attempt")
        if isinstance(attempt_id, str) and attempt_id:
            attempts_by_id[attempt_id] = attempt
        if not convergence_fields_present(attempt):
            continue

        raw_scope = attempt.get("review_scope")
        raw_epoch = attempt.get("review_epoch")
        if raw_scope not in REVIEW_SCOPE_DISCOVERY_CEILINGS:
            raise ReviewContractError(f"unsupported review scope {raw_scope!r}")
        if expected_review_scope is not None and raw_scope != expected_review_scope:
            raise ReviewContractError(
                f"review scope {raw_scope!r} does not match expected review owner scope {expected_review_scope!r}"
            )
        if not isinstance(raw_epoch, str) or not raw_epoch.strip():
            raise ReviewContractError("review_epoch must be a non-empty string")

        if epoch is None or raw_epoch != epoch:
            scope = str(raw_scope)
            epoch = raw_epoch
            discovery_epochs = 0
            seen_classes = set()
            failed_rounds = {}
            last_failed_round_content = {}
            post_attempt = None
            post_verdict = None
        elif raw_scope != scope:
            raise ReviewContractError("review scope cannot change inside one review epoch")

        classes = material_defect_classes(attempt)
        kind = review_kind(attempt)
        verdict = attempt.get("verdict")
        is_post = attempt.get("post_convergence_validation") is True

        if is_post:
            attempt_id = attempt.get("attempt")
            if not isinstance(attempt_id, str) or not attempt_id:
                raise ReviewContractError("post-convergence validation requires attempt identity")
            if post_attempt is not None:
                raise ReviewContractError(
                    "only one post-convergence validation is allowed per review epoch"
                )
            post_attempt = attempt_id
            post_verdict = str(verdict) if isinstance(verdict, str) else None

        if kind == "discovery" and verdict == "red" and not is_post:
            if classes - seen_classes:
                discovery_epochs += 1
            seen_classes.update(classes)
        elif kind == "closure_verification":
            # Closure may introduce durable class identity when adapting an open
            # explicit T01 discovery. That class is already known and therefore
            # must not count as a new discovery epoch if it later recurs.
            seen_classes.update(classes)
            if verdict == "red":
                failed_classes = failed_material_defect_classes(attempt)
                if not failed_classes:
                    raise ReviewContractError(
                        "RED closure verification must record failed_material_defect_class_ids"
                    )
                if not failed_classes.issubset(classes):
                    raise ReviewContractError(
                        "failed_material_defect_class_ids must be a subset of verified material defect classes"
                    )
                source_id = attempt.get("source_discovery_attempt")
                source = attempts_by_id.get(source_id) if isinstance(source_id, str) else None
                if source is None or source is attempt:
                    raise ReviewContractError(
                        "RED closure verification requires an earlier source discovery attempt"
                    )
                repaired_content = _review_subject_content_identity(attempt)
                source_content = _review_subject_content_identity(source)
                for defect_class in failed_classes:
                    round_key = (defect_class, str(source_id))
                    previous_content = last_failed_round_content.get(
                        round_key, source_content
                    )
                    if (
                        repaired_content != source_content
                        and repaired_content != previous_content
                    ):
                        failed_rounds[defect_class] = failed_rounds.get(defect_class, 0) + 1
                    # A RED closure over source content is not itself a repair round,
                    # but it still becomes the preceding reviewed state. Returning
                    # later to an older repaired state is therefore another failed
                    # repair transition rather than a globally deduplicated no-op.
                    last_failed_round_content[round_key] = repaired_content

    if scope is None or epoch is None:
        return ReviewConvergenceState(
            review_scope=None,
            review_epoch=None,
            discovery_epochs=0,
            discovery_ceiling=None,
            seen_defect_classes=frozenset(),
            failed_closure_rounds={},
            convergence_required=False,
            post_convergence_attempt=None,
            post_convergence_verdict=None,
        )

    ceiling = REVIEW_SCOPE_DISCOVERY_CEILINGS[scope]
    required = (
        discovery_epochs >= ceiling
        or any(
            rounds >= PER_CLASS_CLOSURE_FAILURE_CEILING
            for rounds in failed_rounds.values()
        )
    )
    return ReviewConvergenceState(
        review_scope=scope,
        review_epoch=epoch,
        discovery_epochs=discovery_epochs,
        discovery_ceiling=ceiling,
        seen_defect_classes=frozenset(seen_classes),
        failed_closure_rounds=dict(failed_rounds),
        convergence_required=required,
        post_convergence_attempt=post_attempt,
        post_convergence_verdict=post_verdict,
    )


def validate_discovery_surface(
    *,
    applicable_acceptance: Iterable[str],
    evaluated_acceptance: Iterable[str],
    stopped_at_first_blocker: bool,
) -> frozenset[str]:
    """Require a discovery pass to cover the complete applicable acceptance surface."""
    applicable = frozenset(item for item in applicable_acceptance if item)
    evaluated = frozenset(item for item in evaluated_acceptance if item)
    if stopped_at_first_blocker:
        raise ReviewContractError("fresh discovery cannot stop at the first blocker")
    missing = applicable - evaluated
    if missing:
        raise ReviewContractError(
            "fresh discovery omitted applicable acceptance: " + ", ".join(sorted(missing))
        )
    return evaluated


def required_closure_scope(scope: Mapping[str, Iterable[str]]) -> frozenset[str]:
    """Build the complete materially implicated closure surface.

    Every causal category must be explicitly accounted for. Categories may be
    empty when no material member exists, while known findings, defect class,
    root-cause evidence, repair diff and regression evidence must each contain
    at least one concrete item.
    """
    missing_keys = [key for key in CAUSAL_SCOPE_KEYS if key not in scope]
    if missing_keys:
        raise ReviewContractError(
            "closure scope omitted causal categories: " + ", ".join(missing_keys)
        )

    normalized: dict[str, frozenset[str]] = {}
    for key in CAUSAL_SCOPE_KEYS:
        raw = scope[key]
        if isinstance(raw, (str, bytes)):
            raise ReviewContractError(f"closure scope {key!r} must be an iterable of concrete items")
        values = frozenset(item for item in raw if isinstance(item, str) and item)
        normalized[key] = values

    for key in (
        "known_findings",
        "defect_classes",
        "root_cause_evidence",
        "repair_diff",
        "regression_evidence",
    ):
        if not normalized[key]:
            raise ReviewContractError(f"closure scope {key!r} must not be empty")

    required: set[str] = set()
    for values in normalized.values():
        required.update(values)
    return frozenset(required)


def validate_closure_surface(
    *,
    scope: Mapping[str, Iterable[str]],
    evaluated_surface: Iterable[str],
) -> frozenset[str]:
    """Require closure verification to cover the known finding and causal blast radius."""
    required = required_closure_scope(scope)
    evaluated = frozenset(item for item in evaluated_surface if item)
    missing = required - evaluated
    if missing:
        raise ReviewContractError(
            "closure verification omitted materially implicated surface: "
            + ", ".join(sorted(missing))
        )
    return evaluated


def remaining_closure_findings(
    attempts: Iterable[Mapping[str, object]],
    source_discovery_attempt: str,
) -> frozenset[str]:
    """Return source-discovery findings not yet covered by GREEN closure attempts."""
    source_findings: set[str] | None = None
    closed: set[str] = set()

    for attempt in attempts:
        if attempt.get("attempt") == source_discovery_attempt:
            if review_kind(attempt) != "discovery" or attempt.get("verdict") != "red":
                raise ReviewContractError("closure source must be a RED discovery attempt")
            raw = attempt.get("material_finding_ids")
            if not isinstance(raw, list) or not all(
                isinstance(item, str) and item for item in raw
            ):
                raise ReviewContractError(
                    "closure source discovery must record material_finding_ids"
                )
            source_findings = set(raw)
            continue

        if source_findings is None:
            continue
        if (
            attempt.get("review_kind") == "closure_verification"
            and attempt.get("source_discovery_attempt") == source_discovery_attempt
            and attempt.get("verdict") == "green"
        ):
            raw = attempt.get("material_finding_ids")
            if not isinstance(raw, list) or not all(
                isinstance(item, str) and item for item in raw
            ):
                raise ReviewContractError(
                    "GREEN closure attempt must record material_finding_ids"
                )
            closed.update(raw)

    if source_findings is None:
        raise ReviewContractError("closure source discovery attempt was not found")
    return frozenset(source_findings - closed)


def can_finalize_review_obligation(attempt: Mapping[str, object]) -> bool:
    """Only a GREEN fresh discovery pass may satisfy the review obligation.

    A GREEN closure pass proves known-finding closure but intentionally requires
    a subsequent fresh full-scope discovery pass.
    """
    return attempt.get("verdict") == "green" and review_kind(attempt) == "discovery"


def attempt_is_observation_aware(attempt: Mapping[str, object]) -> bool:
    """Return whether an attempt carries explicit severity/observation records."""
    return any(bool(attempt.get(key)) for key in OBSERVATION_AWARENESS_KEYS)


def _require_terminal_observation_carrier(attempt: Mapping[str, object]) -> None:
    if attempt.get("verdict") not in {"green", "red"}:
        raise ReviewContractError(
            "severity/observation records require a terminal attempt with durable verdict evidence"
        )


def finding_severity_records(attempt: Mapping[str, object]) -> dict[str, dict[str, str]]:
    """Parse load-bearing evidence records keyed by blocking finding id."""
    raw = attempt.get("finding_severity", [])
    if not raw:
        return {}
    _require_terminal_observation_carrier(attempt)
    if not isinstance(raw, list):
        raise ReviewContractError("finding_severity must be an array of evidence records")
    records: dict[str, dict[str, str]] = {}
    for entry in raw:
        if not isinstance(entry, Mapping):
            raise ReviewContractError("finding_severity entries must be tables")
        finding_id = entry.get("id")
        surface = entry.get("surface")
        evidence = entry.get("evidence")
        if not isinstance(finding_id, str) or not finding_id.strip():
            raise ReviewContractError("finding_severity entries require a non-empty id")
        if finding_id in records:
            raise ReviewContractError(
                f"duplicate finding_severity record for {finding_id!r}"
            )
        if surface not in LOAD_BEARING_SURFACES:
            raise ReviewContractError(
                f"unknown load-bearing surface {surface!r} for finding {finding_id!r}"
            )
        if not isinstance(evidence, str) or not evidence.strip():
            raise ReviewContractError(
                f"finding {finding_id!r} lacks concrete load-bearing evidence"
            )
        records[finding_id] = {
            "id": finding_id,
            "surface": str(surface),
            "evidence": evidence,
        }
    return records


def validate_finding_severity(
    *,
    material_finding_ids: Iterable[str],
    severity: Mapping[str, Mapping[str, object]],
    require_complete: bool,
) -> frozenset[str]:
    """Bind every blocking finding to a load-bearing surface plus concrete evidence.

    RED discovery requires complete coverage. Closure verification inherits its
    source discovery classification and is validated for well-formedness only.
    """
    material = frozenset(material_finding_ids)
    for finding_id, record in severity.items():
        if finding_id not in material:
            raise ReviewContractError(
                f"finding_severity record {finding_id!r} names an unknown blocking finding"
            )
        surface = record.get("surface")
        evidence = record.get("evidence")
        if surface not in LOAD_BEARING_SURFACES:
            raise ReviewContractError(
                f"unknown load-bearing surface {surface!r} for finding {finding_id!r}"
            )
        if not isinstance(evidence, str) or not evidence.strip():
            raise ReviewContractError(
                f"finding {finding_id!r} lacks concrete load-bearing evidence"
            )
    if require_complete:
        missing = material - frozenset(severity)
        if missing:
            raise ReviewContractError(
                "RED discovery lacks load-bearing evidence for blocking findings: "
                + ", ".join(sorted(missing))
            )
    return material


def validate_verdict_severity(
    *,
    verdict: object,
    load_bearing_ids: Iterable[str],
    advisory_ids: Iterable[str],
) -> frozenset[str]:
    """Require RED to rest on load-bearing evidence; advisory-only attempts stay GREEN."""
    load_bearing = frozenset(item for item in load_bearing_ids if item)
    advisory = frozenset(item for item in advisory_ids if item)
    if verdict == "red" and not load_bearing:
        if advisory:
            raise ReviewContractError(
                "advisory observations alone cannot keep the subject RED"
            )
        raise ReviewContractError("RED requires at least one load-bearing finding")
    return load_bearing


def validate_observation_provenance(
    *,
    evidence: object,
    origin_evidence_path: object,
) -> str:
    """Require canonical review evidence; tracker pointers are never provenance."""
    if not isinstance(evidence, str) or not evidence.strip():
        raise ReviewContractError("observation requires concrete originating evidence")
    if not isinstance(origin_evidence_path, str) or not origin_evidence_path.strip():
        raise ReviewContractError("observation requires an originating review evidence path")
    for candidate in (evidence, origin_evidence_path):
        lowered = candidate.lower()
        if any(marker in lowered for marker in TRACKER_PROVENANCE_MARKERS):
            raise ReviewContractError(
                "tracker/Issue pointers cannot serve as observation provenance or evidence"
            )
    return evidence


def observation_records(attempt: Mapping[str, object]) -> list[dict[str, str]]:
    """Parse advisory observations introduced by one terminal attempt."""
    raw = attempt.get("observations", [])
    if not raw:
        return []
    _require_terminal_observation_carrier(attempt)
    if not isinstance(raw, list):
        raise ReviewContractError("observations must be an array of observation records")
    records: list[dict[str, str]] = []
    seen: set[str] = set()
    for entry in raw:
        if not isinstance(entry, Mapping):
            raise ReviewContractError("observation entries must be tables")
        observation_id = entry.get("id")
        category = entry.get("category")
        evidence = entry.get("evidence")
        disposition = entry.get("disposition")
        basis = entry.get("disposition_basis", "")
        if not isinstance(observation_id, str) or not observation_id.strip():
            raise ReviewContractError("observation entries require a non-empty id")
        if observation_id in seen:
            raise ReviewContractError(
                f"duplicate observation {observation_id!r} in one attempt"
            )
        seen.add(observation_id)
        if category not in ADVISORY_CATEGORIES:
            raise ReviewContractError(
                f"unknown advisory category {category!r} for observation {observation_id!r}"
            )
        if not isinstance(evidence, str) or not evidence.strip():
            raise ReviewContractError(
                f"observation {observation_id!r} lacks concrete originating evidence"
            )
        validate_observation_provenance(
            evidence=evidence, origin_evidence_path=evidence
        )
        if disposition != OPEN_OBSERVATION_DISPOSITION and disposition not in OBSERVATION_DISPOSITIONS:
            raise ReviewContractError(
                f"observation {observation_id!r} has unknown disposition {disposition!r}"
            )
        if not isinstance(basis, str):
            raise ReviewContractError(
                f"observation {observation_id!r} has a non-string disposition_basis"
            )
        if disposition == OPEN_OBSERVATION_DISPOSITION and basis.strip():
            raise ReviewContractError(
                f"open observation {observation_id!r} must not claim disposition_basis"
            )
        if disposition != OPEN_OBSERVATION_DISPOSITION and not basis.strip():
            raise ReviewContractError(
                f"observation {observation_id!r} reconciled as {disposition!r} requires disposition_basis"
            )
        records.append({
            "id": observation_id,
            "category": str(category),
            "evidence": evidence,
            "disposition": str(disposition),
            "disposition_basis": basis,
        })
    return records


def observation_update_records(attempt: Mapping[str, object]) -> list[dict[str, str]]:
    """Parse open-to-terminal observation reconciliation records from one attempt."""
    raw = attempt.get("observation_updates", [])
    if not raw:
        return []
    _require_terminal_observation_carrier(attempt)
    if not isinstance(raw, list):
        raise ReviewContractError("observation_updates must be an array of update records")
    records: list[dict[str, str]] = []
    for entry in raw:
        if not isinstance(entry, Mapping):
            raise ReviewContractError("observation update entries must be tables")
        observation_id = entry.get("id")
        disposition = entry.get("disposition")
        basis = entry.get("basis")
        if not isinstance(observation_id, str) or not observation_id.strip():
            raise ReviewContractError("observation updates require a non-empty id")
        if disposition not in OBSERVATION_DISPOSITIONS:
            raise ReviewContractError(
                f"observation {observation_id!r} must reconcile to a terminal disposition, "
                f"got {disposition!r}"
            )
        if not isinstance(basis, str) or not basis.strip():
            raise ReviewContractError(
                f"observation {observation_id!r} reconciliation requires a disposition basis"
            )
        records.append({
            "id": observation_id,
            "disposition": str(disposition),
            "basis": basis,
        })
    return records


def _attempt_epoch_bucket(attempt: Mapping[str, object]) -> str:
    epoch = attempt.get("review_epoch")
    return epoch if isinstance(epoch, str) else ""


def derive_observation_state(
    attempts: Iterable[Mapping[str, object]],
) -> dict[str, dict[str, str]]:
    """Derive durable observation dispositions from append-only attempt history.

    Introductions stay open until exactly one terminal reconciliation. Material
    finding ids and observation ids must remain disjoint inside one review
    epoch: relabeling a load-bearing finding as advisory is a downgrade, and a
    promoted observation keeps its advisory identity while follow-up blocking
    work uses a new finding id. Convenience, repair cost, reviewer fatigue and
    desire to finish never justify such relabeling.
    """
    ordered = list(attempts)
    material_by_epoch: dict[str, set[str]] = {}
    for attempt in ordered:
        raw = attempt.get("material_finding_ids", [])
        if not raw:
            continue
        if not isinstance(raw, list) or not all(
            isinstance(item, str) and item for item in raw
        ):
            raise ReviewContractError("material_finding_ids must contain non-empty strings")
        material_by_epoch.setdefault(_attempt_epoch_bucket(attempt), set()).update(raw)

    state: dict[str, dict[str, str]] = {}
    for attempt in ordered:
        attempt_id = attempt.get("attempt")
        evidence_path = attempt.get("evidence_path", "")
        for record in observation_records(attempt):
            observation_id = record["id"]
            if observation_id in state:
                raise ReviewContractError(
                    f"observation {observation_id!r} is already recorded with durable provenance"
                )
            if observation_id in material_by_epoch.get(_attempt_epoch_bucket(attempt), set()):
                raise ReviewContractError(
                    f"observation {observation_id!r} downgrades a load-bearing finding; "
                    "convenience, repair cost, reviewer fatigue and desire to finish "
                    "never justify a downgrade"
                )
            if not isinstance(attempt_id, str) or not attempt_id:
                raise ReviewContractError("observation introduction requires attempt identity")
            validate_observation_provenance(
                evidence=record["evidence"], origin_evidence_path=evidence_path
            )
            state[observation_id] = {
                "id": observation_id,
                "category": record["category"],
                "evidence": record["evidence"],
                "origin_attempt": attempt_id,
                "origin_evidence_path": str(evidence_path),
                "disposition": record["disposition"],
                "basis": record["disposition_basis"],
            }
        for update in observation_update_records(attempt):
            observation_id = update["id"]
            current = state.get(observation_id)
            if current is None:
                raise ReviewContractError(
                    f"observation update targets unknown observation {observation_id!r}"
                )
            if current["disposition"] != OPEN_OBSERVATION_DISPOSITION:
                raise ReviewContractError(
                    f"observation {observation_id!r} is already reconciled as "
                    f"{current['disposition']!r}"
                )
            current["disposition"] = update["disposition"]
            current["basis"] = update["basis"]

    for attempt in ordered:
        raw = attempt.get("material_finding_ids", [])
        if not raw:
            continue
        for finding_id in raw:
            entry = state.get(finding_id)
            if entry is not None and _attempt_epoch_bucket(attempt) == _epoch_of_origin(
                ordered, entry["origin_attempt"]
            ):
                raise ReviewContractError(
                    f"blocking finding {finding_id!r} reuses advisory observation identity; "
                    "mark the observation promoted and record follow-up blocking work "
                    "under a new finding id"
                )
    return state


def _epoch_of_origin(
    attempts: list[Mapping[str, object]], origin_attempt: str
) -> str:
    for attempt in attempts:
        if attempt.get("attempt") == origin_attempt:
            return _attempt_epoch_bucket(attempt)
    return ""


def unreconciled_observations(state: Mapping[str, Mapping[str, object]]) -> frozenset[str]:
    """Return observation ids that are still open."""
    return frozenset(
        observation_id
        for observation_id, entry in state.items()
        if entry.get("disposition") == OPEN_OBSERVATION_DISPOSITION
    )
