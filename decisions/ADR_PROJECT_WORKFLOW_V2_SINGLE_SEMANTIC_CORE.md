# Decision — Project Workflow V2 uses one runtime-neutral semantic core

- Decision ID: `ADR-PWV2-001`
- Date: `2026-09-22`
- Status: `accepted`
- Authority: `user`
- Supersedes: V1 fixed-policy semantic split for the V2 target
- Related requirements: `requirements/PROJECT_WORKFLOW_V2.md`
- Related milestone/card: `none`

## Context

V1 evolved separate `chatgpt_only` and `codex_only` semantic trees. They duplicated most lifecycle semantics, drifted over time, and encoded runtime realization details into project workflow state. The V2 goal is runtime portability and lower maintenance cost without weakening correctness.

## Decision

Build one clean V2 semantic state machine in one canonical `workflow/` tree.

New V2 durable state:
- declares only the common V2 workflow contract;
- does not select ChatGPT/Codex semantic policies;
- does not persist current runtime/model/session/worker identity;
- remains portable between supported runtimes at durable boundaries.

Project Workflow owns semantic obligations, authority and durable correctness. Runtime owns concrete realization.

## Rationale

The same project obligation should have the same meaning regardless of whether ChatGPT or Codex realizes it. Product identity is delivery/runtime context, not project semantics.

## Alternatives considered

- Keep separate complete ChatGPT/Codex workflows — rejected due duplication/drift.
- Add a generic execution-policy switch to V2 — rejected because it preserves the wrong abstraction.
- Persist runtime identity for recovery — rejected because durable project state is sufficient and runtime identity is transient.

## Consequences

- V2 is a clean repository rather than another policy namespace in V1.
- Migration reads legacy policy state only as transition input.
- Bootstrap differs by surface, but semantic routing after bootstrap is common.
