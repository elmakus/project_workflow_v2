"""Runtime-neutral deterministic continuation completion contract."""

from __future__ import annotations

from dataclasses import dataclass


class ContinuationContractError(ValueError):
    """Raised when a route result cannot be classified safely."""


@dataclass(frozen=True)
class ContinuationDecision:
    action: str
    reason: str

    @property
    def legal_return(self) -> bool:
        return self.action == "return"


def classify_route_completion(*, disposition: str, obligation: str) -> ContinuationDecision:
    """Classify whether a fresh canonical route permits normal invocation return.

    Semantic owner policy remains outside this helper. It only enforces the
    completion boundary: real router stops may return; every non-stop route
    must continue through the exact selected obligation and reroute again after
    durable reconciliation.
    """
    if not isinstance(disposition, str) or not disposition:
        raise ContinuationContractError("missing route disposition")
    if not isinstance(obligation, str) or not obligation:
        raise ContinuationContractError("missing route obligation")

    if disposition == "stop":
        return ContinuationDecision(
            "return",
            "fresh canonical route established a real workflow stop",
        )
    if disposition == "route":
        return ContinuationDecision(
            "continue",
            "non-stop semantic obligation must be consumed and freshly rerouted after reconciliation",
        )
    if disposition == "recovery":
        return ContinuationDecision(
            "recover",
            "fail-closed recovery is not semantic success or a normal workflow stop",
        )
    raise ContinuationContractError(f"unknown route disposition {disposition!r}")


@dataclass(frozen=True)
class ProgressObservation:
    fingerprint: str
    evidence_epoch: str


def classify_progress(
    *,
    previous: ProgressObservation,
    current: ProgressObservation,
    seen: frozenset[tuple[str, str]] = frozenset(),
) -> str:
    """Fail closed on claimed success without semantic progress or on evidence-free cycles.

    Fingerprints and evidence epochs are ephemeral values derived by the caller
    only from authoritative durable semantic inputs. Runtime identity is
    deliberately absent.
    """
    for item in (previous.fingerprint, previous.evidence_epoch, current.fingerprint, current.evidence_epoch):
        if not isinstance(item, str) or not item.strip():
            raise ContinuationContractError("progress identities must be non-empty")

    if current == previous:
        raise ContinuationContractError(
            "claimed reconciliation produced no authoritative semantic progress"
        )

    key = (current.fingerprint, current.evidence_epoch)
    if key in seen:
        raise ContinuationContractError(
            "semantic continuation cycle repeated without new accepted evidence or authority"
        )
    return "continue"


def resume_action(*, durable_semantic_result: bool, external_effect_uncertain: bool) -> str:
    """Choose restart behavior without replaying already durable semantic work."""
    if external_effect_uncertain:
        return "readback_external_effect_before_retry"
    if durable_semantic_result:
        return "reconcile_without_replay"
    return "execute_selected_obligation"
