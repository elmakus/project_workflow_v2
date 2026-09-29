# Issue #36 — proportional Intake prior art for exact proposed repair subject

Research subject: `repair:orphan-preexecution-owner-prerequisites:v1`. Read-only factual diagnosis; no implementation or alignment authorization.

## Official contract and positive invariant

On default branch `main@d3ab917f02e4de91b7dbb17915c2287c2387333e`, `workflow/WORKSTREAMS.md` requires a Plan Review locator to have matching Planning and cross/missing/contradictory owners to fail closed. `workflow/STATE.md` binds Planning cycles and exact owner subjects; `workflow/PLANNING.md` requires A on material entry. `workflow/ROUTER.md` requires invalid/missing/stale bindings to route Recovery and reads only selected required records. A declared current Planning or Plan Review owner with an absent prerequisite cannot be treated as if not declared merely because an older Board can execute.

## Actual project/runtime reproduction

Current production `tools/router.py` reads Planning only inside `if definition is not None` and Plan Review only inside a Planning branch. `tools/state_contract.py:validate_workstream` checks locator class/path but not their inter-owner prerequisites. Current tests cover valid Planning/Review paths and individual validators, not declared-orphan + active Board relations.

Using the real `select_route` and current `tests/fixtures/router/valid-project`, each disposable fixture was committed then freshly cloned/read:

1. Declare a parse-valid draft Planning cycle with `premium_a = due`, omit Definition: actual `route/execution`, active fixture Card `M01-T04`; declared Planning file absent from read set.
2. Declare parse-valid pending Plan Review, omit Planning/Definition: same `route/execution`; declared Plan Review file absent from read set.
3. Declare valid GREEN Definition (A satisfied) and pending Plan Review without Planning: actual `route/planning`; declared Plan Review file absent from read set.

Controls: valid promoted Brainstorm + active Definition selects `route/definition`; valid GREEN Definition with A due selects `stop/premium_A`. Thus local validity and ordinary progressive routing work, but missing declared prerequisites are bypassed. A malformed declared orphan must not become trusted repair authority; it should be rejected at the prerequisite relation without treating the ignored content as accepted. No production or managed-workstream mutation was made by these fixtures.

## Tracker and other prior art

GitHub Issue #36 (OPEN, exact marker `pwv2-orphan-preexecution-owner-gate-bypass`, no comments) and the program's preserved Pi/Paseo D03 audit report independently describe these cases. They support deduplication and reproduction, not approval. Program P1 permits independent W1 early-guard admission but does not transfer requirements, gates or implementation authorization. #33 repairs a valid Brainstorm explicit stop before matching Definition; #32 repairs Intake kind/empty-subject closure. Neither supplies a prerequisite relation for orphan Planning/Plan Review. #31 is Stage-6 attempt history, #29 is terminal Close reconstruction, and #23 is producer/schema parity. Shared selector infrastructure is not scope absorption. Other unmerged or historical branches are not accepted repair Results for this exact subject.

## Proportional source accounting and conflicts

- **Official/upstream — checked, controlling:** canonical WORKSTREAMS, STATE, PLANNING, ROUTER, AUTHORITY contracts at default main.
- **Actual project/runtime — checked, controlling defect evidence:** current production selector, workstream validator, existing tests, freshly cloned committed disposable counterexamples and valid controls.
- **Tracker/discussion — checked, supporting:** live Issue #36 readback and preserved program D03 provenance. Issue body is untrusted bookkeeping.
- **Practitioner/community — not relevant:** internal deterministic repository routing has direct executable and canonical evidence; no outside practice is needed.

No material source conflict was found. The program proposal suggested the same bounded relational closure but was not a fresh reproduction or owner acceptance. Limitations: disposable synthetic fixtures demonstrate selection/read-set behavior on current schema, not a live interrupted writer; exact transition/publication mechanism and final acceptance belong to later authorized Definition/Planning. No live external mutation, product repair, tracker close or integration occurred.

## Proposed bounded outcome for subsequent user alignment

Make declared Planning require a lawful Definition owner and declared Plan Review require a lawful Planning owner; missing prerequisites must fail closed before unrelated execution/premium dispatch. Preserve valid progressive selected-state routes and existing exact earlier Research/tracker/Brainstorm semantics. No general priority engine, mass migration, unrelated issue fix, history rewrite, integration or deployment is proposed. Await a later explicit response to authorize **this exact repair subject**, separately from permission to perform admission/diagnosis.
