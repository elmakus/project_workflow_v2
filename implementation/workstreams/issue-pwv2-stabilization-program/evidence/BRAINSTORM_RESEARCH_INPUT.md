# DRAFT — Brainstorming scope challenge + Definition-preparation inputs
# pwv2-stabilization-program@1 (PWV2-STAB-P1 formalization)

**Status: CANDIDATE DRAFT FOR MAIN RECONCILIATION ONLY — NOT WORKFLOW AUTHORITY.**

- This file is a worker draft for the current Brainstorming/scope-challenge and
  Definition-preparation obligation. It does not create, modify, promote, or
  satisfy durable workflow authority, premium gates, alignment, promotion, Plans,
  Cards, or implementation permission.
- Main is the sole canonical writer. Main must independently reread canonical
  Git/Project Workflow state, reconcile or reject this draft, and perform any
  durable transition under `workflow/ROUTER.md`, `workflow/BRAINSTORMING.md`,
  and `workflow/DEFINITION.md`.
- No implementation, consumer/live-workstream mutation, code/policy edit,
  commits/pushes, issue mutation, merge/deploy, Plan/Card creation, premium
  satisfaction, or canonical-state writes were performed or are authorized by
  this draft.
- No Paseo/session/chat state is workflow authority. No second Task Board,
  queue, approval record, review verdict store, or workflow state was created.

## 0. Exact obligation binding (committed input, read-only)

- Repository: `elmakus/project_workflow_v2`
- Worktree: `/worktrees/1n4cii8x/roasted-squid`
- Branch: `work/pwv2-stabilization-program`
- Committed input HEAD: `7ff3d2a9334b67c264789bc59405a9058de23ee8`
  (`tracker: verify separate formalization bookkeeping and continue exploration`)
- Canonical base: `origin/main` = `main@d3ab917f02e4de91b7dbb17915c2287c2387333e`
- Manifests at HEAD (read-only, NOT modified):
  - `WORKSTREAM.toml` — workstream `issue-pwv2-stabilization-program`
  - `INTAKE.toml` — kind `issue`, state `complete`, diagnosis_revision 1,
    `repair_subject="PWV2-STAB-P1"`,
    `diagnosis_prior_art_subject="PWV2-STAB-P1"`,
    `diagnosis_prior_art_result=".../evidence/INTAKE_PRIOR_ART.md@82f4e5b...:1bd95e6..."`,
    `alignment_state="authorized"`, `alignment_subject="PWV2-STAB-P1"`
  - `RESEARCH.toml` — state `consumed`, `origin_role="intake"`,
    `origin_subject="PWV2-STAB-P1"`, `return_target="intake"`,
    `return_reconciliation="applied"`; four source classes accounted
    (official_upstream / project_runtime / tracker_discussion = checked,
    practitioner_community = not_relevant)
  - `BRAINSTORM.toml` — `scope_id="pwv2-stabilization-program"`, revision 1,
    state `active`, `challenge_audit="pending"`, `explicit_user_stop=false`,
    `promotion_state="pending"`, `promotion_subject=""`
  - `TRACKER.toml` — provider github, `state="linked"`, issue #41,
    `readback_state="verified"`, `final_pr=0`
- Exact input evidence (all read, none modified):
  - `evidence/USER_AUTHORIZATION.md` (U01 verbatim authorization + limits)
  - `evidence/INTAKE_PRIOR_ART.md` (applied/consumed Intake prior-art return)
  - `evidence/PROPOSED_PROGRAM_P1.md` (program diagnosis/planning proposal, §1–§8)
  - `evidence/PROVENANCE_INDEX.md` (preserved-input index + SHA256 anchors)
- Owner material read for this obligation (default branch `origin/main@d3ab917`):
  `workflow/ROUTER.md`, `workflow/BRAINSTORMING.md`, `workflow/DEFINITION.md`,
  plus `workflow/RESEARCH.md`, `workflow/INTAKE.md`, `workflow/STATE.md`,
  `workflow/AUTHORITY.md`, `workflow/CONTINUATION.md`, `workflow/USER_STOP.md`,
  `PROJECT.md`, and the pointed current records above.
- Formalization subject (bounded): `PWV2-STAB-P1` as **pre-execution scope
  formalization only** — canonical Intake/prior-art reconciliation (done),
  Brainstorming (this obligation), and Definition preparation (draft inputs
  only). NOT implementation of any defect, NOT Card creation, NOT premium
  satisfaction, NOT authorization inherited by separately tracked repair subjects.

## 1. Reconciled bounded exploratory scope (candidate)

### 1.1 Scope statement

Formalize a dependency-aware stabilization scope for trustworthy durable-state
production/consumption, immutable proof/history, deterministic authorized
routing/restart, and reconstructible Close — as an exploratory revision
`pwv2-stabilization-program@1`, preserving every independently demonstrated
invariant and acceptance requirement below, with W0–W7 retained as provisional
capability/qualification checkpoints (§5), and with the #25 formal-Research
prerequisite correctly placed as a blocking gate before #25 Definition/repair
(§6), not as a precondition of this challenge. The single concrete candidate
membership is §1.4: the P1 core set INCLUDING #14 as proposed inclusion, with
#20 as narrow side track. No alternative membership is offered; any change to
it is a substantive scope change (revision increment + explicit qualification
consequence, §1.4).

### 1.2 In-scope (exploration + Definition preparation only)

- Challenge the P1 candidate: scope/boundaries, eight repair families, wave
  order, subsumption distinctions, and qualification discipline.
- Preserve audit provenance chains and all issue-specific invariants (§2).
- Produce Definition-ready inputs (§9): requirements/decision locators,
  completeness checklist, open-decision register — WITHOUT creating or
  promoting Definition.
- Surface ordering/boundary refinements W0–W7 need (§5).

### 1.3 Out-of-scope / explicitly excluded (U01 + P1 §2/§8)

- No repair implementation; no consumer-repository modification; no live
  workstream migration; no issue closure/merge/reopen/relabel; no merge/deploy.
- No adoption, merge, or semantic import of PR #9 (separate PWv2.1
  policy-kernel candidate; its body forbids merge before its own gates).
- No PWv2.1/PWv2.2 feature expansion; no approved consumer scope change.
- No alternate child spawner, daemon/shell bypass, fallback delegation, or
  final PWv2.2 helper (hard #20 boundary).
- No rewriting of historical Results/Reviews/approvals; no provenance deletion;
  no fabricated GREEN; no similarity-based closure.
- No premium A/B/C satisfaction; no Plan; no Cards; no Task Board.
- No transfer of any existing A/B/C satisfaction or approval to a larger scope.
- Inclusion of deferred #14 in a new stabilization scope additionally requires
  explicit approval and does NOT lift the deferral inside PWv2.2.0. The candidate
  scope (§1.4) retains P1's PROPOSED inclusion of #14 for that explicit
  promotion consideration; it is not pre-excluded or pre-deferred here.

### 1.4 Concrete exact proposed scope (single candidate, promotion pending)

Offered as the ONE candidate subject for `pwv2-stabilization-program@1`
promotion. This resolves the prior draft's contradiction (candidate GREEN with
unspecified membership): the revision is GREEN-challengeable exactly because
its membership is fully specified here; the only outstanding act is the user's
exact promotion authorization, which IS the legal stop carrying the membership
verdict.

- **Core repair set (proposed):** #23, #25–#40, #18, **#14 (proposed inclusion)**.
- **Narrow side track:** #20 — official caller-scoped readiness/configuration
  only (§2.2); never a semantic-layer subject.
- **Regression baselines (not reopened):** closed #11/#16/#17/#22 (+ merged
  PR #24); prior merged PRs #12/#19/#21; PR #10 co-bound Board precedence.
- **History only:** #13 (superseded), #15 (withdrawn — never regression evidence).
- **Excluded:** PR #9 adoption; PWv2.1/PWv2.2 feature expansion; consumer scope
  change; mass migration; live deployment; spawner/helper; history rewriting;
  similarity closure (§1.3).
- **#14 status:** P1 proposes INCLUSION (cross-gate cycle legality analyzed at
  W0, positive-path integration after immutable acceptance/history settle).
  This draft RECOMMENDS retaining that proposed inclusion for the promotion
  decision — i.e., the user is asked to authorize a scope that contains #14.
  No exclusion is smuggled in: there is no "default deferred" fallback.
  IF the user instead excludes #14 at promotion, that is a substantive scope
  change with explicit consequence: revision increments (prior authorization,
  if any, goes stale); W4 loses the combined execution/acceptance DAG-check
  acceptance; program qualification no longer covers the S07/R03-class cycle
  and must state that gap; the PWv2.2.1 deferral remains the sole owner of the
  strategic-gate defect. The consequence must be recorded, not described as
  "no scope change."
- **Ownership:** dedicated new stabilization scope — already AUTHORIZED by U01
  and MATERIALIZED as this branch/workstream. Not a question (§3 A1).

## 2. Preserved invariants and acceptance needs (must survive verbatim into Definition)

### 2.1 #23 boundary (controls; evidence excerpts at `b076e08…`)

Requirements R1–R13 remain intact: one machine-enforced executable schema
authority; validate-before-successful-persistence; fresh-producer → fresh-router
resume without drift-Recovery; no parallel per-stage schemas; deterministic
fail-closed bounded intra-V2 reconciliation (supported-known-shapes only;
ambiguous/corrupt stays Recovery); authority/subject-identity preservation
rules (D4/D5: retain subject-bound gates ONLY on proven identical immutable
subject; otherwise the gate becomes due again); deterministic idempotent
restart-safe reconciliation; regression fixtures (fresh materialization, #22
malformed shape, #20 legacy shape, older-V2 premium/review-boundary resume,
subject-preserved vs subject-changed reset, ambiguous fail-closed,
idempotent/restart); workflow-vs-runtime identity separation. Decisions D1–D7
control: executable consumer contract authoritative; validation before success;
structural/bounded/fail-closed reconciliation; authority preservation dominates
convenience; subject identity controls gate preservation; the two supplied
reproductions are drift under the already-current contract (D6), NOT proven
schema evolution; test the real transition path (D7). Plan order M01→M02→M03→M04
stands; M01-T01 `in_progress` with Result + frozen R01 is NOT GREEN/qualified
and must be reconciled/reviewed, never replaced or overwritten.

### 2.2 #20 boundary (controls; durable scope at `c5e9ba1…`)

Temporary readiness/configuration repair for the current Paseo/Pi deployment
ONLY: official caller-scoped `create_agent` path, injection-prerequisite
verification, fail-closed diagnostic when unavailable. Non-goals are hard:
no spawner, no daemon/shell bypass, no alternate lifecycle/readback, no
fallback delegation, no final PWv2.2 helper here. Issue title/body breadth does
NOT supersede the narrower durable BRAINSTORM/DEFINITION scope. P2 C-due is a
described boundary, not permission to continue that workstream here. #20 runs
as an independently authorizable narrow side track; it never justifies
semantic-layer changes.

### 2.3 Defect-by-defect invariants (each retains its own acceptance; none absorbed)

- #25 — eligible fresh A/B/C/Review handoff receiver must derive expectations
  from durable owner state and consume only the transferable boundary; receiver
  must not replay the producer-side Premium B stop; same-context/stale/wrong/
  replayed/malformed-handoff negatives required. **Plus the unresolved formal
  1+1+8 Research prerequisite (§6).** Adjacent to but distinct from
  #11/#17/#23.
- #26 — three separable gaps: (a) short B/C bindings vs full
  `repo@commit:path@blob` key; (b) literal backslash-n board corruption passing
  continuation; (c) missing/ineffective continuation-time validation.
  Serialization portions (a/b) may QUALIFY #23's producer boundary WITHOUT
  changing #23's subject and WITHOUT declaring #26 a duplicate. The
  pending-reservation replacement gap is NOT subsumed by #23, #18, or #37 and
  stays separately named within #26 absent an explicit later scope/dedup decision.
- #27 — terminal DONE requires exact Result + current acceptance + required
  GREEN Review + evidence before Close/dependency/JIT consumption; does NOT
  subsume #29.
- #28 — manifest Research locator must not shadow a valid execution Research
  return; returns route once to the exact owner; applied/consumed returns never
  replay. Independently analyzable early; W4 is the shared-router integration
  checkpoint, not a logical-dependence claim.
- #29 — minimal Close-owned durable proof must reconstruct in-progress Close,
  accepted completion, and end-of-scope from target-side state + immutable
  integration evidence; depends on #27 and W1–W5; conversational booleans are
  not proof; exact-subject external finalization (reviewed source head vs
  refreshed target vs PR head/check subject vs merge commit/tree vs post-merge
  reconciliation subject).
- #30 — acceptance identity must be immutable/bound to the accepted owner
  surface; GREEN must not survive acceptance drift; changed bytes never parsed
  together with an old approval (reject or explicitly consume the exact
  still-selected historical subject).
- #31 — Stage-6 needs durable reachable append-only attempt history across
  material cycles without conflating A/B/C premium semantics with ordinary
  implementation Review.
- #32 — empty Intake repair remains diagnosis; manifest/Intake intent must
  agree; materialized owner prerequisites cannot be silently ignored. Bounded
  admission guard, intentionally early (W1), needs no new history model.
- #33 — explicit user stop cannot be bypassed into Definition/Planning;
  explicit-stop preservation is early safety (W1).
- #34 — Review consumption must verify repository + exact commit + path + blob
  resolve consistently AND consume the identified bytes; WHICH-bytes/proof
  tests required (not blind Recovery when bound historical proof is available).
- #35 — active no-Result resume must refresh stable Card/authority/dependencies;
  started Cards cannot be silently refined in place. Depends on trustworthy
  proof/authority/history.
- #36 — orphan Planning/Plan-Review locators cannot be ignored while the router
  selects Execution; small fail-closed admission/precedence guard, early (W1),
  not a schema-producer fix.
- #37 — terminal implementation attempts immutable; repair publishes a new
  exact Result subject/version; existing terminal Review retains original
  subject/acceptance/evidence. Distinct from #18 (invalid-terminal) and #31
  (Stage-6 storage).
- #38 — required evidence resolved in the subject's declared durable context;
  missing/unretrievable/wrong-subject proof never qualifies a transition;
  existence ≠ semantic success. Add a truly-nonexistent-proof-at-bound-subject
  case.
- #39 — Card Result parser must reject arbitrary non-Git implementation
  subjects; distinguish implementation subject / normalized Result subject /
  Review subject / Card-acceptance surface; publish identities without
  self-referential commits (implementation → Result → Review freeze).
- #40 — `in_progress` Stage-6 verdict fails closed under the recommended scope
  (neither silently extended nor defaulted to RED); any future support needs its
  own accepted semantic contract. Independently analyzable early.
- #18 — invalid terminal GREEN needs append-only supersession: preserve the
  invalid record immutably, record invalidity + lawful successor, authorize a
  fresh attempt; downstream consumes only valid terminal attempts; metadata-vs-
  prose precedence specified.
- #14 — Planning audit / Plan Review must compose execution dependencies,
  result-consumption rights, and acceptance/composed-review gates into one
  legality graph; distinguish constituent acceptance (bounded implementation-
  input consumption) from composed acceptance. Independently researchable at W0;
  positive-path integration safer after immutable acceptance/history settle.
  P1-PROPOSED INCLUSION in this candidate scope (§1.4); the exact promotion
  authorization is the explicit approval. Deferred for PWv2.2.1 inside the
  consumer program — inclusion here does NOT lift that deferral (§1.3).
- Regression baselines (NOT reopened): closed #11 (handoff delivery), #16 (RED
  continuation), #17 (redundant confirmation), #22 (CI continuation, integrated
  by MERGED PR #24). Superseded/withdrawn history only: #13 (superseded
  parking), #15 (withdrawn pre-fix evidence — MUST NOT be used as regression
  evidence). Prior merged PRs #12/#19/#21 (cover #11/#16/#17) and PR #10
  co-bound Board precedence remain baselines.

### 2.4 Audit provenance (two distinct chains; neither authorizes repair)

- Pi/Paseo audit: canonical `main@d3ab917`; local evidence commit
  `6f1a047c912898281a645594b8518140172a8682`; REPORT (72 primary observations;
  23 fresh + 7 resumed-session native consumptions via guarded
  `pi/meta/muse-spark-1.3-contributor`, thinking max); 271-test pass +
  `scripts/test.sh` M01 baseline = BASELINE, not runtime-integration
  certification. Findings D01–D07 → new #34–#40; D08 B/#23; D09–D17 existing-
  issue evidence (#26/#30/#27/#28/#29/#31/#18/#32/#33). Portable bundle +
  histories preserved workstream-locally.
- ChatGPT adversarial audit (2026-09-29): workstream
  `research/pwv2-adversarial-stabilization-bug-hunt@95d74bad…`; committed report
  = #27–#33 provenance (N01–N07; C01–C07 already-covered/existing). Stopped
  exploratory state, Brainstorm active / promotion pending /
  `explicit_user_stop=true`; importing findings does NOT clear its stop or
  authorize promotion. Research completion ≠ promotion/repair authorization.
- Correction enforced (per INTAKE_PRIOR_ART): the two audits filed DIFFERENT
  seven-tracker sets (#27–#33 vs #34–#40); any draft stating otherwise is wrong.
  Supported conclusion is "no overarching common cause established; distinct
  invariants remain separate" — not a categorical "no shared root cause."
- Tracker: 26 issues + 2 comments read back at two epochs with no material
  title/state/body/comment drift (comparison: `material_changes: []`); #24 is a
  MERGED PR for #22, not a defect; 15 raw scope-state copies verified
  byte-for-byte against source blobs (preservation, not validity/approval).
  Tracker prose is bookkeeping, never authority. This workstream's correlation
  is issue #41 (linked, readback verified).

### 2.5 Relation discipline (a)/(b)/(c)

Use P1 §3's three relations: (a) observed mechanism; (b) reusable repair
boundary; (c) scope subsumption. Sharing (b) never establishes (a) and never
permits (c)/closure. Subsumption proposals retained as PROPOSALS for Definition
to challenge — notably: #23 already subsumes machine-constrained structural
producers/validation-before-success/supported-V2-reconciliation but EXCLUDES
unrelated premium/review/orchestration/semantic changes; #34/#38/#39/#30 share
machinery with no mutual subsumption; #18/#31/#37 are not duplicates.

## 3. Alternatives and tradeoffs (challenged)

| # | Alternative | Tradeoff | Disposition (draft recommendation) |
|---|-------------|----------|-------------------------------------|
| A1 | Dedicated new stabilization scope (P1/U01) vs silently resume/expand either diagnosis-only audit workstream or #23/#20 | Resume reuses context but inherits stopped/active subjects, violates U01 + #23/#20 boundaries, and launders audit completion into repair authority | FIXED CONSTRAINT (not a question): dedicated scope already authorized by U01 and materialized as this branch/workstream. W0 records it as decided. |
| A2 | Absorb #26 serialization into #23 as duplicate vs keep #26 with qualification-only coupling | Absorption shrinks the program but destroys #26's pending-reservation gap and contradicts U01's explicit anti-absorption rule | RETAIN separation: #26 counterexamples qualify #23's boundary; #26 stays separately tracked |
| A3 | One shared fix for #34/#38/#39/#30 vs four role-separated acceptances on shared machinery | Shared-only fix is cheaper but proven insufficient (SHA-format/existence/equality checks each miss a different role binding) | RETAIN shared machinery + four separate acceptance predicates (W2) |
| A4 | Minimal Close proof (Close-owned completion record) vs universal event-log redesign | Event log is more general but unbounded, unowned, and reinvents lifecycle state | RETAIN minimal Close-owned proof (W6); reject log redesign |
| A5 | Preserve invalid history + successor disposition vs rewrite invalid record valid | Rewrite is expedient but fabricates authority and violates append-only terminal history | RETAIN preserve + lawful successor (W3); separate pending-reservation cancellation from invalid-terminal supersession |
| A6 | Include #14 now vs defer to PWv2.2.1 | Inclusion fixes the strategic gate sooner but widens scope and needs explicit approval without lifting the PWv2.2.0 deferral | RETAIN proposed inclusion as the single candidate (§1.4) for explicit promotion consideration. If excluded instead: revision increments and the W4/DAG-check qualification consequence in §1.4 must be recorded explicitly — a scope change, not a no-change deferral. |
| A7 | Early landing of #32/#33/#36 + #28/#40 analysis (W1/W4-split) vs gate everything behind W2/W3 | Gating is simpler to schedule but delays cheap fail-closed safety with no logical dependence on identity/history | RETAIN split: land guards early, integrate shared-router behavior at W4 |
| A8 | Full #23 qualification at W5 vs declare fixed by early writer capability (W1) | Early declaration is faster but false: writer enforcement ≠ consumer admission, migration qualification, or runtime continuation | RETAIN W5 qualification; W1 establishes structural safety only |
| A9 | Import the final PWv2.2 helper / second queue to make W5 tests pass vs scope runtime-adapter gaps separately | Import unblocks tests but smuggles unapproved architecture into stabilization | REJECT import; runtime-adapter gaps are separately owned/scoped |
| A10 | Treat audit import as satisfying #25 formal Research vs retain it as a separate gate | Import saves ~10-lane orchestration but directly contradicts #25 items 7–8, U01 limits, and both audits' own statements | REJECT waiver; retain gate (§6) |

## 4. W0–W7 ordering / boundary refinement (provisional checkpoints, NOT Cards)

W0–W7 remain **proposed capability/qualification checkpoints**, not
implementation Cards, not immutable authority, and not permission to reorder
#23's approved Cards, launch concurrent shared writers, merge partial scopes,
declare role stops, or transfer A/B/C. Needed refinements Main/Definition must
enforce:

1. **W0 gates everything.** Entry: P1 + both immutable audit reports + fresh
   readbacks; no implementation permission inferred. Exit (all PROPOSED until
   GREEN Definition): dedicated ownership recorded as already-decided (U01-authorized, materialized); IDs/reproducers/provenance/
   branches/accepted-subject boundaries preserved with
   active / supported-historical / archival separation; W0 decisions frozen
   (committed-vs-dirty authority; object-publication sequencing; schema/record
   compatibility support; Stage-6 verdict states; pending-cancellation vs
   invalid-terminal-supersession law; minimal Close ownership; integration
   scope); per-transition acceptance defined as shape + relational bindings +
   object/proof closure + permitted before/after (not TOML-parse success);
   combined execution/acceptance DAG check with no circular
   Card-DONE/composed-review prerequisite; required Research reconciled;
   GREEN Definition → real premium A → exact frozen Planning → fresh
   independent B → C as applicable.
2. **Hard dependencies (must be respected as stated in P1 §4):**
   writer-uses-executable-contract AND consumer-rejects-raw-bypass (writer
   helper alone insufficient); W2 identity/proof resolution before credible
   GREEN reuse, supersession, or supported identity-changing recovery; W3 lawful
   pending/invalid-history replacement before any normalization that changes a
   subject bound to an attempt (no R01 rebinding, no fabricated verdict); DONE
   proof closure (exact Result + acceptance + history + required evidence)
   before Close/dependency/JIT consumption; Close needs that closure PLUS a
   separate reconstructible completion record; handoff receipt derived from
   valid owner/identity/history BEFORE runtime enforcement.
3. **Explicitly NOT hard (independently researchable early; integration later):**
   #33 stop preservation + #32/#36 guards need no history model (early W1);
   #28/#40 focused handling analyzable early with W4 as preferred integration
   point; #14 legality analysis at W0 with positive-path integration after
   immutable acceptance/history; #20 readiness checks independently ONLY when
   legally authorized, never justifying semantic-layer changes.
4. **Boundary corrections:** (a) full #23 scope qualifies at W5, not at W1;
   existing #23 producer work may supply a reviewed prerequisite Result that
   later checkpoints qualify WITHOUT rewriting its authorization; (b) any
   program dependency requiring a change to an existing approved strategy needs
   an explicit owning-Planning replan with renewed subject-bound gates —
   no automatic reordering/partial integration; (c) downstream may consume a
   predecessor's independently GREEN constituent result when explicitly
   sufficient, but must NOT depend on a final composed review that itself needs
   the downstream work (apply #14's DAG check to this program itself);
   (d) intermediate PRs use reference-only linkage; wave acceptance never closes
   a tracker or merges a branch; exact-head CI + target compatibility refreshed
   before any authorized integration; material change resets affected coverage;
   (e) qualification records belong in canonical owning records ONLY once the
   program is authorized/materialized — the P1 proposal/issue map is NOT a
   second Task Board.
5. **W5 entry condition restated (no-postponement rule):** "required #25
   Research resolved" is a gate BEFORE #25 repair authorization. It must NOT be
   read as permission to postpone that prerequisite past #25's Definition
   boundary (§6).

## 5. #25 formal 1+1+8 Research — canonical determination (no waiver, no false completion)

**Determination: the #25 substantial formal Research (one whole-scope lane +
one independent red-team lane + at least eight targeted lanes, frozen common
subject, one integration pass, per #25 items 7–8 under repository-root
`COORDINATOR_PROTOCOL.md` in `elmakus/project-research`) REMAINS a blocking
prerequisite before any later scope can approve #25 Definition/repair. It is
NOT required to complete THIS bounded Brainstorming formalization challenge,
and it is NOT satisfied by anything in this workstream.**

Canonical ownership chain:

- #25 body items 7–8 (tracker evidence, preserved in `issue-readback.json`)
  demand the 1+1+8 exercise + frozen subject + integration pass, with the
  integrated evidence returned to PWv2 Intake and Brainstorming
  alternatives/tradeoffs BEFORE any Definition/implementation authorization
  **of #25's repair**. That requirement is scoped to #25's Definition/repair
  boundary, not to this workstream's exploratory formalization.
- The pinned protocol (`provenance/COORDINATOR_PROTOCOL.md` §4, blob
  `3bd10eec…`, fetched read-only at `193e6f38…`) confirms the 1+1+8 minimum
  applies once Main chooses formal/swarm Research for a substantial question;
  it is a non-authoritative orchestration convention — it cannot replace
  consumer workflow authority, and its minimum does NOT apply to bug-hunt
  swarms. It therefore confirms the SHAPE of the outstanding gate without
  converting this formalization draft into that gate's satisfaction.
- U01 reconciliation limits: "The formal Research requirement recorded in
  issue #25 is not marked complete by importing the two audits. Any missing
  research remains a separate prerequisite, not an implied approval."
- `INTAKE_PRIOR_ART.md` (consumed return): "This proportional Intake return is
  NOT that exercise… must be retained before any downstream scope attempts to
  authorize #25 repair; a W5 entry condition must not be interpreted as
  permission to postpone that prerequisite past its required Definition
  boundary."
- Both audits' own statements: Pi report — #25's real receiver-loop NOT newly
  run as a connected loop; adversarial C05 — additional evidence for an
  existing issue, no new issue. P1 §5/W0: "Existing audits do not demonstrate
  completion of that exercise."
- This workstream's consumed RESEARCH.toml limitations already record:
  "#25 substantial formal Research remains unsatisfied before its
  Definition/repair authorization."

Consequences:

1. This challenge may complete (candidate GREEN, §8) WITHOUT performing 1+1+8.
2. W0 must "validate canonical ownership and explicitly adopt/reconcile this
   research gate; do not mark it satisfied by a summary" (P1 §5).
3. W5 entry "required #25 Research resolved" is enforced BEFORE #25 repair
   authorization; Definition preparation must carry it as an explicit
   unresolved prerequisite, never as a waived or satisfied item.
4. Any later attempt to treat summary import as completion is a real stop, not
   coding permission.

## 6. Agent-findable facts — Research questions and return owners (NOT user questions)

No agent-findable fact blocks this bounded challenge: the proportional prior
art is consumed and the scope is challengeable from durable evidence. The
following factual follow-ups, if pursued, are owned by future Research
(`origin_role=brainstorming`, `return_target=brainstorming` under
`workflow/RESEARCH.md`; cf. `tools/state_contract.py`
`RESEARCH_RETURN_TARGETS = {"intake", "brainstorming", "definition"}`),
never offloaded to the user:

- RQ-B1 (drift check): do the live heads of `work/pwv2-durable-state-schema`
  and `work/pwv2-paseo-child-delegation` still equal the preserved snapshots
  `b076e08…` / `c5e9ba1…`, or has material drift occurred that Definition must
  reconcile? Owner: brainstorming-origin Research; return to brainstorming.
- RQ-B2 (fresh-tracker delta): has any of issues #14/#18/#20/#23/#25–#40/#41
  or PR #9 changed title/state/body/comments since the verified fresh-readback
  epoch (`material_changes: []`)? Owner: brainstorming-origin Research; return
  to brainstorming.
- RQ-B3 (#25 lane existence): does any durable `elmakus/project-research`
  package already constitute commenced 1+1+8 lanes against a frozen common
  subject for #25, or is the gate entirely unstarted? Owner: brainstorming-origin
  Research; return to brainstorming. (Expected answer informs W0/W5 scheduling;
  any partial lanes do NOT satisfy the gate without the full wave + integration
  pass + Intake return + Brainstorming alternatives per #25 items 7–8.)

Practitioner/community consultation remains `not_relevant` for scope authority;
any later community insight is secondary and cannot override canonical weight.

## 7. Pending gate + fixed/deferred registers (needed now vs later)

(Admission control for this section: compliance with already-required
constraints — immutable identity, explicit legacy profiles, preserved #23/#20
scopes, no unauthorized merges, current U01 authorization, and the
already-authorized/materialized dedicated ownership — is NOT posed as user
questions. Those are fixed constraints carried into Definition (§2–§4).
Likewise, W0 decision detail and the qualification envelope are future
Definition/Planning design, not current-scope choices. What is truly needed
NOW for bounded formalization is exactly one act: the user's exact promotion
authorization of the single candidate scope (§1.4), which carries the #14
membership verdict. Per `workflow/BRAINSTORMING.md`, questions must target
genuine CURRENT choices; the remaining opens are Definition outputs, decided
there — so no further grilling round is posed.)

**Single pending gate G1 — exact promotion authorization (the legal stop)**

- G1. Authorize `pwv2-stabilization-program@1` for Definition promotion with
  the §1.4 membership (core #23/#25–#40/#18/#14-proposed-inclusion; #20 narrow
  side track; stated baselines/exclusions)?
  Recommendation: AUTHORIZE as specified — it preserves P1's proposed #14
  inclusion for explicit consideration instead of silently dropping it, keeps
  every invariant separately traceable, and leaves all design detail to
  Definition/Planning where it belongs. Tradeoff: authorizing WITH #14 commits
  Definition to freezing the cross-gate DAG-check acceptance; excluding #14
  instead triggers the §1.4 revision-increment + qualification-gap consequence.
  Either verdict is legal; silence or partial edits are not — Main must surface
  the membership actually authorized rather than treat P1 as mutable authority.

**Fixed constraints carried into Definition (NOT questions now)**

The following are already required by canonical sources, U01, or P1 preferred
defaults challenged in §3; Definition freezes them, Planning implements them.
No user verdict is solicited here:

- F1. Immutable-identity discipline: consume explicitly bound immutable Git
  bytes; never a mixed mutable/historical subject (STATE/AUTHORITY + P1 W0 default).
- F2. Publication sequencing: implementation → Result publication → Review
  freeze; no self-referential commits (P1 W0 default; §2.3 #39).
- F3. Compatibility: explicitly supported legacy V2 profiles only; ambiguous/
  corrupt stays Recovery (D3; §2.1).
- F4. Stage-6 verdicts: canonical pending/GREEN/RED; `in_progress` fails closed
  unless a later scope authorizes its own contract (§2.3 #40).
- F5. Replacement law: pending-reservation cancellation and invalid-terminal
  supersession are separate dispositions; preserve + lawful successor in both;
  no R01 rebinding, no fabricated verdicts (§2.3 #18/#26/#37).
- F6. Close: minimal Close-owned completion proof; no universal event-log
  redesign (§2.3 #29).
- F7. Integration: reference-only intermediate linkage; wave acceptance never
  merges/closes; exact-head CI + target compatibility refreshed before any
  authorized integration; material change resets coverage (P1 §5–§6).

**Deferred to owning phases (NOT questions now)**

- Definition outputs: the W0 decision register (F1–F7 frozen with rationale),
  per-transition acceptance (shape + relational bindings + object/proof closure
  + permitted before/after), combined execution/acceptance DAG check.
- Planning/Plan Review outputs: per-wave qualification discipline (P1 §6) and
  the connected-runtime matrix (guarded Muse Spark contributor/max, no
  fallback; genuine-external-observation-only cross-harness certification;
  disposable authorized fault-injection infrastructure) as acceptance design.
  These are implementation-design matters for their owning gates (A/B/C +
  independent reviews), not bounded-formalization choices.

## 8. Final challenge audit (candidate verdict for Main)

**Candidate verdict: GREEN — ready-for-definition (promotion EXPLICITLY pending).**

Justification against the bounded current scope:

- Exploratory scope is bounded (§1) with explicit in/out exclusions honoring U01.
- Every independently demonstrated invariant and acceptance need is preserved
  (§2); both audit provenance chains retained with immutable locators; #23/#20
  boundaries intact; anti-absorption rule enforced; tracker kept as
  bookkeeping.
- Alternatives/tradeoffs genuinely challenged (§3, A1–A10) with dispositions.
- W0–W7 validated as provisional checkpoints with explicit ordering/boundary
  refinements (§4); no wave treated as Card, authority, or reorder permission.
- #25 prerequisite correctly placed without waiver or false completion (§5).
- Agent-findable facts routed to canonical brainstorming-origin Research
  owners, not the user (§6); the single pending user act is identified as the
  promotion gate (§7 G1) rather than hidden inside the scope.
- No unresolved exploratory gap remains that would prevent offering this
  revision for promotion: membership is exactly specified (§1.4, including
  P1's proposed #14 inclusion); remaining opens are Definition outputs and
  Planning design (§7 fixed/deferred registers), which is exactly what
  Definition + the promotion stop exist to resolve.

**Promotion state (unchanged by this draft):** `promotion_state="pending"`,
`promotion_subject=""`, `challenge_audit="pending"` in durable
`BRAINSTORM.toml`. Per `workflow/BRAINSTORMING.md` and U01 limits,
ready-for-definition is NOT permission to enter Definition: the exact current
`pwv2-stabilization-program@1` must still be explicitly user-authorized for
promotion (U01 does not name this materialized `scope_id@revision`), and any
substantive scope change increments revision and stales prior authorization.
Main must not infer promotion from this candidate GREEN, from chat
continuation, or from Research completion. The promotion authorization, when
given, carries the #14-membership verdict for §1.4; any other membership is
a substantive change under §1.4 rules.

## 9. Draft Definition inputs (inputs only — Definition NOT created)

For Main's eventual Definition cycle, once exact promotion exists:

- **Source promoted subject:** `pwv2-stabilization-program@1` (pending exact
  user promotion; see §8).
- **Requirements locator (draft):** §1 (bounded scope) + §2 (invariants/
  acceptance needs) of this draft, grounded in `evidence/INTAKE_PRIOR_ART.md`,
  `evidence/PROPOSED_PROGRAM_P1.md` (§1–§4, §6–§7), `evidence/USER_AUTHORIZATION.md`,
  `evidence/PROVENANCE_INDEX.md`, both audit reports, and the preserved
  `evidence/provenance/*` locators listed in INTAKE_PRIOR_ART §"Durable evidence
  locators".
- **Decision locators (draft):** §3 dispositions (A1–A10) + §4 refinements +
  §7 gate G1 verdict once given; W0 decision register (§7 F1–F7) to be frozen
  in Definition with preferred defaults from P1 §5/W0.
- **Completeness checklist (draft, all must hold before Definition GREEN):**
  1. requirements/decisions needed for downstream planning durably identifiable
     (this §9 bound to promoted subject);
  2. challenge audit GREEN reconciled by Main (this §8 is a candidate only);
  3. exact `scope_id@revision` promotion authorized by the user;
  4. no unresolved user/product choice inside the accepted scope (G1 verdict
     recorded; #14 membership verdict explicit per §1.4);
  5. #25 gate carried as explicit UNRESOLVED prerequisite (never waived);
  6. premium stop A due (then real human-facing stop with best-available-model
     recommendation + locator-only handoff per `workflow/USER_STOP.md`).
- **Premium A note:** Definition GREEN does not enter Planning; premium A is a
  real stop. Staying in the current context is allowed only if it already
  satisfies the best-available-planning-context recommendation, and the stop
  must still render the ready-to-copy locator-only handoff.

## 10. Draft provenance and non-mutation statement

- Read: project-recovery skill + bootstrap; `origin/main` ROUTER/PROJECT.md;
  `WORKSTREAM.toml`, `INTAKE.toml`, `RESEARCH.toml`, `TRACKER.toml`,
  `BRAINSTORM.toml` at `7ff3d2a…`; `evidence/USER_AUTHORIZATION.md`,
  `evidence/INTAKE_PRIOR_ART.md` (+ its draft input
  `evidence/INTAKE_RESEARCH_INPUT.md` as corrected non-authority),
  `evidence/PROPOSED_PROGRAM_P1.md`, `evidence/PROVENANCE_INDEX.md`;
  `evidence/provenance/` readbacks, snapshots, bundles, protocol; owner modules
  BRAINSTORMING/DEFINITION/RESEARCH/INTAKE/STATE/AUTHORITY/CONTINUATION/
  USER_STOP at `origin/main@d3ab917`.
- Wrote NOTHING to the repository: no commits, pushes, issue mutations,
  merges, deploys, promotions, premium satisfactions, Plans, Cards, or
  canonical-state writes.
- Candidate output locator (DRAFT, not authority):
  `/tmp/pwv2-stabilization/formalization-drafts/brainstorm-scope.md`
- Next canonical owner: Main — reread durable state, reconcile or reject this
  draft, and continue deterministic authorized transitions until the canonical
  router reaches a real stop (expected: Definition-promotion stop for
  `pwv2-stabilization-program@1` carrying gate G1, via `workflow/USER_STOP.md`).

## 11. Correction summary (rev 2 vs unaccepted rev 1)

The raw rev-1 candidate remains UNACCEPTED; this rev-2 replaces it as the draft
for Main reconciliation. Repairs made, all within the same bounded obligation
(no canonical writes; no repair/Definition acceptance; no #25 waiver; all
boundaries preserved):

1. **Canonical Research roles:** all future Research obligations now use
   `origin_role=brainstorming` / `return_target=brainstorming` (rev 1 wrongly
   used `brainstorm`). Source: `tools/state_contract.py`
   `RESEARCH_RETURN_TARGETS = {"intake", "brainstorming", "definition"}` +
   `origin_role ∈ {"intake", "brainstorming", "definition", …}`.
2. **Redundant questions removed:** rev-1 Groups S/D/Q turned already-required
   compliance and future design into user questions. Removed: S2 ownership
   (dedicated scope already U01-authorized and materialized — now fixed §1.4/§3
   A1); D1–D7 reframed as fixed constraints F1–F7 (immutable identity, legacy
   profiles, preserved scopes, no unauthorized merges are already required —
   Definition freezes them, no verdict solicited); Q1–Q2 deferred to
   Planning/Plan Review as implementation-design acceptances. §7 now states
   explicitly what is needed NOW (only gate G1) versus later (Definition
   outputs, Planning design).
3. **#14 restored as proposed inclusion:** rev-1 recommended "DEFERRED by
   default," silently changing P1 membership. Rev-2 offers the single
   candidate WITH #14 included as P1 proposed (§1.4), recommends authorizing
   it as specified, and states the explicit consequence of excluding it
   instead (revision increment + W4 DAG-check qualification gap + PWv2.2.1
   sole ownership) — a scope change, never "no scope change."
4. **GREEN/membership contradiction resolved:** rev-1 claimed candidate GREEN
   while leaving membership unspecified across S-group questions. Rev-2
   specifies exactly one membership (§1.4), so GREEN means
   "challengeable-because-specified"; the pending promotion authorization
   (gate G1) is the legal stop that carries the membership verdict, not a
   second open exploratory question.
