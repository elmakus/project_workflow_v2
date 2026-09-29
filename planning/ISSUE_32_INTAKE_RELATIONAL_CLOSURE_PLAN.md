# Issue #32 — Intake relational closure implementation plan P1

## 1. Exact subject and authority

Workstream: `issue-intake-relational-closure`
Planning cycle: `1`
Entry subject: Definition `D1`
Plan revision: `P1`

Accepted authority:

- `requirements/ISSUE_32_INTAKE_RELATIONAL_CLOSURE.md` — I32-R1–R10;
- `decisions/ISSUE_32_INTAKE_RELATIONAL_CLOSURE.md` — I32-D1–D8;
- canonical `workflow/INTAKE.md`, `workflow/WORKSTREAMS.md`,
  `workflow/STATE.md`, `workflow/AUTHORITY.md`, `workflow/PLANNING.md`,
  `workflow/EXECUTION_PREP.md`, `workflow/REVIEW.md` and
  `workflow/CONTINUATION.md`.

Premium A is satisfied for D1. This plan authorizes only the bounded #32 repair
after its remaining B/independent Plan Review/C gates. It does not authorize
#23, #33, #36, migration, tracker closure, integration or deployment.

## 2. Baseline and prior art

Implementation baseline is current default branch
`d3ab917f02e4de91b7dbb17915c2287c2387333e`, with workstream-only authority
commits layered on `work/issue-32-intake-relational-closure`.

Current production behavior and accepted evidence are recorded in
`implementation/workstreams/issue-intake-relational-closure/evidence/INTAKE_PRIOR_ART.md`:

- empty issue `repair_subject` reaches `stop / issue_alignment / subject=''`;
- contradictory manifest `change` and Intake `issue` reaches issue alignment
  instead of Recovery;
- current 71-test state/router baseline passes without covering either defect;
- historical `c94a348...` contains only an unaccepted partial empty-subject
  guard on a broad divergent branch.

Implementation must reproduce against the exact launch baseline and reimplement
the accepted behavior directly; no broad cherry-pick is planned.

## 3. Implementation strategy

### 3.1 Composite selected-state relation

Add one small production relation validator in `tools/state_contract.py` (exact
name implementation-owned) that receives an already shape-validated selected
workstream and Intake record and requires exact `kind` equality. It performs no
write, migration, coercion or fallback selection.

In `tools/router.py`, when the manifest declares an Intake locator:

1. read and shape-validate that exact Intake record immediately after validating
   the selected manifest;
2. apply the composite kind relation before returning active/completed Research
   or any later obligation for that selected state;
3. retain the validated Intake object for the existing later Intake routing so
   there is no duplicate semantic read or second authority path.

A mismatch raises the existing validation failure consumed as Recovery. It is
not a user stop. Once the relation is valid, current Research precedence and
return semantics remain unchanged.

### 3.2 Concrete issue subject guard

Before active issue alignment-response dispatch, treat
`not repair_subject.strip()` as incomplete diagnosis and return:

- disposition `route`;
- obligation `intake`;
- subject `issue`;
- owner `workflow/INTAKE.md`;
- a reason stating that no concrete repair subject exists and prior-art Research
  must follow only after one is proposed.

The guard applies for every allowed response class. It does not erase response
data, synthesize authorization, start Research with an empty origin subject or
change valid concrete-subject prior-art handling.

### 3.3 Canonical wording

Update `workflow/INTAKE.md` only if needed to state explicitly that empty or
whitespace-only subjects remain diagnosis and selected manifest/Intake kind
contradiction fails closed. No other workflow module, state key or schema
version is planned.

## 4. One-Card execution boundary

Execution Prep should materialize one stable Card, `M01-T01`, after C.

### M01-T01 — Enforce Intake relational closure

**Included:**

- composite manifest/Intake kind validation on the production selected-state
  path;
- early exact Intake read needed for the relation while preserving Research
  semantics after validation;
- blank-subject diagnosis guard;
- focused production tests and necessary Intake wording;
- cumulative tests and clean-consumer evidence.

**Excluded:**

- #23/#33/#36 behavior, migrations and historical normalization;
- Task Board/Review/Close/runtime changes;
- broad policy-kernel branch adoption;
- tracker mutation, issue closure, PR integration or deployment.

**Dependencies:** none. Program P1 selected #32 for independent early admission;
no #23 constituent or later wave Result is consumed.

**Authority:** I32-R1–R10 and I32-D1–D8.

**Acceptance:**

1. blank issue subjects cannot stop/continue alignment for any response class;
2. all unequal issue/feature/change kind pairings recover before contradictory
   Research/Intake/downstream dispatch;
3. all same-kind controls preserve lawful routes;
4. concrete issue prior-art/alignment and active/completed Research controls
   remain correct;
5. no durable schema/runtime identity or migration side effect is introduced;
6. exact committed implementation passes cumulative and clean-consumer tests;
7. independent exact-subject implementation review is GREEN.

**Review requirement:** REQUIRED independent review.

**Technical contract:** none. Existing state/router contracts fully express the
bounded behavior; a new API/schema artifact would be unjustified.

One Card is preferable to splitting the guard and relation: both alter the same
selected-state read/routing boundary, share the positive-control matrix and
must be accepted together to close #32. Runtime workers may internally divide
code/test inspection without creating multiple Cards or shared-state writers.

## 5. Test and evidence strategy

### 5.1 State-contract tests

Add direct production-helper coverage for:

- same-kind issue/feature/change pairs accepted;
- every unequal ordered pairing rejected with a stable relational validation
  reason;
- no mutation/coercion of either record.

Standalone `validate_workstream` and `validate_intake` shape behavior remains
covered separately.

### 5.2 Router negative matrix

Using production `select_route`:

- empty and whitespace-only active issue subject;
- response classes `none`, `question`, `concern`, `alternative`,
  `authorization` with schema-valid observed flags;
- each case routes to Intake diagnosis, never stop/Brainstorming/authorization;
- each unequal manifest/Intake kind pairing selects Recovery;
- at least one mismatch fixture with active Research proves contradiction wins
  before Research dispatch.

### 5.3 Positive and precedence controls

- same-kind issue with concrete exact prior-art binding and no response retains
  exact alignment stop;
- same-kind feature/change discovery retains current routes;
- consistent active Research and completed return-owner cases retain existing
  precedence and once-only behavior;
- existing progressive read-set assertions are updated only for the exact early
  Intake read now required by I32-D4;
- stale prior-art and malformed records still fail closed.

### 5.4 Cumulative qualification

Run at minimum:

- `python3 -m unittest tests.test_state_contract tests.test_router`;
- execution, recovery and continuation contract suites affected by read/routing
  precedence;
- full repository unittest discovery if it remains bounded;
- `git diff --check`.

After implementation publication, verify from a clean detached worktree/clone
at the exact commit that production imports, the focused reproductions and the
cumulative suite pass. Preserve exact command/result evidence in the Card
Result; do not claim connected runtime or real-LLM qualification because this
repair requires neither.

## 6. Review, correction and completion

1. Publish implementation bytes and normalized Result without self-reference.
2. Freeze a REQUIRED implementation review attempt against the exact immutable
   implementation subject and the exact `M01-T01` acceptance surface.
3. A context that implemented or repaired that subject cannot verdict it.
4. RED evidence remains append-only; bounded correction produces a new subject
   and fresh independent attempt.
5. GREEN permits deterministic Card finalization only for the still-current
   exact subject.
6. Close and any later integration remain separately owned; this Card does not
   close issue #32 or merge to main.

## 7. Requirements and decisions coverage

| Authority | Plan coverage |
|---|---|
| I32-R1–R2; D1, D5 | §3.2 and §5.2 blank/response matrix; no rewrite or manufactured authorization |
| I32-R3; D1, D4 | §§3.2, 5.3 preserve concrete-subject prior art and Research semantics |
| I32-R4–R5; D2–D3 | §3.1 composite equality, Recovery, no silent winner/duplicate authority |
| I32-R6–R7; D4, D7 | §§3.1, 5.2–5.3 precedence and lawful positive controls |
| I32-R8; D3 | §§3.1–3.2 production helper/router enforcement |
| I32-R9; D7 | §§4–6 exact matrix, cumulative/clean evidence and independent review |
| I32-R10; D6, D8 | §§1–4 exclusions, direct current-baseline implementation, minimal artifacts |

Every accepted requirement and decision is mapped. No accepted behavior depends
on a later program wave or unavailable Result.

## 8. Planner challenge audit

**GREEN for P1.**

- Challenged splitting into two Cards: rejected because partial completion leaves
  the same Intake boundary inconsistent and duplicates the acceptance matrix.
- Challenged a router-only ad hoc kind check: a small composite state relation is
  clearer and directly testable; exact helper naming remains implementation
  detail.
- Challenged moving manifest kind into `validate_intake`: rejected because it
  breaks record-local shape validation and couples unrelated callers.
- Challenged preserving Research-before-Intake reads: rejected for contradictory
  selected identity; accepted D4 requires proving the exact declared relation
  first, while preserving Research dispatch after proof.
- Challenged rejecting or migrating every premature-response record: rejected;
  bounded diagnosis routing is sufficient and safer.
- Challenged cherry-picking `c94a348...`: rejected as broad, divergent and
  incomplete.
- Challenged a technical-contract artifact or schema revision: rejected under
  D8/YAGNI because current interfaces and discriminating tests are sufficient.
- Challenged unit success as final acceptance: rejected; exact commit,
  clean-consumer readback and independent implementation review remain required.

No unresolved scope, strategy, dependency or acceptance choice remains. Freeze
this exact plan subject for premium B and independent Stage-6 Plan Review. The
planning context must not review or repair its own frozen P1.
