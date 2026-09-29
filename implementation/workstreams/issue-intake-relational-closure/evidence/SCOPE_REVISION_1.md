# Intake relational closure — scope revision 1

Scope subject: `intake-relational-closure@1`
Authorized issue-repair subject: `repair:intake-relational-closure:v1`

This exploratory revision converts the authorized diagnosis into a bounded
Definition candidate. It is not Definition promotion, accepted requirements,
Planning, a Task Card, or implementation permission.

## Problem

The selected default-branch contracts validate the workstream manifest and
Intake record independently, but do not close two relations required before
issue alignment:

1. an issue can reach a real alignment stop with no concrete repair subject;
2. the stable manifest kind can disagree with Intake kind while routing follows
   the Intake value.

Both failures were reproduced and prior art was reconciled in
`evidence/INTAKE_PRIOR_ART.md` at the exact locator owned by `INTAKE.toml`.

## Selected outcome

At selected-state consumption, Intake may reach issue-alignment behavior only
when:

- the issue has a nonblank concrete repair subject and its exact consumed
  diagnosis-prior-art binding; and
- the manifest and Intake agree on managed-intent kind.

An empty or whitespace-only issue repair subject remains diagnosis regardless
of a prematurely recorded response class. A kind contradiction fails closed
before either record can silently override the other. Lawful consistent
issue/feature/change states retain their existing routes.

The repair must use the smallest current production boundary that enforces both
relations without adding a second authority value or widening durable schemas.
Definition/Planning will decide exact code placement and tests.

## Included

- production enforcement of concrete nonblank issue subject before alignment;
- production enforcement of `WORKSTREAM.kind == INTAKE.kind` before Intake
  semantics are consumed;
- focused negative coverage for empty/blank subjects and all mismatched kind
  pairings;
- positive controls for consistent issue/feature/change state, including exact
  issue prior-art/alignment behavior;
- minimal canonical documentation clarification if required by the executable
  contract;
- committed, clean-consumer and independent exact-subject review evidence.

## Excluded

- #33 stop precedence, #36 orphan Planning state, general schema migration or
  historical compatibility profiles;
- Task Board/Card, Review history, Close, runtime orchestration or external
  effect redesign;
- tracker mutation, issue closure, integration or deployment;
- adoption of the broad `work/pwv21-policy-kernel` branch;
- widening or claiming completion of #23.

## Required invariants

1. Empty and whitespace-only issue subjects never become alignment stops,
   alignment continuations, authorization, or micro-fix eligibility.
2. A premature response value cannot turn missing diagnosis into repair
   permission.
3. Contradictory manifest/Intake kinds fail closed deterministically before
   issue, feature or change semantics are selected.
4. Consistent records preserve their current lawful routing and exact
   diagnosis-prior-art requirements.
5. The manifest remains stable workstream identity; no duplicate registry or
   fallback authority is introduced.
6. Tracker text and historical candidate code remain evidence only.
7. Implementation and independent review bind exact immutable bytes and the
   accepted scope.

## Alternatives challenged

- **Trust Intake over the manifest:** rejected because it silently changes
  stable workstream identity.
- **Trust the manifest and reinterpret Intake:** rejected because it hides a
  contradictory owner record rather than failing closed.
- **Treat an empty subject as a valid alignment question:** rejected because no
  exact repair exists for the user to authorize.
- **Only add a test/helper check:** rejected because production selected-state
  consumption must enforce the relation.
- **Cherry-pick historical `c94a348...`:** rejected as incomplete for the kind
  relation and embedded in a broad unaccepted branch.
- **Absorb into #23 or the stabilization program:** rejected because this is a
  separately tracked current-schema-valid relational invariant with dedicated
  ownership.
- **Add new schema/runtime identity state:** rejected as unnecessary and outside
  the bounded defect.

## Challenge audit

GREEN. The two counterexamples, lawful controls, authority precedence, exact
scope and exclusions are concrete. The historical candidate reduces uncertainty
for one half but supplies no accepted Result. No unresolved user/product choice
has material expected value before Definition; remaining placement and test
structure are agent-resolvable technical decisions constrained by this scope.
Promotion of exact `intake-relational-closure@1` remains a separate user gate.
