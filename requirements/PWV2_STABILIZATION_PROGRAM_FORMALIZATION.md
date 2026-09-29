# Accepted requirements — PWV2 stabilization program formalization

**Definition R1, source `pwv2-stabilization-program@1`: authority for bounded program formalization ONLY. No individual repair Definition or implementation is approved by this document.**

- Formalization subject (bounded): exact promoted revision
  `pwv2-stabilization-program@1`, source proposal `PWV2-STAB-P1`.
- This Definition performs **program-scope formalization only**: pre-execution Intake/prior-art reconciliation, promoted Brainstorming and accepted formalization requirements/decisions. It does **NOT** approve any individual issue's repair Definition, authorize implementation/Cards/Plans, satisfy premium A/B/C, mutate consumers/live workstreams, or close/merge issues.
- Canonical requirements authority: `requirements/PWV2_STABILIZATION_PROGRAM_FORMALIZATION.md`.
- Companion decision authority: `decisions/PWV2_STABILIZATION_PROGRAM_FORMALIZATION.md`.
- Workstream-local evidence remains provenance, not a replacement for these accepted requirements/decision locators.

## Canonical bindings recovered (input, read-only)

- Repository `elmakus/project_workflow_v2`, branch
  `work/pwv2-stabilization-program`, input commit
  `7134ff44116864653edb51dba9eff85ec8170ebe`.
- Manifest `implementation/workstreams/issue-pwv2-stabilization-program/WORKSTREAM.toml`;
  INTAKE complete/authorized (`PWV2-STAB-P1`); RESEARCH consumed/applied;
  BRAINSTORM **promoted**, challenge GREEN, promotion authorized for
  `pwv2-stabilization-program@1`; TRACKER linked, issue #41, readback verified.
- Scope artifact (exact, verified byte-identical at HEAD):
  `implementation/workstreams/issue-pwv2-stabilization-program/evidence/SCOPE_REVISION_1.md@aefce92718705aab806897f97f619b3b697b0722:b5b96eec1f23bb12d4cf2bf849ca21ca8aebde34`.
- Authorizations: U01 (`evidence/USER_AUTHORIZATION.md`, bounded formalization,
  W0–W7 provisional, anti-absorption); U02
  (`evidence/DEFINITION_PROMOTION_AUTHORIZATION.md`, exact promotion of
  `pwv2-stabilization-program@1` for Definition formalization only, #25 gate
  retained).
- Consumed prior art:
  `evidence/INTAKE_PRIOR_ART.md@82f4e5bd4e449c6180d167bf70e44ad8f05b036d:1bd95e6ddbfc65b1262266eeff5d1bd4b4b663cd`.
- Preparation inputs: `evidence/DEFINITION_PREPARATION.md` (unaccepted).
- Executable validation at input commit: canonical router routes
  `definition / pwv2-stabilization-program@1` ("Exact current exploratory
  revision is authorized for Definition"); `scripts/test-state-envelope.sh`
  (28 tests OK) and `scripts/test-router.sh` (43 tests OK) pass.
- Drift verification 2026-09-29 (live `git ls-remote origin`): `main@d3ab917`,
  `work/pwv2-durable-state-schema@b076e08`,
  `work/pwv2-paseo-child-delegation@c5e9ba1`,
  `research/pwv2-adversarial-stabilization-bug-hunt@95d74bad` — all unchanged
  vs preserved snapshots. Fresh issue-readback comparison:
  `material_changes: []` (26 issues, 2 comments).

## R1 — Bounded membership (exact)

Core program-scope consideration set: **#23, #25–#40, #18, #14 (proposed
inclusion)**. Narrow side track: **#20**. Regression baselines, not reopened
repair subjects: closed #11/#16/#17/#22, merged PR #24, prior merged PRs
#12/#19/#21, PR #10 co-bound Board precedence. History only: #13 (superseded),
#15 (withdrawn — never regression evidence). Tracker #41 is this workstream's
verified human-visible bookkeeping only. Scope exclusions and canonical prohibitions are preserved under R6: PR #9 adoption, PWv2.1/PWv2.2 feature expansion, consumer scope change, mass migration, live deployment, alternate spawner/shell-daemon bypass/final helper, history rewrite, similarity-based closure, and second registry/ledger/approval-store creation. Ordinary phase advancement does not remove these boundaries.

## R2 — Existing #23 boundary preserved

#23 remains structural producer/schema parity + explicitly supported bounded V2
reconciliation exactly as declared at `b076e08` (requirements R1–R13, decisions
D1–D7; plan order M01→M04 stands; M01-T01 in_progress with Result + frozen R01
is NOT GREEN/qualified). Candidate M01 is not assumed independently accepted.
No requirement/decision/approval transfers to this program; no reordering of
#23's approved Cards; no partial-integration authorization. Changes to #23's
strategy return to its own Planning/gates.

## R3 — Existing #20 boundary preserved (narrow side track)

#20 remains official caller-scoped native capability injection/readiness and
specific fail-closed diagnostics only (`c5e9ba1` durable scope controls;
issue-body breadth does not supersede it). No fallback spawn, broader runtime
helper, spawner, daemon/shell bypass, or final PWv2.2 helper. #20 never
justifies semantic-layer changes.

## R4 — Separately preserved acceptance obligations (every row survives verbatim)

| Issue | Independent invariant / acceptance need (unchanged) |
|---|---|
| #23 | Per R2; current executable schema shared by producers/consumers validated before accepted success; supported structural V2 mapping preserves only provable authority/identity, deterministic/idempotent/restart-safe, rejects ambiguous inputs. |
| #25 | Eligible independent receiver consumes the exact transferable handoff (derives expectations from durable owner state); rejects stale/wrong/replayed/malformed/non-independent receipts; never replays producer-side Premium B. **Separate formal 1+1+8 Research gate UNRESOLVED — see R9.** |
| #26 | Preserve ALL masking layers (short B/C vs full immutable key; literal backslash-n Board corruption; invalid Card status `review`; raw Result refs w/ backticks/trailing period; ineffective continuation-time enforcement) + unstarted pending-reservation replacement gap. Serialization portions may QUALIFY #23's producer boundary without changing #23's subject and without duplicate verdict. Pending-reservation gap NOT subsumed by #23/#18/#37. Progression mechanism/actor not established. |
| #27 | DONE consumable only with exact Result + current acceptance + required valid GREEN Review + proof; no inferred Close/dependency/JIT eligibility from status. Does not supply #29's proof. |
| #28 | Both manifest/Board Research entry paths return once to the exact execution owner; applied/consumed results never replay nor shadow. |
| #29 | Minimal Close-owned durable completion proof reconstructs unfinished/completed Close and true end-of-scope from target-side/immutable integration evidence. |
| #30 | Acceptance binds to the actual immutable accepted owner surface; GREEN never authorizes changed/unrelated acceptance. |
| #31 | Stage-6 retains durable append-only attempts across material planning cycles; distinct A/B/C and planner/reviewer semantics preserved. |
| #32 | Empty issue repair remains diagnosis, not empty authorization stop; Intake and manifest intent agree. |
| #33 | Explicit user stop cannot be bypassed by later Definition/Planning state. |
| #34 | Claimed Git coordinates resolve consistently AND their exact bytes are consumed; string equality insufficient. |
| #35 | Active no-Result resume refreshes stable Card, authority, dependencies; started scope never silently refined. |
| #36 | Declared orphan Planning/Plan Review prerequisites cannot be ignored while selecting Execution. |
| #37 | Valid terminal implementation attempts immutable; new repaired subject gets a new attempt; old evidence stays immutable. Distinct from #18 and #31. |
| #38 | Required proof actually resolvable in its declared durable subject context; locator/existence alone insufficient; historical Git availability distinguished from absent current-worktree files. |
| #39 | Implementation subject has verifiable Git identity, not arbitrary prose; implementation / normalized Result / Review / acceptance roles distinct. |
| #40 | Canonical Stage-6 pending/GREEN/RED handled explicitly; unsupported in_progress fails closed, never falls through as terminal RED. |
| #18 | Invalid terminal history immutable and non-authorizing; exact-bound invalidity + lawful successor provides recovery; no fabricated independence, no rewrite. Distinct from #37 (valid-terminal) and #26-pending (unstarted). |
| #14 | Compose execution, result-consumption, acceptance/composed-review edges; reject cycles hidden by execution-only DAG; distinguish accepted constituent input from final composed acceptance. **Program consideration membership — see R8; not repair authorization.** |
| #20 | Per R3. |

## R5 — Both audit/provenance chains preserved

Pi/Paseo audit (canonical `main@d3ab917`; evidence commit `6f1a047c...`;
#34–#40 provenance; 271-test baseline is NOT runtime-integration
certification) and ChatGPT adversarial audit
(`research/pwv2-adversarial-stabilization-bug-hunt@95d74bad`; #27–#33
provenance; stopped exploratory state NOT adopted) remain distinct chains with
independent invariants. The two audits filed DIFFERENT seven-tracker sets
(#27–#33 vs #34–#40). No encompassing common cause is established;
infrastructure reuse is capability reuse only, never issue absorption,
duplicate classification, widened authorization, or closing evidence. Relation
discipline (a) observed mechanism / (b) reusable repair boundary / (c) scope
subsumption: sharing (b) never establishes (a) and never permits (c)/closure.

## R6 — Authorization layers: stage limit, scope exclusions and canonical prohibitions

1. **Current U01/U02 stage permission:** bounded Definition formalization only. No material Planning, Master Plan freeze, Plan/Card/Task Board creation, premium satisfaction, repair implementation, consumer mutation, live migration, issue closure, merge or deployment is authorized now. Later Strategic Planning requires explicit premium-A continuation and durable satisfaction under the owning Definition contract; later repairs/external operations require their own lawful scope and gates. This is not a permanent prohibition of otherwise legal later phases.
2. **Scope exclusions remain exclusions:** PR #9 adoption, feature expansion, changed consumer scope, alternate spawning/final helper and mass migration are not unlocked merely by A/B/C or phase advancement. Admitting a different subject requires explicit lawful scope change and its applicable owner/gates; existing #23/#20 boundaries are never silently expanded or reordered.
3. **Canonical invariants remain mandatory in every phase:** no history rewrite, manufactured GREEN, invalid approval transfer, tracker absorption by similarity, second Task Board/approval store or runtime identity as workflow authority. These are not actions that a later generic authorization makes valid.

No existing approval transfers to this or any later scope by formalization. Requirements R4 define separately preserved program acceptance obligations, not individual issue repair authorization.

## R7 — W0–W7 provisional with validated hard vs non-hard dependencies

W0–W7 are provisional capability/qualification checkpoints, NOT Cards,
authority, or reorder permission. Validated classification (P1 §4 as refined by
SCOPE_REVISION_1 §5; **no scope/wave boundary change found necessary** — see
DECISIONS.md D8 and COMPLETENESS.md):

- **Hard:** writer uses executable contract AND consumer rejects raw-write
  bypass (writer helper alone insufficient); W2 identity/proof resolution
  before credible GREEN reuse, supersession, or supported identity-changing
  recovery; W3 lawful pending/invalid-history replacement before any
  normalization changing a subject bound to an attempt (no R01 rebinding, no
  fabricated verdict); DONE proof closure (exact Result + acceptance + history
  + required evidence) before Close/dependency/JIT consumption; Close needs
  that closure PLUS a separate reconstructible completion record; handoff
  receipt derived from valid owner/identity/history BEFORE runtime enforcement.
- **Not hard (independently researchable early; integrate later):** #32/#33/#36
  guards need no history model (early W1); #28/#40 analyzable early with W4 as
  preferred shared-router integration checkpoint; #14 legality analyzable at W0
  with positive-path integration after immutable acceptance/history settle; #20
  readiness checks independently only when legally authorized.
- **Refinements carried:** W1's #23 writer capability is not whole-issue
  completion (full #23 scope qualifies at W5); any program dependency requiring
  a change to an existing approved strategy needs an explicit owning-Planning
  replan with renewed subject-bound gates; downstream may consume an
  independently GREEN constituent result when explicitly sufficient but must NOT
  depend on a final composed review that itself needs the downstream work
  (#14's DAG check applies to this program's own strategy); intermediate PRs
  use reference-only linkage; wave acceptance never closes a tracker or merges
  a branch; exact-head CI + target compatibility refreshed before any
  authorized integration; material change resets affected coverage.

## R8 — #14 inclusion for program consideration without lifting consumer deferral

#14 is retained as PROPOSED inclusion in this candidate scope (U02 authorizes
promotion with that membership). Inclusion here is explicit program-scope
consideration ONLY: it does not lift the separate consumer PWv2.2.0 deferral,
does not authorize #14 implementation, and applies #14's combined-gate check to
this program's own eventual strategy. Excluding #14 instead is a substantive
scope change: requires a new exploratory revision/challenge, and qualification
must then state the strategic combined-gate-cycle gap.

## R9 — #25 formal 1+1+8 Research explicitly UNRESOLVED; this formalization approves NOTHING of #25's repair

The #25 substantial formal Research (one whole-scope lane + one independent
red-team lane + at least eight targeted lanes, frozen common subject, one
integration pass, per #25 items 7–8 under the pinned repository-root protocol;
protocol is orchestration convention, not product authority) REMAINS a blocking
prerequisite BEFORE #25's Definition/repair approval. Existing audit imports
and this proportional Intake check are NOT that exercise. **A GREEN
formalization of THIS bounded program subject must explicitly NOT approve #25's
individual repair Definition nor waive its prerequisite.** W5 entry "required
#25 Research resolved" is enforced BEFORE #25 repair authorization and must
never be read as permission to postpone that prerequisite past #25's Definition
boundary. Current formalization subject (program-scope preparation) is distinct
from later repair authorization (individual issue repair approval); Definition
must keep that distinction durable.

## R10 — Acceptance shape and qualification discipline

Each transition's acceptance is required shape + required relational bindings +
object/proof closure + permitted before/after transition — not TOML-parse or
helper success. Program acceptance derives from complete transition shape,
required relations, exact subject/acceptance/proof, lawful before/after
history, and qualified consumer behavior. Qualification (future Planning/
execution design, not current authorization): frozen counterexamples + positive
controls per invariant through actual producers, exact committed readback,
fresh consumers, state/publication interruption, independent subject reviews,
exact integrated-subject/end-of-scope reconstruction; cumulative contract suite
+ prior-wave adversarial cases per wave; commit → clean clone/worktree → fresh
canonical consumer; supported historic active state distinguished from archival
material (never mass-rewrite history for a green scan); failure injection at
publication/acceptance boundaries proving restart/idempotency; independent
exact-subject review by a non-executing/non-repairing context with immutable
verdicts; qualification locators recorded in canonical owning records ONLY once
authorized/materialized.

## R11 — No unresolved user/product choice inside the accepted scope

The single pending gate (exact promotion of `pwv2-stabilization-program@1`,
carrying the #14-membership verdict) is resolved by U02. Compliance items
(immutable identity, legacy profiles, preserved scopes, no unauthorized merges,
U01 limits, already-authorized dedicated ownership) are fixed constraints, not
choices. W0 decision detail, per-transition acceptance mechanics, and the
connected-runtime qualification matrix are future Definition/Planning outputs
governed by their owning gates — explicitly deferred, not hidden choices.
