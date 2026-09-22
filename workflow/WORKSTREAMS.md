# Project Workflow V2 — Workstream Binding

Managed changes are branch-first and manifest-bound. Correctness never depends on a mutable repository-global workstream registry.

A selected workstream contains stable identity, original branch, exact creation commit, integration target, accepted authority locators and only concrete workstream-local state locators currently needed.

Supported M02 locators:
- `intake -> implementation/workstreams/<id>/INTAKE.toml`;
- `brainstorm -> .../BRAINSTORM.toml`;
- `research -> .../RESEARCH.toml`;
- `definition -> .../DEFINITION.toml`;
- `planning -> .../PLANNING.toml`;
- `plan_review -> .../PLAN_REVIEW.toml`;
- `task_board -> .../TASK_BOARD.toml` once implementation state exists.

Pre-execution state may therefore exist without a Task Board. This preserves branch-first durability without manufacturing execution state early.

Every locator is exact, workstream-bound and class-checked. A Plan Review locator requires matching Planning state and its immutable subject/revision/cycle. Cross-workstream, malformed, missing or contradictory owners must fail closed to Recovery; there is no root/default Task Board fallback.

The manifest locates records only. Intake owns alignment; Brainstorming owns promotion; Research owns return/reconciliation; Definition owns accepted authority/completeness/A; Planning owns plan lifecycle/A-B-C; Plan Review owns its verdict; Task Board owns implementation state.

Parent/stacked and later integration/review/cleanup fields are added only by their owning milestones.
