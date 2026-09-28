import pytest

from tools.continuation_contract import (
    ContinuationContractError,
    classify_route_completion,
)


@pytest.mark.parametrize(
    "obligation",
    [
        "execution",
        "execution_prep",
        "post_review_finalization",
        "result_reconciliation",
        "review",
        "research",
        "research_cleanup",
        "close",
        "planning",
        "definition",
    ],
)
def test_non_stop_obligations_must_continue(obligation):
    decision = classify_route_completion(disposition="route", obligation=obligation)
    assert decision.action == "continue"
    assert not decision.legal_return


@pytest.mark.parametrize(
    "obligation",
    [
        "explicit_user_stop",
        "premium_A",
        "premium_B",
        "premium_C",
        "independent_review",
        "runtime_blocker",
        "end_of_approved_scope",
    ],
)
def test_real_router_stop_permits_return(obligation):
    decision = classify_route_completion(disposition="stop", obligation=obligation)
    assert decision.action == "return"
    assert decision.legal_return


def test_recovery_is_fail_closed_not_normal_return():
    decision = classify_route_completion(
        disposition="recovery", obligation="recovery_boundary"
    )
    assert decision.action == "recover"
    assert not decision.legal_return


@pytest.mark.parametrize(
    ("disposition", "obligation"),
    [("", "execution"), ("route", ""), ("unknown", "execution")],
)
def test_invalid_route_shape_fails_closed(disposition, obligation):
    with pytest.raises(ContinuationContractError):
        classify_route_completion(disposition=disposition, obligation=obligation)
