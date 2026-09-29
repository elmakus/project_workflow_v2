# Independent Plan Review — Issue #28 execution Research return-owner precedence

Verdict: GREEN

Subject: `git-blob:ac6f8c9ab6a9612a8bd6471537292f2bfdf6b023`

Acceptance authority:
- `requirements/ISSUE_28_EXECUTION_RESEARCH_RETURN_PRECEDENCE.md` — I28-R1–R9
- `decisions/ISSUE_28_EXECUTION_RESEARCH_RETURN_PRECEDENCE.md` — I28-D1–D7
- Definition revision `D1`

## Review result

The frozen P1 plan is consistent with the accepted Definition and contains an executable bounded strategy for the demonstrated defect.

- R1 / D1 / D3: it makes validated `execution_resolution:<subject>`, `execution_prep:<subject>`, and `execution:<subject>` return targets resolve to the same exact owner semantics already used by the Task-Board path.
- R2 / D2: it treats manifest and Task Board locators as two references to one Research record and does not introduce a duplicate obligation, lifecycle, queue, or durable state.
- R3 / D4: it distinguishes complete/pending, complete/applied, and consumed/applied behavior and preserves stale Board-pointer cleanup without replay.
- R4 / D5: it explicitly preserves active Research plus Intake/Brainstorming/Definition returns and existing fail-closed validation.
- R5–R6: its production-selector matrix covers all three execution prefixes, dual-locator behavior, applied reconciliation, cleanup, pre-execution controls, malformed/unsupported targets, existing Task-Board controls, focused contracts, and the full repository suite.
- R7 / D6: the planned implementation is a small routing/owner-resolution repair and rejects broader router, state, Research, Execution, and Recovery redesign.
- R8: the plan requires an exact semantic Result and REQUIRED independent implementation review before Card completion.
- R9 / D7: the Card and Close boundaries keep #28 isolated from integration, Issue closure, and other stabilization constituents.

The current selector structure makes the plan mechanically plausible: manifest-level completed Research currently resolves through a pre-execution-only owner map, while the Task-Board path already recognizes the three execution prefixes and maps them to Recovery, Execution Prep, and Execution. The proposed shared classifier/resolver therefore removes the demonstrated semantic divergence without requiring a new architecture.

No unresolved product decision, missing acceptance requirement, or material planning correction was found. P1 is suitable for approval and downstream Execution Prep after Premium C.
