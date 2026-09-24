# Project Workflow V2 — Execution/review recovery and continuation

Status: M03-T04 common recovery contract.

Recovery reconstructs the next semantic obligation from durable repository state. Runtime/session disappearance is not authority and never causes replay by itself.

## Recovery precedence

1. Validate project/workstream/Task Board binding.
2. If the Task Board points to implementation Research, recover that exact Research obligation and return target before unrelated execution.
3. If an active Card already has a valid durable semantic result, reconcile from that result before considering implementation replay.
4. If an exact review attempt exists, recheck that its subject still covers the current result before GREEN finalization or RED correction.
5. Only then route current execution/correction/blocker state.

No worker/model/session/invocation identifier is required.

## Durable result before replay

A valid result locator on the active Card is authoritative completion evidence for implementation work. Loss of the process/context that produced it does not make the implementation undone.

If the result is missing/invalid, recover the current Card. If the result exists and validates, continue to review/finalization/reconciliation as required. Never replay solely because runtime memory disappeared.

## Review subject refresh

For a reviewable Card result, the result locator carries exact immutable Git identity for the normalized result artifact. The current review attempt must cover that exact repository/commit/path/blob plus the exact Card acceptance.

- pending/in-progress attempt for a different current result is inconsistent and routes Recovery;
- terminal history for an older result remains immutable, but the changed current result requires a new attempt;
- GREEN can finalize only the exact still-current result.

## RED / blocker classification

The execution-resolution classifier has these semantic outcomes:
- bounded correction inside accepted authority -> Execution;
- plan strategy/order/outcome correction -> Strategic Planning;
- accepted product/global authority correction -> Project Definition;
- missing factual evidence -> Research;
- unresolved human authority/authorization -> real user stop;
- non-remediable runtime/access/input blocker -> real blocker stop.

A RED verdict alone is not a user stop.

## Review convergence and structural resolution

When derived review history reaches either the scope-specific material discovery ceiling or the default 3 failed repair→closure-verification rounds for one material defect class, ordinary RED correction stops looping. Recovery routes `review_convergence` to Main/root-cause convergence analysis inside accepted authority. The mode switch preserves RED and all valid evidence; it cannot manufacture GREEN or reset the stable review epoch.

After convergence analysis, the lifecycle may freeze exactly one fresh post-convergence full-scope discovery with durable convergence basis. If that validation is RED, `review_structural_resolution` classifies the smallest broader correction owner: bounded Execution Prep restructuring when accepted milestone strategy remains intact, Strategic Planning for strategy/order/outcome change, Project Definition for accepted product/global authority change, Research for missing facts, or a real user/blocker stop only when the existing recovery classifier reaches one. It must not automatically create ordinary review N+1.

## Implementation Research handoff

Implementation/recovery Research is owned by the selected Task Board through one exact `research_obligation` locator. The Research record owns origin, return target, state and once-only reconciliation.

Keep the pointer through Research `complete`. Final return-owner mutation and `return_reconciliation = applied` are one durable transition. After that, consume/clear without replay. A stale pointer to already-consumed Research is cleanup/recovery work, never permission to repeat the factual or implementation work.

## Blockers

A blocked Card has one proportional workstream-local blocker record. It contains only Card identity, semantic class, concise summary and evidence reference when material. It does not store runtime identity.

Ordinary role changes, GREEN/RED verdicts and deterministic correction/Research return are not stops.
