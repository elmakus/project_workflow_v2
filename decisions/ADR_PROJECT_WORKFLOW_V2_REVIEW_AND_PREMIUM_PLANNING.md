# Decision — Use exact-subject independent review and explicit premium planning handoffs

- Decision ID: `ADR-PWV2-005`
- Date: `2026-09-22`
- Status: `accepted`
- Authority: `user`
- Related requirements: `requirements/PROJECT_WORKFLOW_V2.md`
- Related milestone/card: `none`

## Context

The user wants common capability-first review semantics for implementation work but also wants the highest-leverage Strategic Planning and Plan Review to use deliberately separate best-model contexts.

## Decision

- Implementation/final review uses generic exact-subject append-only attempts with semantic independence.
- REQUIRED and activated RECOMMENDED block completion.
- Runtime identity does not define independence; material subject production/repair does.
- Stage-6 Plan Review is a deliberate exception to generic internal capability-first review.
- Premium stop A occurs after Definition before material Planning.
- Premium stop B occurs after Master Plan freeze; planner may not spawn its own Stage-6 reviewer.
- Plan Review occurs in a fresh independent best-available-model context.
- Premium stop C occurs after GREEN plan approval before Execution Prep.
- Material later replan repeats A/B/C.
- Micro-fixes can bypass full Planning only after issue user alignment.

## Rationale

This spends the strongest reasoning budget on the decisions with the highest downstream leverage while retaining efficient capability-first review elsewhere.

## Consequences

The router must treat A/B/C as real human-facing stops that survive Recovery. Canonical workflow must not hard-code current model product names.
