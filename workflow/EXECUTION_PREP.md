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

## Semantic Card sizing

A Card is the smallest meaningful execution-and-review ownership unit producing one coherent independently falsifiable outcome substantial enough to justify its own execution/result/review lifecycle.

Before materializing or merging non-trivial Card scope, Execution Prep records one durable sizing audit per affected Card in `TASK_BOARD.toml` (`sizing_audits`, bound to the materialized Card id). Every Card in an executable lifecycle status (`planned`/`ready`/`in_progress`) must carry exactly one audit; omitting the audit array, or omitting one active Card from it, is a bypass, not a trivial-scope exemption — trivial single-outcome scope is recorded the same way, with one coherent outcome and no separability. `done` Cards need no audit so historical terminal state stays valid, and `blocked` Cards need none while blocked so legacy migrated boards validate; any return to an executable status re-triggers the gate. The audit names every candidate acceptance/contract/invariant/independently useful outcome, records the `single`/`split` sizing decision, and explicitly addresses all seven dimensions: independent implementability, falsifiability/testability, reviewability, invariant/contract family, dependency ordering, atomic mutation/migration constraints and cross-surface coupling. Omitted, empty or placeholder dimension evidence fails closed.

Two or more separable outcomes — each able to reach a valid independently verifiable state, with GREEN on one staying valid/useful while another is RED — are split by default. A `single` decision over separable outcomes requires concrete rebuttal evidence whose class is exactly one of `atomicity`, `invalid_intermediate_state`, `inseparable_acceptance` or `material_coupling`, plus a non-empty rationale statement. Generic convenience, same-milestone or fewer-cards claims, structural file/module/layer/test/tool/step-boundary claims and seam-only predecessor evidence cannot rebut the split. File/module/layer/test/tool/step boundaries alone neither force nor prevent a split, scaffolding stays with the outcome it enables unless independently consumed, and a `split` decision over a coherent non-separable scope is rejected as meaningless fragmentation. Outcomes that are not independently falsifiable or not substantial enough for their own lifecycle are rejected as micro-Cards. A `split` decision never stands in for actual topology: every outcome carries a durable `allocated_to` binding to a materialized Card (`card:<id>`) or an existing JIT trigger (`jit:<id>`), the bindings must span at least two distinct destinations, at least one outcome stays in the audited Card itself, Card destinations must be `planned`/`ready`/`in_progress` (never historical DONE, never blocked), and trigger destinations must exist, be unconsumed, and be bounded after the audited Card; a `single` decision must not claim allocation. Deterministic helpers live in `tools/card_sizing_contract.py`.

## Risk-scoped topology challenge

Materially risky proposed Card topology must receive a fresh independent topology challenge before first launch. Risk triggers are merger of a planner-declared preferred seam, a Card spanning multiple independently falsifiable invariant families, whole-milestone absorption despite explicit seams, Card Review substituting for Milestone integration review, or other material deviation from accepted decomposition intent.

Every Card in an executable lifecycle status (`planned`/`ready`/`in_progress`) records one durable topology audit in `TASK_BOARD.toml` (`topology_audits`, bound to the materialized Card id) with a `simple`/`risky` classification, durable risk basis, and review-scope layering. Omitting the audit array, or omitting one active Card from it, is a bypass. `done` Cards need no audit so historical terminal state stays valid, and `blocked` Cards need none while blocked; any return to an executable status re-triggers the gate.

Simple/non-risky topology carries the durable record but no mandatory fresh-challenge ceremony: a `simple` audit must not list triggers or claim a challenge. A `risky` audit names at least one trigger and, before first launch, a fresh independent challenge evaluating exactly the narrow concrete dimensions — Card-boundary fidelity, falsifiability, and review separation. The challenge never re-litigates Plan Review scope (milestone strategy/ordering, requirement coverage, premium gates); self-certified or reused/stale challenges are rejected. A `ready` risky Card must record its challenge, and RED holds the launch in Execution Prep under the `topology_challenge` obligation; an `in_progress` Card must already hold a GREEN challenge. `planned` risk may defer the challenge until launch.

Risk composes with seam fidelity and sizing: a preferred merge needs an owning risky audit, whole-milestone absorption needs explicit declared seams, and an effective sizing boundary spanning two or more invariant families forces the multiple-family trigger. The challenge is second-order: GREEN never cures an invalid primary sizing audit.

Every recorded challenge binds its exact subject with deterministic `sha256:` digests so an old GREEN cannot launch a materially changed proposal. The `proposal_digest` covers the Card's sizing audit, the topology risk/scope/trigger fields (excluding the challenge itself), and the accepted seam decisions and Planning seam declarations; Board validation recomputes it, so a material proposal change stales the challenge while ordinary revision/status transitions do not. The `card_contract_digest` covers the stable Card contract file bytes and is verified by the router at launch refresh — the only stage that reads Card content — so this Card-content check lives in the router, not in Board-only validation. Missing, mismatched or unsupported bindings fail closed before launch. The digest proves subject identity only; the independent challenger still judges semantic truth. Deterministic helpers live in `tools/topology_contract.py`.

## Card versus Milestone review layering

Card Review owns bounded local correctness; Milestone Review owns broader composition/integration acceptance. A topology audit declares its review scope: `card_local`, or `milestone_integration` when the Card boundary is so broad that Card Review would substitute for Milestone review. The substituting scope is rejected unless concrete atomicity evidence justifies the single boundary; generic convenience or non-atomicity rationale is insufficient. A substituting boundary is always risky and challenged before first launch.

## Selective technical contract

A separate technical contract/OpenSpec artifact is optional. Use it only when the current Card materially needs cross-component behavior/API/schema/idempotency/security/migration detail beyond the Task Card.

A simple Card with `Technical contract: none` is fully valid and must not load an OpenSpec/technical-contract artifact.

## Runtime boundary

Project Workflow state must not add a runtime role catalog, model/provider preference, worker adapter API, session identifier or persisted invocation schema. Concrete runtime realization belongs outside this semantic contract.
