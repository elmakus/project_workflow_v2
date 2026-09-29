# Completeness assessment — PWV2 stabilization program formalization (DRAFT)

**Status: UNACCEPTED DRAFT for Main reconciliation only — NOT workflow authority,
NOT a GREEN verdict. Only Main's durable Definition record + audit can establish
GREEN. Do not treat this assessment as completeness proof.**

## Subject boundary (what GREEN would — and would not — cover)

- GREEN candidate subject: **bounded program-scope formalization** of exact
  promoted `pwv2-stabilization-program@1` (requirements/decisions needed for
  downstream planning durably identifiable; scope, boundaries, invariants,
  provenance, dependency refinements frozen as accepted formalization inputs).
- GREEN would explicitly NOT: approve #25's (or any issue's) individual repair
  Definition; waive the #25 formal 1+1+8 prerequisite; freeze a Master Plan;
  create Plans/Cards/Task Boards; satisfy premium A (A becomes DUE at GREEN —
  a real stop); authorize implementation, consumer/live mutation, migration,
  merges, issue closure, or deployment.

## Checklist against `workflow/DEFINITION.md` GREEN criteria

| # | Criterion | Candidate status | Evidence |
|---|---|---|---|
| C1 | Exact promoted subject `scope_id@revision` | HELD | BRAINSTORM.toml: promoted, `promotion_subject="pwv2-stabilization-program@1"`, U02 exact authorization; scope blob `b5b96eec...` verified byte-identical at HEAD; INTAKE prior-art binding `...INTAKE_PRIOR_ART.md@82f4e5b...:1bd95e6...` intact. |
| C2 | Requirements/decisions for downstream planning durably identifiable | CANDIDATE HELD (pending Main) | Drafts REQUIREMENTS.md (R1–R11, every SCOPE_REVISION_1 §4 row preserved) + DECISIONS.md (D1–D10) in this directory; recommended canonical locators `requirements/PWV2_STABILIZATION_PROGRAM_FORMALIZATION.md` + `decisions/PWV2_STABILIZATION_PROGRAM_FORMALIZATION.md` (valid future authority paths; evidence paths NOT used as authority). |
| C3 | Challenge audit GREEN | HELD at Brainstorming; Definition audit pending Main | BRAINSTORM `challenge_audit="green"`; SCOPE_REVISION_1 §7 GREEN within bounded exploratory obligation; executable router + state-envelope suites pass (43 + 28 tests). Main must render the Definition-side audit. |
| C4 | No unresolved user/product choice inside accepted scope | HELD | Single pending gate (exact promotion + #14-membership verdict) resolved by U02 with #14 proposed inclusion retained. #25 gate is an explicitly carried out-of-scope prerequisite (R9/D7), not a hidden choice. W0 detail + runtime matrix are deferred owning-gate outputs, explicitly registered. |
| C5 | #23/#20 boundaries intact | HELD | R2/R3 pinned to `b076e08` (R1–R13/D1–D7, plan order, non-GREEN M01-T01) and `c5e9ba1` (caller-scoped readiness only); heads verified unchanged 2026-09-29. |
| C6 | Every distinct invariant/acceptance preserved; both provenance chains | HELD | R4 table (all rows: #23/#25–#40/#18/#14/#20); R5 (distinct #27–#33 vs #34–#40 sets; anti-absorption; (a)/(b)/(c) discipline). 15 scope-state copies byte-verified (`preserved-scope-verification.json`); readback comparison `material_changes: []`. |
| C7 | #14 inclusion without lifting deferral | HELD with explicit consequence | R8/D6: proposed inclusion retained; consumer PWv2.2.0 deferral untouched; exclusion defined as scope change with stated gap. |
| C8 | #25 gate carried unresolved; no repair approval | HELD by construction | R9/D7: 1+1+8 shape, owner chain (#25 items 7–8 → Intake return + Brainstorming alternatives), W5 no-postponement rule; formalization-vs-repair distinction durable in all three drafts. |
| C9 | W0–W7 validated; scope/wave changes surfaced | HELD — none required | R7/D8: hard vs non-hard classification validated; refinements carried; **no necessary scope/wave boundary change found**; surfacing rule recorded for future discovery. No Master Plan frozen, no Cards fabricated. |
| C10 | Premium A due at GREEN (real stop) | CONDITIONAL on Main's GREEN | No A/B/C inferred from U01/U02/tracker/preparation (per U02 limits + DEFINITION_PREPARATION.md). On GREEN, Main records premium A due + renders USER_STOP handoff. |

## Agent-findable facts — none blocking THIS Definition

All facts needed for this bounded formalization were recovered from durable
evidence and independently verified where executable:

- Default `main@d3ab917` and the three preserved source heads verified
  unchanged via live `git ls-remote origin` (2026-09-29): no drift, so
  brainstorm-draft RQ-B1 resolves to NO-ACTION.
- Fresh issue-readback comparison `material_changes: []`: no tracker drift at
  its epoch (RQ-B2); live re-check is Main's reconcile-time duty, not a
  Definition content gap.
- #25 lane-existence in `elmakus/project-research` (RQ-B3) is future-owner
  business for the LATER #25 repair gate, not this formalization: no Research
  question blocks the current Definition. **No exact Research question/owner is
  returned for this bounded Definition** — there is no genuine unresolved
  factual gap inside its scope. The carried #25 prerequisite's future owner
  will be selected by that later scope's canonical router (per #25 items 7–8:
  integrated evidence returns to PWv2 Intake + Brainstorming alternatives
  before #25 Definition/implementation authorization); it is recorded here as a
  prerequisite, not posed as a current question.

## Genuine choices / scope changes surfaced

- **None silently accepted.** The one genuine scope choice pending at challenge
  time (#14 membership verdict) was resolved explicitly by U02 (inclusion
  retained as proposed). No additional product/scope choice was discovered
  during formalization. No scope/wave boundary change proved necessary (C9).
- Standing surfacing rule (not a current change): if Definition/Planning
  discovers required wave reordering or repair-boundary change, it must be
  surfaced explicitly via owning gates; substantive scope change increments the
  exploratory revision and stales prior promotion.

## Residual duties for Main (why GREEN is NOT claimed here)

1. Independently re-recover canonical state at reconcile time (router, PROJECT,
   manifest, pointed INTAKE/RESEARCH/TRACKER/BRAINSTORM records, U01/U02,
   SCOPE_REVISION_1, DEFINITION_PREPARATION, INTAKE_PRIOR_ART) and confirm U02's
   promotion binding (authorized at published `5d160c6`; reconciled at
   `7134ff4`) still exact.
2. Reconcile or reject these drafts; author the canonical requirements/decision
   files at the recommended authority paths.
3. Materialize `DEFINITION.toml` (no such record exists yet — expected pre-
   Definition state), render the Definition completeness audit, and decide
   GREEN/RED. Suggested fields below.
4. On GREEN: record premium stop A DUE (real human-facing stop with
   best-available-planning-context recommendation + locator-only handoff per
   `workflow/USER_STOP.md`); continue deterministic routing thereafter.

## Recommended DEFINITION record shape (for Main; DO NOT create here)

Minimal VALID shape per production `tools/state_contract.py`
`validate_definition` (independently read) and `templates/DEFINITION.toml`:
required keys are `workstream_id`, string `source_scope_subject`, string
`revision`, `state` (`active`|`green`), `completeness_audit`
(`pending`|`green`), `premium_a` (`not_due`|`due`|`satisfied`), `requirements`
as a `class="authority"/path` table, and `decisions` as an array of
`class="authority"/path` tables. State rules: `active` requires
`premium_a="not_due"`; `green` requires audit `green`, non-empty decisions,
and premium A `due`/`satisfied`. No `subject`/`definition_revision`
integer/`completeness` aliases, no bare string locator arrays, and no `/tmp`
pointer in canonical state (drafts live outside the repo; only the
recommended authority paths below enter canonical records). U02 authorization
and the exact scope blob remain durably recorded in BRAINSTORM.toml +
evidence files; they are not DEFINITION keys.

Initial materialization (Main's audit still pending):

```toml
workstream_id = "issue-pwv2-stabilization-program"
source_scope_subject = "pwv2-stabilization-program@1"
revision = "R1"
state = "active"
completeness_audit = "pending"
premium_a = "not_due"

[requirements]
class = "authority"
path = "requirements/PWV2_STABILIZATION_PROGRAM_FORMALIZATION.md"

[[decisions]]
class = "authority"
path = "decisions/PWV2_STABILIZATION_PROGRAM_FORMALIZATION.md"
```

GREEN transition (ONLY if Main's audit holds C1–C10): same file with
`state = "green"`, `completeness_audit = "green"`, `premium_a = "due"`
(real stop; never inferred satisfied). Later Strategic Planning additionally
requires that premium A be durably satisfied under DEFINITION.md before
Planning owns continuation; later issue-specific repair approval needs its own
lawful scope/gates.

Validator result (temporary diagnostic inputs under /tmp/pwv2-def-validation/,
no repo writes; production `read_toml` + `validate_definition` at input commit
`7134ff4`):

- `CANDIDATE_DEFINITION.toml` (active/pending/not_due shape above) -> VALID
- `CANDIDATE_DEFINITION_GREEN.toml` (green/green/due shape) -> VALID
- Prior draft's recommended example (subject/definition_revision/completeness
  aliases, bare string locators) -> INVALID as expected
  (`definition: missing source_scope_subject`)

## Correction summary (rev 2 vs rev 1 of these drafts)

1. **Schema repair:** replaced the incompatible recommended DEFINITION example
   with the minimal VALID shape above (source_scope_subject, string revision,
   state, completeness_audit, premium_a, authority-table requirements, array
   of authority-table decisions); removed non-canonical aliases, bare string
   arrays, and the /tmp pointer from canonical state. Validated both the
   initial and GREEN-transition shapes against the production validator.
2. **Boundary clarification (R6 + R1 exclusion line + DECISIONS.md boundary
   note):** exclusions now read explicitly as the CURRENT U01/U02
authorization boundary. Future Strategic Planning requires separate explicit
   premium-A authorization (not a permanent ban contradicting the owning
   phase); future issue-specific repair approval/implementation still needs
   its own lawful scope/gates; no approvals transfer.
3. No scope, wave, invariant, or #25-prerequisite change: all distinct
   invariants (R4), both provenance chains (R5), #14 inclusion terms (R8),
   and the unresolved #25 gate with formalization-vs-repair distinction (R9)
   are preserved verbatim from rev 1. No product-code fix, no canonical
   writes.

**Assessment summary (candidate, not verdict):** C1–C9 candidate-HELD on
durable evidence with executable validation; C10 conditional on Main's GREEN +
A-due recording. No blocking Research question; no hidden choice; no required
scope/wave change. Main reconciles and decides.
