# Project Workflow V2 — Definition Complete / Premium Stop A

Date: 2026-09-22
Workstream: `feature-common-preexecution-core`
Branch: `feat/common-preexecution-core`
State: `definition_complete`
Next obligation: `strategic_planning`
Stop: `premium_stop_A`

## Canonical accepted authority

Requirements:
- `requirements/PROJECT_WORKFLOW_V2.md` revision R1 — approved

Accepted decisions:
- `decisions/ADR_PROJECT_WORKFLOW_V2_SINGLE_SEMANTIC_CORE.md`
- `decisions/ADR_PROJECT_WORKFLOW_V2_DELIVERY_BOOTSTRAP.md`
- `decisions/ADR_PROJECT_WORKFLOW_V2_MANAGED_CHANGE_LIFECYCLE.md`
- `decisions/ADR_PROJECT_WORKFLOW_V2_EXECUTION_BOUNDARY.md`
- `decisions/ADR_PROJECT_WORKFLOW_V2_REVIEW_AND_PREMIUM_PLANNING.md`
- `decisions/ADR_PROJECT_WORKFLOW_V2_CONTEXT_RESEARCH_YAGNI.md`

Supporting coverage/validation:
- `brainstorming/V1_TO_V2_COVERAGE_MATRIX.md`
- `brainstorming/V2_VALIDATION_MATRIX.md`

Target implementation repository:
- `elmakus/project_workflow_v2` — verified existing, private and empty at Definition time.

## Definition verdict

GREEN.

All material target-state requirements, constraints, non-goals and strategic decisions needed before Planning are accepted. No blocking Research obligation or unresolved user/product choice remains.

## Premium stop A

Do not begin Strategic Planning in the Definition context.

The next context should use the best available model for Strategic Planning and:
1. recover this workstream manifest;
2. treat the approved requirements + ADRs above as canonical authority;
3. build the Master Plan mapping PWV2-REQ-001..076 to staged implementation in the new V2 repository;
4. preserve the V1->V2 coverage matrix and validation matrix as mandatory planning inputs;
5. stop again at premium stop B after the exact Master Plan review subject is durably frozen.

No production V2 implementation has started.
