# PWV3 Brainstorming R5 — owner direction: 3.x consolidation + /goal execution path

Date: 2026-10-02
Workstream: `change-workflow-successor-product`
Status: **OWNER DIRECTION ACCEPTED / RESEARCH REQUIRED**
New Brainstorming subject: `workflow-successor-product@5`

## Trigger

The previously accepted Definition D09 reached Premium A. Before authorizing Strategic Planning, the human owner changed the product scope.

This is a substantive product/scope change and therefore reopens Brainstorming. The prior `workflow-successor-product@4` Definition/Review evidence remains immutable historical authority for that exact old subject but is stale for forward progression of revision 5. Premium A on the old subject is not forward-consumable while revision 5 is active.

## Fixed owner direction

### 1. Consolidate later PWV3 roadmap into 3.0

Everything previously planned as compatible PWV3 product evolution for later `3.x` releases is to be reconsidered as part of the initial `3.0.0` product scope rather than intentionally deferred merely because it had been assigned to `3.1`, `3.2+` or “later compatible evolution”.

This includes the current Definition's deferred/evolution candidates such as:
- historical-reader / contract-evolution support;
- explicit safe active-workstream adopt-release / roll-forward behavior;
- release/contract compatibility matrix and downgrade refusal;
- post-materialization/JIT refinement improvements;
- semantic Review reuse optimization;
- richer affected-cone diagnostics;
- richer health/maintenance and doctor/inspect/resume explanations;
- richer deterministic context packs;
- improved Pi/Paseo Generic Worker ergonomics / allow-lists;
- richer GitHub Issue mutation/reconciliation helpers;
- safe anomaly dedup/file-and-continue where evidence supports it;
- multi-generation historical reader/conversion support where it can be meaningfully expressed for initial release;
- historical-reader retirement/compaction where meaningful;
- generalized within-PWV3 migration helpers;
- material fingerprint optimization;
- branch cleanup automation;
- other current Definition statements whose only reason for exclusion from 3.0 is “later compatible evolution”.

Explicitly removed/out-of-roadmap product ideas remain excluded unless separately reopened by owner authority. The research must distinguish “move into 3.0” from impossible future-only semantics that need reformulation rather than literal implementation.

### 2. Add a second execution mode using Pi `/goal`

PWV3 must support an execution choice in addition to native PWV3 Card-by-Card execution:

- **native PWV3 execution** — the existing deterministic PWV3 execution path;
- **`/goal` execution** — hand the accepted implementation objective/package to a Pi goal-mode runtime that autonomously implements the product, runs tests, fixes known/discovered implementation bugs within accepted scope, and continues until its exact completion/stop condition is met.

The target owner intent for `/goal` mode is:
- build/implement the accepted functionality;
- run and repair tests;
- fix known implementation defects found during execution when doing so does not require upstream product/Definition/Plan authority changes;
- deliver a working candidate;
- stop before the independent **Global Bug Hunt** boundary;
- Global Bug Hunt remains a separate ChatGPT/OP operation after goal execution rather than being delegated to `/goal`.

No final decision is yet made on whether `/goal` begins after accepted Plan Review or only after accepted Execution Package Review.

No final decision is yet made on whether Plan / Execution Package artifacts must differ by execution mode, or whether one execution-neutral package can support both and the mode can be selected only immediately before execution.

## Required research questions

Research must establish, from official/upstream evidence, actual runtime/project evidence, tracker/discussion evidence and practitioner/community evidence:

1. What current Pi `/goal` implementations actually guarantee: persistence, auto-continuation, branch/session behavior, completion/blocking, testing/verification behavior, safety limits and recovery.
2. Whether a goal can reliably consume a detailed reviewed Plan directly, or whether it needs a concretized Execution Package/task decomposition before autonomous work.
3. Which boundary is safer and simpler:
   - launch `/goal` after accepted Plan Review and let it perform execution-prep-like decomposition itself; or
   - launch only after accepted Execution Package Review and make `/goal` a pure execution engine.
4. Whether one Plan Package and one Execution Package can be execution-mode-neutral, with `native_pwv3` vs `goal` chosen later, or whether mode-specific information must be frozen earlier.
5. What exact contract a `/goal` objective needs: inputs, repo/branch/worktree binding, allowed changes, test obligations, stop predicate, escalation conditions, durable result/evidence and crash/resume semantics.
6. How `/goal` should interact with PWV3 Result/Review semantics while it performs many implementation/test/repair iterations internally.
7. How to stop `/goal` at the correct boundary so that the resulting candidate is ready for independent Global Bug Hunt without accidentally performing/consuming that OP boundary.
8. Whether Targeted Bug Hunt remains before/inside goal execution, moves into normal execution verification, or remains a separate OP obligation; owner only fixed that Global Bug Hunt is separate and after `/goal`.
9. Which currently-deferred 3.x capabilities are structurally required to make long-running `/goal` execution/recovery safe in 3.0.
10. What compatibility/versioning model is coherent when formerly “future 3.x” evolution support becomes first-release capability.
11. What changes to Brainstorming/Definition/Planning/Execution Prep/Execution/Final Qualification acceptance surfaces are required without importing `/goal` implementation internals into PWV3 semantics.
12. Whether current third-party `/goal` implementations are sufficient production dependencies or PWV3 needs a qualified adapter/contract around one selected implementation.

## Non-decisions

Research must not decide user/product authority questions by popularity. It should produce evidence-backed alternatives and a recommendation for the owner where genuine choices remain.

The prior D09 accepted Definition is not silently edited during Research. Revision 5 must be reconciled in Brainstorming and then explicitly promoted before a new Definition revision can become accepted authority.
