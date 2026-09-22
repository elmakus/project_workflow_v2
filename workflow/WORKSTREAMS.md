# Project Workflow V2 — Workstream Binding

Managed changes are branch-first and manifest-bound. Correctness never depends on a mutable repository-global workstream registry.

A selected workstream contains stable identity, original branch, exact creation commit, integration target, accepted authority locators and only the concrete workstream-local state locators currently needed.

Supported M02 locators:
- `intake -> implementation/workstreams/<id>/INTAKE.toml`;
- `brainstorm -> .../BRAINSTORM.toml`;
- `research -> .../RESEARCH.toml`;
- `definition -> .../DEFINITION.toml`;
- `task_board -> .../TASK_BOARD.toml` once implementation state exists.

A pre-execution workstream may therefore exist with Intake/Brainstorming/Research/Definition state and no Task Board. This preserves branch-first durability without manufacturing execution state early.

Every locator is exact, workstream-bound and class-checked. Cross-workstream, malformed or missing owners fail closed; there is no root/default Task Board fallback.

The manifest locates records only. Intake owns alignment contents; Brainstorming owns promotion; Research owns return/reconciliation; Definition owns accepted authority/completeness/premium-A; Task Board owns implementation state.

Parent/stacked and later integration/review/cleanup fields are added only by their owning milestones.
