# Project Workflow V2 — Workstream Binding

Managed changes are branch-first and manifest-bound. Correctness never depends on a mutable repository-global workstream registry.

A selected workstream contains stable identity, original branch, exact creation commit, integration target, accepted authority locators and only concrete workstream-local state locators currently needed.

Supported M02 locators:
- `intake -> implementation/workstreams/<id>/INTAKE.toml`;
- `tracker -> .../TRACKER.toml`;
- `brainstorm -> .../BRAINSTORM.toml`;
- `research -> .../RESEARCH.toml`;
- `definition -> .../DEFINITION.toml`;
- `planning -> .../PLANNING.toml`;
- `plan_review -> .../PLAN_REVIEW.toml`;
- `task_board -> .../TASK_BOARD.toml` once implementation state exists.

Pre-execution state may exist without a Task Board. Every locator is exact, class-checked and workstream-bound.

Tracker state is bookkeeping only. `discovery` and `create_pending_readback` route through GitHub Issue recovery; `ambiguous` must fail closed to Recovery. Linked/unavailable tracker state cannot become authorization.

A Plan Review locator requires matching Planning state and exact immutable subject/revision/cycle. Cross-workstream, malformed, missing, stale or contradictory owners must fail closed to Recovery; there is no root/default Task Board fallback.

The manifest locates records only. Each pointed record owns only its semantic domain. Parent/stacked provenance and integration/cleanup ownership remain workstream-level semantics; terminal recovery never rewrites original branch/base/parent identity.

## Terminal recovery boundary

Before final integration, all unique knowable workstream-owned recovery artifacts must be present in the exact merge subject. After integration, closure may recover from that target-side package plus immutable PR/merge evidence even when the source ref has already disappeared; source-ref recreation for bookkeeping is forbidden.

A surviving source branch is cleanup input only. `safe_to_delete` is an optional fallback after terminal truth is independently durable, and deletion requires exact-head revalidation plus absence readback. Automatic deletion of a merged head needs no fallback record. Terminal-unmerged closure preserves only recovery/history metadata on the durable target-side package and never imports rejected implementation content.
