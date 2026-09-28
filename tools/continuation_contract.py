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
