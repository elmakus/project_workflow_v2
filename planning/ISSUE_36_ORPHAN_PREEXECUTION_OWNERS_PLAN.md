# Issue #36 — orphan pre-execution owner closure plan P1

## 1. Exact subject and accepted authority

Workstream `issue-orphan-preexecution-owners`, cycle `1`, entry Definition `D1`, revision `P1`. Premium A was satisfied for D1 before material Planning.

Accepted authority: `requirements/ISSUE_36_ORPHAN_PREEXECUTION_OWNERS.md` I36-R1–R9; `decisions/ISSUE_36_ORPHAN_PREEXECUTION_OWNERS.md` I36-D1–D7; exact promoted `orphan-preexecution-owners@1`; canonical `workflow/WORKSTREAMS.md`, `STATE.md`, `AUTHORITY.md`, `ROUTER.md`, `INTAKE.md`, `RESEARCH.md`, `PLANNING.md`, `REVIEW.md`, `CONTINUATION.md` and `USER_STOP.md` as applicable.

The user authorized the exact repair subject at Intake and the exact exploratory revision for Definition. This P1 authorizes only a bounded #36 strategy after its remaining B/independent Plan Review/C gates. It neither imports program P1 gates nor authorizes #33/#32/#28/#31/#29/#23/#26 repairs, integration, tracker closure or deployment.

## 2. Baseline and defect

Production baseline: default branch `main@d3ab917f02e4de91b7dbb17915c2287c2387333e` with this branch's pre-execution authority commits layered on it. Exact diagnosis and proportional source accounting: `implementation/workstreams/issue-orphan-preexecution-owners/evidence/INTAKE_PRIOR_ART.md`; Intake binds the immutable result for `repair:orphan-preexecution-owner-prerequisites:v1`.

`tools/state_contract.py:validate_workstream` validates locator shape/class, not prerequisites. `tools/router.py` reads Planning only under a valid Definition, and Plan Review only under Planning. Three current-schema disposable commit→fresh-clone cases using production `select_route` confirmed:

1. declared draft Planning/A due, no Definition, active Board → `route/execution`, Planning unread;
2. declared pending Plan Review, no Planning/Definition, active Board → `route/execution`, Plan Review unread;
3. valid GREEN Definition/A satisfied and declared pending Plan Review, no Planning → `route/planning`, Plan Review unread.

Valid active Definition and GREEN Definition/A due still route their accepted owners. The defect is *declared missing owner*, not a generic validator/schema failure. The #33 branch fixes a distinct explicit Brainstorm stop and remains unintegrated with this baseline. No accepted #36 implementation exists.

## 3. Direct production strategy

### 3.1 Selected-state prerequisite guard

In the production `tools/router.py` selected-workstream path, after existing active/return Research, Intake and tracker dispatch and after loading/validating the selected Brainstorm record, but **before** Definition, Planning, premium or Board dispatch:

- if manifest contains `planning` and lacks `definition`, raise the existing `ValidationError` with an explicit missing Definition prerequisite;
- if manifest contains `plan_review` and lacks `planning`, raise the existing `ValidationError` with an explicit missing Planning prerequisite (the transitive Definition edge then follows from the first check).

The existing exception-to-`recovery / recovery_boundary` path owns both. Check locator membership only, not the orphan file bytes; do not read, validate, normalize, delete or claim acceptance of its content. Keep the rest of the selector's progressive local validation unchanged. Prefer the first missing edge in deterministic order for a double orphan; either must fail closed without an unrelated route. Do not add a new state key, owner registry, generic priority engine or eager full-file scan.

This placement preserves currently earlier Research/Intake/tracker ownership. On the #36 isolated baseline, do not claim #33's missing early-stop implementation or duplicate its fix. In future composition, #33's post-Brainstorm-validation explicit stop must remain ahead of this relational guard; test both exact cases on the composed candidate before integration. If composition requires a material strategy change, return to the owning Planning gates rather than importing #33 code into this Card or silently changing its stop precedence.

### 3.2 Canonical route wording

Add one small `workflow/ROUTER.md` implemented-route clarification that manifest-declared Planning and Plan Review lacking their exact upstream locators fail closed before unrelated pre-execution/Board dispatch, without claiming all downstream content is eagerly validated. No new workflow owner module or status is needed; `workflow/WORKSTREAMS.md` already declares the controlling relation.

## 4. Single Card and scope

After Premium C, Execution Prep should materialize one stable `M01-T01` Card: **Reject declared orphan Planning/Plan Review owners**.

Included: two prerequisite edges on production selected route, diagnostic Recovery reason, minimal Router wording and exact stop/valid-route regression tests. Excluded: changing earlier Research/Intake/tracker routes; #33 explicit-stop implementation; all #32/#28/#31/#29/#23/#26 scopes; blanket downstream eager validation, schema or migration, tracker mutation, integration or deployment.

Dependencies: accepted D1 and current production baseline only. #33 is a later *composition compatibility* check, not a hidden DONE prerequisite or source to cherry-pick. No #23 or program Result is consumed. Card acceptance:

1. Planning without Definition, including draft A due plus active Board, fails closed before executing or silently routing Brainstorming;
2. Plan Review without Planning fails closed with/without Definition and with a Board or potential premium return; transitive missing Definition cannot bypass the check;
3. orphan file contents are not accepted or mutated by prerequisite classification; missing-locator and malformed-present-record behavior are distinguished;
4. valid Definition/Planning/Plan Review and Board routes remain lawful, as do earlier independent owners;
5. exact committed implementation passes focused, cumulative and clean detached readback qualification;
6. required independent exact-subject implementation review is GREEN.

Review requirement: **REQUIRED independent**. Technical contract: **none** — current manifest locator, selector and validation contracts express the two edges; a second API/schema artifact would be unjustified. Keep code, docs and discriminating tests in one Card because partial acceptance would leave an orphan path open.

## 5. Qualification matrix and publication

Extend `tests/test_router.py` through real `select_route` (not a test-only selector). Exercise both exact counterexamples against fixture Board `M01-T04`, plus no-Board alternatives if useful, and the GREEN Definition + orphan Review case. Assert `recovery / recovery_boundary`, `workflow/RECOVERY.md` owner, reason identifying the missing edge, no unrelated premium/Execution route, and a read set that includes manifest but not orphan file nor Board when the relation is checked before Board. Hash downstream bytes before/after. Cover a malformed orphan file (missing relation takes precedence without reading it) and malformed present/prerequisite-bound owner (existing selected validation still recovers). Cover lawful active Definition, A due/satisfied and draft Planning, frozen B and pending matched Review, approved C, and active Board controls. Earlier Research and tracker ownership should remain unchanged; Brainstorm stop compatibility requires a real composed #33 candidate, not a claim that this baseline already fixes #33.

Run at least:

- `python3 -m unittest tests.test_router tests.test_state_contract`;
- `python3 -m unittest tests.test_user_stop_contract tests.test_continuation_contract tests.test_m05_trajectory`;
- `python3 -m unittest discover -s tests -v`;
- `git diff --check`.

Commit implementation bytes first. Then import production selector and run focused/full suites from a clean detached worktree at the exact implementation commit; verify changed blob IDs and unchanged excluded surfaces. Record commands/results and immutable subject in the workstream-local semantic Result. No real LLM inference or live external mutation is required for these tests. Do not claim #33 composition or globally stable W1 merely from isolated #36 tests.

## 6. Review and downstream boundary

1. Main validates return and publishes one semantic `results/M01-T01.md` with exact implementation subject, workstream-local evidence and tests/readback; Board is the only mutable Card state.
2. Freeze R01 against the exact immutable Result Git blob and stable Card acceptance; fresh independent reviewer must not have implemented/repaired it.
3. GREEN permits deterministic Card finalization for that same subject. RED preserves failed attempt and routes bounded classification; material plan/authority change renews its gates.
4. Close distinguishes completed branch-local repair from separately authorized final integration/tracker closure. No composed #33/#36 integration is performed by this Card; target movement or differing combined behavior requires later affected compatibility proof and, if material, fresh review.

## 7. Requirement and decision coverage

| Authority | Strategy / evidence |
|---|---|
| R1–R2; D1 | §§2–3, 5: two missing prerequisite edges and transitive chain before unrelated routes |
| R3; D2, D4 | §§3–5: selected locator checks only, no eager content read or generic engine |
| R4; D3, D7 | §§3.1, 5–6: earlier owner/explicit-stop preservation and honest #33 composition boundary |
| R5; D5 | §§4–5: valid Definition/Planning/Review/Board positive controls and malformed-selected behavior |
| R6 | §5: production fixture matrix, cumulative and clean detached readback |
| R7 | §§4–6: exact Result, independent blocking review, GREEN finalization |
| R8–R9; D6 | §§1, 4, 6: subject/gate isolation, explicit exclusions and no hidden constituent transfer |

Every accepted requirement/decision is accounted for. No current scope or strategy change is required to repair the two named missing-locator relations on this baseline.

## 8. Planner challenge audit and freeze

**GREEN for P1** (bounded #36 only).

- Challenged placing the relation check in `validate_workstream`: rejected for this strategy because bootstrap validation could preempt active/return Research and an already-selected explicit stop without reading only the required owner.
- Challenged validating all Planning/Review file content to detect absence: rejected; the missing upstream locator is decidable without a downstream read, and content validation remains the lawful owner's work.
- Challenged checking only after Definition/premium returns: rejected; the GREEN Definition + orphan Review counterexample would still vanish into `planning` or A stop.
- Challenged skipping the Planning edge when no Board exists: rejected; the contradiction is in the selected manifest, not the Board.
- Challenged cherry-picking #33 or adding its early explicit-stop fix: rejected as a distinct subject; composition compatibility is separately tested on actual combined code.
- Challenged splitting tests/docs from the guard: rejected; only the atomic production path with negative/positive tests establishes the invariant.
- Challenged declaring unit success equivalent to program W1 qualification: rejected; separate clean exact-commit verification, independent review and later composed compatibility remain mandatory.

No unresolved product or technical strategy decision blocks this exact P1. Freeze this artifact as an immutable Git blob for Premium B. The planning context must stop and must neither perform nor spawn Stage-6 Plan Review of the plan it authored.
