---
name: project_workflow_v2
description: Enter or recover Project Workflow V2 through the canonical runtime-neutral router.
---

Use this Skill only as the thin Codex entrypoint for the installed `pw` package.

1. Locate the installed package root that contains this Skill, `.codex-plugin/`, `hooks/`, and `workflow/`.
2. Read the bundled canonical router at `<plugin-root>/workflow/ROUTER.md`.
3. Let that router recover the consumer repository's exact durable project/workstream state and progressively select only the current module and authority it requires.
4. If the installed root/router is missing, malformed, ambiguous, or escapes the package root, fail closed.

The accepted invocation is `$pw:project_workflow_v2`.

Do not fetch remote workflow policy during ordinary operation, fall back to V1, reconstruct policy from chat memory, copy workflow semantics into this Skill, or select semantics from runtime/model/session identity.
