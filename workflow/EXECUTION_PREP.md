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

## Late-oversize return

When execution or review first produces material evidence that the active Card is oversized or contains newly exposed separable review-worthy outcomes, Main reconciles one durable late-oversize return in `TASK_BOARD.toml` (`late_oversize_returns`, at most one record per returning Card). The record binds the `in_progress` Card, the `execution`/`review` origin, the material new evidence, the preserved independently valid evidence refs plus basis, the residual unaccepted scope with at least one separable review-worthy outcome, and the Card's own `waiting` downstream JIT trigger that parks the residual scope — the smallest safe durable boundary for bounded re-decomposition. A review-discovered return additionally binds the originating attempt id to one exact durable review-attempt locator on the same Card; foreign or fabricated attempt bindings are rejected and the router verifies the locator carries that attempt id.

The return moves from `pending` to `residual_bound` and is never removed. While `pending`, the router holds the original in Execution Prep until the residual Card is materialized and bound. While `residual_bound` with the original still `in_progress`, Execution Prep owns handoff finalization: transition the original to `returned`, its non-GREEN terminal disposition. A `returned` Card keeps the bound return still marked `claims_green = false` plus any existing result, review history and preserved evidence, but never claims Card GREEN and is never a full DONE predecessor. Full `done` stays reserved for accepted GREEN-reviewed completion and can never hold a return; an unbound `returned` Card is rejected. After the terminal transition the exact residual trigger advances only through a distinct validated handoff path bound to the residual Card, and the residual Card proceeds through the ordinary launch gates.

The return preserves the durable result locator and review-attempt history, never claims GREEN, and is not a new product-scope authorization. Only Execution Prep re-decomposes the residual scope, and any downstream Card it materializes is subject to the ordinary required-seam, sizing-audit and topology-challenge gates; a contrary seam strategy needs the owning Planning stage. Binding is by outcome coverage, not by Card id alone: every residual outcome must match an outcome in the residual anchor Card's sizing audit on identity and content (id, kind, statement, family), and the anchor audit must persist on the board while the return is bound. Missing, changed, or unrelated outcomes fail closed, as do duplicate residual ids. The anchor audit may split covered outcomes across further `card:`/`jit:` destinations under the ordinary T05 rules — coverage flows through the allocation graph, so legitimate multi-Card re-decomposition is preserved without forcing a mega-Card. Each consumed JIT trigger on that graph must record which Card it became (`jit_resolutions`); the resolution must name an existing consumed trigger actually allocated residual scope and a real downstream Card. At Close, every residual outcome must terminate in accepted (`done`) downstream Cards through allocations, resolutions, and chained handoffs; anything else routes back to a concrete Execution Prep obligation instead of Close. `done` remains Main's attestation of accepted GREEN-reviewed completion — review acceptance itself stays human-owned. Deterministic helpers live in `tools/late_oversize_contract.py`.

## Live-finding intake

Planning-to-Execution-Prep fidelity defects discovered during real execution return to Execution Prep through the durable `live_findings` intake (see `workflow/RECOVERY.md`); accepted-authority defects escalate to their owning accepted-authority stage, and speculative hardening never auto-materializes Cards or scope.

## Affected-JIT reconciliation

Before consuming a satisfied downstream JIT trigger, Execution Prep checks the durable affected-JIT bindings (`live_findings.downstream`, see `workflow/STATE.md`): a trigger with a `pending` material finding stays held until the owning stage's reconciliation is accepted through a typed reconciliation-decision record and verified by readback; consuming it earlier is invalid and fails closed. Explicitly unrelated findings, findings without a downstream disposition, already-reconciled findings and speculative hardening never block consumption merely by being present.

## Intentional live-consumer admission

Before consuming a satisfied downstream JIT trigger explicitly declared as an intentional live-consumer test (`jit_triggers.live_consumer` with `intended = true`, see `workflow/STATE.md`), Execution Prep checks the durable readiness binding: a `pending` trigger stays held until verified admission proves the board-selected corrected authority plus every required Definition, Planning, Plan Review, predecessor-result, Card review and Milestone gate complete by exact readback; consuming it earlier is invalid and fails closed. The declaration pins the exact corrected-authority subject, which must be the exact current accepted Planning subject; Execution Prep refreshes that pin on replan, which stales any pin/admission citing the superseded subject until refreshed. Admission cites one typed admission-decision record and releases only the exact declared trigger through the normal JIT lifecycle. Prompt text, tracker bookkeeping, generic GREEN/status, Worker self-certification and wrong-source/stale/ambiguous records cannot satisfy the proof. Undeclared ordinary triggers and historical Boards acquire no prerequisite. A trigger held by both a pending material finding and pending live-consumer readiness requires both reconciliations; the affected-finding hold routes first.

## Selective technical contract

A separate technical contract/OpenSpec artifact is optional. Use it only when the current Card materially needs cross-component behavior/API/schema/idempotency/security/migration detail beyond the Task Card.

A simple Card with `Technical contract: none` is fully valid and must not load an OpenSpec/technical-contract artifact.

## Runtime boundary

Project Workflow state must not add a runtime role catalog, model/provider preference, worker adapter API, session identifier or persisted invocation schema. Concrete runtime realization belongs outside this semantic contract.
