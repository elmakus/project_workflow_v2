# Project Workflow V2 — Execution Prep / JIT refinement

Status: M03-T01 common execution-readiness contract.

Execution Prep materializes only currently well-defined useful Cards and prepares one exact READY Card for launch. It never chooses a runtime worker/model/session and never persists runtime orchestration identity.

## Stable Card contract

A Task Card is stable authority. It must identify:
- exact Card ID;
- bounded included and excluded scope;
- exact authority refs;
- exact completed-result dependencies bound as result path + immutable commit/blob identity, or `none`;
- observable acceptance;
- required tests/readback;
- review requirement;
- optional technical-contract path, or `none`.

Mutable status, result and review state stays in the selected Task Board.

## READY and launch refresh

READY is semantic readiness, not runtime availability.

Before a READY Card can launch, reread:
1. the selected Task Board and exact Card contract;
2. every authority ref named by the Card;
3. every exact dependency result named by the Card and verify its path + commit/blob identity is still the result of a DONE predecessor;
4. the optional technical contract only when the Card names one.

Missing/stale authority, dependency or technical-contract input fails closed before execution. Worker/provider/model availability is not a READY prerequisite.

## JIT decomposition

Materialize Cards only when their stable contract is currently knowable. When a downstream Card boundary depends on a predecessor result, retain a bounded Task Board JIT trigger instead of creating a placeholder Card.

JIT trigger lifecycle is `waiting -> satisfied -> consumed`. A satisfied trigger requires its predecessor Card to be DONE with a durable result before the downstream contract is materialized.

## Refinement / escalation

L1/L2 execution-detail refinement may change only not-yet-started Card contracts inside accepted authority.

- bounded execution detail -> remain in Execution Prep;
- milestone strategy/order/outcome change -> Strategic Planning;
- accepted product/global intent change -> Project Definition;
- missing facts needed to classify/prepare -> Research;
- evidence that a required seam is wrong -> Strategic Planning for accepted revision, never a silent JIT override.

Do not silently rewrite an in-progress Card through JIT refinement.

## Seam fidelity

Execution Prep materializes Cards against the accepted Planning seam declarations from `workflow/PLANNING.md`:

- a `required_seam` must not be merged into another Card boundary; splitting within the seam boundary is allowed because the boundary itself survives;
- a `preferred_seam` is preserved by default; merge/split deviation is permitted only with durable technical rationale whose class is exactly one of `coupling`, `atomicity`, `invalid_intermediate_state`, `non_separable_acceptance` or `new_predecessor_evidence`, plus a non-empty rationale statement;
- generic convenience, same-milestone or fewer-cards rationale is insufficient and rejected;
- `illustrative` intent is non-binding and needs no rationale.

JIT seam decisions are recorded durably in `TASK_BOARD.toml` (`preserved`/`merged`/`split` per declared seam id); a decision naming an undeclared seam is rejected, and every declared seam needs exactly one decision — silently omitting a seam is a bypass, not preservation. Deterministic helpers live in `tools/seam_contract.py`.

## Selective technical contract

A separate technical contract/OpenSpec artifact is optional. Use it only when the current Card materially needs cross-component behavior/API/schema/idempotency/security/migration detail beyond the Task Card.

A simple Card with `Technical contract: none` is fully valid and must not load an OpenSpec/technical-contract artifact.

## Runtime boundary

Project Workflow state must not add a runtime role catalog, model/provider preference, worker adapter API, session identifier or persisted invocation schema. Concrete runtime realization belongs outside this semantic contract.
