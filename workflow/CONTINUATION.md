# Project Workflow V2 — Deterministic continuation contract

Status: Issue #16 M01 common continuation contract.

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
