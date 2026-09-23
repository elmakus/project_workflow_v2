# Project Workflow V2 — Strategic Planning

Status: M02-T03 common Strategic Planning contract.

Strategic Planning converts GREEN Definition authority into a revisioned executable strategy. It never changes accepted product/Definition authority silently.

## Premium cycle

Every material planning cycle has one positive integer `cycle` and exact `entry_subject`.

Before material Planning, premium stop A for that exact cycle must be satisfied. A later material re-entry creates a new cycle and therefore requires a new A/B/C sequence. The new draft cycle is first materialized with `premium_a = due` and `premium_a_subject` equal to its exact entry subject; the router must stop there until that exact A is satisfied. Old gate subjects cannot authorize a new cycle.

## Planner work

The planning record owns:
- exact workstream and cycle;
- exact entry subject;
- plan revision and plan artifact locator;
- draft / frozen / approved lifecycle;
- planner completeness/challenge audit;
- premium A/B/C states and exact gate subjects;
- exact immutable frozen plan subject once frozen;
- review mode: normal independent review, or a bounded `editorial_exempt` classification with exact prior reviewed subject and non-empty semantic basis.

The planner:
1. works only after A is satisfied for the current entry subject;
2. maintains requirement/decision coverage and milestone/gate strategy;
3. completes a GREEN planner audit;
4. freezes one exact immutable Git-blob subject;
5. sets premium B due for that exact subject;
6. stops. The planner must not perform or internally spawn Stage-6 Plan Review.

## Approval and C

A GREEN independent Plan Review for the exact frozen subject is consumed by Planning:
- state becomes approved;
- premium C becomes due for the same exact subject.

Premium C must be satisfied before Execution Prep. RED never mutates the failed review subject; material correction creates a new planning cycle/revision and repeats A/B/C. Pure mechanical/editorial correction may remain in the same accepted cycle only when strategy, milestone structure, requirement coverage and gates do not change. It may use `editorial_exempt` only when the cycle already has an exact prior GREEN Plan Review and satisfied C: the new subject is different, the exemption records that prior reviewed subject plus a bounded semantic basis, and prior B/C subjects remain bound to the reviewed base. No new B/Plan Review/C sequence is created for that editorial-only change.

## Human-facing premium recommendations

The premium stops carry recommendation semantics without storing runtime identity:
- A recommends the best available model/context for Strategic Planning; continuing in the current context is allowed, but the stop also renders an optional ready-to-copy locator-only handoff for moving Planning to another context/harness;
- B requires a fresh independent best-available context for Plan Review and MUST render the ready-to-copy locator-only handoff in the same stop response;
- C recommends switching to a lighter/cheaper model/context before Execution Prep; continuing is allowed, but the stop also renders an optional ready-to-copy locator-only handoff for moving downstream execution preparation to another context/harness.

The handoff rendering contract is owned by `workflow/USER_STOP.md`. These recommendations are user-facing guidance only. Canonical state stores semantic gates/subjects, never current model/session identity or a hard-coded product model name.
