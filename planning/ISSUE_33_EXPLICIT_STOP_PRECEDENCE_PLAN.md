# Issue #33 — Explicit stop precedence implementation plan P1

## 1. Exact subject and authority

Workstream: `issue-explicit-stop-precedence`  
Planning cycle: `1`  
Entry subject: Definition `D1`  
Plan revision: `P1`

Accepted authority:

- `requirements/ISSUE_33_EXPLICIT_STOP_PRECEDENCE.md` — I33-R1–R9;
- `decisions/ISSUE_33_EXPLICIT_STOP_PRECEDENCE.md` — I33-D1–D7;
- canonical `workflow/ROUTER.md`, `workflow/BRAINSTORMING.md`,
  `workflow/STATE.md`, `workflow/AUTHORITY.md`, `workflow/USER_STOP.md`,
  `workflow/PLANNING.md`, `workflow/REVIEW.md` and
  `workflow/CONTINUATION.md`.

Premium A is satisfied for D1. This plan authorizes only the bounded #33 repair
after its remaining B/independent Plan Review/C gates. It does not authorize
#36 orphan-owner closure, #31 Stage-6 history, #29 Close reconstruction, #28
Research-return precedence, #23/#26 reconciliation, migration, tracker closure,
integration or deployment.

## 2. Baseline and prior art

The production implementation baseline is current default branch
`d3ab917f02e4de91b7dbb17915c2287c2387333e`, with workstream-only authority
commits through D1/Premium A layered on
`work/issue-33-explicit-stop-precedence`.

The accepted diagnosis is preserved in
`implementation/workstreams/issue-explicit-stop-precedence/evidence/INTAKE_PRIOR_ART.md`:

- `tools/router.py` reads and locally validates the selected Brainstorm record,
  but delays its `explicit_user_stop` check until after Definition, Planning,
  Plan Review and part of implementation dispatch;
- valid active Definition therefore returns `route / definition`, and valid
  GREEN Definition can proceed to a premium or Planning route despite the
  durable stop;
- without later Definition, the existing production path already returns the
  correct `stop / explicit_user_stop` identity and USER_STOP delivery;
- clearing the flag already permits the expected promoted-scope routes;
- no accepted implementation result exists for this exact repair subject.

Implementation must repair the current production selector directly. Broad
policy-kernel history is neither an accepted dependency nor a cherry-pick
source.

## 3. Implementation strategy

### 3.1 Early Brainstorm-owned stop dispatch

In `tools/router.py`, retain the current selected-state order through Intake,
Research and tracker handling. Once the exact Brainstorm record has been read
and `validate_brainstorm` has succeeded:

1. derive the existing exact `scope_id@revision` subject;
2. when `explicit_user_stop` is true, immediately return the existing
   `stop / explicit_user_stop` result;
3. preserve owner `workflow/BRAINSTORMING.md`, canonical reason
   `Brainstorming carries an explicit user stop`, and the common `result(...)`
   path that loads `workflow/USER_STOP.md`;
4. only when the flag is false may the selector read or validate Definition and
   any later Planning, Plan Review, Execution Prep or Task Board state.

Remove the now-unreachable late duplicate stop branch rather than retaining a
second precedence path. Keep the existing active/ready/promoted Brainstorm
routing after downstream prerequisite handling for stop-cleared records. No
state is mutated, normalized, deleted or accepted by this dispatch.

This is a direct ordering correction, not a new validator, priority registry,
stop type, handoff contract or durable state key.

### 3.2 Canonical route wording

Update `workflow/ROUTER.md` with one explicit implemented-route statement that
a locally valid selected Brainstorm explicit stop is returned before Definition
and later pre-execution reads/dispatch. Preserve the existing Brainstorm owner
and USER_STOP composition. `workflow/BRAINSTORMING.md` and
`workflow/USER_STOP.md` already define the controlling semantics and require no
new policy.

## 4. One-Card execution boundary

Execution Prep should materialize one stable Card, `M01-T01`, after Premium C.

### M01-T01 — Enforce explicit Brainstorm stop precedence

**Included:**

- early production-selector dispatch after local Brainstorm validation;
- removal of the late duplicate check;
- exact stop identity, owner, reason and USER_STOP read-set preservation;
- progressive deferral of Definition and later pre-execution reads while
  stopped;
- lawful resume and malformed-state controls;
- focused, cumulative and clean-consumer qualification;
- the minimal canonical Router wording needed to reflect production order.

**Excluded:**

- changing Intake/Research/tracker precedence before the selected Brainstorm
  record;
- clearing the stop, rewriting later records or migrating historical state;
- #36/#31/#29/#28/#23/#26 behavior;
- a generic priority/policy engine or schema change;
- Task Board, Review, Close, handoff-schema or runtime orchestration changes;
- tracker mutation, issue closure, PR integration or deployment.

**Dependencies:** none beyond accepted D1 and the current production baseline.
The repair consumes no #28, #32 or stabilization-program implementation Result.

**Authority:** I33-R1–R9 and I33-D1–D7.

**Acceptance:**

1. every locally valid selected Brainstorm record with
   `explicit_user_stop = true` returns the exact Brainstorm-owned stop before
   Definition or later pre-execution state is read;
2. active Definition and GREEN Definition with A due or satisfied cannot bypass
   the stop;
3. proportional Planning/Plan Review/Board fixtures are deferred and absent
   from the stop-time read set;
4. the stop subject is exact `scope_id@revision`, the reason and owner remain
   canonical, and `workflow/USER_STOP.md` is loaded;
5. malformed Brainstorm state still recovers before the stop can be selected;
6. clearing the flag restores existing active Definition, premium A and
   Planning behavior, including Recovery for malformed downstream state;
7. no downstream file or state is mutated by selection;
8. the exact committed implementation passes focused, cumulative and clean
   detached readback tests;
9. an independent exact-subject implementation review is GREEN.

**Review requirement:** REQUIRED independent review.

**Technical contract:** none. Existing selector, state and stop contracts fully
express the bounded behavior; adding a new API or schema artifact would be
unjustified.

One Card is preferable to splitting code, docs and tests: they describe one
atomic ordering invariant at one selector boundary, and partial completion
would either leave the bypass open or leave production behavior unqualified.

## 5. Test and evidence strategy

### 5.1 Focused production-selector matrix

Extend `tests/test_router.py` using the real `select_route` path. Cover:

- explicit stop with matching active Definition;
- explicit stop with GREEN Definition for both Premium A due and satisfied;
- explicit stop with valid later Planning/Plan Review or Task Board locators
  where useful to prove the complete pre-execution deferral boundary;
- exact disposition, obligation, `scope_id@revision`, owner, canonical reason,
  `handoff_policy = none`, and USER_STOP read-set entry;
- absence of Definition, Planning, Plan Review and Board paths from the
  stop-time read set;
- stop-only, active Brainstorm and ready-for-Definition controls;
- stop-cleared active Definition, A-due and A-satisfied/Planning controls;
- malformed Brainstorm Recovery before dispatch;
- malformed downstream state deferred while stopped and recovered after lawful
  clearing.

Use shared fixture helpers only when they reduce duplication without hiding the
specific precedence/read-set assertions. Tests must not call a test-only
selection helper in place of production `select_route`.

### 5.2 Cumulative qualification

Run at minimum:

- `python3 -m unittest tests.test_router tests.test_state_contract`;
- `python3 -m unittest tests.test_user_stop_contract tests.test_continuation_contract tests.test_m05_trajectory`;
- full `python3 -m unittest discover -s tests -v`;
- `git diff --check`.

After implementation publication, verify from a clean detached worktree at the
exact commit that production imports, the focused stop/resume matrix and the
full cumulative suite pass. Record exact commands/results and immutable subject
identity in the Card Result. This repair requires no real-LLM inference or live
external mutation.

## 6. Review, correction and completion

1. Publish implementation bytes and a normalized Result without self-reference.
2. Freeze a REQUIRED implementation review attempt against the exact immutable
   implementation subject and the exact `M01-T01` acceptance surface.
3. A context that implemented or repaired that subject cannot verdict it.
4. RED evidence remains durable; bounded correction creates a new exact subject
   and fresh independent attempt.
5. GREEN permits deterministic Card finalization only for the still-current
   exact subject.
6. Close and later integration remain separately owned; this Card does not
   close issue #33 or merge to main.

## 7. Requirements and decisions coverage

| Authority | Plan coverage |
|---|---|
| I33-R1–R3; D1–D3 | §§3.1, 5.1 early post-validation dispatch before Definition/later state |
| I33-R2; D4 | §§3.1, 4–5 exact subject, owner, reason and USER_STOP delivery |
| I33-R4; D3 | §§3.1, 4 no downstream read-time mutation, normalization or acceptance |
| I33-R5; D7 | §§4–5 stop-cleared lawful routes and resumed malformed-state Recovery |
| I33-R6; D5 | §§1, 3.1, 4 preserved earlier Research ownership and explicit exclusions |
| I33-R7; D2, D6 | §§3–4 direct production-selector placement, no generic policy engine |
| I33-R8; D7 | §§4–6 discriminating matrix, cumulative/readback evidence and independent review |
| I33-R9 | §§1, 4 scope isolation and explicit exclusions |

Every accepted requirement and decision is mapped. No accepted behavior depends
on a later unrelated workstream Result.

## 8. Planner challenge audit

**GREEN for P1.**

- Challenged moving the stop ahead of local Brainstorm validation: rejected;
  malformed selected owner state must still fail closed.
- Challenged moving the stop ahead of Intake/Research/tracker handling: rejected
  as #28 scope expansion; D5 preserves current earlier precedence.
- Challenged validating Definition before stopping: rejected because downstream
  validity cannot control or bypass the earlier Brainstorm-owned human boundary.
- Challenged classifying promoted-plus-stop as Recovery: rejected because the
  accepted Definition makes the boolean an orthogonal valid real stop.
- Challenged preserving the late check as defense in depth: rejected because it
  creates duplicate precedence logic and can mask future ordering drift.
- Challenged a generic priority registry: rejected under D6/YAGNI; one direct
  selector guard closes the demonstrated defect.
- Challenged updating multiple workflow modules: rejected; Router wording is
  sufficient because Brainstorming and USER_STOP already own the semantics.
- Challenged splitting production and qualification Cards: rejected because the
  invariant is not accepted until the same exact subject proves stop and resume.
- Challenged unit success as final acceptance: rejected; exact commit,
  clean-consumer readback and independent implementation review remain required.

No unresolved scope, strategy, dependency or acceptance choice remains. Freeze
this exact plan subject for Premium B and independent Stage-6 Plan Review. The
planning context must not review or repair its own frozen P1.
