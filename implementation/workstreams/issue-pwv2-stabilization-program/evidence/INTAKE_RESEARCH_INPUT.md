# Intake-origin Research draft — PWV2-STAB-P1 scope formalization prior art

**Status: CANDIDATE DRAFT FOR MAIN RECONCILIATION ONLY — NOT WORKFLOW AUTHORITY.**

- This file is a child-worker diagnosis/scope-formalization draft for the currently
  selected Intake-origin Research obligation. It does not create, modify, or satisfy
  durable workflow authority, premium gates, alignment, promotion, or implementation
  permission.
- Main is the sole canonical writer. Main must independently reread canonical
  Git/Project Workflow state, reconcile this draft, and perform any durable
  `RESEARCH.toml` / `INTAKE.toml` transition under `workflow/ROUTER.md`,
  `workflow/RESEARCH.md`, and `workflow/INTAKE.md`.
- No implementation, consumer/live-workstream change, code/policy edit, Git
  commit/push, issue mutation, merge/deploy, authority promotion, or premium
  satisfaction was performed or is authorized by this draft.
- Read repository/canonical sources only. No Paseo/session/chat state is workflow
  authority. No second Task Board, queue, approval record, review verdict store, or
  workflow state was created.

## 1. Exact obligation binding (committed input)

- Repository: `elmakus/project_workflow_v2`
- Worktree: `/worktrees/1n4cii8x/roasted-squid`
- Branch: `work/pwv2-stabilization-program`
- Committed HEAD: `cbabd7b4b1a7def7533f573324e3342a1c281313`
  (`research: bind exact Intake prior-art obligation for PWV2-STAB-P1`)
- Parent: `2daa77e27e95ca7836a580f22601df65719252ec`
  (`intake: bind bounded PWv2 stabilization scope formalization`)
- Canonical base: `origin/main` = `main@d3ab917f02e4de91b7dbb17915c2287c2387333e`
  (Merge PR #24, `work/pwv2-ci-pending-continuation`)
- Manifests (at HEAD):
  - `implementation/workstreams/issue-pwv2-stabilization-program/WORKSTREAM.toml`
    blob `62ab4b52c25241fd551d0e7880587907b8dbb95e`
  - `implementation/workstreams/issue-pwv2-stabilization-program/RESEARCH.toml`
    blob `907699c75dc8300d6622d0963b41564a2fd6e4ff`
  - `implementation/workstreams/issue-pwv2-stabilization-program/INTAKE.toml`
    blob `64380ad7f48520bd79133eef446546442ec785b9`
- Current durable values (read-only, NOT modified):
  - `RESEARCH.toml`: `workstream_id="issue-pwv2-stabilization-program"`,
    `state="active"`, `origin_role="intake"`,
    `origin_subject="PWV2-STAB-P1"`, `return_target="intake"`,
    `return_reconciliation="pending"`, `return_result=""`,
    `finding=""`, `limitations=""`, `conflicts=""`,
    four `[[sources]]` all `status="pending"`.
  - `INTAKE.toml`: `workstream_id="issue-pwv2-stabilization-program"`,
    `kind="issue"`, `state="active"`, `diagnosis_revision=1`,
    `repair_subject="PWV2-STAB-P1"`,
    `diagnosis_prior_art_subject=""`, `diagnosis_prior_art_result=""`,
    `response_kind="authorization"`, `response_observed=true`,
    `alignment_state="pending"`, `alignment_subject=""`,
    `micro_fix_candidate=false`.
- Exact formalization subject: `PWV2-STAB-P1` as **bounded pre-execution
  formalization** (canonical Intake/prior-art reconciliation, Brainstorming and
  Definition preparation). NOT implementation of any defect, NOT Card creation,
  NOT premium satisfaction, NOT authorization inherited by separately tracked
  repair subjects.
- Router (default branch, reread): `workflow/ROUTER.md`
  at `origin/main@d3ab917` blob `3160528dddb9197b9bc41bba707f56cd9c470fa9`.
  Related owner modules at same commit:
  `workflow/RESEARCH.md` blob `89b48b26653a7133ff7f7c0b9cc1644844ddc37e`,
  `workflow/INTAKE.md` blob `69b70c6a91dec55a24533f304c171beb8cb839f9`,
  `workflow/BRAINSTORMING.md` blob `b2029ea70666c1898a1ffeb318c4e14ce99d74fa`,
  `workflow/DEFINITION.md` blob `07a36c687f0b67311931abbb2c4d70620e8b32ac`,
  `workflow/STATE.md` blob `abc70478a19fe0ad806c71cee0d27e72084663fe`,
  `workflow/AUTHORITY.md` blob `f7af4b180834c2d8ec55f925bff6a9a683de37cb`,
  `workflow/CONTINUATION.md` blob `2bff46f3cc1fa66b03456eab483211640a746102`,
  `workflow/USER_STOP.md` blob `8cb2f3917991ce0c24c455f775dcdaeaec585160`,
  `PROJECT.md` blob `a9b2ece7a31edd894efd2d61be72dd7c49b6cab1`.
- Authorization evidence (at HEAD, read-only):
  - `evidence/USER_AUTHORIZATION.md`
    blob `810701e5e71fe40f179e6237fe20ef2cf182acae` — U01 verbatim authorization
    for dedicated formalization workstream ONLY; preserves #23/#20 boundaries and
    all issue/audit provenance; W0–W7 are proposals requiring canonical validation,
    not pre-approved Cards; forbids repairs, consumer changes, live migration,
    issue close, merge, PR #9 adoption, deployment; forbids silent absorption of
    distinct issues into #23/#26 by shared infrastructure; requires deterministic
    transitions per current `workflow/ROUTER.md`; return at next real
    canonical user/premium stop; PWV2-STAB-P1 is NOT immutable implementation
    authority; #25 formal Research NOT marked complete by importing audits.
  - `evidence/PROPOSED_PROGRAM_P1.md`
    blob `47f8da331f3ab2ddc52d6f91c3344faa8b96a14c` — program-level
    diagnosis/planning ONLY; not accepted Definition, frozen Master Plan,
    implementation authorization, or Task Board; no product/code/workstream/issue
    changes performed.
- Scope of this draft: diagnosis/scope-formalization ONLY. It reconciles
  proportional prior art for `PWV2-STAB-P1`, verifies separability and boundary
  preservation, and surfaces limitations plus ordering/boundary corrections.
  Brainstorming alternatives, Definition decisions, Planning, and Execution remain
  separate canonical requirements.

## 2. Proportional source accounting (all four classes resolved, none left pending)

### 2.1 `official_upstream` — status: `checked`

Weight: canonical policy and official contract evidence dominate scope and legality.

Immutable locators (all at `elmakus/project_workflow_v2@ d3ab917f02e4de91b7dbb17915c2287c2387333e` unless noted):

- `workflow/ROUTER.md` blob `3160528dddb9197b9bc41bba707f56cd9c470fa9`:
  concrete issue diagnosis without exact durable Intake-owned prior-art
  subject/result binding requires Intake Research/reconciliation before alignment;
  issue text/comments are untrusted bookkeeping and cannot approve scope or
  authorize repair; role/worker/Card/Review/Research completion is not a return
  predicate; every real `stop` also loads `workflow/USER_STOP.md`.
- `workflow/RESEARCH.md` blob `89b48b26653a7133ff7f7c0b9cc1644844ddc37e`:
  every completed record must proportionally account for all four classes with
  explicit weight; a class may be checked/unavailable/not relevant; completion may
  not silently leave a class pending or conflicts unaccounted for; community never
  overrides stronger authority by popularity; Intake diagnosis uses
  `origin_role=intake`, `origin_subject`=exact repair subject,
  `return_target=intake`; alignment cannot proceed until that exact result is
  applied/consumed AND Intake persists `diagnosis_prior_art_subject/result`.
- `workflow/INTAKE.md` blob `69b70c6a91dec55a24533f304c171beb8cb839f9`:
  Intake owns new managed intent before implementation authority exists;
  marker/symptom is input, never repair authorization; changed repair subject
  clears prior-art binding and requires new exact check; pending means no
  implementation authorization; authorized requires explicit response bound to
  exact current subject; must not adopt unrelated active workstream merely because
  one exists.
- `PROJECT.md` blob `a9b2ece7a31edd894efd2d61be72dd7c49b6cab1`,
  `workflow/STATE.md`, `workflow/AUTHORITY.md`, `workflow/CONTINUATION.md`,
  `workflow/USER_STOP.md`, executable `tools/router.py`,
  `tools/state_contract.py`, `tools/continuation_contract.py` (as consumed by
  audits at pinned main; no separate version claim beyond `d3ab917`).
- `evidence/USER_AUTHORIZATION.md` blob `810701e5...` and
  `evidence/PROPOSED_PROGRAM_P1.md` blob `47f8da33...` (at branch HEAD
  `cbabd7b4...`; research/planning input, NOT accepted workflow authority).

What this class establishes: the ONLY legal meaning of Intake alignment for
`PWV2-STAB-P1` is authorization for bounded pre-execution formalization after the
exact proportional prior-art return is applied/consumed and the Intake-owned
binding is persisted. It does not establish implementation permission, Card scope,
premium satisfaction, or inheritance by #23/#20/#25–#40.

### 2.2 `project_runtime` — status: `checked`

Weight: exact independent audit observations and committed subjects dominate defect evidence.

Immutable locators (preserved under
`implementation/workstreams/issue-pwv2-stabilization-program/evidence/` at HEAD
`cbabd7b4...`):

- `evidence/PI_PASEO_AUDIT_REPORT.md`
  blob `9a57e197a60e4e673266dfb672eb084e1117de79`:
  verdict PWv2 cannot currently be certified deterministic/fail-closed end-to-end
  through Pi/Paseo; 72 primary observations; 23 fresh native consumptions + 7
  resumed-session consumptions (all via guarded `pi/meta/muse-spark-1.3-contributor`,
  thinking `max`, `notifyOnFinish=true`; Main model unchanged); 271-test suite
  pass + `scripts/test.sh` M01 baseline PASS (does NOT certify runtime
  integration); canonical snapshot `main@d3ab917`; local evidence commit
  `6f1a047c912898281a645594b8518140172a8682`; synthetic commits are LOCAL audit
  subjects, not product-remote commits (bundles preserve histories); confirmed
  classes D01–D07 distinct new defects (→ #34–#40) plus D08 B/#23, D09–D17
  A/existing-issue evidence (#26,#30,#27,#28,#29,#31,#18,#32,#33); no shared root
  cause assigned by symptom overlap; invalid-state selection of an owner is NOT a
  claim of performed unauthorized implementation/merge.
- `evidence/CHATGPT_ADVERSARIAL_AUDIT_REPORT.md`
  blob `c2d4e91f12dd35ab23e862db9b876e0ec5a41b71`:
  date 2026-09-29, diagnosis/research only, canonical snapshot
  `main@d3ab917`, audit workstream `change-adversarial-stabilization-bug-hunt`;
  consolidated map C01–C07 already-covered/existing plus N01–N07 distinct defects
  (→ #27–#33); root-cause partition into 8 separable classes; no repair authorized;
  next legal transition is explicit user stop.
- `evidence/provenance/pi-paseo-audit.bundle`
  blob `82cc2b5804a4985007c397c1a943e5ee0ddf42e2` (binary; histories/paths/HEADs
  recorded in report; NOT product authority).
- `evidence/provenance/source-snapshots.json`
  blob `422ab7d278be693325d22820c179da06c26eb06c`:
  - `research/pwv2-adversarial-stabilization-bug-hunt@95d74bad11115419696a684c8eef11fda076f92f`
    (evidence/boundary only; Brainstorm active, promotion pending,
    `explicit_user_stop=true`; Research consumed/applied; completion is NOT
    promotion/repair authorization);
  - `work/pwv2-durable-state-schema@b076e081fb91815ff570fb70566e71f8cc53154e`
    (evidence/boundary only; M01-T01 `in_progress` with Result + frozen R01; NOT
    assumed GREEN/qualified; must be reconciled/reviewed, not reimplemented);
  - `work/pwv2-paseo-child-delegation@c5e9ba1d3da8d339e882b43b86b4e8a8dd2e9a28`
    (evidence/boundary only; official caller-scoped `create_agent` readiness only;
    P2 declares C due; describes scope boundary, not proof every record validates).
- `evidence/provenance/scope-snapshots/` tree `6ce7ac3c5d931b66dcdcd8125fb34338928898ee`:
  adversarial `BRAINSTORM.toml`/`INTAKE.toml`/`RESEARCH.toml`/`WORKSTREAM.toml` +
  `evidence--ADVERSARIAL_STABILIZATION_AUDIT_2026-09-29.md`;
  `issue-durable-state-schema/` BRAINSTORM (promoted GREEN) / DEFINITION R1 GREEN
  premium A satisfied / INTAKE complete authorized / PLANNING P1 approved
  A/B/C satisfied / RESEARCH consumed / WORKSTREAM;
  `issue-paseo-child-delegation/` BRAINSTORM promoted authorized
  `temporary-paseo-create-agent-readiness@1` / DEFINITION R1 GREEN A satisfied /
  INTAKE authorized diagnosis_revision 2 / PLANNING P2 approved A/B satisfied C due /
  WORKSTREAM. All are boundary evidence ONLY, not canonical product policy or
  selected live continuation.
- `evidence/provenance/issue23-existing-authority.md`
  blob `a84c83735291d8900a4c4808bbcd42b993e62e7f` (excerpts at `b076e08...`:
  requirements 1–13, decisions D1–D7, plan M01–M04 + cardization order
  M01→M02→M03→M04; planner challenge GREEN).
- `evidence/provenance/issue20-existing-authority.md`
  blob `88759bdb6143419bf59489e33e6a1caeed8025ad` (excerpts at `c5e9ba1...`:
  BRAINSTORM scope/non-goals/future_direction/challenge; PLANNING P2).
- `evidence/provenance/planning-provenance.json`
  blob `617d69c0d7bc3221561c9b754d844b1903d3fef7`:
  `proposal=PWV2-STAB-P1`, `implementation_authorized=false`,
  `canonical_repository=elmakus/project_workflow_v2`,
  `canonical_commit=d3ab917...`, `pi_audit_evidence_commit=6f1a047...`, plus
  sha256 list for `/tmp` inputs (noncanonical diagnosis/planning provenance; no
  workflow state or approval).

What this class establishes: two provenance-distinct independent audits overlap on
existing-issue evidence and separately demonstrate seven new consumer defects each
(same seven trackers #27–#33 mapped as N01–N07 / D01–D07 families); #23/#20
branches supply ONLY existing-scope boundaries; cumulative 271-test success is a
baseline, not acceptance.

### 2.3 `tracker_discussion` — status: `checked`

Weight: dedup and issue-specific invariants; never authorization.

Immutable locator: `evidence/provenance/issue-readback.json`
blob `479982b16ba8348c3c9562ac7cf809e07c99b9dc` — all 26 currently listed
open/closed issues (bodies, metadata, both comments read back):

- OPEN (20): #14 (strategic gate legality; deferred for PWv2.2.1), #18 (invalid
  terminal GREEN supersession), #20 (Paseo child delegation), #23 (durable-state
  producer/consumer parity), #25 (Premium B handoff loop + formal Research
  requirement), #26 (short B/C + literal backslash-n + pending-reservation gap),
  #27 (DONE without proof), #28 (execution Research shadow), #29 (Close not
  reconstructible), #30 (acceptance drift), #31 (Plan Review no append-only
  history), #32 (empty repair alignment / kind disagreement), #33 (explicit stop
  bypass), #34 (Git-object binding), #35 (active-Card resume), #36 (orphan owner),
  #37 (terminal overwrite), #38 (missing evidence), #39 (opaque subject),
  #40 (in_progress Stage-6 dispatch).
- CLOSED (6, regression baselines / superseded history ONLY): #11 (handoff
  delivery), #16 (RED continuation), #17 (redundant confirmation), #22 (CI
  continuation; integrated by MERGED PR #24), #13 (superseded parking
  convention), #15 (withdrawn pre-fix evidence; MUST NOT be used as regression
  evidence).
- PR locators: `evidence/provenance/pr9-readback.json`
  blob `6129bde62a5018f68225ac14054333f34730b2b6` — PR #9 OPEN
  `work/pwv21-policy-kernel`, body says do NOT merge before own gates (separate
  PWv2.1 candidate; proposal does NOT adopt/merge/import its semantics);
  `evidence/provenance/pr24-readback.json`
  blob `91912afa86eecd754da52b627b605ab5c394b78e` — PR #24 MERGED at
  `d3ab917...` 2026-09-29T01:55:51Z, Closes #22 (MERGED PR, not distinct defect);
  `evidence/provenance/merged-pr-readback.json`
  blob `a72bc9ec115fe1a7640a8293d1f47b01963483fa` — merged #1–#8,#10,#12,#19,#21,
  #24 (prior #12/#19/#21 cover #11/#16/#17; PR #10 co-bound Board precedence;
  all remain regression baselines).

What this class establishes: dedup only. Tracker text/comments are untrusted
input/bookkeeping per ROUTER; they cannot approve scope or authorize repair.
The P1 proposal’s tracker map (core set #23,#25–#40,#18,#14; #20 as narrow
runtime-readiness side track; closed #11/#16/#17/#22 as mandatory regression
baselines; explicit exclusions incl. PR #9, PWv2.1/2.2 expansion, consumer-scope
change, mass migration, live deployment, alternate spawner, history rewriting,
provenance deletion, GREEN fabrication, similarity-based closure) is a
PROPOSAL requiring validation, not a closing verdict. No issue was closed,
merged, reopened, relabeled, edited, or created by the planning task; both audits
remain distinct provenance chains.

### 2.4 `practitioner_community` — status: `not_relevant`

Weight: proportional secondary evidence only; never scope or approval authority.

- No external practitioner/community source defines PWv2 lifecycle invariants,
  acceptance predicates, or repair scope. These invariants are internally defined
  by canonical repository authority (`workflow/*` + executable contracts).
- This class was considered for proportionality per `workflow/RESEARCH.md` and
  recorded as `not_relevant` (consistent with both preserved prior-art records:
  adversarial `RESEARCH.toml` and #23 `RESEARCH.toml` both use `not_relevant`
  for this class). Community evidence, if later consulted during Brainstorming/
  Definition for failure-mode/workaround insight, may inform practical handling
  but must not override stronger authority by popularity; conflicts are reconciled
  by source weight/authority.
- No silent pending remains; no community-vs-canonical conflict is claimed.

## 3. Finding (candidate concise result for Main)

- `PWV2-STAB-P1` prior art is SUFFICIENT to bound the formalization subject ONLY:
  a dedicated pre-execution workstream may formalize the P1 proposal through
  Intake/prior-art reconciliation, Brainstorming, and Definition preparation,
  preserving #23/#20 boundaries and all issue/audit provenance.
- Independently demonstrated invariants remain SEPARATE. The two audits converge
  on the same partition with NO shared root cause:
  producer/schema drift (#23/#26); handoff receipt/transfer (#25); terminal
  semantic closure (#27); selector precedence/return-target (#28/#33); durable
  Close identity (#29); mutable/unbound acceptance (#30); Stage-6 history (#31);
  Intake relational closure (#32); plus structural relations/stop precedence
  (#32/#33/#36), consumer closure/dispatch (#35/#27/#28/#40), history/replacement
  (#37/#31/#18 + #26 pending-reservation gap), exact identity/proof
  (#34/#39/#38/#30), handoff/runtime (#25/#20 + #11/#16/#17/#22 baselines),
  strategic legality (#14), Close reconstruction (#29). Sharing reusable repair
  machinery (b) does NOT establish shared observed mechanism (a) or permit scope
  subsumption/closure (c).
- Existing #23 scope REMAINS INTACT: producer/consumer schema authority,
  validate-before-success, one executable schema, deterministic fail-closed
  intra-V2 reconciliation with authority preservation ONLY on proven exact
  subject identity, no parallel schema, no widened scope/history rewriting; plan
  order M01→M02→M03→M04; M01-T01 `in_progress` with Result + frozen R01 is NOT
  GREEN/qualified and must be reconciled/reviewed, not replaced.
- Existing #20 scope REMAINS INTACT: temporary readiness/configuration repair for
  current Paseo/Pi deployment via ONLY official caller-scoped `create_agent`,
  with injection-prerequisite verification and fail-closed diagnostic; NO spawner,
  daemon/shell bypass, alternate lifecycle/readback, fallback delegation, or final
  PWv2.2 helper. Title/body breadth does NOT supersede this narrower durable
  boundary. P2 C due is a described boundary, not permission to continue it here.
- W0–W7 are PROPOSALS ONLY (`PROPOSED_PROGRAM_P1.md` §5 header “all proposed,
  none authorized”; §8 implementation-authorization stop). They must themselves be
  validated through canonical Intake→Brainstorming→Definition→A→Planning→B→
  Plan Review→C→Execution Prep. They do NOT reorder #23’s approved Cards, launch
  concurrent shared writers, merge partial scopes, declare role stops, or transfer
  any existing A/B/C satisfaction.
- Preserved subsumption/bookkeeping boundaries hold as PROPOSED distinctions (to
  be challenged in Brainstorming/Definition): #23 already subsumes
  machine-constrained structural producers/validation-before-success/supported V2
  reconciliation but its accepted requirements EXCLUDE unrelated premium/review/
  orchestration/semantic changes; #26 serialization counterexamples may QUALIFY
  that boundary WITHOUT changing #23’s subject and WITHOUT declaring #26 a
  duplicate; #26 pending-reservation replacement is NOT subsumed by #23/#18/#37;
  #34/#38/#39/#30 share infrastructure but none subsumes another; #18/#31/#37 are
  not duplicates; #27 does not subsume #29; #23 does not subsume #32/#36/#40;
  #17 does not subsume #25; withdrawn #15 is not regression evidence; #13 is
  superseded bookkeeping.
- This prior-art return does NOT satisfy, waive, or transfer the SEPARATE
  substantial formal Research precondition recorded in #25 (see §5). It also does
  NOT authorize W1 implementation, #14 inclusion (which additionally requires
  explicit approval and does not lift the PWv2.2.0 deferral), PR #9 adoption,
  consumer migration, live deployment, or any tracker closure/merge.

## 4. Limitations (factual; must survive into Definition/Planning)

1. Anchored ONLY to `main@d3ab917...` + branch HEAD `cbabd7b4...` + preserved
   evidence blobs listed in §2. Dirty-local input vs committed authority,
   object-publication sequencing, schema/record compatibility support, Stage-6
   verdict states, pending-cancellation vs invalid-terminal-supersession law,
   minimal Close ownership, and program integration scope are UNDECIDED pending
   W0 Definition (preferred defaults in P1 §5/W0 are proposals, not decisions).
2. 271-test pass + `scripts/test.sh` M01 PASS are baselines, NOT runtime-integration
   certification. No normal production machine-constrained writer exists for most
   lifecycle records; tests prove concrete consumer acceptance/rejection of
   committed subjects, NOT universal validity of arbitrary agent-authored output.
   Fixture helpers are not shipped writers.
3. Synthetic commits/histories are LOCAL audit subjects (bundles preserve them);
   NOT product-remote commits. No live PR merge, issue closure, CI
   trigger/cancellation, remote concurrent publication, UI persistence restore,
   kill/restart during external write, or hostile child write into a real
   workstream was performed.
4. Invalid-state selection of an execution/finalization owner does NOT claim that
   unauthorized implementation/merge was performed; a later prose-obeying owner
   might still block — that is NOT an executable selector guarantee.
5. `exact_subject_observed` / caller fingerprints/epochs are caller-supplied
   (default true); helpers have no actual run/head data and cannot themselves prove
   exact subject. Pending observation is distinct from semantic reconciliation;
   unchanged progress still raises the no-progress fuse. No timing-safety or
   connected polling-loop certification is inferred from unit tests. Live
   queued→terminal latency/technical timeout was not exercised by creating CI work.
6. The #22 classifier regression is NOT reproduced at `d3ab917`; current requested
   matrix is correct for the exercised synthetic states. This does not reopen #22.
7. Concurrency assurance is limited to parallel read-only native diagnostics in
   isolated spaces + a synthetic unsafe two-writer barrier that VIOLATES the
   canonical sole-Main rule (operational non-enforcement risk, NOT a new lawful
   defect). Real hostile/two-Main, competing-writer/stale-coordinator races with
   durable effects were not authorized.
8. Fresh-context/restart coverage is bounded: new session at lifecycle boundaries,
   consumed-locator replay, wrong/stale locators, independence failure,
   RED/repair/re-review, child/parent context loss, committed-result-but-missing-
   notification, malformed #22/#20 profiles, normalization after pending R01,
   repeated/interrupted recovery apply, missing native capability, isolated
   reversed-finish-order contributions. Restart during merge/publication/closure
   and externally moving the real target were NOT induced. Target movement or
   material coverage change requires refresh/requalification; stale CI is never
   inherited.
9. Pi/Paseo runtime identity (provider/model/session/worker, parent relationship,
   max thinking) is diagnostic metadata ONLY, never workflow authority. No
   mechanism preventing arbitrary parent narrative from manufacturing authority is
   proven. Caller-supplied four-field locator expectations and receiver
   independence are not auto-derived from Git by a shipped adapter. #25’s real
   receiver-loop was NOT newly run as a connected Pi loop in the Pi audit;
   adversarial C05 records it as additional evidence, not a new issue.
10. Cross-harness (ChatGPT entry/delivery/recovery) certification requires a genuine
    external lifecycle observation through an allowed harness; absent evidence is
    BLOCKED, not simulated from Markdown tests. All real-LLM tests here used the
    guarded Muse Spark contributor/max profile with no fallback; Main’s model
    stays user-selected.
11. Historical scope: at pinned main, 86 artifacts scanned, 45 fail individual
    current validators — SOME are unselected historical records, NOT all active
    route blockers. Supported historic active state must be checked separately
    from unselected archival material; no bulk history rewriting to obtain a green
    scan. Malformed PROJECT frontmatter aborts technically (TOMLDecodeError), not
    semantic success; Markdown-body text after frontmatter is correctly ignored.
12. #23 second-reproduction scope note: the two supplied reproductions do NOT
    establish a real historical V2 schema-version transition (relevant blobs at
    declared creation base identical to current main). Future supported older-V2
    migration contract still needs explicit design/fixtures.
13. #14 positive-path integration, #20 readiness handling, and runtime-adapter gaps
    are separately owned; inclusion/expansion requires explicit approval and
    owning-Planning authority. Deferred #14 in a new scope does not lift the
    deferral inside PWv2.2.0.
14. Practitioner/community class is `not_relevant` for scope authority; any later
    community insight is secondary and cannot override canonical weight.
15. This draft alone does NOT complete Intake alignment. Per `workflow/INTAKE.md`,
    Main must still apply/consume the exact Research result AND persist
    `diagnosis_prior_art_subject=PWV2-STAB-P1` plus the exact non-empty
    `diagnosis_prior_art_result` binding. Changed repair subject would stale that
    binding and require a new exact check.

## 5. Conflicts (explicit accounting; reconciled by weight, not popularity)

- `SINGLE-ROOT-CAUSE vs PARTITION`: REJECTED single explanation. Both audits
  independently partition into separable failure classes with independent
  reproducers (see §3). Resolution: preserve every issue ID, exact reproducer,
  audit provenance, candidate branch, and accepted-subject boundary; distinguish
  active selected state, supported historical state, and unselected archival
  material. Common infrastructure MAY be reused; every separately demonstrated
  invariant/acceptance requirement REMAINS separately traceable.
- `#23 CONTRACT-EVOLUTION CHARACTERIZATION vs EXACT GIT EVIDENCE`: #23 text at
  one point characterizes a reproduction as contract evolution; exact blob
  comparison (relevant validator/router/workflow blobs at declared creation base
  identical to current main, per preserved #23 prior art) conflicts with that
  characterization. Resolution: treat as producer/consumer drift under
  already-current contract; missing intra-V2 migration mechanism REMAINS a real
  architectural gap but is NOT the cause of those two malformed writes.
- `W0–W7 PROPOSAL vs EXISTING #23/#20 AUTHORITY`: any reading of wave ordering as
  permission to reorder #23 Cards, expand #20 into a spawner/helper, merge
  partial scopes, or transfer A/B/C conflicts with owning-workstream authority.
  Resolution: waves are capability/qualification checkpoints; if a program
  dependency requires changing an existing approved strategy, request explicit
  owning-Planning replan first (with renewed subject-bound gates when required).
  Downstream may consume a predecessor’s independently GREEN constituent result
  when explicitly sufficient; must NOT depend on a final composed review needing
  the downstream work (apply #14 DAG check to the program itself).
- `#20 TITLE/BODY BREADTH vs DURABLE NARROW SCOPE`: issue #20 prose suggests a
  broader semantic/runtime-neutral direction; durable BRAINSTORM/DEFINITION at
  `c5e9ba1...` narrowly bounds to temporary official-path readiness.
  Resolution: durable scope controls; broader direction belongs to a separate
  PWv2.2 helper, not this stabilization formalization.
- `TRACKER SIMILARITY vs DEDUP/SEPARATION`: sharing (b) reusable repair boundary
  must NOT be read as (a) shared mechanism or (c) subsumption/closure permission.
  Resolution: §3 subsumption distinctions stand as proposals to be challenged;
  no issue is absorbed/duplicated/closed/broadened/reassigned by overlap
  statement; tracker remains bookkeeping, never authorization.
- `PRACTITIONER vs CANONICAL`: no material community conflict found; to the extent
  any future community workaround suggests a shortcut, canonical policy +
  executable contracts dominate. Explicit `none` for additional
  community-originated scope conflict beyond this precedence rule.
- No unresolved conflict authorizes implementation, closure, merge, or premium
  satisfaction. Any unknown choice or failed independence is a real stop, not
  coding permission.

## 6. Verifications performed (read-only)

- [x] Reread `workflow/ROUTER.md` from `origin/main@d3ab917`, plus
  `workflow/RESEARCH.md` / `workflow/INTAKE.md`; followed progressive read order
  (router → PROJECT.md → exact workstream manifest → pointed pre-execution
  records → NO Task Board/Card, since no implementation state exists).
- [x] Reread `WORKSTREAM.toml` / `RESEARCH.toml` / `INTAKE.toml` at HEAD
  `cbabd7b4...`; confirmed `origin_role=intake`,
  `origin_subject=PWV2-STAB-P1`, `return_target=intake`, pending reconciliation,
  empty finding/limitations/conflicts, four pending source classes (the gap this
  draft fills as CANDIDATE).
- [x] Reread `USER_AUTHORIZATION.md` (U01) + `PROPOSED_PROGRAM_P1.md` (§1–§8) +
  full preserved `evidence/provenance/*` (issue-readback 26 issues, PR #9/#24/
  merged-PR readbacks, planning-provenance, source-snapshots, all scope snapshots
  + adversarial evidence file, #23/#20 authority excerpts, `pi-paseo-audit.bundle`
  reference).
- [x] Verified D01–D17 ↔ #34–#40/#23/#26/#30/#27/#28/#29/#31/#18/#32/#33 and
  N01–N07 ↔ #27–#33 and C01–C07 ↔ #16/#22/#23/#26/#25/#18/#14 mappings preserve
  independently demonstrated invariants; no duplicate-issue creation or
  issue-scope edit performed.
- [x] Verified #23 requirements/decisions/plan boundaries + M01-T01
  in_progress/Result/R01-frozen (not GREEN) intact; #20 temporary-readiness
  boundary + P2 C-due intact; PR #9 NOT adopted; PR #24 correctly treated as
  merged integration of #22; closed #11/#16/#17/#22 + #13/#15 correctly treated
  as baselines/history only.
- [x] Verified W0–W7 language is proposal-only (P1 §5 “all proposed, none
  authorized”, P1 §8 stop + suggested user instruction, U01 reconciliation
  limits + explicit Brainstorm-promotion/premium-A/B/C separation).
- [x] Surfaced #25 unfulfilled precondition WITHOUT marking satisfied (see §7).

## 7. Necessary ordering/boundary correction (Main must enforce; NOT satisfied here)

1. **#25 formal Research precondition is UNFULFILLED and MUST NOT be marked
   satisfied by this prior-art return or by importing the two audits.**
   - #25 body “Required diagnosis and research” item 7 demands: substantial formal
     Research using repository-root `COORDINATOR_PROTOCOL.md` in
     `elmakus/project-research`: one whole-scope lane, one independent red-team
     lane, at least eight targeted lanes, frozen common analysis subject, one
     integration pass; then return integrated evidence to PWv2 Intake, then
     Brainstorming alternatives/tradeoffs before any Definition/implementation
     authorization.
   - Both preserved audits explicitly do NOT demonstrate that exercise
     (Pi report: “#25 real receiver-loop not newly run”; adversarial C05:
     “additional evidence for existing issue; no new issue”; P1 §5/W0: “Existing
     audits do not demonstrate completion of that exercise”; U01: “formal Research
     requirement recorded in issue #25 is not marked complete by importing the two
     audits”).
   - Correction: W5 entry MUST require “required #25 Research resolved” BEFORE
     #25 repair authorization; W0 MUST “resolve #25’s outstanding formal Research
     requirement … validate canonical ownership and explicitly adopt/reconcile
     this research gate; do not mark it satisfied by a summary.” Main must keep
     this as a separate prerequisite and surface any attempt to treat summary
     import as completion as a real stop.

2. **W0 admission/evidence-lock/Definition-decisions MUST precede any repair wave.**
   Required W0 outcomes (all PROPOSED until GREEN Definition): dedicated new scope
   vs explicitly selected legal ownership (do NOT silently resume/expand either
   diagnosis-only audit workstream); preserve IDs/reproducers/provenance/branches/
   accepted-subject boundaries with active/supported-historical/archival
   separation; freeze decisions for committed-vs-dirty authority,
   publication sequencing, compatibility support, Stage-6 states,
   pending-cancellation vs invalid-terminal-supersession, minimal Close ownership,
   integration scope; define each transition’s acceptance as
   shape + relational bindings + object/proof closure + permitted before/after
   (not TOML parse success); independent combined execution/acceptance DAG check
   (no circular Card-DONE/composed-review prerequisite); required Research
   reconciled; GREEN Definition → real premium A → exact frozen Planning → fresh
   independent B → C as applicable.

3. **Capability order MUST be respected as stated in P1 §4 (proposed, to be
   challenged):**
   `W0 admission → W1 structural integrity/early safety → W2 exact
   identity/proof → W3 lawful history/replacement → W4 complete
   routing/strategic legality → W5 Recovery/receipt/runtime integration → W6 Close
   reconstruction → W7 independent end-to-end acceptance`.
   - Hard: writer serialization must use executable contract AND consumer admission
     must reject raw-write bypasses; W2 resolution must precede GREEN
     reuse/supersession/supported recovery; W3 lawful pending/invalid-history
     replacement must precede normalization changing a subject-bound attempt (no
     R01 rebinding / fabricated verdict); DONE proof closure (W4) requires exact
     Result + acceptance + history + evidence; Close (W6) requires that closure +
     separate reconstructible completion record; handoff receipt must derive from
     valid owner/identity/history BEFORE runtime enforcement.
   - NOT hard (independently researchable early, integration checkpoint later):
     #33 stop preservation + #32/#36 structural guards do NOT need new history
     model (intentionally early W1); #28/#40 focused owner/enum handling may be
     analyzed early with W4 as preferred shared-router checkpoint; #14 legality
     analysis independently researchable at W0 with positive-path integration
     safer after immutable acceptance/history; #20 readiness checks may run
     independently ONLY when legally authorized and do NOT justify semantic-layer
     changes.
   - Full #23 structural reconciliation qualification belongs in W5, NOT declared
     fixed by early writer capability alone. Existing #23 producer work may supply
     a reviewed prerequisite Result; later checkpoints qualify it WITHOUT
     rewriting original authorization.
   - Runtime adapter gaps discovered in W5 are separately owned; do NOT import the
     final PWv2.2 helper or a second queue to make tests pass.

4. **Boundary corrections Main must preserve:**
   - Do NOT silently absorb distinct issues into #23/#26 by shared infrastructure.
     #26 serialization portions may qualify #23’s boundary WITHOUT changing #23’s
     subject; #26 pending-reservation stays separately named within #26 absent an
     explicit later scope/dedup decision.
   - #14 inclusion in any new stabilization scope requires EXPLICIT approval and
     does NOT lift the deferral inside PWv2.2.0.
   - Intermediate PRs use reference-only linkage; wave acceptance does NOT close a
     tracker or merge a branch; exact-head CI + target compatibility must be
     refreshed before any authorized integration; material change resets affected
     coverage.
   - Qualification records belong in canonical owning records ONLY once the
     program is authorized/materialized; the P1 proposal/issue map is NOT a second
     Task Board.

## 8. Recommended completed `RESEARCH.toml` field values (for Main ONLY)

Main must independently validate before writing. Do NOT write from this draft
without canonical reread. `return_reconciliation` stays `pending` until Main
applies/consumes via Intake; `return_result` stays empty until Main binds the
exact durable evidence locator on apply. Intake’s
`diagnosis_prior_art_subject/result` binding and any alignment transition remain
separate Main-owned durable steps per `workflow/INTAKE.md`.

```toml
workstream_id = "issue-pwv2-stabilization-program"
state = "complete"
origin_role = "intake"
origin_subject = "PWV2-STAB-P1"
return_target = "intake"
return_reconciliation = "pending"
return_result = ""
finding = "PWV2-STAB-P1 prior art bounds pre-execution formalization only: two independent audits overlap on existing-issue evidence and separately demonstrate seven new consumer defects (#27-#33 / #34-#40 families) with no shared root cause; existing #23 producer/consumer-parity and #20 temporary caller-scoped readiness scopes remain intact; W0-W7 are proposals requiring canonical Brainstorming/Definition/A/B/C validation; no implementation, closure, merge, PR #9 adoption, or premium satisfaction is authorized."
limitations = "Anchored to main@d3ab917 and branch cbabd7b4 plus preserved evidence blobs; 271-test pass is baseline not integration proof; synthetic subjects are local not remote; no live merge/close/CI/concurrent/hostile coverage; exact-subject/pending helpers are caller-supplied; W0 Definition decisions undecided; #25 substantial COORDINATOR_PROTOCOL Research (1 whole-scope + 1 red-team + >=8 targeted lanes + integration) remains UNFULFILLED and is not satisfied by importing audits; #14 inclusion needs explicit approval."
conflicts = "Single-root-cause rejected: 8 separable classes with independent reproducers. #23 evolution wording conflicts with identical-blob evidence: resolved as drift, migration gap remains but not cause. W0-W7 vs existing #23/#20 authority: proposal does not reorder/expand/transfer A/B/C; owning-Planning replan required for strategy change. #20 prose breadth vs durable narrow scope: durable controls. Similarity never implies subsumption/closure; tracker is bookkeeping only. No residual community scope conflict beyond canonical precedence."

[[sources]]
class = "official_upstream"
status = "checked"
weight = "canonical policy and official contract evidence dominate scope and legality"

[[sources]]
class = "project_runtime"
status = "checked"
weight = "exact independent audit observations and committed subjects dominate defect evidence"

[[sources]]
class = "tracker_discussion"
status = "checked"
weight = "dedup and issue-specific invariants; never authorization"

[[sources]]
class = "practitioner_community"
status = "not_relevant"
weight = "proportional secondary evidence only; never scope or approval authority"
```

## 9. Draft provenance (this file only)

- Draft read inputs: `PROJECT.md`; `origin/main:workflow/ROUTER.md`,
  `workflow/RESEARCH.md`, `workflow/INTAKE.md`; branch HEAD `cbabd7b4...`
  `WORKSTREAM.toml`/`RESEARCH.toml`/`INTAKE.toml`;
  `evidence/USER_AUTHORIZATION.md`, `evidence/PROPOSED_PROGRAM_P1.md`,
  `evidence/PI_PASEO_AUDIT_REPORT.md`,
  `evidence/CHATGPT_ADVERSARIAL_AUDIT_REPORT.md`, full
  `evidence/provenance/*` (issue-readback 26 issues, pr9/pr24/merged-PR readbacks,
  planning-provenance, source-snapshots, all scope snapshots + adversarial
  evidence file, #23/#20 authority excerpts, bundle reference).
- Draft wrote NOTHING to the repository. No commits, pushes, issue mutations,
  merges, deploys, promotions, or premium satisfactions.
- Candidate output locator (DRAFT, not authority):
  `/tmp/pwv2-stabilization/formalization-drafts/intake-prior-art.md`
- Next canonical owner: Main. Main must reread durable Git/Project Workflow state,
  reconcile or reject this draft, and continue deterministic authorized transitions
  until the canonical router reaches a real stop.
