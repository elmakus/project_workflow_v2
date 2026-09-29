"""Runtime-neutral deterministic continuation completion contract."""

from __future__ import annotations

from dataclasses import dataclass


class ContinuationContractError(ValueError):
    """Raised when a continuation input cannot be classified safely."""


@dataclass(frozen=True)
class ContinuationDecision:
    action: str
    reason: str

    @property
    def legal_return(self) -> bool:
        return self.action == "return"


def classify_route_completion(*, disposition: str, obligation: str) -> ContinuationDecision:
    if not isinstance(disposition, str) or not disposition:
        raise ContinuationContractError("missing route disposition")
    if not isinstance(obligation, str) or not obligation:
        raise ContinuationContractError("missing route obligation")
    if disposition == "stop":
        return ContinuationDecision("return", "fresh canonical route established a real workflow stop")
    if disposition == "route":
        return ContinuationDecision("continue", "non-stop semantic obligation must be consumed and freshly rerouted after reconciliation")
    if disposition == "recovery":
        return ContinuationDecision("recover", "fail-closed recovery is not semantic success or a normal workflow stop")
    raise ContinuationContractError(f"unknown route disposition {disposition!r}")


TERMINAL_SUCCESS = frozenset({"success", "passed"})
TERMINAL_FAILURE = frozenset({"failure", "failed", "cancelled", "timed_out", "action_required"})
PENDING_EXTERNAL = frozenset({"queued", "requested", "waiting", "pending", "in_progress"})


def classify_external_evidence(
    *,
    status: str,
    conclusion: str | None = None,
    exact_subject_observed: bool = True,
) -> str:
    """Classify exact-subject external evidence without claiming semantic reconciliation."""
    if not isinstance(status, str) or not status.strip():
        raise ContinuationContractError("external evidence status must be non-empty")
    if not isinstance(exact_subject_observed, bool):
        raise ContinuationContractError("exact_subject_observed must be boolean")
    normalized = status.strip().lower()
    normalized_conclusion = conclusion.strip().lower() if isinstance(conclusion, str) else None
    if conclusion is not None and (not isinstance(conclusion, str) or not normalized_conclusion):
        raise ContinuationContractError("external evidence conclusion must be non-empty when supplied")
    if normalized == "completed":
        if not exact_subject_observed:
            raise ContinuationContractError("completed evidence is not bound to the exact subject")
        if normalized_conclusion in TERMINAL_SUCCESS:
            return "terminal_success"
        if normalized_conclusion in TERMINAL_FAILURE:
            return "terminal_failure"
        raise ContinuationContractError("completed evidence requires a supported terminal conclusion")
    if normalized in TERMINAL_SUCCESS:
        if not exact_subject_observed:
            raise ContinuationContractError("terminal success is not bound to the exact subject")
        return "terminal_success"
    if normalized in TERMINAL_FAILURE:
        if not exact_subject_observed:
            raise ContinuationContractError("terminal failure is not bound to the exact subject")
        return "terminal_failure"
    if normalized in PENDING_EXTERNAL:
        if not exact_subject_observed:
            raise ContinuationContractError("pending evidence is not bound to the exact subject")
        return "pending_observation"
    if normalized == "missing":
        return "readback_exact_subject"
    raise ContinuationContractError(f"unsupported external evidence status {status!r}")


@dataclass(frozen=True)
class ProgressObservation:
    fingerprint: str
    evidence_epoch: str


def classify_progress(*, previous: ProgressObservation, current: ProgressObservation, seen: frozenset[tuple[str, str]] = frozenset()) -> str:
    for item in (previous.fingerprint, previous.evidence_epoch, current.fingerprint, current.evidence_epoch):
        if not isinstance(item, str) or not item.strip():
            raise ContinuationContractError("progress identities must be non-empty")
    if current == previous:
        raise ContinuationContractError("claimed reconciliation produced no authoritative semantic progress")
    key = (current.fingerprint, current.evidence_epoch)
    if key in seen:
        raise ContinuationContractError("semantic continuation cycle repeated without new accepted evidence or authority")
    return "continue"


def resume_action(*, durable_semantic_result: bool, external_effect_uncertain: bool) -> str:
    if external_effect_uncertain:
        return "readback_external_effect_before_retry"
    if durable_semantic_result:
        return "reconcile_without_replay"
    return "execute_selected_obligation"
