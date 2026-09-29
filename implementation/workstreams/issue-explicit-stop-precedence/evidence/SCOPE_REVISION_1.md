# Issue #33 — Brainstorming scope revision 1

Scope subject: `brainstorm-explicit-stop-precedence@1`
Repair subject: `repair:brainstorm-explicit-stop-precedence:v1`
Status: ready for Definition; promotion authorization pending.

## Problem boundary

A selected, valid Brainstorm record can carry `explicit_user_stop = true` while a matching later Definition record exists. The current router validates and dispatches Definition before evaluating the durable Brainstorm stop, so active Definition routes to Definition and GREEN Definition can route toward Planning.

The accepted repair outcome must preserve the already-declared explicit real stop. It must not merely improve stop rendering after selection, because the defect occurs before the stop is selected.

## Recommended product outcome

When the selected workstream has a valid Brainstorm record with `explicit_user_stop = true`, the router must return the Brainstorm-owned `explicit_user_stop` real stop before selecting any Definition, Planning, Plan Review, Execution Prep, or Task Board obligation from later state.

Later records do not clear or supersede the stop. Clearing the stop requires a lawful Brainstorm-owner transition. After it is cleared, normal progressive validation/routing of any later records resumes and malformed state still fails closed.

This chooses stop precedence rather than treating `promoted + explicit_user_stop` as inherently invalid. The choice follows the canonical Brainstorming contract, which accepts an explicit stop as an orthogonal durable signal and states that it produces a real stop.

## Included scope

- production selector ordering for a selected valid Brainstorm explicit stop;
- active Definition and GREEN Definition/premium variants that currently bypass the stop;
- preservation of `workflow/USER_STOP.md` delivery through the existing stop path;
- focused tests for stop-plus-later-state cases;
- lawful controls for stop-only, stop-cleared promoted Definition, active Brainstorm, and existing premium routing;
- only necessary canonical wording clarifying that later state cannot supersede the Brainstorm owner.

## Excluded scope

- #36 orphan Planning/Plan Review prerequisite ownership;
- #31 Stage-6 review history and #29 Close reconstruction;
- #28 execution-Research return precedence;
- #23/#26 schema or migration work;
- a generic policy registry or broad priority-kernel adoption;
- mutation, deletion, or normalization of later records while the stop is active;
- tracker closure, PR integration, default-branch mutation, or deployment.

## Acceptance direction

Definition should require at minimum:

1. selected `explicit_user_stop = true` always produces `stop / explicit_user_stop` with Brainstorm ownership before downstream phase dispatch;
2. active and GREEN Definition cannot bypass that stop;
3. clearing the stop restores the exact lawful downstream route and does not erase or rewrite later state;
4. stop-only and active Brainstorm behavior remain correct;
5. no unrelated priority, premium, review, Research, or execution semantics change;
6. production tests call the real selector and include read-set/USER_STOP delivery checks where discriminating;
7. exact committed implementation receives cumulative qualification and independent review.

## Challenge audit

**GREEN.**

- Challenged fail-closed Recovery instead of preserving the stop: rejected because canonical Brainstorming explicitly defines the durable flag as a real stop and validation already treats it as orthogonal to promoted state.
- Challenged clearing or invalidating Definition/Planning records: rejected; later state is not authorized to mutate Brainstorm ownership, and removal would destroy durable history.
- Challenged a validator-only prohibition: rejected as unnecessary product restriction and insufficient if the selected-state precedence path remains wrong.
- Challenged moving every human boundary into a generic priority engine: rejected as scope expansion; one explicit owner check closes the demonstrated invariant.
- Challenged absorbing #36: rejected because orphan prerequisite ownership is a separate malformed-state relation with different records and controls.
- Challenged implementation as a micro-fix without Definition/Planning: rejected; precedence, read ordering, malformed-state interaction, and USER_STOP delivery require exact accepted authority and independent review.

No unresolved factual or user/product choice remains inside this revision. Exact implementation placement and test decomposition remain Definition/Planning details under the bounded outcome above.
