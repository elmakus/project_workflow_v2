# Issue #32 — Intake relational closure requirements

Revision: `R1`
Status: `accepted`
Definition subject: `intake-relational-closure@1`
Repair subject: `repair:intake-relational-closure:v1`

## Goal

Close the two selected-state relations that currently allow Intake to present an
empty issue-repair alignment boundary or to consume Intake semantics that
contradict stable workstream identity.

## Requirements

### I32-R1 — Concrete issue subject before alignment

An active issue Intake whose `repair_subject` is empty or whitespace-only MUST
remain in Intake diagnosis. It MUST NOT emit an `issue_alignment` stop, enter a
question/concern/alternative Brainstorming route, reconcile authorization,
become a micro-fix candidate, or reach implementation preparation.

### I32-R2 — Premature response is non-authorizing

For a missing concrete repair subject, every currently allowed response class
(`none`, `question`, `concern`, `alternative`, `authorization`) MUST remain
non-authorizing. A recorded response cannot manufacture the missing diagnosis
subject or its prior-art binding.

### I32-R3 — Exact prior-art sequencing remains intact

Proportional Intake-origin Research MUST remain required only after a concrete
current repair subject exists. For a concrete issue subject, existing exact
subject/result binding, stale-binding rejection and once-only return behavior
MUST remain unchanged.

### I32-R4 — Manifest/Intake kind agreement

When a selected workstream points to Intake, `WORKSTREAM.kind` and
`INTAKE.kind` MUST be equal. Any issue/feature/change disagreement MUST fail
closed to Recovery before the contradictory value can select Intake-derived
semantics or downstream work.

### I32-R5 — Stable identity remains authoritative

The manifest remains stable workstream identity, but a mismatch MUST NOT be
repaired by silently overwriting or reinterpreting Intake. No fallback value,
second registry, migration side effect or implicit state rewrite may be added.

### I32-R6 — Lawful positive controls remain stable

Consistent issue, feature and change records MUST preserve their current lawful
routes. In particular:

- a concrete issue with exact consumed diagnosis prior art and no response still
  reaches the exact issue-alignment stop;
- an empty issue remains diagnosis;
- consistent feature/change discovery does not manufacture issue alignment;
- active/completed Research and tracker bookkeeping retain their existing
  authority boundaries after selected identity has been proven consistent.

### I32-R7 — Fail-closed precedence

The kind relation MUST be checked during selected-state validation before a
route that relies on that selected workstream's Intake-derived identity is
returned. A contradiction is Recovery evidence, not a normal stop and not a
Research/Brainstorming/Execution obligation.

### I32-R8 — Production enforcement

The fix MUST enforce both relations on the production router/validation path.
A test-only helper, documentation-only change or caller convention is
insufficient. The smallest reusable composite validation boundary MAY be added
when it avoids duplicated checks, but it MUST NOT broaden state schema.

### I32-R9 — Regression and acceptance evidence

Automated coverage MUST include:

1. empty and whitespace-only issue subjects across all response classes;
2. all unequal pairings among issue/feature/change manifest and Intake kinds;
3. same-kind positive controls for issue/feature/change;
4. concrete issue prior-art and alignment controls;
5. cumulative state-contract and router suites;
6. committed clean-consumer readback of the exact implementation subject.

The exact implementation subject MUST receive independent review against this
accepted authority before Card completion.

### I32-R10 — Scope isolation

The repair MUST NOT implement #33 stop precedence, #36 orphan Planning state,
historical schema migration, Task Board/Review/Close redesign, runtime
orchestration, tracker closure, integration or deployment. It MUST NOT claim
#23 completion or adopt the broad `work/pwv21-policy-kernel` branch.

## Constraints and invariants

- `workflow/INTAKE.md`, `workflow/WORKSTREAMS.md`, `workflow/STATE.md` and the
  accepted project-level requirements remain controlling.
- Progressive disclosure remains proportional: Intake is read when its declared
  cross-record identity must be checked; unrelated workflow trees are not
  loaded.
- Tracker prose and historical code are evidence only.
- No runtime/model/session/worker identity becomes durable state.
- YAGNI forbids a new schema version, migration framework or technical-contract
  artifact unless Planning demonstrates a current need.

## Acceptance boundary

Definition acceptance specifies behavior and authority precedence, not a claim
that code is already repaired. Planning must map I32-R1–R10 to a bounded Card,
exact tests/readback and independent review without expanding the scope.
