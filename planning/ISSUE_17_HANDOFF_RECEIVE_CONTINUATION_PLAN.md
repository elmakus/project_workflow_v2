# Issue #17 — Handoff receive continuation plan

Planning cycle: 1  
Entry subject: `D01`  
Definition authority: `requirements/ISSUE_17_HANDOFF_RECEIVE_CONTINUATION.md`, `decisions/ISSUE_17_HANDOFF_RECEIVE_CONTINUATION.md`

## Strategy

Implement the receive seam as a small runtime-neutral contract layered on the accepted Issue #16 continuation machinery. A fresh-session locator remains untrusted input. Receipt validates its four fields against canonical repository state and the freshly selected route, consumes only an owner-declared transferable boundary, then hands the resulting non-stop obligation into the existing continuation loop. No second router, session ledger, model/provider state, or generic confirmation phase is introduced.

## Milestone M06 — Receive contract and qualification

### M06-T01 — Runtime-neutral locator receive contract

Add the smallest production helper needed to parse/validate the four-field locator and bind it to repository, branch, durable pointer, and expected current route/subject. Define explicit outcomes for transferable receipt, stale/contradictory input, malformed input, and boundaries that remain genuine stops.

Acceptance:
- locator prose is never authority;
- exact current Premium A/B/C handoffs can be recognized without weakening their owner semantics;
- independent Review transfer rejects a receiver that is not semantically independent when independence is required;
- wrong repository/branch/workstream/pointer/entry subject fails closed;
- no runtime/model/session identity becomes canonical state.

Required verification:
- focused unit tests for exact, stale, malformed, forged and contradictory locators;
- negative tests proving locator fields cannot manufacture authorization or a review verdict.

Review requirement: REQUIRED.

### M06-T02 — Canonical bootstrap and continuation composition

Integrate successful receipt with the existing router and Issue #16 continuation contract. The first receiver invocation must enter the selected obligation immediately and, after durable reconciliation, reroute repeatedly until the next real stop.

Acceptance:
- valid receipt consumes only the transferable handoff/context-selection boundary;
- no generic second `continue` is requested;
- durable semantic results reconcile without replay;
- uncertain external effects still require readback before retry;
- Recovery/no-progress fencing remains intact;
- genuine authorization, blocker, explicit-user and end-of-scope stops remain intact.

Required verification:
- route/continuation tests covering advancement after receipt and duplicate receipt after durable advancement;
- regression tests for readback, Recovery and no-progress behavior.

Dependency: M06-T01 exact GREEN result.  
Review requirement: REQUIRED.

### M06-T03 — Supported harness delivery adapters

Wire the common receive contract into supported ChatGPT/Codex bootstrap surfaces without copying workflow policy into adapter prompts or package metadata. Keep the emitted fresh-session form exactly four locator fields.

Acceptance:
- ChatGPT fresh-context entry and Codex/local bootstrap reach equivalent common receive semantics;
- adapters contain only bootstrap/UX glue;
- four-field locator remains narrative-free;
- Premium B retains mandatory fresh independence; Premium A/C remain transferable optional handoffs;
- existing sender-side delivery behavior from Issue #11 remains unchanged except for compatible receive consumption.

Required verification:
- ChatGPT delivery tests;
- Codex delivery/bootstrap tests;
- adapter-equivalence assertions against the common receive contract.

Dependency: M06-T02 exact GREEN result.  
Review requirement: REQUIRED.

### M06-T04 — End-to-end qualification and regression closure

Exercise producer → emitted locator → fresh receiver → useful obligation work → canonical reroute through the complete accepted matrix.

Acceptance matrix:
- Premium A, B and C transfer;
- independent implementation Review and rejection of non-independent receipt;
- stale, wrong, forged and inconsistent Entry obligation;
- durable-state advancement and duplicate receipt without replay;
- external-effect uncertainty/readback and Recovery;
- continuation through subsequent non-stop steps until a new real stop;
- equivalent semantics across supported adapters/harnesses;
- four-field locator without narrative imperative;
- genuine authorization and end-of-scope stops remain intact.

Required verification:
- focused Issue #17 qualification suite;
- full repository test suite;
- no forbidden second router/session ledger/provider catalog/runtime authority;
- final affected-surface regression against Issue #16 continuation tests and user-stop delivery tests.

Dependency: M06-T03 exact GREEN result.  
Review requirement: REQUIRED.

## JIT / execution preparation

Materialize stable Task Cards from these four tasks after Plan Review and Premium C. M06-T01 is initially READY. Later Cards bind exact predecessor result identities before launch; if implementation details become unknowable until a predecessor lands, retain them as Task Board JIT triggers rather than speculative contracts.

## Coverage audit

- Receive consumption: M06-T01 + M06-T02.
- Canonical authority/fail-closed safety: M06-T01 + M06-T04.
- Issue #16 composition/no duplicate lifecycle: M06-T02 + M06-T04.
- Premium and independent-review transfer: M06-T01 + M06-T03 + M06-T04.
- Replay/readback/Recovery: M06-T02 + M06-T04.
- Supported adapters and locator-only delivery: M06-T03 + M06-T04.
- Genuine stops/end-of-scope preservation: M06-T02 + M06-T04.

Planner challenge audit: GREEN. The plan covers every accepted Definition requirement, keeps runtime-specific glue outside canonical semantics, sequences dependencies so each later Card can bind immutable predecessor results, and introduces no product decision beyond the promoted Issue #17 scope.
