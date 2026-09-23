# Decision — Keep one active Project Card and move implementation topology to the runtime

- Decision ID: `ADR-PWV2-004`
- Date: `2026-09-22`
- Status: `accepted`
- Authority: `user`
- Supersedes: V1 Codex Project-Card bounded-parallel scheduler for the V2 target
- Related requirements: `requirements/PROJECT_WORKFLOW_V2.md`
- Related milestone/card: `none`

## Context

V1 Codex introduced durable batch/lane/parallel-Card machinery. The user explicitly removed Project Workflow Card-level parallel execution while still wanting runtime/subagent parallelism inside one Card and wanting Main to preserve expensive reasoning capacity by delegating implementation when possible.

## Decision

- Exactly one Project Workflow Card executes at a time in a selected workstream.
- Remove Project-Card batch/lane scheduler state, universal `active_execution`, `returned`, and `transfer_ready`.
- Runtime may internally use any valid subagent topology, including concurrency, inside one Card.
- If a qualifying delegated implementation context exists, Main delegates implementation.
- Worker returns bounded result/evidence; Main validates/reconciles/persists project truth.
- A runtime without delegated implementation capability may execute directly.

## Rationale

This keeps durable state simple and portable without preventing Codex from exploiting internal orchestration capability.

## Consequences

V2 Task Board/Card schema becomes smaller. Runtime orchestration packages must satisfy Card authority but do not become Project Workflow state.
