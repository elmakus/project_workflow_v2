# M01-T01 — Implementation evidence

## Implementation subject

`elmakus/project_workflow_v2@331ab118fb77dde1bdd703c91e2dee50ce6f77ae`

## Delivered scope

- Added `validate_selected_intake_relation` in `tools/state_contract.py` to require exact selected `WORKSTREAM.kind` / `INTAKE.kind` equality without mutation, coercion, fallback, or schema expansion.
- Moved the exact declared Intake read and local/composite validation ahead of Research dispatch in `tools/router.py`, while reusing the validated record for later Intake routing.
- Added a non-whitespace issue repair-subject guard that keeps empty and whitespace-only subjects in Intake diagnosis for every response class before prior-art/alignment dispatch.
- Clarified the two routing invariants in `workflow/INTAKE.md`.
- Added direct relation tests, all six unequal ordered kind pairings, blank/response matrices, mismatch-before-Research coverage, and same-kind issue/feature/change plus Research controls.

## Acceptance verification

Main verified exact implementation commit `331ab118fb77dde1bdd703c91e2dee50ce6f77ae` in the selected worktree:

- `python3 -m unittest tests.test_state_contract tests.test_router tests.test_execution_contract tests.test_recovery_contract tests.test_continuation_contract` — 99 tests passed.
- `python3 -m unittest discover -s tests -p 'test_*.py'` — 282 tests passed.
- Production router/composite-validator import and same-kind control — passed.
- `git diff --check` for the exact implementation commit — clean.

A clean detached consumer at exact commit `331ab118fb77dde1bdd703c91e2dee50ce6f77ae` independently passed:

- production imports and direct composite same-kind control;
- `python3 -m unittest tests.test_state_contract tests.test_router` — 78 tests passed;
- full unittest discovery — 282 tests passed;
- `git diff --check` — clean.

## Scope check

No #23/#33/#36 behavior, migration or historical normalization, Task Board/Review/Close redesign, runtime identity, tracker mutation, issue closure, integration, deployment, or broad policy-kernel adoption was introduced. No real-LLM or connected-runtime qualification was required by this Card.
