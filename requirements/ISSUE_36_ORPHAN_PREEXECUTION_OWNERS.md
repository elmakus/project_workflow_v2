# Issue #36 — orphan pre-execution owner requirements

Revision: `R1`  
Status: `accepted`  
Definition source: `orphan-preexecution-owners@1`  
Repair subject: `repair:orphan-preexecution-owner-prerequisites:v1`

## Goal

A manifest-declared current Planning or Plan Review owner must not disappear from the legal route merely because its prerequisite owner locator is missing. Reject the inconsistent selected state before dispatching an unrelated downstream obligation, while preserving valid progressive owner selection.

## Requirements

### I36-R1 — Planning prerequisite closure

A selected workstream that declares `[planning]` without a current `[definition]` locator MUST fail closed to Recovery rather than route to Execution, Brainstorming, or any other downstream/ordinary phase. This includes a syntactically valid draft planning cycle with premium A due and an otherwise active Task Board.

### I36-R2 — Plan Review prerequisite closure

A selected workstream that declares `[plan_review]` without a current `[planning]` locator MUST fail closed to Recovery. A present GREEN/active Definition, an active Board or a premium route cannot make the orphan Plan Review disappear. The chain through Definition is also required for Plan Review via I36-R1.

### I36-R3 — Selected-owner precedence and progressive reading

Enforce these **locator prerequisite relations** on the production selected-state path before an unrelated pre-execution/implementation stage may be dispatched. Do not silently consume the orphan as an accepted Planning/Review result, invent a missing owner, or normalize/delete a record. Validation of locally selected records and earlier owner routes remains progressive; do not scan or validate every downstream file at bootstrap merely to establish a missing-locator relation.

### I36-R4 — Earlier independent owner semantics

Do not change Intake diagnosis/alignment, active or returning Research, GitHub tracker recovery, or the Brainstorm-owned explicit user stop. A valid selected explicit stop retains its controlling semantics when the #33 constituent is composed; #36 does not reimplement #33 in its separate branch. Co-bound compatibility of these guards must be qualified before any composed integration; an isolated #36 baseline MUST NOT claim that #33 is already present or GREEN.

### I36-R5 — Positive valid routes

With lawful owner relations, preserve valid active Definition, Definition GREEN/A due, A satisfied/draft Planning, frozen B, approved C and matched Plan Review, and valid Task Board dispatch. Declared prerequisites that exist but whose records are malformed or stale retain their own existing fail-closed validation when reached.

### I36-R6 — Exact defect coverage

Automated tests MUST use production `select_route` for: Planning-without-Definition and Plan-Review-without-Planning (both with active Board); Plan Review orphan with GREEN Definition; missing owner vs malformed content distinction; valid owner controls; read-set behavior and no mutation. Compare with current-baseline defect evidence and include cumulative state/router/stop/continuation regression coverage. A clean detached exact-commit readback MUST exercise the production selector and full repository suite.

### I36-R7 — Independent exact-subject review

The implementation subject, normalized semantic Result and stable Card acceptance must be durably identified; a context that implemented/repaired the subject MUST NOT issue its independent implementation verdict. GREEN on the exact subject is required before Card completion. A review verdict does not authorize integration or tracker closure.

### I36-R8 — Scope and authorization isolation

No generic policy engine, universal event log, historical migration, #33 explicit-stop implementation, #32 Intake repair, #28 Research-return reorder, #31 Stage-6 history, #29 Close proof, #23/#26 parity/reconciliation, tracker mutation/closure, integration or deployment under this repair. Program P1 and Issue #36 text are provenance/strategy inputs, not this repair's approval or premium satisfaction.

### I36-R9 — No hidden authority transfer

This Definition accepts behavior and qualification for the exact aligned subject only. Material strategy changes require its own Planning cycle/gates; accepted product/scope changes return to Definition/Brainstorming. Valid concurrent branch work or another constituent Result does not silently satisfy #36 tests or review.

## Acceptance boundary

The selected repair subject has a testable behavior and bounded exclusions. Premium A is due before Strategic Planning; B/independent Plan Review/C and Execution Prep remain separate. Definition GREEN neither implements the guard nor authorizes integration.
