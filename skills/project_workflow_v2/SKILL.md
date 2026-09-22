---
name: project_workflow_v2
description: Enter or recover Project Workflow V2 by locating this installed plugin's bundled canonical router.
---

Use this Skill only as a thin Project Workflow V2 entry/recovery bootstrap.

1. Resolve this installed Skill's plugin root (the repository root containing `.codex-plugin/`, `skills/`, and `workflow/`).
2. Read the canonical bundled router at `<plugin-root>/workflow/ROUTER.md`.
3. Follow only that router and the exact durable project authority/state it selects.
4. Durable repository state outranks chat recollection.

Do not copy Project Workflow semantics into this Skill.
If the bundled router is absent or unreadable, fail closed instead of reconstructing policy.
