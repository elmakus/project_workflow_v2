# PWv2.1 Mechanical Policy Projection

> GENERATED from `policy/mechanical_policy.json` by `tools/policy_kernel.py`.
> Do not edit rule semantics here; change the registry and regenerate/verify this projection.

Registry version: `1`  
Schema version: `1`

This projection documents only named mechanical predicates over canonical repository state.
It is not a workflow DSL, does not own semantic judgment, and authorizes no canonical writes.

## PWV21-K001 — `tracker_ambiguous`

- Precedence: `100`
- Canonical inputs: `tracker.state`
- Outcome: `recovery / recovery_boundary`
- Owner: `workflow/RECOVERY.md`
- Semantics: An ambiguous durable tracker binding fails closed to Recovery; duplicate create is forbidden.

## PWV21-K009 — `brainstorm_explicit_user_stop`

- Precedence: `150`
- Canonical inputs: `brainstorm.explicit_user_stop`
- Outcome: `stop / explicit_user_stop`
- Owner: `workflow/BRAINSTORMING.md`
- Semantics: An explicit durable Brainstorming user stop remains a real user stop.

## PWV21-K002 — `definition_premium_a_due`

- Precedence: `200`
- Canonical inputs: `definition.premium_a`
- Outcome: `stop / premium_A`
- Owner: `workflow/DEFINITION.md`
- Semantics: A GREEN Definition with premium A due stops before material Strategic Planning.

## PWV21-K003 — `planning_premium_a_due`

- Precedence: `210`
- Canonical inputs: `planning.premium_a`
- Outcome: `stop / premium_A`
- Owner: `workflow/PLANNING.md`
- Semantics: A material planning re-entry with exact premium A due stops before Planning resumes.

## PWV21-K004 — `planning_state_draft`

- Precedence: `220`
- Canonical inputs: `planning.state`
- Outcome: `route / planning`
- Owner: `workflow/PLANNING.md`
- Semantics: A draft planning cycle with its prerequisite gate satisfied remains owned by Strategic Planning.

## PWV21-K005 — `planning_frozen_premium_b_due`

- Precedence: `230`
- Canonical inputs: `planning.state`, `planning.premium_b`
- Outcome: `stop / premium_B`
- Owner: `workflow/PLANNING.md`
- Semantics: A frozen plan with exact premium B due requires the mandatory fresh independent Plan Review boundary.

## PWV21-K006 — `plan_review_pending`

- Precedence: `240`
- Canonical inputs: `plan_review.verdict`
- Outcome: `route / plan_review`
- Owner: `workflow/PLAN_REVIEW.md`
- Semantics: A pending exact Plan Review attempt is owned by independent Plan Review.

## PWV21-K007 — `plan_review_green`

- Precedence: `250`
- Canonical inputs: `plan_review.verdict`
- Outcome: `route / planning`
- Owner: `workflow/PLANNING.md`
- Semantics: A GREEN exact Plan Review returns to Planning for deterministic approval consumption.

## PWV21-K008 — `planning_approved_premium_c_due`

- Precedence: `260`
- Canonical inputs: `planning.state`, `planning.premium_c`
- Outcome: `stop / premium_C`
- Owner: `workflow/PLANNING.md`
- Semantics: An approved GREEN-reviewed plan with exact premium C due stops before Execution Prep.

## PWV21-K010 — `brainstorm_active`

- Precedence: `310`
- Canonical inputs: `brainstorm.state`
- Outcome: `route / brainstorming`
- Owner: `workflow/BRAINSTORMING.md`
- Semantics: An active exploratory scope remains owned by Brainstorming.

## PWV21-K011 — `board_one_ready_card`

- Precedence: `400`
- Canonical inputs: `board.cards`
- Outcome: `route / execution_prep`
- Owner: `workflow/EXECUTION_PREP.md`
- Semantics: Exactly one READY Card identifies the launch-refresh candidate for Execution Prep.

## PWV21-K012 — `board_all_cards_done`

- Precedence: `410`
- Canonical inputs: `board.cards`
- Outcome: `route / close`
- Owner: `workflow/CLOSE.md`
- Semantics: A non-empty Task Board whose current Cards are all DONE routes to Close; terminal Cards are not themselves a stop.
