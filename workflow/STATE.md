# Project Workflow V2 — Durable State Envelope

M01 established common ownership/binding. M02 extends only concrete pre-execution state through Intake, Brainstorming, Research, Definition and Strategic Planning.

## Owners

- PROJECT.md identifies the V2 project contract/workstream root; it is not a live phase/Card registry.
- WORKSTREAM.toml owns stable workstream identity/provenance and exact locators for currently materialized workstream-local records.
- INTAKE.toml owns managed-intent diagnosis and exact issue-repair alignment.
- BRAINSTORM.toml owns one exploratory revision, challenge audit, explicit user stop and exact Definition-promotion authorization.
- RESEARCH.toml owns one factual obligation, source accounting, exact return owner and once-only reconciliation.
- DEFINITION.toml owns exact promoted scope, accepted authority, completeness and premium-A state.
- PLANNING.toml owns one material planning cycle, plan revision/artifact, planner audit, immutable frozen subject and exact premium A/B/C gate subjects.
- PLAN_REVIEW.toml owns one independent Stage-6 attempt for one immutable plan subject.
- TASK_BOARD.toml is materialized only when implementation state exists and then owns mutable Card/milestone execution state.
- Stable Task Cards own bounded execution contracts; implementation/final review attempts remain exact-subject records.
- External-effect records are obligation-local; V2 has no universal event/action ledger.

## Intake/alignment

Issue markers/symptoms never authorize repair. Questions/concerns/alternatives are responses but not authorization. Authorization is bound to the exact current repair subject; changed repair makes it stale. Micro-fix candidacy is illegal before exact issue alignment.

## Brainstorming promotion

Definition readiness requires GREEN challenge audit. Promotion is bound to exact `scope_id@revision`; a changed revision invalidates old authorization. Ready-for-definition without exact promotion is a real user stop.

## Research return

Completed Research accounts for official/upstream, project/runtime, tracker/discussion and practitioner/community source classes with explicit status/weight. A pending completed result returns to exactly one owner. An applied result carries an exact result and is consume-only.

## Definition / premium A

Definition GREEN requires accepted authority and GREEN completeness. Premium A becomes due before material Planning. Canonical state stores semantic gate state only, never model/session identity.

## Planning / Plan Review / premium B/C

Each material Planning entry has a positive `cycle` and exact `entry_subject`. Premium A satisfaction must match that cycle. Material re-entry uses a new cycle, so stale A cannot authorize it.

A plan may freeze only after GREEN planner audit. Its exact Git blob becomes the premium-B subject. B must be satisfied before a fresh independent PLAN_REVIEW attempt exists. Plan Review subject/revision/cycle must match the frozen plan exactly.

GREEN Plan Review is consumed by Planning into `approved`; only then premium C becomes due for the same exact subject. C must be satisfied before Execution Prep. RED never mutates the failed attempt subject.

## Mutation guard / one-Card invariant

Mutable Task Board revision rejects stale expected writes. At most one Project Workflow Card may be in_progress. Runtime-internal topology remains outside canonical state.

## Prohibited canonical keys

New V2 state rejects execution-policy, runtime/model/session/worker identity, orchestration binding, universal active/returned/transfer state, Project-Card batch/lane/scheduler state and Context Health.

Production validation lives in `tools/state_contract.py`; tests import those production helpers.
