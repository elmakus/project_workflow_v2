# Project Workflow V2 — Durable State Envelope

M01 established common ownership/binding. M02 extends only the concrete pre-execution state required by Intake, Brainstorming, Research and Definition.

## Owners

- PROJECT.md identifies the V2 project contract and workstream-root convention. It is not a live phase/Card registry.
- WORKSTREAM.toml owns stable workstream identity/provenance and exact locators for currently materialized workstream-local records.
- INTAKE.toml owns managed-intent diagnosis and exact issue-repair alignment.
- BRAINSTORM.toml owns one exploratory scope revision, challenge audit, explicit user stop and exact Definition-promotion authorization.
- RESEARCH.toml owns one factual obligation, proportional source accounting, exact origin/return target and once-only return reconciliation.
- DEFINITION.toml owns the exact promoted scope subject, Definition revision, accepted authority locators, completeness audit and premium stop A state.
- TASK_BOARD.toml is materialized only when implementation state exists and then owns mutable Card/milestone execution state.
- Stable Task Cards own scope/authority/acceptance contracts; review attempts own immutable review subjects/verdicts.
- External-effect records are obligation-local; V2 has no universal event/action ledger.

## Intake/alignment

Issue markers/symptoms never authorize repair. Questions/concerns/alternatives are responses but not authorization. Authorization is bound to the exact current repair subject; changing that subject makes the old authorization stale. Micro-fix candidacy is illegal before exact issue alignment.

## Brainstorming promotion

Definition readiness requires a GREEN challenge audit. Promotion authorization is bound to exact `scope_id@revision`; substantive revision movement makes it stale. Ready-for-definition without exact authorization is a real user-owned stop.

## Research return

Completed Research accounts for official/upstream, project/runtime, tracker/discussion and practitioner/community source classes with explicit status/weight. A completed pending result returns to exactly one owner. An applied result retains an exact return result and may only be consumed/cleared, never replayed.

## Definition and premium A

Definition GREEN requires accepted authority, GREEN completeness audit and semantic `premium_a = due|satisfied`. `due` is a real stop before material Strategic Planning. Canonical state stores no model/session identity.

## Mutation guard and one-Card invariant

A mutable Task Board carries integer revision; stale expected revision fails closed. At most one Project Workflow Card may be in_progress. Runtime-internal work topology remains outside canonical state.

## Prohibited canonical keys

New V2 state rejects execution-policy, runtime/model/session/worker identity, orchestration binding, universal active/returned/transfer state, Project-Card batch/lane/scheduler state and Context Health.

Production validation lives in `tools/state_contract.py`; tests import those production helpers.
