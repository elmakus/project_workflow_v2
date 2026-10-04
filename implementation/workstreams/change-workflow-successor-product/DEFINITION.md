# Definition — Project Workflow V3 successor product

Status: DRAFT / revision-10 promoted R6 product delta; pending fresh full Definition Review; external execution bootstrap is non-authoritative  
Subject: `workflow-successor-product@6`  
Definition revision: 10  
Initial product release: `3.0.0`

## Product outcome

Build PWV3 as a clean successor to Project Workflow V2: a deterministic, runtime-neutral workflow for long-lived software/project work that preserves exact durable authority in Git/GitHub, survives fresh contexts and host changes, and supports ChatGPT and Pi/Paseo.

PWV3 optimizes for reconstructibility, exact evidence, safe continuation and low semantic machinery rather than maximal orchestration. Being simpler than V2/V2.2 is product intent, not an independent pass/fail acceptance predicate.

## Canonical lifecycle

The semantic lifecycle is:

1. entry/resume health + freshness admission;
2. Brainstorming for genuine owner/product choices;
3. mandatory Brainstorming Research through Orchestration Protocol, returning its exact durable result to the Brainstorming owner for applicability reconciliation and single semantic consumption;
4. Definition;
5. mandatory Orchestration Protocol Definition Review; a RED/repair-required result returns to Definition and the same review obligation remains unresolved until a compatible applicable OP result establishes acceptance;
6. Strategic Planning, with optional Technical Design inside the Plan Package;
7. mandatory Orchestration Protocol Plan Review;
8. Execution Prep / Execution Package;
9. mandatory Orchestration Protocol Execution Package Review;
10. sequential Project Card execution;
11. Result + proportional implementation Review/revalidation;
12. Final Qualification, including a mandatory internal non-independent Targeted Qualification Campaign, exact candidate freeze/pre-Global readiness, and mandatory independent OP Global Bug Hunt;
13. fresh terminal acceptance under the applicable exact terminal predicate;
14. one final managed integration path;
15. Close from durable target-side evidence.

Named lifecycle steps do not imply user stops except where this Definition explicitly creates one. A stop exists at genuine owner authority, required fresh-context/runtime boundary, the mandatory post-OP accepted-result owner gate defined below for non-Global OP boundaries, the external Global Bug Hunt boundary, non-remediable blocker, explicit pause or end-of-approved-scope.

Semantic return routing is deterministic. Genuine product-outcome or owner-choice change returns to Brainstorming. Requirement, product-scope or Definition-level acceptance meaning change returns to Definition. Strategy, decomposition or dependency meaning that remains inside the accepted Definition returns to Strategic Planning. Concrete execution-package refinement that preserves the reviewed Plan remains owned by Execution Prep. When multiple classes appear to apply, route to the earliest upstream semantic owner whose accepted meaning must change; no downstream stage may silently absorb an upstream semantic change.

## Orchestration Protocol boundary

Orchestration Protocol is a mandatory normal dependency of PWV3 at:
- Brainstorming Research;
- Definition Review;
- Plan Review;
- Execution Prep / Execution Package Review;
- Final Qualification Global Bug Hunt.

PWV3 owns:
- that an OP obligation is due;
- the exact workstream/boundary;
- the exact subject and acceptance/coverage surface;
- the exact durable result identity/type expected from that obligation;
- the durable result applicability check;
- single semantic consumption of an applicable result;
- the mandatory post-OP accepted-result owner gate for non-Global OP boundaries;
- deterministic Global Bug Hunt result disposition without a routine post-CLEAR owner gate;
- canonical continuation only after an explicit owner CONTINUE choice.

For every OP-backed boundary, wrong-subject, stale, duplicate-as-new, incomplete, unsupported, BLOCKED or otherwise non-applicable evidence fails closed and cannot advance the lifecycle. Re-observing an already consumed exact result after restart is idempotent evidence, not permission to replay the semantic transition.

Every dispatchable PWV3-owned OP obligation has exactly one durable **current attempt frontier** before any OP execution is attempted. The frontier binds the exact OP boundary, exact subject + acceptance/coverage binding and one exact OP-attempt identity. This applies to the first attempt, owner-triggered repeats and any later same-obligation successor attempt; RUN OP AGAIN is therefore one way to establish a successor frontier, not the only place where attempt currentness exists.

Each current OP attempt has caller-visible semantic phases, independent of representation:
- **DUE** — the exact current attempt identity exists durably and execution of that exact attempt has not yet been positively acknowledged;
- **IN_PROGRESS** — execution of that exact attempt has been positively acknowledged and no caller-visible terminal result is yet durably bound;
- **TERMINAL** — exactly one caller-visible terminal result is durably bound to that attempt.

Dispatch/resume for the exact current attempt must be idempotent or durably acknowledged/read back. UNKNOWN occurrence never permits minting or blindly dispatching another attempt. Recovery from DUE may dispatch that same exact attempt; Recovery from IN_PROGRESS resumes/queries that same exact attempt; Recovery from TERMINAL consumes only its bound terminal result under current applicability rules.

The **first** attempt frontier is established when an exact OP obligation first becomes dispatchable. A non-advancing TERMINAL result closes that attempt for advancement. If repair or upstream correction changes the subject/binding, the resulting exact unresolved OP obligation establishes one new first/current attempt for that new binding. If the same exact obligation remains due after a recoverable non-advancing terminal result and the blocker/UNKNOWN cause is positively resolved without semantic drift, the owning semantic stage **must establish exactly one durable successor attempt frontier on the same binding as the sole next routing transition before any redispatch**; the predecessor attempt remains immutable history and can never regain currentness.

For every OP-backed boundary other than the Final Qualification Global Bug Hunt, when the caller-visible terminal result is advance-permitting for that exact bound obligation, PWV3 must establish exactly one real human user/workstream-owner authority gate before forward continuation. No agent, runtime, semantic-stage owner or coordinator may infer, default or synthesize either choice.

The Final Qualification Global Bug Hunt is the exception. The user explicitly launches the exact independent Global attempt. An applicable CLEAR result advances deterministically to fresh terminal acceptance without creating a routine CONTINUE / RUN OP AGAIN gate. REPAIR_REQUIRED returns bounded implementation-only findings to the current execution obligation; changed implementation invalidates all affected evidence and requires a new applicable Global result whenever the exact candidate or materially relevant acceptance surface changed. Findings that require Plan, Execution Package, Definition or owner-authority change route to the earliest upstream semantic owner. BLOCKED/UNKNOWN fails closed. A repeated same-binding Global attempt remains legal when explicitly requested before closure, but is not a mandatory continuation choice.

That pending gate is a canonical durable non-derivable routing fact. It binds:
- the exact PWV3 OP boundary;
- the exact accepted OP result and OP-attempt identity;
- the exact subject + acceptance/coverage binding;
- its unresolved/resolved status;
- and, once resolved, exactly one durable owner disposition.

The owner chooses exactly one of:
- **CONTINUE** — authorize exactly one forward semantic consumption of that exact current accepted result and derive the canonical next workflow obligation;
- **RUN OP AGAIN** — durably close that exact gate/result for forward authorization while preserving it as immutable historical evidence, remain at the same semantic OP boundary and establish exactly one new current repeat-attempt frontier over the same exact subject + acceptance/coverage binding.

The owner disposition must be durably published and positively read back before its semantic effect is acted on. Re-observation of the same resolved gate/choice is idempotent and single-use; stale, mismatched, duplicate-as-new or differently bound choice evidence fails closed.

For **RUN OP AGAIN**, resolving the human gate and consuming that disposition are distinct semantic facts. At semantic consumption of the resolved RUN OP AGAIN disposition, PWV3 MUST revalidate current applicability/freshness of the exact subject + acceptance/coverage binding even though the gate is no longer pending. Material or UNKNOWN scope/acceptance/authority drift fails closed and routes under the normal upstream rules.

A RUN OP AGAIN disposition is consumed exactly once through one durable semantic cut:
- before the cut, the prior accepted result is closed for forward continuation but the resolved disposition is not yet consumed into a repeat frontier;
- the cut durably binds one exact new repeat-attempt identity to the same applicable boundary/binding and positively reads that frontier back;
- after the cut, that exact attempt is the sole current frontier and the resolved disposition cannot create any second attempt.

A RUN OP AGAIN successor uses the same universal current-attempt phases and dispatch/resume rules above. The repeat-specific durable cut determines which successor attempt becomes current; it does not create a separate attempt model.

No earlier accepted result or earlier owner choice may regain forward authority after the repeat frontier cut. RED/repair-required/BLOCKED/UNKNOWN at the current frontier remains non-advancing and cannot fall back to an older GREEN. Only an advance-permitting accepted TERMINAL result at the current frontier creates the next distinct owner gate. There is no fixed repeat limit.

RED/repair-required evidence returns to the owning semantic stage; after bounded repair the OP obligation remains unresolved until a compatible applicable OP result establishes acceptance. BLOCKED/UNKNOWN cannot advance and do not create the post-GREEN choice gate. Brainstorming Research additionally binds the exact Brainstorming return owner/obligation and may be reused only when applicability and freshness to that exact subject are proven.

PWV3 does **not** own:
- lane counts;
- worker roles;
- lane topology;
- fresh-context launcher mechanics;
- profile-specific search strategy;
- convergence mechanics;
- integrator topology;
- internal reclaim/allocator state.

Those belong to the separate `elmakus/orchestration-protocol-skill` product.

A compatible change to OP internals must not require a PWV3 product change. PWV3 depends only on the stable caller/result boundary.

OP executes in ChatGPT. If Pi/Paseo reaches an OP boundary, it performs a runtime-neutral handoff to ChatGPT and stops at that boundary. If the owner-facing Main is already ChatGPT, that Main may remain the coordinator; OP creates/uses whatever fresh contexts its own protocol requires. Ordinary same-runtime stage changes do not create ceremonial handoffs.

The external OP Skill architecture Research is parallel product work and is not a prerequisite to authoring or approving this PWV3 Definition. Its production capability becomes an implementation/qualification dependency for PWV3 3.0.

## Ordinary Review completeness

Per-Card or other Reviews that do not use OP still inspect the complete declared bounded review/acceptance surface. A reviewer must not intentionally stop merely because the first valid defect already implies RED.

This is single-review completeness, not orchestration. It does not imply lanes or swarms.

## Core authority invariants

- One semantic workflow and one legal current/next obligation.
- GitHub remote durable state is canonical across runtimes.
- Runtime/model/session/worker/local-worktree state is never semantic authority.
- One versioned current/recovery checkpoint stores only non-derivable routing facts and exact pointers; its bounded contents are defined by semantic necessity rather than a subjective size adjective.
- Immutable/revisioned artifacts carry semantic history.
- Exact Git object identity is part of correctness where acceptance, reuse, compatibility or non-replay depends on it.
- Results are immutable.
- Review attempts are append-only and bind exact subject + exact acceptance surface.
- Canonical publication is freshness-fenced and followed by positive remote readback.
- Required semantic independence is based on material authorship/repair of the exact subject, never merely a fresh session/model/runtime.
- Independence-waiver eligibility is boundary-scoped. For **ordinary non-OP Review**, the default is owner-waivable: an explicit, durable, exact-scope human owner waiver may waive the independence requirement unless that exact Review boundary explicitly forbids waiver. The owner waiver exercises that global ordinary-Review default; no prior per-Card waiver-eligible marker is required. OP-backed boundaries and QF terminal acceptance use their own explicit rules and are not broadened by this default. Any waived result must bind the exact waived scope and owner authorization honestly, must not be called independent GREEN, and uses **WAIVED_ACCEPTANCE** only when the applicable boundary defines waiver as acceptance-sufficient.
- The canonical confirmed-PWV3-defect health predicate is the sole narrow GitHub-Issue-based semantic-authority exception; all other Issue content remains bookkeeping/untrusted input.
- UNKNOWN semantic/effect state fails closed.

## Planning and execution

- Plan Package owns strategy, ordered logical work, acceptance coverage, dependencies/material inputs, risk and qualification expectations.
- Technical Design is optional and Plan-owned, never a separate lifecycle authority.
- The reviewed Plan may contain logical work slots rather than every final concrete Card.
- Execution Prep materializes stable Cards as refinements of the exact reviewed Plan.
- The exact accepted reviewed Execution Package is the single portable direct execution artifact. It is semantically identical regardless of the supported runtime/executor that later realizes it.
- The owner does not predeclare an execution mode/runtime/provider in the Plan or Execution Package. Execution realization is derived from the invocation environment only after Package Review.
- The exact runtime/executor/provider bundle actually used is positively observed and recorded as execution provenance/readback after launch; it is not prior semantic authority and cannot alter the accepted package.
- Card identity remains immutable after materialization, but 3.0 includes semantics-preserving runtime refinement beneath a Card into subordinate execution steps/subtasks when that refinement cannot alter Card scope, dependencies, acceptance, Review obligation or authority. Such subordinate refinement is execution mechanics, never replacement/reuse/splitting of the semantic Card.
- Semantic changes return according to the deterministic upstream-owner rule above.
- Exactly one Project Card owns the execution-stage current obligation at a time.
- A Card's completion cycle is: implementation -> immutable Result -> every applicable deterministic check / Review / affected-cone revalidation -> accepted completion. Publishing a Result does not advance the execution pointer while any required acceptance obligation for that Card remains unresolved or non-accepted.
- Only after accepted completion may the durable Card pointer advance to the next Card in the total order.
- An implementation-only non-accepted Review/revalidation outcome keeps or reopens that same stable Card for bounded repair. Changed implementation MUST produce a new immutable Result and repeat every Review/revalidation invalidated by that change before the Card can complete. If the finding changes product, Definition, Plan strategy/dependencies or Execution Package meaning, the existing earliest-upstream semantic-owner rule applies instead.
- Card identity is stable after materialization; execution order is explicit and total.
- Dependencies bind exact accepted Results and exist for validation/impact propagation, not scheduling.
- Before execution, the reviewed Plan/Execution Package must prove that total execution order, material-input dependencies and acceptance/Review gates are jointly satisfiable and cycle-free as semantic constraints; this is validation, not a parallel scheduler.
- Every materialized Card carries an objectively decidable Review obligation fixed by the reviewed Plan/Execution Package or another explicitly named durable authority. Missing or ambiguous Review applicability fails closed rather than being guessed at execution time.
- No product-level parallel Card scheduler, claims/fan-in state or parallel execution DAG is part of PWV3.

## Result, Review and revalidation

A Result records exact implementation subject, obligation/Card, material input Results, required evidence/readbacks, outcome and producing contract version.

Changed implementation creates a new Result.

Independent Review is required where risk/semantic authority warrants it. Low-risk Cards may complete from deterministic Result/tests/readback only when their exact durable Review obligation says independent Review is not required. A context that materially authored or repaired an exact subject is ineligible to independently approve that subject. Fresh context/runtime/model identity alone does not prove independence.

For ordinary non-OP Review, independence is globally owner-waivable by an explicit durable exact-scope human waiver unless the exact Review boundary explicitly forbids waiver. Silence therefore means waiver-eligible for ordinary non-OP Review only. A waiver does not relabel the outcome independent GREEN and does not alter OP-backed or QF waiver semantics.

Prior Review evidence is immutable. Reuse is an applicability decision.

Changed dependency, implementation/integration subject, shared contract or acceptance surface invalidates the exact transitive materially affected cone over declared material-input dependencies, acceptance/Review dependencies and relevant shared surfaces. Preserve evidence outside the proven cone. If the cone or impact cannot be bounded safely, widen revalidation to the full potentially affected current acceptance surface rather than assuming narrow applicability.

For every OP-backed PWV3 boundary, PWV3 requires only the stable caller/result semantics defined in the Orchestration Protocol boundary: exact obligation/binding, an applicable caller-visible terminal result, fail-closed non-advancing outcomes, and the post-result owner gate. Discovery breadth, lane topology, integration, convergence, repair-loop realization, focused revalidation mechanics and any internal wave-count policy remain exclusively Orchestration Protocol Skill responsibility.

This does not weaken ordinary non-OP Review completeness or PWV3's responsibility to decide whether the caller-visible OP result permits semantic advancement.

## Recovery and external effects

Recovery reconstructs durable truth and does not replay chat/session execution.

- Durable accepted Result suppresses replay.
- A pending/resolved post-OP owner gate and the exact current OP-attempt frontier for every dispatchable OP obligation are reconstructed from canonical durable state. Recovery never re-prompts a resolved gate, reapplies an old choice to a later result, relaunches an already-established attempt, mints a second attempt while occurrence is UNKNOWN, or falls back from a current non-advancing attempt/result to an older GREEN.
- Local unpublished progress may continue only when the exact remote canonical predecessor/head against which that local attempt was based, together with the exact semantic authority inputs consumed by the attempt, is positively verified unchanged. If that relation cannot be proven, Recovery fails closed.
- Remote canonical state wins over divergent stale local WIP.
- No mandatory continuous WIP publication.
- Duplicable external effects require durable intent before attempt.
- External-effect flow: intent -> attempt -> authoritative readback -> verified outcome.
- UNKNOWN occurrence forbids blind retry.

## Helper/state boundary

The deterministic helper is a stateless executor/projection over canonical inputs, not a second workflow engine/state store.

Required capabilities include:
- inspect/resume/derive-next;
- validate identities/contracts/dependencies/acceptance;
- classify freshness and local-vs-remote state;
- build deterministic bounded context packs;
- derive version/evolution impact;
- guarded publish/readback;
- effect reconciliation;
- exact reconstruction/validation of pending or resolved post-OP owner gate and the universal current OP-attempt frontier;
- health;
- runtime/package doctor/handshake.

A missing, denied, unverifiable or incompatible capability required by the current obligation never counts as completion. **Handoff-first precedence applies:** when exactly one safe qualified supported runtime is positively available and the exact obligation can be reconstructed there, PWV3 must perform a runtime-neutral handoff to that runtime, which reconstructs canonical state and re-derives the same obligation before any work continues. A durable blocker is used when no such unique qualified safe handoff can be positively established. Ambiguous availability, multiple non-equivalent candidate routes, or UNKNOWN qualification fails closed as a blocker rather than inviting a guessed handoff.

No helper-local workflow DB, scheduler journal, agent registry or hidden durable semantic cache.

## Runtime realization

PWV3 defines one execution semantic path. ChatGPT, Pi/Paseo or another future qualified supported host may realize that path without creating a different Plan, Execution Package, Card model or acceptance contract.

The same exact accepted reviewed Execution Package is portable across supported execution venues. The user does not set a durable `execution_mode`. A runtime may derive a transient launch envelope from its invocation context, but exact runtime/package/provider identity is only execution provenance and recovery input after positive readback.

### ChatGPT

- Minimal Project Instructions + live GitHub discovery.
- Qualified locator-only bootstrap fallback.
- No static Project Source required.
- Resolve trusted release origin -> immutable package identity -> handshake -> helper -> canonical GitHub read/write/readback.
- Capabilities are probed rather than inferred.
- Required OP boundaries use the external Orchestration Protocol Skill in ChatGPT.

### Pi/Paseo

- One globally managed exact PWV3 package identity is resolved and verified before semantic work.
- The host realization is thin over the same deterministic helper/semantic contract used by PWV3; exact adapter, CLI/debug, bootstrap and package-component decomposition remain Strategic Planning/implementation choices unless a separately accepted stable external contract requires them.
- Paseo owns runtime/child lifecycle; PWV3 owns semantics.
- Generic Workers may be used for ordinary bounded work where permitted.
- Generic Workers are bounded non-recursive workers in 3.0 and do not spawn/delegate to further Generic Workers.
- Generic Workers/child agents cannot substitute for mandatory OP.
- No mandatory MCP/Paseo semantic plugin.

Specific third-party autonomous-execution extensions, provider packages and local bootstrap configuration are outside PWV3 semantic Definition/Plan/Execution Package authority. They may be used externally to execute the accepted package only if the invocation environment satisfies the package's required capability/effect/currentness constraints.

## Donor policy

PWV2/V2.2 is a semantic parts bin, not an inherited subsystem.

- State the surviving PWV3 invariant before reuse.
- Literal COPY_AS_IS is exceptional.
- Small architecture-neutral utilities/algorithms may be ported.
- Architecture-owning lifecycle/state/routing logic is reimplemented from PWV3 contracts.
- Regression scenarios, fixtures and counterexamples are reused aggressively when the invariant survives.
- Provenance for reused/ported donor code and translated regression evidence is preserved as durable non-authoritative metadata, never as semantic authority.
- PWV3 has no runtime/build dependency on `elmakus/project_workflow_v2`.
- No shared V2/V3 semantic compatibility library.
- No ordinary native reader for V1/V2/V2.2 workflow state.

## Historical defect memory

Do not mechanically copy old Issues.

Historical failures become PWV3 invariant/root-cause regressions when applicable. A V2 defect becomes a new PWV3 Issue only after current applicability/reproduction or structural proof, root-cause dedup and rewrite in PWV3 terms.

The integrated minimum 3.0 regression corpus is mandatory qualification evidence.

## Release scope — PWV3 3.0.0

3.0.0 is the smallest complete semantic safety kernel plus qualification needed to govern real work and then its own continued development.

Required in 3.0.0:
- entry/resume freshness and health;
- Brainstorming;
- mandatory OP Research;
- Definition + mandatory OP Definition Review;
- Strategic Plan Package + mandatory OP Plan Review;
- Execution Prep + mandatory OP Execution Package Review;
- sequential Cards;
- immutable Results;
- proportional ordinary implementation Reviews;
- affected-cone revalidation;
- Recovery/no replay;
- external-effect safety;
- exact Git identity/fenced publication/readback;
- per-artifact contract versioning from the first durable write;
- deterministic helper;
- ChatGPT and Pi/Paseo surfaces over one semantic contract;
- mandatory external OP Skill caller/result integration;
- confirmed-defect health and bounded maintenance path;
- Final Qualification semantics;
- mandatory internal non-independent Targeted Qualification Campaign and mandatory independent OP Global Bug Hunt;
- fresh terminal acceptance under the applicable exact terminal predicate;
- one qualified final integration method;
- target-side Close;
- safe compatible patch adoption within the 3.0.x line.

Before qualified 3.0.0 GA:
- mandatory host-neutral regression corpus is GREEN;
- live ChatGPT qualification is GREEN only when the exact frozen candidate demonstrates every applicable required ChatGPT realization semantic and declared blocker/failure behavior;
- live Pi/Paseo qualification is GREEN only when the exact frozen candidate demonstrates every applicable required Pi/Paseo realization semantic and declared blocker/failure behavior;
- at least one real cross-host continuation is proven;
- the mandatory internal Targeted Qualification Campaign covers the exact reviewed risk/acceptance surface and all required findings are dispositioned before pre-Global readiness;
- one mandatory Global Bug Hunt OP obligation/result for the exact frozen qualification surface must reach the caller-visible terminal disposition required by the stable PWV3↔OP contract; profile breadth and internal notions of “fullness” remain OP Skill responsibility. Applicable CLEAR continues without a routine post-Global owner gate; explicit repeats remain legal before closure and a changed candidate/surface requires a new applicable Global result;
- every repair/revalidation obligation produced by the internal Targeted Qualification Campaign or exported by the applicable current Global Bug Hunt result and required for advancement is satisfied before qualification can advance; PWV3 does not independently reinterpret OP-internal Global finding admission;
- representative PWV3-on-PWV3 dogfood reaches valid Close and exercises, at minimum, Research/Definition/Planning, Plan Review, Execution Prep, dependent sequential Cards, routine and independently reviewed Results, restart/host transition, guarded external effect/readback, ordinary Final Qualification, internal Targeted Qualification, external Global Bug Hunt, repair/revalidation, terminal acceptance, final integration/Close and fresh terminal reconstruction;
- after the corrected exact final candidate QF and its current acceptance surface are fixed, and applicability of every required prior qualification item to that QF/current acceptance has been proven, a **newly produced post-QF terminal acceptance result** is required. An older acceptance result cannot satisfy this fresh terminal gate merely by later applicability proof;
- the post-QF terminal-acceptance gate owns one exact **current acceptance-attempt frontier** bound to that exact QF + current acceptance surface. Establishing any later same-binding terminal-acceptance attempt must first durably supersede the prior current attempt; superseded attempts/results remain immutable history and cannot authorize advancement;
- only the current acceptance attempt/result can satisfy the gate. A current RED/BLOCKED/UNKNOWN/stale/ambiguous attempt or result prevents any older INDEPENDENT_GREEN or WAIVED_ACCEPTANCE from remaining advancement-sufficient. Recovery reconstructs that one current acceptance-attempt frontier and never falls back to an older success;
- the current newly produced post-QF terminal acceptance is sufficient when it is either **INDEPENDENT_GREEN** from a semantically independent reviewer or **WAIVED_ACCEPTANCE** produced under an explicit, durable, exact-scope human owner waiver for that exact QF/current acceptance surface. WAIVED_ACCEPTANCE is never labeled independent GREEN;
- after an applicable Global CLEAR, a qualified semantically independent, read-only, non-authoring closure reviewer may execute the fresh terminal predicate automatically without a separate manual handoff; provider/runtime self-review or an authoring/repairing reviewer cannot satisfy semantic independence;
- immutable publication/promotion and readback succeed.

PWV3 construction for this workstream has no mid-implementation PWV2 -> partial-PWV3 semantic authority cut. PWV2 governs only through the accepted reviewed Execution Package. That exact package is then handed to an external qualified execution environment which performs implementation outside PWV2 governance. Runtime/provider choice and installation are outside PWV3 semantic artifacts.

Self-hosting is still mandatory qualification/dogfood after a runnable PWV3 candidate exists. That qualification must prove the complete native lifecycle, Recovery/no-replay, external-effect safety, mandatory OP boundaries, Final Qualification, terminal acceptance, final integration and target-side Close from canonical PWV3 state.

## Product versioning and compatibility

Initial product release is `3.0.0`.

- `3.0.x`: bug-fix/maintenance line.
- `3.1.0`, `3.2.0`, ...: compatible product/contract evolution.
- major increment: genuinely breaking semantic/contract boundary that cannot safely preserve or interpret valid prior-lineage work.

Release labels do not prove compatibility.

Every durable artifact kind carries a producing contract version. Product/package version, helper/API contract, artifact contract version and runtime capability are separate axes.

A normal `3.0.x` patch preserves 3.0-line artifact contracts and reads valid earlier 3.0.x history without rewriting immutable Results/Reviews. An active workstream pinned to an exact 3.0.x package/helper identity may explicitly adopt a qualified compatible 3.0.x identity without rewriting immutable semantic history when durable artifact contracts remain compatible. The identity transition is freshness-fenced and positively read back, and prior evidence is reused only after current applicability is established. The generalized guarded roll-forward/adoption mechanism and compatibility matrix are required 3.0 capabilities. Invalid state created through an implementation defect may correctly enter Recovery/repair.

If a fix requires a genuinely new compatible durable contract, prefer the next minor release with explicit old+new reader/applicability support.

A genuinely breaking contract/semantic correction requires a major boundary rather than a disguised patch.

No automatic rollback controller. Prefer qualified forward repair. Blind downgrade after writing an unsupported newer contract is forbidden.

## Compatible-evolution foundations required in 3.0

Initial 3.0 includes the known compatibility/evolution machinery rather than intentionally reserving it for later minor releases:
- historical-reader registry/dispatch, current-reader projection, unknown-newer refusal and synthetic old/current/newer/malformed fixtures;
- guarded active-workstream release adoption/roll-forward;
- machine-checkable release/artifact/helper/runtime compatibility matrix and downgrade refusal;
- semantics-preserving subordinate runtime refinement beneath immutable Cards;
- proof-based Review/evidence applicability reuse;
- richer affected-cone diagnostics;
- richer health/maintenance diagnostics and remediation guidance;
- doctor/inspect/resume explanations that expose exact identity, mismatch, next obligation and recovery reason;
- richer deterministic context packs;
- Pi/Paseo bounded-worker ergonomics/allow-lists consistent with the runtime-neutral execution contract;
- richer GitHub Issue mutation/reconciliation helpers while preserving Issues as non-authority except the narrow health predicate;
- deterministic anomaly dedup and file-and-continue only for explicitly nonblocking non-authoritative anomaly classes;
- multi-generation reader/conversion framework;
- reader retirement/compaction lifecycle metadata and removal conditions;
- generalized within-PWV3 migration harness with exact-source binding, dry-run/proof/staging/readback/idempotence/forward-repair;
- material-fingerprint optimization;
- qualified branch/worktree cleanup automation that preserves dirty/divergent/UNKNOWN state.

Concrete adapters/readers for future schemas that do not yet exist naturally arrive with those future schemas; their enabling framework and qualification harness belong to 3.0.

Rich TUI/web dashboards and additional managed merge-queue/repository-policy product capabilities remain outside the current PWV3 roadmap unless a future concrete owner decision reopens them.

## Explicit exclusions / removed roadmap

PWV3 does not plan:
- Assurance Profile, OP enable/disable form, OP presets or project OP defaults;
- OP lane/profile configuration inside PWV3;
- historical/status browser as a separate product feature;
- additional managed merge methods beyond the one qualified path unless future concrete need reopens it;
- staged/ring rollout automation;
- automatic rollback controller;
- persistent telemetry/tracing backend;
- fleet/cross-workstream analytics;
- Paseo status/semantic plugin;
- optional MCP adapter under the current extension/package design;
- additional runtimes/providers beyond ChatGPT and Pi/Paseo;
- additional external tracker integrations beyond GitHub Issues;
- expanded signing/attestation/SBOM/provenance subsystem under the current single-owner threat model;
- permanent V1/V2/V2.2 compatibility adapters;
- workflow DB/event store;
- cross-runtime lock/lease/takeover machinery;
- recursive Generic Worker delegation as semantic authority;
- RAG as authority;
- LangGraph/Temporal/Jev/System-One as canonical workflow state;
- fixed semantic repair-attempt ceilings;
- stacked workstreams;
- separate OpenSpec lifecycle;
- mandatory continuous WIP publication;
- second Close/cleanup PR;
- Gauntlet/loop-until-win system.

## Package trust

One fixed owner-controlled canonical PWV3 package/release origin per supported host/bootstrap.

Moving channel metadata is discovery only. Exact execution resolves immutable release/artifact identity and verifies it.

No separate trust service, PKI, signing hierarchy or trust DB under the current owner model.

## GitHub Issues and health

GitHub Issues remain bookkeeping, not semantic workflow authority except for the single narrow confirmed-defect health predicate below.

The canonical confirmed-defect Issue set is the sole Issue-based semantic-authority exception. A defect counts only when its durable classification proves that it is a confirmed PWV3 product defect applicable to the currently governing release/subject; unrelated, unconfirmed or merely reported Issues do not enter the health set.

Health:
- zero open applicable confirmed PWV3 defects -> HEALTHY;
- one or more -> BLOCKED for ordinary work;
- incomplete/unreliable classification or complete-query evidence -> UNKNOWN/nonhealthy;
- a bounded maintenance workstream may repair the exact declared blocking defects without deadlocking on those same defects.

Health is positively re-evaluated at minimum on workstream entry/resume, before each new ordinary Card, at Final Qualification entry, at final integration/merge when not covered by the same current verified operation, and after a qualified maintenance release before paused consumers resume.

No second health database.

## Final integration and Close

Use one qualified managed final integration method for PWV3 3.0.

Before merge freeze exact source, target/base, integrated candidate, final acceptance and required checks. On target movement, derive the target delta and refreshed integrated candidate, then classify impact against the accepted surface: proven non-material movement may reuse prior semantic acceptance only after required affected checks are GREEN; material or UNKNOWN movement creates a new required revalidation/review subject. The qualified managed integration path must enforce target/base freshness (or equivalent atomic proof) across acceptance-to-merge so the accepted integration context is the one actually integrated. Positively read back merge/target containment.

Close derives from durable pre-merge close-ready evidence plus verified target-side integration/effects. Branch deletion is non-semantic. No second Close PR.

## PWV2 construction handoff

PWV2 is a temporary **pre-execution authoring/governance harness only** for this construction workstream.

Accepted sequence:
1. this PWV3 Definition becomes accepted product authority;
2. Strategic Planning and Plan Review complete under PWV2;
3. Execution Prep materializes the exact portable Execution Package and mandatory Execution Package Review accepts it;
4. the exact accepted package is frozen and handed to an external qualified execution environment;
5. implementation, tests, bounded repair, ordinary Review/revalidation and qualification work execute outside PWV2 governance;
6. a complete runnable PWV3 candidate is then qualified, including PWV3-on-PWV3 dogfood, Global Bug Hunt, fresh terminal acceptance, final integration and Close.

No partial PWV3 checkpoint becomes semantic authority midway through implementation for this construction workstream. PWV2 does not execute the accepted package, and third-party executor installation/configuration is not part of the PWV3 Definition, Plan or Execution Package.

## Acceptance obligations for Planning

Strategic Planning must preserve this Definition and cover at least:
- native PWV3 checkpoint/artifact contracts;
- exact authority and derive-next kernel;
- donor extraction boundaries and non-authoritative provenance metadata;
- regression corpus;
- package/helper identity;
- ChatGPT and Pi/Paseo host-realization and host-integration semantics;
- external OP Skill invocation/result contract and build dependency;
- mandatory OP boundary integration;
- Planning/Execution Package/Result/Review semantics;
- one portable reviewed Execution Package with no predeclared execution runtime/provider;
- invocation-derived runtime binding with positive provenance/readback and no provider-specific semantic authority;
- Recovery/external effects;
- full 3.0 compatibility/evolution foundations, including historical-reader framework, guarded roll-forward, compatibility matrix, migration harness, material fingerprints and cleanup;
- health/maintenance;
- Final Qualification with internal Targeted Qualification and external independent Global Bug Hunt;
- one final integration/Close path;
- PWV2 pre-execution authoring -> external package execution -> qualified 3.0.0 product completion.

Exact filenames, serialization, helper operation names, API schemas, package names and other representation choices remain Planning/implementation choices unless required by an external stable contract.

## Definition completion

No unresolved owner/product choice remains in this draft.

Definition revision 2 received a complete independent OP-backed review with overall RED and 20 canonical blocking findings. Definition revision 3 incorporated and independently revalidated all FR-01..FR-20 repairs as GREEN. Revision 4 added the owner-fixed 3.0.0 post-OP CONTINUE / RUN OP AGAIN invariant and then received a new complete full independent Definition Review.

That revision-4 full review was RED with three canonical bounded findings:
- R4-F01: durable gate/choice/current-attempt frontier was incomplete;
- R4-F02: PWV3 still leaked OP-internal discovery/integration/revalidation mechanics;
- R4-F03: Global Bug Hunt baseline cardinality was ambiguous against owner-selected repeats.

Definition revision 5 incorporated the three R4 bounded repairs and later received focused revalidation GREEN. The human owner then chose RUN OP AGAIN, creating repeat Definition Review attempt `D05-OP-DEFREV-A02`. A02 completed with RED and five blocking findings A02-F01..A02-F05 plus one non-blocking precision finding A02-F06.

Definition revision 6 incorporates the bounded A02 repairs:
- explicit repeat-disposition consumption, applicability fence and caller-visible DUE / IN_PROGRESS / TERMINAL dispatch-resume contract;
- explicit SH0 mandatory-OP prerequisites and fail-closed deferral of Final Qualification OP capability;
- Final Qualification expressed in stable caller/result obligations rather than OP-internal “full”/finding-admission language;
- terminal acceptance freshness plus owner-selected **Option B**, allowing exact-scope terminal independence waiver through WAIVED_ACCEPTANCE for QF and SH0 while forbidding the independent-GREEN label;
- Pi/Paseo Definition text reduced to semantic host/runtime constraints rather than component topology;
- non-blocking subjective “materially simpler” / “small checkpoint” wording made non-normative or objective.

Fresh focused revalidation of revision 6 closed A02-F01, A02-F02 and A02-F03 and confirmed A02-F06 cleanup, but remained RED on two residual incomplete repairs:
- R1-F01 / A02-F04: lifecycle step 13 and the 3.0.0 required-scope list still said unconditional `fresh independent final acceptance`, contradicting owner Option B and the detailed `WAIVED_ACCEPTANCE` terminal predicate;
- R1-F02 / A02-F05: Planning still normatively required `ChatGPT and Pi/Paseo adapters`, preserving a topology term that the repaired runtime section had explicitly returned to Planning/implementation freedom.

Definition revision 7 applies only those two residual repairs:
- higher-level lifecycle/release wording now requires fresh terminal acceptance under the already-defined applicable exact terminal predicate, preserving newly-produced post-QF freshness and Option B without requiring the independent-GREEN label for waived acceptance;
- the Planning obligation now requires ChatGPT and Pi/Paseo host-realization and host-integration semantics rather than an adapter decomposition.

Revision 7 received focused revalidation GREEN, after which the owner selected RUN OP AGAIN. Repeat attempt `D07-OP-DEFREV-A03` used 15 independently rotated review lenses and integrated RED with seven canonical blocking findings.

Definition revision 8 consumes that A03 RED and the owner decisions **OD-01=1A, OD-02=2B, OD-03=3A**:
- all mandatory OP dispatches now have a universal exact current-attempt frontier with deterministic first/successor attempt and Recovery semantics, not only RUN OP AGAIN repeats;
- each Card now remains the sole execution-stage obligation through Result plus all required Review/revalidation until accepted completion, with same-Card repair/new-Result/re-review semantics for implementation-only RED;
- capability failure is handoff-first to one positively verified qualified safe supported runtime, otherwise durable blocker;
- SH0 closes predecessor PWV2 governance and starts from one reviewed native PWV3 checkpoint/current obligation; predecessor evidence is provenance until explicitly reaccepted;
- SH0 records host paths qualified for semantic mutation and fences unqualified hosts to handoff/blocker behavior;
- post-QF terminal acceptance has one exact current acceptance-attempt frontier with explicit supersession/no-stale-success fallback;
- ordinary non-OP Review independence is globally owner-waivable by exact durable waiver unless that exact boundary explicitly forbids waiver; OP and QF/SH0 rules remain separate.

These repairs preserve the accepted lifecycle stage set, mandatory OP boundary set, owner-fixed CONTINUE / RUN OP AGAIN gate, supported runtimes, OP/PWV3 ownership split, release qualification ordering, versioning policy, final integration and Close semantics while making the previously under-specified currentness/authority transitions total.

Fresh focused revalidation of revision 8 closed A03-CF02..CF07 and preserved owner decisions OD-01=1A, OD-02=2B and OD-03=3A, but remained RED on one residual incomplete closure of A03-CF01: successor-frontier creation after a positively resolved same-binding recoverable non-advancing terminal result was permissive (`may establish`) rather than deterministic.

Definition revision 9 applies only that residual repair: once the same exact OP obligation remains due and the recoverable blocker/UNKNOWN cause is positively resolved without semantic drift, the owning semantic stage must establish exactly one durable same-binding successor attempt frontier as the sole next routing transition before any redispatch. This preserves the one-current-frontier invariant, immutable predecessor history, UNKNOWN/no-blind-retry rules and current-result-only owner-gate creation.

Revision 9 became GREEN for exact subject workflow-successor-product@4 and remains immutable historical evidence.

Definition revision 10 is a material promoted-scope update for workflow-successor-product@6. It incorporates the accepted R5/R6 product decisions: one portable reviewed Execution Package, invocation-derived execution realization with no user predeclaration, internal Targeted Qualification plus external Global Bug Hunt, the Global CLEAR no-routine-owner-gate exception, automatically executable semantically independent terminal closure, all previously planned later-3.x compatibility/evolution capabilities in 3.0, and the owner-fixed construction handoff in which PWV2 ends after accepted Execution Package Review and implementation runs externally.

Because these changes alter lifecycle, qualification, release scope and construction-governance surfaces, D10 requires a fresh complete independent OP-backed Definition Review. D09 GREEN cannot approve D10. Strategic Planning remains unauthorized until the exact D10 Definition Review obligation reaches applicable advance-permitting acceptance, any required owner disposition is consumed, Definition becomes GREEN and Premium A is satisfied.

The external architecture Research for `elmakus/orchestration-protocol-skill` remains a separate product effort and is not a gate for authoring this Definition, though a compatible production OP capability remains a 3.0 implementation/qualification dependency.

No Strategic Planning or PWV3 implementation is authorized by this draft.
