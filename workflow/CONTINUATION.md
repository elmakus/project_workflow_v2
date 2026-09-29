# Project Workflow V2 — Deterministic continuation contract

Status: Issue #16 M03 Review/USER_STOP composition.

This module is not a workflow phase. It defines the runtime-neutral completion rule that applies after any semantic owner obligation has been reconciled durably.

## Route-after-reconcile

After every reconciled semantic step that did not itself establish a real stop, the invoking context MUST:

1. reread durable project/workstream state required by the canonical router;
2. invoke the canonical one-step router again;
3. consume only the exact newly selected obligation.

Completion of a worker, role, Task Card action, Review verdict, Research return, reconciliation action, or owner-module call is never by itself permission for the invocation to return normally.

The router remains a selector only. This contract does not execute owner policy, mutate workflow state, or grant authority.

## Legal return

Normal invocation return is legal only when the fresh canonical route establishes an existing real stop. Real-stop semantics remain owned by the canonical router and its owner modules, including explicit/user authority boundaries, premium gates, independence boundaries, genuine non-remediable blocker boundaries, and durable end-of-approved-scope.

A non-stop `route` result requires continuation. A fail-closed `recovery` result is not semantic success and must not be relabeled as a normal stop by this contract; recovery remains owned by `workflow/RECOVERY.md`.

Runtime safety fuses may abort execution technically, but they never establish semantic completion or a workflow stop.

## State boundary

This contract introduces no Continuation phase, durable continuation/session ledger, event log, runtime role catalog, model/provider/session/worker identity, or invocation identity. Fresh rerouting is reconstructed from existing durable workflow authority.

## Progress, restart and external-effect safety

Continuation must fail closed when a semantic owner claims successful reconciliation but the freshly derived authoritative obligation/evidence fingerprint is unchanged. A repeated semantic fingerprint already seen in the same invocation is a cycle unless new accepted durable evidence or authority changes its evidence epoch.

These fingerprints are ephemeral and derive only from durable semantic inputs. Runtime/model/provider/session/worker/invocation identity is neither an input nor durable authority. Runtime iteration/time bounds may abort technically but cannot establish semantic success or a workflow stop.

On restart, already durable semantic results, Review verdicts, Research returns and reconciled external effects are consumed from durable state rather than replayed. If an external mutation may have occurred but its effect is uncertain, exact target readback is required before any retry; unresolved occurrence fails closed under the owning external-effect contract.

## Review and USER_STOP composition

Review verdicts remain owned by `workflow/REVIEW.md`. GREEN routes through deterministic post-review finalization and fresh rerouting; RED routes through the corrective classification in `workflow/RECOVERY.md`. Neither verdict, nor Card/Research completion, creates a stop or handoff by itself.

Exact-subject independence is evaluated for every review subject. A context that produced or repaired subject S cannot independently verdict S. If correction creates S2, the repairing context is likewise non-independent for S2. A genuinely independent internal review context may satisfy the review without an external handoff; when qualifying independence cannot be realized, the existing fresh independent-review boundary is a real stop.

`workflow/USER_STOP.md` is applied only after such a boundary (or another canonical real stop) already exists. Its handoff is a delivery postcondition, never a continuation decision. Non-boundary GREEN, RED, Card and Research transitions therefore emit no synthetic handoff.


## Pending exact-subject external evidence

Required external CI/check evidence is observed against the exact immutable implementation subject before consumption. Terminal success is positive evidence; terminal failure remains correction evidence. Queued, requested, waiting, pending and in-progress observations are pending external evidence and do not claim semantic reconciliation. Temporary absence immediately after a known trigger requires bounded exact-subject readback rather than success.

Pending observation therefore does not invoke the successful-reconciliation no-progress fuse merely because durable workflow state is unchanged. A claimed reconciliation with unchanged authoritative fingerprint and accepted evidence epoch still fails closed. Pending observation is ephemeral and creates no durable polling/session state or new authority.
