# Decision — Use branch-first managed changes, mandatory issue alignment, and GitHub Issue tracking

- Decision ID: `ADR-PWV2-003`
- Date: `2026-09-22`
- Status: `accepted`
- Authority: `user`
- Related requirements: `requirements/PROJECT_WORKFLOW_V2.md`
- Related milestone/card: `none`

## Context

V1 branch-isolated workstreams provide strong recovery and cleanup semantics. Separately, V1 `#issue` could diagnose and autonomously implement a micro-fix before the user finished specifying the desired repair. The user explicitly rejects that behavior and also wants GitHub Issues to become the visible tracker for both issues and features.

## Decision

- One project = one durable project repository.
- Managed changes use branch-first, manifest-bound workstreams without a correctness-critical mutable global registry.
- `#feature` enters discovery/Brainstorming.
- `#issue` authorizes diagnosis/intake only.
- After diagnosis proposes a repair, at least one subsequent user alignment response is mandatory before implementation mutation, including micro-fixes.
- GitHub Issue tracker is created/recovered for `#issue` and `#feature` when supported, after deduplication.
- GitHub Issue is tracking/bookkeeping, not canonical workflow authority.
- Final scope-completing integration closes the tracker; intermediate PRs do not close it prematurely.

## Rationale

This preserves strong durable workstream recovery while restoring human control over intended repair behavior and adding a familiar external lifecycle tracker.

## Consequences

A micro-fix remains proportional but is no longer autonomous. Tracker correlation must be durable in workstream state. Close must read back tracker state.
