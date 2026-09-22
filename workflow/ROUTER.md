# Project Workflow V2 Router — M01 feasibility stub

This file exists only to prove the accepted installed-package delivery shape during M01-T02.

- Canonical V2 workflow authority is bundled under this plugin's local `workflow/` tree.
- The Codex bootstrap Skill and SessionStart hook may locate this router, but must not duplicate its semantics.
- Ordinary operation must not fetch remote workflow policy to replace this bundled authority.
- Missing or unreadable bundled authority is a blocking package error and must fail closed.

The complete obligation router and lifecycle semantics are intentionally deferred to the approved M01-T03/M01-T04 work. This feasibility stub is not production acceptance and must not be treated as the final V2 router.
