# Project Workflow V2 — Strategic Planning

Status: M02-T03 common Strategic Planning contract.

Strategic Planning converts GREEN Definition authority into a revisioned executable strategy. It never changes accepted product/Definition authority silently.

## Premium cycle

Every material planning cycle has one positive integer `cycle` and exact `entry_subject`.

Before material Planning, premium stop A for that exact cycle must be satisfied. A later material re-entry creates a new cycle and therefore requires a new A/B/C sequence. Old gate subjects cannot authorize a new cycle.

## Planner work

The planning record owns:
- exact workstream and cycle;
- exact entry subject;
- plan revision and plan artifact locator;
- draft / frozen / approved lifecycle;
- planner completeness/challenge audit;
- premium A/B/C states and exact gate subjects;
- exact immutable frozen plan subject once frozen.

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

Premium C must be satisfied before Execution Prep. RED never mutates the failed review subject; material correction creates a new planning cycle/revision and repeats A/B/C. Pure mechanical/editorial correction may remain in the same accepted cycle only when strategy, milestone structure, requirement coverage and gates do not change.

Canonical state stores semantic gates/subjects, never current model/session identity.
