# Master Plan — deterministic non-stop continuation

Status: FROZEN  
Cycle: 1  
Entry subject: `deterministic-nonstop-continuation@2`

## Objective

Close Issue #16 by making normal invocation completion contingent on fresh canonical rerouting after every reconciled non-stop semantic step, while preserving the existing one-step router, owner-module authority, exact-subject review independence, USER_STOP composition, restartability, and readback-first external effects.

## Strategy

Implement the repair as a small common continuation contract plus a mechanically testable trajectory driver. Keep `tools/router.py` responsible only for selecting the next semantic obligation. The continuation layer owns only completion enforcement: durable reread, reroute, exact-obligation consumption, progress/cycle fencing, and legal-return classification. Runtime-specific entry/adapters consume that contract without copying workflow semantics.

No new canonical phase or durable runtime identity is introduced.

## Milestone M01 — Common continuation contract

Define the runtime-neutral route-after-reconcile contract in canonical workflow authority and the smallest implementation helper needed to evaluate whether normal return is legal.

Acceptance:
- every reconciled non-stop step requires fresh durable reread and reroute;
- return is legal only for an existing real stop, genuine non-remediable/fail-closed blocker boundary, or durable end-of-approved-scope;
- worker/role/Card/review/Research completion is never itself a return predicate;
- helper does not execute semantic owner policy or grant authority;
- no canonical Continuation phase/state/event ledger/session identity is added.

Primary coverage: PWV2-REQ-004..006, 031..037, 066..071; Definition invariants C1-C7, C11-C12.

## Milestone M02 — Progress, restart and external-effect safety

Add semantic progress/no-op/cycle fencing around continuation using ephemeral fingerprints derived only from authoritative semantic inputs.

Acceptance:
- unchanged obligation/fingerprint after claimed success fails closed;
- semantic cycles without new accepted evidence/authority fail closed;
- runtime safety bounds are technical fuses, never semantic success/stops;
- durable results/reviews/Research/external effects resume without replay after runtime loss;
- uncertain external effects require readback before retry;
- runtime/model/session/worker identifiers are not persisted as workflow authority.

Primary coverage: PWV2-REQ-004, 031..033, 037, 069; Definition invariants C4-C5, C8-C10.

## Milestone M03 — Review and USER_STOP composition

Integrate continuation with exact-subject Review realization and existing stop-delivery behavior.

Acceptance:
- a context that produced/repaired exact subject S cannot independently verdict S;
- RED may route to authorized corrective work without becoming a stop;
- if correction creates S2, its repairer cannot review S2;
- a genuinely independent internal reviewer may continue without fabricated external handoff;
- when independence cannot be realized, the existing fresh independent-review boundary is honored and USER_STOP delivery is applied;
- Issue #11 handoff behavior remains a stop postcondition only;
- non-boundary RED/GREEN/Card/Research transitions emit no synthetic handoff.

Primary coverage: PWV2-REQ-034..038, 067..071; Definition invariants C6-C7.

## Milestone M04 — Production entry/adaptor realization

Wire the common continuation contract into the production paths that currently can consume one correct route and return prematurely. Keep adapters thin and semantic-policy-free.

Acceptance:
- supported ChatGPT/manual and agent-style/Codex realizations follow the same canonical route trajectory from equivalent durable state;
- each adapter performs route -> exact owner obligation -> durable readback/reconcile -> reroute;
- adapters do not hard-code RED/GREEN/gate/Close semantics;
- runtime replacement between non-stop steps reconstructs the same next obligation from durable state;
- one canonical reconciler/writer remains responsible for shared workflow state.

Primary coverage: PWV2-REQ-005..015, 025..027, 067..071.

## Milestone M05 — Trajectory conformance and regression qualification

Add a test-only trajectory harness over the real production selector and disposable durable fixtures. Retain all existing pointwise router/state tests.

Required trajectory cases:
1. active Card -> valid result -> reconciliation -> review;
2. Review GREEN -> finalization -> next Card/Close;
3. Review RED -> bounded correction -> new subject/review;
4. RED reviewer repairs -> independent review required;
5. internal independent reviewer available;
6. external fresh-independence boundary required;
7. RED -> Research -> return-owner reconciliation;
8. RED -> Planning/Definition and due premium/authority gate;
9. durable result + runtime loss, no replay;
10. JIT predecessor success and stale-predecessor failure;
11. Close incomplete continues; Close complete ends exactly once;
12. issue alignment/promotion and Premium A/B/C boundaries stop exactly;
13. remediable inconsistency continues through Recovery; non-remediable blocker stops;
14. same fingerprint/no progress fails closed;
15. semantic cycle without new authority/evidence fails closed;
16. uncertain external effect readback-first;
17. runtime/model/session noise does not change semantic trajectory;
18. explicit user stop stops immediately;
19. non-boundary RED/GREEN/Card/Research completion has no handoff.

Acceptance:
- full existing automated suite remains GREEN;
- new trajectory suite proves both positive continuation and negative authority/safety boundaries;
- no regression broadens USER_STOP, Review authority, or end-of-scope semantics;
- live/manual qualification is limited to behavior that cannot be proven deterministically in fixtures.

Primary coverage: PWV2-REQ-074 and issue-specific acceptance surface from the Research regression matrix T01-T25.

## Execution ordering and Card strategy

Execution Prep should materialize bounded Cards in milestone order. M01 and M02 establish the common contract/safety core before adapter wiring. M03 may be implemented after the core but must be complete before production adapter qualification. M04 wires production realization only after common semantics are testable. M05 is the final qualification milestone, with trajectory tests added incrementally alongside earlier Cards and completed as a full regression gate.

Cards may be split by independently testable code/document surfaces, but must not split semantic authority between competing implementations. Exactly one Project Workflow Card executes at a time.

## Gates

- Every implementation Card follows normal result/review semantics.
- Any material change to strategy, milestone structure, accepted authority, or requirement coverage returns to a new Strategic Planning cycle.
- Any newly discovered factual uncertainty that can change architecture routes to Research.
- Any unresolved product/authority choice routes to the appropriate human-owned stop.
- Final integration requires affected verification and exact-subject independent review coverage under existing workflow rules.

## Planner challenge audit

GREEN.

Challenges considered and rejected:
- RED-only patch: fails equivalent GREEN/Research/Card/Close cases.
- router-as-executor: mixes selection, mutation and runtime realization.
- unconditional loop: unsafe without progress/cycle fencing.
- fixed iteration cap as semantic termination: runtime fuse cannot establish completion.
- generic retry: violates external-effect uncertainty/readback rules.
- handoff after each role boundary: broadens USER_STOP incorrectly.
- same-context self-review after repair: violates exact-subject independence.
- durable continuation/session ledger: unnecessary second state machine and runtime identity leakage.

The plan covers the complete promoted Definition and Research invariants without changing accepted product authority.
