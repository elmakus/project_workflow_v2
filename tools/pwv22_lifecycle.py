from __future__ import annotations
from typing import Any, Callable, Mapping, Sequence

from tools.pwv22_native_foundation import NativeFoundationError
from tools.pwv22_native_results import accepted_dependency, exact_identity
from tools.pwv22_parallel import compatible_fan_in
from tools.pwv22_review import completion_allowed, typed_attempt
from tools.pwv22_recovery import classify_repair
from tools.pwv22_evolution import classify_evolution
from tools.pwv22_close import close_transition
from tools.pwv22_native_routing import QUALIFICATION, next_qualification


def _req(ok: bool, msg: str) -> None:
    if not ok:
        raise NativeFoundationError(msg)


def integrated_lifecycle(
    *,
    expected_results: Sequence[Mapping[str, Any]],
    results: Sequence[Mapping[str, Any]],
    constituent_acceptances: Sequence[Mapping[str, Any]],
    verify_identity: Callable[[Mapping[str, Any]], Any],
    review_attempt: Mapping[str, Any],
    expected_review_subject: Mapping[str, Any],
    expected_acceptance_surface: Mapping[str, Any],
    findings: Sequence[Mapping[str, Any]],
    qualification_completed: Sequence[str],
    repair_issue: Mapping[str, Any] | None,
    evolution: Mapping[str, Any],
    close_record: Mapping[str, Any],
    fan_in: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compose the accepted S06-S10 contracts without replacing their validators."""
    _req(len(expected_results) == len(results) == len(constituent_acceptances) and bool(results),
         "incomplete constituent Result set")

    accepted = []
    for expected, result, acceptance in zip(expected_results, results, constituent_acceptances):
        accepted.append(accepted_dependency(expected, result, acceptance, verify_identity))

    if fan_in is not None:
        integrated = compatible_fan_in(
            fan_in["expected_card_ids"],
            fan_in["expected_card_subjects"],
            expected_results,
            results,
            fan_in["acceptance_identities"],
            fan_in["sibling_claims"],
            fan_in["admission_identity"],
            fan_in["read_admission"],
            fan_in["admission_acceptance_identity"],
            fan_in["read_acceptance"],
            verify_identity,
            fan_in["compatibility"],
        )
        _req([x["result_artifact"] for x in integrated] == [x["result_artifact"] for x in accepted],
             "fan-in changed accepted constituent set")

    attempt = typed_attempt(review_attempt)
    _req(attempt["subject"] == exact_identity(expected_review_subject), "stale integrated review subject")
    _req(attempt["acceptance_surface"] == exact_identity(expected_acceptance_surface),
         "wrong integrated review acceptance surface")
    _req(attempt["verdict"] == "GREEN", "integrated review is not GREEN")
    _req(completion_allowed(findings), "blocking or unknown finding prevents lifecycle completion")

    _req(next_qualification(qualification_completed) == "done", "qualification remains incomplete")

    if repair_issue is not None:
        repair = classify_repair(repair_issue)
        _req(repair["class"] == "mechanical", "semantic repair requires return to owner")

    disposition = classify_evolution(**evolution)
    _req(disposition in ("preserve", "revalidate"), "stale/recovery evolution prevents Close")
    _req(close_record.get("evolution_disposition") == disposition, "Close evolution disposition mismatch")

    closed = close_transition(close_record)
    return {
        "state": closed["state"],
        "accepted_result_ids": [x["result_id"] for x in accepted],
        "qualification": list(QUALIFICATION),
        "evolution_disposition": disposition,
        "durable_confirmation": closed["durable_confirmation"],
    }
