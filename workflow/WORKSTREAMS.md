# Project Workflow V2 — Workstream Binding Minimum

Managed changes are branch-first and manifest-bound. No mutable repository-global workstream registry participates in correctness.

A selected workstream minimum contains:
- stable workstream_id;
- original branch;
- exact created_from Git commit;
- integration_target;
- exact task_board locator.

The Task Board must bind back to the same workstream_id and original branch. Locator class and path must match the selected artifact class. Cross-workstream, cross-branch, malformed or missing locators fail closed; never fall back to a root/default board.

Parent/stacked provenance and later routing fields are added only when a concrete milestone owns them.
