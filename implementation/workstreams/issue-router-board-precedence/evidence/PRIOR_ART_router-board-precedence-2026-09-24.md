# Prior art — router board precedence (2026-09-24)

Result: `prior-art:router-board-precedence:v1:no-blocker` for
`repair:approved-plan-co-bound-board-precedence:v1`. Conflicts: none.

- official_upstream (checked, primary): `workflow/ROUTER.md` progressive read
  order and approved-plan/execution_prep routes; `workflow/STATE.md` Task Board
  ownership and fail-closed binding rules; `workflow/INTAKE.md`,
  `workflow/RESEARCH.md` Intake-origin prior-art contract; installed
  `tools/router.py` and `tools/state_contract.py` as executable authority.
- project_runtime (checked, direct): inspected `tools/router.py:408-430`
  (early `execution_prep` returns) vs line 473 (Board read); branch
  `work/pwv2-router-board-precedence-hotfix` at base
  `986affffb7ba816e260e48549bf56e198ed51c21`; no Board locator in this
  workstream yet, so no-board prep path is preserved by construction.
- tracker_discussion (checked, supporting): read-only `gh issue list` on
  `elmakus/project_workflow_v2` returned `[]` (zero issues); no prior-art
  issue found. Tracker is bookkeeping-only per `workflow/STATE.md` and cannot
  authorize or block the repair.
- practitioner_community (not_relevant, supporting): internal canonical state
  semantics; external opinion cannot override accepted repository authority.
