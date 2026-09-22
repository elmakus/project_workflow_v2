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

The manifest locates records only. Each pointed record owns only its semantic domain. Parent/stacked and later integration/review/cleanup fields are added only by their owning milestones.
