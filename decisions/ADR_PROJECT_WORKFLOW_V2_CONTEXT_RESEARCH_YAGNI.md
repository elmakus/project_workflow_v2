# Decision — Make progressive disclosure, broad prior-art Research, YAGNI, and selective technical contracts global V2 invariants

- Decision ID: `ADR-PWV2-006`
- Date: `2026-09-22`
- Status: `accepted`
- Authority: `user`
- Related requirements: `requirements/PROJECT_WORKFLOW_V2.md`
- Related milestone/card: `none`

## Context

Codex context is costly, V1 already contains valuable Research/YAGNI guidance, and the user wants agents to compare their own ideas against real-world prior art rather than repeatedly reinventing solutions. The user also wants rigor without mandatory duplicate OpenSpec artifacts for trivial fixes.

## Decision

- Bootstrap/router/stages use progressive disclosure and exact refs rather than broad preload.
- Every Research/diagnosis performs a mandatory-but-proportional prior-art check.
- Source classes include official/upstream, actual project/runtime evidence, public issues/discussions and practitioner/community sources such as forums/Reddit where relevant.
- Source weight/conflicts are explicit; community practice informs but does not automatically override stronger evidence.
- YAGNI/proportional design is global.
- Every change has a precise Task Card/fix contract.
- Separate technical-contract/OpenSpec artifact is JIT/selective only when it materially adds behavior/design-contract value beyond the Card.
- Adaptive grilling remains intrinsic to Brainstorming and `#grill` is removed.

## Rationale

This balances evidence breadth, context economy, rigor and simplicity.

## Consequences

Research tests must prove source breadth/weighting. Skill/router tests must prove progressive disclosure. Technical-contract tests must include both trivial no-extra-artifact and complex-trigger cases.
