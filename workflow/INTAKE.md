# Project Workflow V2 — Intake and issue alignment

Status: M02 common Intake/alignment slice.

Intake owns new managed intent before implementation authority exists. A marker or symptom is input, never repair authorization.

## Entry kinds

- `issue`: read-only diagnosis first. After a concrete repair outcome is proposed, implementation remains forbidden until a later user response explicitly authorizes that exact repair subject.
- `feature`: enter discovery; no issue-repair authorization is implied.
- `change`: neutral managed intent when issue/feature semantics are not asserted.

A new managed intent must not adopt an unrelated active workstream merely because one exists.

## Durable issue alignment

The exact workstream-local INTAKE record owns kind/lifecycle, diagnosis revision, current repair subject, semantic user-response class, alignment state/subject and bounded micro-fix candidacy.

For an issue:
- pending means no implementation authorization;
- question/concern/alternative is a response but not authorization;
- authorized requires an explicit authorization response bound to the exact current repair subject;
- changed repair subject invalidates stale alignment;
- micro-fix candidate is illegal before exact authorization.

Feature/change discovery may use `not_required`; later Brainstorming/Definition promotion remains separate.

## GitHub tracker

When supported for issue/feature work, Intake materializes or recovers the exact workstream-local tracker correlation after deduplication. Tracker operations follow `workflow/GITHUB_ISSUES.md`.

Tracker availability/state is bookkeeping only. It neither replaces alignment nor authorizes implementation. Ambiguous duplicate matches route to Recovery instead of creating another Issue.

## Routing

- no subsequent issue response -> real alignment stop;
- question/concern/alternative -> Brainstorming;
- exact authorized issue or completed feature/change Intake -> next durable obligation;
- malformed/stale/cross-workstream state -> Recovery.

Intake does not implement Execution, Planning, implementation review or Close.
