# Project Workflow V2 — Intake and issue alignment

Status: M02-T01 common Intake/alignment slice.

Intake owns new managed intent before implementation authority exists. A marker or symptom is input, never repair authorization.

## Entry kinds

- `issue`: read-only diagnosis first. After a concrete repair outcome is proposed, implementation remains forbidden until a later user response explicitly authorizes that exact repair subject.
- `feature`: enter discovery; no issue-repair authorization is implied.
- `change`: neutral managed intent when issue/feature semantics are not asserted.

A new managed intent must not adopt an unrelated active workstream merely because one exists.

## Durable issue alignment

The workstream may point to one exact `INTAKE.toml` record. That record owns:
- kind and lifecycle state;
- diagnosis revision;
- current exact repair subject;
- semantic class of the latest relevant user response;
- alignment state and the exact subject authorized;
- whether the already-aligned repair is a bounded micro-fix candidate.

For an issue:
- `alignment_state = "pending"` means no implementation authorization;
- a `question`, `concern` or `alternative` response is durable evidence that the user responded, but is not authorization;
- `alignment_state = "authorized"` is valid only with `response_kind = "authorization"` and `alignment_subject == repair_subject`;
- changing `repair_subject` makes old authorization stale and validation fails closed until alignment is reconciled;
- `micro_fix_candidate = true` is illegal before exact authorization.

For feature/change discovery, alignment may be `not_required`; later Brainstorming/Definition promotion gates remain separate.

## Routing

- no subsequent issue response yet -> real user alignment stop;
- question/concern/alternative -> Brainstorming owns continuation (full semantics arrive in M02-T02);
- exact authorized issue or completed feature/change Intake -> continue to the next durable obligation;
- malformed/stale/cross-workstream Intake state -> Recovery.

Intake does not implement Execution, Brainstorming, Research, Definition, Planning, tracker writes or Close.
