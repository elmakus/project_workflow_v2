# Issue #32 — Intake relational closure decisions

Status: `accepted`
Definition revision: `D1`
Source scope: `intake-relational-closure@1`

## I32-D1 — Treat nonblank repair subject as the alignment prerequisite

**Decision:** A concrete issue repair subject is a string with non-whitespace
content. Empty and whitespace-only values remain diagnosis regardless of the
recorded response class.

**Why:** There is no exact repair for the user to align with or authorize when
the subject is blank. This preserves the existing prior-art sequencing and
prevents an empty real stop.

## I32-D2 — Require exact manifest/Intake kind equality

**Decision:** The selected manifest and its Intake record are jointly valid only
when their issue/feature/change kinds are equal. Any mismatch routes Recovery.
Neither side silently wins.

**Why:** `WORKSTREAM.kind` is stable workstream identity while `INTAKE.kind`
owns Intake semantics. Contradiction between owner records is malformed state,
not a choice of precedence.

## I32-D3 — Enforce the relation at the composite consumption boundary

**Decision:** Keep standalone record validation for local shape and add the
smallest production composite check where the selected manifest and Intake are
consumed together. The router must apply it before returning an obligation based
on contradictory selected identity.

**Why:** Changing `validate_intake` to accept unrelated manifest context would
couple a record-local validator unnecessarily; duplicating authority in durable
state would worsen the defect. A small composite helper or equivalently single
production check is sufficient. Planning may choose the exact function name.

## I32-D4 — Preserve Research semantics after identity proof

**Decision:** A declared Intake record must be read early enough to prove its
kind relation before selected-workstream Research or later semantics are
returned. Once identity is consistent, current active/completed Research
precedence and once-only reconciliation remain unchanged.

**Why:** Otherwise a malformed selected workstream can temporarily route work
under contradictory identity. Reading one exact declared Intake record is a
proportional progressive-disclosure cost.

## I32-D5 — Do not make premature response data a schema migration

**Decision:** The repair guarantees that a blank subject cannot advance even if
a response is present. It does not introduce a schema migration or rewrite old
records merely because they contain a premature response value.

**Why:** Routing safely back to diagnosis closes the authorization defect.
Historical normalization is separate scope and would add unnecessary risk.

## I32-D6 — Reimplement the bounded invariant on current main

**Decision:** Historical commit `c94a348a0490b11c014f02d57931a5829046f1a9`
may inform the empty-subject behavior and tests, but it is not an accepted Result
and must not be wholesale cherry-picked. The kind relation must be implemented
and qualified on the exact current baseline.

**Why:** The historical branch is broad, diverged and incomplete for issue #32.

## I32-D7 — Use discriminating matrix coverage

**Decision:** Tests must distinguish blank subject from concrete subject,
premature response from exact alignment, mismatched kind from same-kind state,
and malformed-state Recovery from real user stops. Tests call production
validators/router paths.

**Why:** A single happy-path assertion would not prove either relational
closure or preserve existing semantics.

## I32-D8 — Keep the implementation artifact set minimal

**Decision:** The expected implementation surface is the current router/state
contract, focused tests and only necessary canonical wording. No separate
technical-contract/OpenSpec artifact, migration subsystem or new durable key is
accepted by Definition.

**Why:** The behavior is bounded and testable in existing contracts. Planning
must return to Definition if implementation reveals a material API/schema or
compatibility choice outside these decisions.

## Consequences

- Some progressive router read sets will include the exact declared Intake
  record earlier than before; tests must assert the intentional read boundary.
- Contradictory kind state becomes explicit Recovery rather than whichever route
  the Intake value currently selects.
- Empty issue diagnosis remains actionable by Intake without presenting a fake
  user authorization boundary.
- #23, #33 and #36 retain separate ownership and acceptance.
