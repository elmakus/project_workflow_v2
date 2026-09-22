# Project Workflow V2 — Workstream Binding

Managed changes are branch-first and manifest-bound. No mutable repository-global workstream registry participates in correctness.

A selected workstream minimum contains:
- stable workstream_id;
- original branch;
- exact created_from Git commit;
- integration_target;
- exact accepted authority locators;
- at least one concrete workstream-local state locator owned by the current stage.

During pre-execution Intake, the manifest may contain the exact Intake locator before any Task Board exists. This is required so branch/workstream identity exists before the first change-specific durable record without manufacturing execution state early.

When implementation state is materialized, the Task Board locator must bind back to the same workstream_id and original branch. Intake and Task Board locators, when present, must use their exact workstream-local paths. Cross-workstream, cross-branch, malformed or missing locators fail closed; never fall back to a root/default board.

Intake owns diagnosis/alignment contents; the manifest only locates it. Task Board owns mutable implementation state after it exists. Parent/stacked provenance and later routing fields are added only when a concrete milestone owns them.
