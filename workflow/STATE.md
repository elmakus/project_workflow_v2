# Project Workflow V2 — Durable State Envelope

M01 established the common ownership/binding envelope. M02-T01 extends it only for pre-execution Intake and exact issue-repair alignment.

## Owners

- PROJECT.md identifies the V2 project contract and workstream-root convention. It is not a live phase/Card registry.
- A selected WORKSTREAM.toml owns stable workstream identity, branch provenance, integration target and exact locators for the currently materialized workstream-local state.
- Before implementation state exists, a managed workstream may point only to its exact INTAKE.toml. A Task Board is not required merely to diagnose/refine a request.
- Once Execution Prep materializes implementation state, the selected TASK_BOARD.toml owns mutable milestone/Card execution state for that workstream.
- Stable Task Cards own scope/authority/acceptance contracts and do not mirror mutable execution status.
- Review attempts own exact immutable subject, acceptance surface, semantic independence proof, verdict and evidence.
- External-effect records are obligation-local. V2 has no universal action/event ledger.

## Intake/alignment state

An issue Intake owns exact diagnosis/repair-alignment semantics before implementation:
- the marker/symptom alone is never repair authorization;
- a later question, concern or alternative is a response but not authorization;
- authorization is bound to the exact current repair subject;
- changing the repair subject invalidates stale authorization;
- a micro-fix candidate cannot exist before exact issue alignment.

Feature/change discovery may record alignment as not required; later Brainstorming/Definition promotion remains separate.

## Mutation guard

A mutable Task Board carries integer revision. A writer must compare the expected revision before replacing shared state and increment it on a successful write. A stale expected revision fails closed.

## One-Card invariant

At most one Project Workflow Card in a selected Task Board may be in_progress. Runtime-internal work topology is outside this state and must not create extra Project Workflow Cards or competing writers.

## Prohibited canonical keys

New V2 canonical state must not contain keys for execution_policy, runtime/model/session/worker identity, orchestration bindings, universal active/returned/transfer state, Project-Card batch/lane/scheduler state, or Context Health.

The production validation helper is tools/state_contract.py; tests import that same helper rather than reimplementing these rules.
