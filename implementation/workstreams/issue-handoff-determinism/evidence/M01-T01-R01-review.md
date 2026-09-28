# Independent Review Evidence — M01-T01-R01

Verdict: RED

Reviewed exact result subject:
- result commit: `5cf28e4a9456e5889e5ce51215a3708f409b47f7`
- result path: `implementation/workstreams/issue-handoff-determinism/results/M01-T01.md`
- result blob: `23886091d1b34874d49b56657208f9fe0ddf5ee3`
- implementation subject declared by that result: `82671ae01696e39bc66d50cff2f29e5115a65fd9`

Acceptance authority:
- `implementation/workstreams/issue-handoff-determinism/cards/M01-T01.md`
- `requirements/PROJECT_WORKFLOW_V2.md`
- `workflow/ROUTER.md`
- `workflow/REVIEW.md`
- `workflow/USER_STOP.md`
- `workflow/EXECUTION_PREP.md`

## Finding 1 — delivery validator does not enforce the exact locator-only handoff

Severity: blocking acceptance defect.

`tools/user_stop_contract.py::_has_exact_locator` scans the entire response for any contiguous four lines beginning with the locator labels and accepts any non-empty values that do not contain angle brackets. `validate_user_stop_delivery` separately checks only that the response contains the text `NEW CHAT START PROMPT`.

Consequences:
1. A handoff containing extra narrative or extra fields inside/around the alleged prompt can pass, although the Card and `workflow/USER_STOP.md` require the exact locator-only prompt.
2. Incorrect locator values such as a wrong repository, branch, entry obligation, or durable pointer can pass because `DeliveryRequirement` carries no expected locator identity against which the supplied values can be checked.
3. Placeholder-like values such as `TBD`, `unknown`, or arbitrary non-empty strings pass; the implementation rejects only empty values and values containing `<` or `>`, while the accepted contract says missing/placeholder locator data must fail closed.

Minimal examples accepted by the current predicate include:
- `Repository: wrong/repository`
- `Branch: TBD`
- `Entry obligation: anything`
- `Durable start pointer: nowhere.toml`

provided the four lines are contiguous and the response contains `NEW CHAT START PROMPT` (plus `USER ACTION REQUIRED:` for required policy).

This fails the Card acceptance clause requiring the exact four-field locator and fail-closed missing/placeholder behavior, and weakens PWV2-REQ-071's locator-only handoff contract.

## Required correction

Bind delivery validation to the expected locator values for the already-established boundary and validate the prompt as exactly the four permitted locator fields, not merely a matching four-line substring. Reject unresolved/placeholder locator values fail-closed. Add negative tests for wrong-but-nonempty repository/branch/obligation/pointer values, common unresolved placeholders, and extra narrative/fields in the prompt.

The existing policy separation is otherwise directionally correct: handoff policy is downstream of an established router/Review boundary, Premium A/C remain offered, Premium B required, and Review fresh-context realization remains transient.
