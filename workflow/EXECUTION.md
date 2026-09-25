# Project Workflow V2 — Execution and result reconciliation

Status: M03-T02 common runtime-neutral execution contract.

Exactly one Project Workflow Card executes at a time in the selected workstream. Project Workflow owns the Card, authority, semantic result and durable state transition; the runtime owns how implementation work is realized.

## Main responsibility

Main/coordinator is the sole Project Workflow state reconciler/writer for the active Card.

Main:
1. performs the launch refresh from `workflow/EXECUTION_PREP.md`;
2. decides whether a qualifying delegated context exists;
3. supplies only bounded Card authority/context to implementation work;
4. validates returned implementation/evidence against the Card;
5. normalizes an accepted return into one semantic Card result;
6. persists that result and the Task Board transition;
7. retains review/recovery/integration responsibility.

A worker/subagent must not finalize Task Board/manifest state or create another Project Workflow Card.

## Typed obligation/result boundary

Before runtime realization, Project Workflow derives the transport-neutral typed package defined by `workflow/EXECUTION_CONTRACTS.md`. PW resolves exact authority content and hashes, binds the relevant freshness fingerprint and mutation pre/postconditions, and supplies only that bounded package.

Before accepting a returned typed result, PW validates its exact obligation/freshness binding and reconciles any stale result according to that contract. Runtime infrastructure may realize the package, but it cannot add/drop authority or directly finalize canonical PW state.

## Delegated or direct realization

Delegation qualifies only when all are true:
- the runtime actually exposes delegated implementation capability;
- the child can receive the bounded authority/context needed by the Card;
- a valid result/evidence return path exists.

When all qualify, Main delegates substantive implementation/debugging/testing. Otherwise Main implements directly under the same Card contract. Runtime/provider/model/session/worker identity is never stored in Project Workflow state.

Runtime-internal work may use zero, one or many workers sequentially or concurrently inside the one active Card. Those workers may produce multiple evidence contributions, but only Main may reconcile them into the single semantic result.

## Returned result classification

Returned implementation is classified before durable reconciliation:
- acceptance/evidence valid -> reconcile one durable accepted result;
- contract still valid but return is incomplete/incorrect -> keep Card `in_progress` and correct it;
- material evidence that the Card is oversized or exposes separable review-worthy outcomes -> preserve independently valid evidence and return only the residual unaccepted scope to Execution Prep for bounded re-decomposition (never reconcile as GREEN; the handoff terminal is `returned`, never `done`);
- a real unresolved blocker prevents the Card contract -> persist proportional blocker state and mark Card `blocked`.

A bad worker result is not a new Project Card and is not by itself a real stop. A worker must not silently broaden scope, merge Cards, self-split or rewrite the stable Card; Main owns the late-oversize return decision (see `workflow/EXECUTION_PREP.md`).

## Accepted semantic result

An accepted result is a workstream-local `results/*.md` artifact using the Card-result contract. It records:
- exact Card ID;
- exact implementation subject;
- one or more durable evidence refs;
- concise tests/readback summary.

It does not record runtime/provider/model/session/worker/invocation identity.

Once a valid result locator is durable on the active Card, runtime/session disappearance must not cause implementation replay. Later review/finalization/recovery starts from that durable result.

## Concurrency boundary

Runtime-internal concurrency does not relax the one-Card invariant and does not create competing shared-state writers. Mutating parallel workers require runtime/filesystem isolation appropriate to their environment; that isolation topology is runtime configuration, not Project Workflow state.

## Runtime portability

The same semantic result contract applies to delegated and direct execution. Pi/Codex-specific adapters, worker launch schemas and model selection remain outside this module.
