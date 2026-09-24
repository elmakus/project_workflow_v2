# Project Workflow V2 — Durable State Envelope

M01 established common ownership/binding. M02 adds concrete pre-execution state. M03-T01 adds runtime-neutral Card readiness/JIT preparation without runtime orchestration identity.

## Owners

- PROJECT.md identifies the V2 project contract/workstream root; it is not a live phase/Card registry.
- WORKSTREAM.toml owns stable workstream identity/provenance and exact locators for currently materialized workstream-local records.
- INTAKE.toml owns managed-intent diagnosis, the exact reconciled diagnosis-prior-art subject/result binding, and exact issue-repair alignment.
- TRACKER.toml owns GitHub Issue bookkeeping/correlation only; it never owns requirements, repair authorization, planning or execution state.
- BRAINSTORM.toml owns one exploratory revision, challenge audit, explicit user stop and exact Definition-promotion authorization.
- RESEARCH.toml owns one factual obligation, source accounting, exact return owner and once-only reconciliation.
- DEFINITION.toml owns exact promoted scope, accepted authority, completeness and premium-A state.
- PLANNING.toml owns one material planning cycle, plan revision/artifact, planner audit, immutable frozen subject, exact premium A/B/C gate subjects, and any bounded editorial-review exemption classification/base.
- PLAN_REVIEW.toml owns one independent Stage-6 attempt for one immutable plan subject.
- TASK_BOARD.toml is materialized only when implementation state exists and then owns mutable Card/milestone execution state plus bounded predecessor-dependent JIT triggers.
- Stable Task Cards own bounded authority/scope/acceptance/tests/review and optional technical-contract refs; implementation/final review attempts remain exact-subject records.
- External-effect records are obligation-local; V2 has no universal event/action ledger.

## Intake/alignment

Issue markers/symptoms never authorize repair. A concrete issue repair subject cannot enter alignment until proportional Intake-origin Research is consumed and reconciled into the Intake-owned exact diagnosis-prior-art subject/result binding. That durable binding survives later legitimate reuse of the single current Research slot; changing the repair subject clears/invalidates it. Questions/concerns/alternatives are responses but not authorization. Authorization is bound to the exact current repair subject; changed repair makes it stale. Micro-fix candidacy is illegal before exact issue alignment.

## GitHub tracker correlation

Tracker lifecycle is `discovery | create_pending_readback | linked | ambiguous | unavailable`.

- discovery performs exact repository/dedup recovery before create;
- create_pending_readback requires readback/search before any retry;
- linked requires one positive Issue number and verified readback;
- ambiguous requires multiple candidates and fails closed instead of creating a duplicate;
- unavailable records capability absence without inventing a tracker.

Tracker records reject workflow authorization/approval fields. Optional `final_pr` is reserved for later M04 correlation and requires an already linked Issue.

## Brainstorming / Research / Definition

Definition readiness requires GREEN challenge audit and exact `scope_id@revision` promotion. Completed Research accounts for all proportional source classes and has one exact return owner. Definition GREEN requires accepted authority/completeness and premium A before Planning.

## Planning / Plan Review / premium B/C

Each material Planning entry has an exact cycle/entry subject; stale A cannot authorize a new cycle. A material re-entry persists its new draft cycle with exact premium A due before Planning resumes. GREEN planner audit freezes one exact Git blob for B. Independent Plan Review must match the frozen subject/revision/cycle. GREEN is consumed into approved plan, then C becomes due for the same subject before Execution Prep. A later purely editorial/mechanical change may omit a new review only by preserving the same approved cycle, naming the exact prior GREEN-reviewed subject, preserving satisfied B/C on that base, and recording a non-empty bounded semantic basis.

## Execution Prep / readiness

READY means the stable Card has current accepted authority, complete testable scope, and exact dependency results; it does not depend on whether a runtime worker/model/session exists. Each predecessor dependency is bound to its result path plus immutable commit/blob identity. Launch refresh rereads the exact Card, authority refs, DONE predecessor results and only the optional technical contract named by that Card. Missing/stale or same-path-changed dependency inputs fail closed before execution.

Predecessor-dependent downstream work remains a Task Board JIT trigger until its stable Card contract becomes knowable. Simple Cards do not load a second technical contract.

## Execution / semantic result

Exactly one Card remains the canonical execution unit. Runtime-internal zero/one/many worker topology is non-canonical and never creates extra Cards or shared-state writers.

Only Main/coordinator reconciles an accepted implementation into the Card's exact workstream-local `result` locator. The result stores semantic implementation subject, evidence and verified tests/readback, never runtime/provider/model/session/worker/invocation identity. A durable valid result is recovery truth and prevents replay solely because a runtime context disappeared.

An incomplete/incorrect return with a still-valid Card remains `in_progress` for correction. Only a real unresolved blocker moves the Card to `blocked`.

## Independent review attempts

Implementation review attempts are append-only workstream-local records referenced by the Card. Each attempt binds one immutable Git subject to its exact acceptance surface and stores only semantic independence provenance.

New PWv2.1 attempts also bind an explicit review kind. A `discovery` attempt records whether complete acceptance-surface discovery finished and the complete material finding IDs frozen by that pass. A `closure_verification` attempt names its earlier RED discovery source plus the subset of frozen finding IDs it is verifying. Historical terminal attempts without these fields remain valid only as the initial legacy history prefix and are interpreted as discovery; pending/in-progress attempts must use the explicit PWv2.1 fields, and legacy shape cannot resume after explicit history begins.

For REQUIRED/activated RECOMMENDED review, pending/in-progress/RED blocks terminal Card completion. GREEN closure attempts cumulatively close only the named findings from their source RED discovery. If any source finding remains unverified, the next review obligation remains closure verification; after the full frozen set is closure-verified, the router freezes one fresh full-scope discovery attempt. Only a GREEN discovery attempt for the exact current subject permits deterministic post-review finalization. A context that materially produced/repaired the subject cannot issue its independent verdict, and runtime reviewer identity is never canonical state.

Convergence-aware attempts also bind `review_scope`, one stable `review_epoch`, material defect-class IDs, and whether the attempt is the single post-convergence validation. A RED closure additionally binds `failed_material_defect_class_ids` to the exact subset that remained blocking. Discovery-epoch and per-class closure-failure counts are derived from immutable attempt history; no mutable counter store is canonical. An epoch change requires a durable accepted-redesign reset basis plus an exact immutable redesign subject from the reviewed project repository that binds either the exact acceptance surface or one exact authority ref accepted by the current Card; its commit/path/blob must read back exactly, remain the accepted content at the new reviewed subject, and differ from the preceding epoch's content at that path. Card/Milestone/Final discovery ceilings are 5/4/3 and each material defect class permits at most 3 failed repair→closure-verification rounds over subject-changing repaired-content transitions that actually failed for that class before Main convergence analysis; source-discovery content is not a repair round, unchanged repeated verification and commit-only movement of identical repository/path/blob content do not consume another round, while a return to an earlier repaired state after an intervening content change does. A post-convergence validation records its convergence basis; a RED result routes to structural resolution rather than another ordinary review cycle.

## Mutation guard / one-Card invariant

Mutable Task Board revision rejects stale expected writes. At most one Project Workflow Card may be in_progress. Runtime-internal topology remains outside canonical state.

## Prohibited canonical keys

New V2 state rejects execution-policy, runtime/model/session/worker identity, orchestration binding, universal active/returned/transfer state, Project-Card batch/lane/scheduler state and Context Health.

Production validation lives in `tools/state_contract.py`; tests import those production helpers.
