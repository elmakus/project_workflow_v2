# Issue #28 — execution Research return owner precedence requirements

Revision: `R1`  
Status: `accepted`  
Definition source: `execution-research-return-owner-precedence@1`  
Repair subject: `repair:execution-research-return-owner-precedence:v1`

## Goal

A lawful execution-owned Research record must return once to its exact durable execution owner even when the same Research record is reachable through both the workstream manifest and Task Board. A manifest Research locator must not shadow or corrupt the later valid execution-return semantics.

## Requirements

### I28-R1 — Exact execution return owners

A completed Research record whose `return_target` is `execution_resolution:<subject>`, `execution_prep:<subject>`, or `execution:<subject>` MUST route to the corresponding execution/recovery owner with the exact subject semantics already supported by the Task-Board Research path. It MUST NOT fail because a pre-execution-only owner map cannot index the return target.

### I28-R2 — Same-record dual-locator safety

When the workstream manifest `[research]` locator and Task Board `[research_obligation]` locator resolve to the same lawful Research record, routing MUST preserve one semantic Research obligation and one exact return. The earlier manifest read MUST NOT steal, duplicate, replay, or invalidate the execution-owned return.

### I28-R3 — Once-only reconciliation and cleanup

`complete + pending` and `complete + applied` execution-owned Research MUST return to the exact owner without replaying Research. `consumed + applied` MUST remain historical and, when the Task Board still references it, route only to the existing bounded stale-pointer cleanup behavior. No new Research lifecycle state or second queue is introduced.

### I28-R4 — Preserve pre-execution Research

Existing manifest-level Research semantics for `intake`, `brainstorming`, and `definition` remain unchanged. Active Research remains the next factual obligation. Malformed, unsupported, stale, or cross-workstream Research continues to fail closed under existing validation/recovery semantics.

### I28-R5 — Positive execution coverage

Automated production-selector tests MUST cover all three execution return prefixes with the same Research record co-bound through manifest and Task Board, including at least complete/pending, complete/applied, and consumed/applied states where applicable. Existing Task-Board-only execution Research tests remain GREEN.

### I28-R6 — Negative and compatibility coverage

Tests MUST prove there is no generic `KeyError`-style recovery for valid execution targets, no duplicate owner return, no replay after applied reconciliation, and no regression to Intake/Brainstorming/Definition Research routing. Router/state-contract/continuation suites and the full repository suite must remain GREEN.

### I28-R7 — Bounded implementation

Prefer the smallest production routing/owner-resolution change that makes manifest and Task-Board handling semantically consistent. Do not redesign Research storage, Task Board ownership, Execution, Recovery, continuation, workflow state, or add a generic orchestration/priority engine.

### I28-R8 — Independent exact-subject review

The implementation subject, semantic Result, acceptance surface, and required evidence must be durably bound. A context that materially implements or repairs the subject MUST NOT issue its independent implementation verdict. GREEN review is required before Card completion.

### I28-R9 — Integration isolation

This Definition authorizes only the exact #28 repair scope. It does not merge or close #28, integrate other stabilization constituents, transfer their gates, or claim W4/global stabilization qualification.
