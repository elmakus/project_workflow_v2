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
