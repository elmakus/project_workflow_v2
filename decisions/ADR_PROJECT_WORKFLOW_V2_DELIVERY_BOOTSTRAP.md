# Decision — Deliver one V2 product through GitHub to ChatGPT and a thin plugin to Codex

- Decision ID: `ADR-PWV2-002`
- Date: `2026-09-22`
- Status: `accepted`
- Authority: `user`
- Related requirements: `requirements/PROJECT_WORKFLOW_V2.md`
- Related milestone/card: `none`

## Context

The user wants to update Project Workflow once, then make the latest semantics available to ChatGPT from the repository and to Codex by updating the plugin. The plugin must not become a second product to maintain or a context-heavy policy copy.

## Decision

- New production target repository: `elmakus/project_workflow_v2`.
- ChatGPT Project Instructions point to that repository and enter the common V2 bootstrap/router.
- Codex uses installed plugin namespace `pw`, Skill `project_workflow_v2`, target invocation `$pw:project_workflow_v2`.
- Plugin packages the same canonical `workflow/` files directly.
- SessionStart/Skill are tiny bootstrap/location/recovery surfaces only.
- Codex reads bundled workflow policy locally during ordinary operation.
- Project-local enablement/provisioning belongs to `newproject-skill`.
- No project-level exact workflow version pin is added for the user's current operational model.

## Rationale

One canonical semantic tree eliminates policy synchronization and keeps Codex context small.

## Consequences

Normal semantic changes touch only canonical workflow files. Skill/hook/manifest changes are needed only for bootstrap/package behavior changes. Plugin update propagation must be live-tested before production acceptance.
