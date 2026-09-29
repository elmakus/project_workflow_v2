# Issue #28 Intake prior-art and reproducer

Status: diagnosis confirmed; evidence only, no implementation authorization.

## Exact subject

`repair:execution-research-return-owner-precedence:v1`

Baseline: `main@d3ab917f02e4de91b7dbb17915c2287c2387333e`.

## Canonical contract readback

`workflow/RESEARCH.md` requires a completed Research obligation to return once to its exact recorded owner. The executable state contract accepts execution-owned return targets with prefixes `execution_resolution:`, `execution_prep:`, and `execution:`.

## Current selector behavior

The manifest-level Research branch in `tools/router.py` executes before Task Board routing. For a completed manifest Research record it resolves the return owner through a fixed map containing only `intake`, `brainstorming`, and `definition`.

The later Task-Board Research branch explicitly recognizes all three execution return prefixes and maps them to the correct execution/recovery obligation.

## Fresh executable reproducer

A fresh clone of this branch used the existing current-schema Router test fixture. The fixture's Task Board was given a Research obligation whose exact Research record was also declared by the workstream manifest. The record was:

- state: complete
- origin_role: execution_resolution
- origin_subject: M01-T04
- return_target: execution_resolution:M01-T04
- return_reconciliation: pending

Observed selector result:

`disposition = recovery`
`obligation = recovery_boundary`
`reason = selected workstream identity invalid: 'execution_resolution:M01-T04'`

This confirms the early manifest-level owner lookup shadows the valid later Task-Board execution-return path.

## Positive control

The existing production test `RouterTests.test_task_board_research_return_is_recovered_before_execution` passes on the same fresh clone. Without the shadowing manifest locator, the same completed execution-resolution Research correctly routes to `execution_resolution`.

## Adjacent scope

This is distinct from durable-schema drift and continuation policy. All participating records can satisfy the current executable schema. The defect is owner/precedence composition in the canonical selector when the single Research record is reachable through both lawful locators.

A bounded repair should preserve one exact Research return semantic across both locator paths, keep once-only reconciliation/cleanup behavior, and avoid broad restructuring of Execution, Research state, or continuation semantics.

## Source accounting

- Official/upstream: checked — canonical Router/Research/State contracts.
- Project/runtime: checked — current selector source plus fresh executable negative reproducer and positive control.
- Tracker/discussion: checked — Issue #28 exact diagnosis/dedup marker.
- Practitioner/community: not relevant — internal deterministic router defect with direct canonical and executable evidence.

No material source conflict was found.
