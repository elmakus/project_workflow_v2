# Definition — Project Workflow V3 successor product

Status: DRAFT / revision-3 bounded repair of RED Definition Review; pending fresh focused revalidation; external OP Skill Research is non-blocking  
Subject: `workflow-successor-product@3`  
Definition revision: 3  
Initial product release: `3.0.0`

## Product outcome

Build PWV3 as a clean successor to Project Workflow V2: a deterministic, runtime-neutral workflow for long-lived software/project work that preserves exact durable authority in Git/GitHub, survives fresh contexts and host changes, supports ChatGPT and Pi/Paseo, and is materially simpler than V2/V2.2.

PWV3 optimizes for reconstructibility, exact evidence, safe continuation and low semantic machinery rather than maximal orchestration.

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
12. Final Qualification, including OP Targeted Bug Hunt and OP Global Bug Hunt;
13. fresh independent final acceptance;
14. one final managed integration path;
15. Close from durable target-side evidence.

Named lifecycle steps do not imply user stops. A stop exists only at genuine owner authority, required fresh-context/runtime boundary, non-remediable blocker, explicit pause or end-of-approved-scope.

Semantic return routing is deterministic. Genuine product-outcome or owner-choice change returns to Brainstorming. Requirement, product-scope or Definition-level acceptance meaning change returns to Definition. Strategy, decomposition or dependency meaning that remains inside the accepted Definition returns to Strategic Planning. Concrete execution-package refinement that preserves the reviewed Plan remains owned by Execution Prep. When multiple classes appear to apply, route to the earliest upstream semantic owner whose accepted meaning must change; no downstream stage may silently absorb an upstream semantic change.

## Orchestration Protocol boundary

Orchestration Protocol is a mandatory normal dependency of PWV3 at:
- Brainstorming Research;
- Definition Review;
- Plan Review;
- Execution Prep / Execution Package Review;
- Final Qualification Targeted Bug Hunt;
- Final Qualification Global Bug Hunt.

PWV3 owns:
- that an OP obligation is due;
- the exact workstream/boundary;
- the exact subject and acceptance/coverage surface;
- the exact durable result identity/type expected from that obligation;
- the durable result applicability check;
- single semantic consumption of an applicable result;
- canonical continuation after consuming the result.

For every OP-backed boundary, wrong-subject, stale, duplicate-as-new, incomplete, unsupported, BLOCKED or otherwise non-applicable evidence fails closed and cannot advance the lifecycle. Re-observing an already consumed exact result after restart is idempotent evidence, not permission to replay the semantic transition. GREEN/accepted evidence permits only the canonical next obligation. RED/repair-required evidence returns to the owning semantic stage; after bounded repair the OP obligation remains unresolved until a compatible applicable OP result establishes acceptance. UNKNOWN/BLOCKED cannot advance. Brainstorming Research additionally binds the exact Brainstorming return owner/obligation and may be reused only when applicability and freshness to that exact subject are proven.

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
- One small versioned current/recovery checkpoint stores only non-derivable routing facts and exact pointers.
- Immutable/revisioned artifacts carry semantic history.
- Exact Git object identity is part of correctness where acceptance, reuse, compatibility or non-replay depends on it.
- Results are immutable.
- Review attempts are append-only and bind exact subject + exact acceptance surface.
- Canonical publication is freshness-fenced and followed by positive remote readback.
- Required semantic independence is based on material authorship/repair of the exact subject, never merely a fresh session/model/runtime.
- An exact-scope owner waiver may waive an independence requirement, but the durable result must record that waiver honestly and must not call the outcome independent GREEN.
- The canonical confirmed-PWV3-defect health predicate is the sole narrow GitHub-Issue-based semantic-authority exception; all other Issue content remains bookkeeping/untrusted input.
- UNKNOWN semantic/effect state fails closed.

## Planning and execution

- Plan Package owns strategy, ordered logical work, acceptance coverage, dependencies/material inputs, risk and qualification expectations.
- Technical Design is optional and Plan-owned, never a separate lifecycle authority.
- The reviewed Plan may contain logical work slots rather than every final concrete Card.
- Execution Prep materializes stable Cards as refinements of the exact reviewed Plan.
- In 3.0, semantics-preserving split/refinement is confined to Plan-slot/Execution-Prep materialization before the concrete execution package is accepted. After Card materialization its identity/history is irreversible and must not be replaced, reused or silently split; genuinely future-dependent post-materialization/JIT refinement is later compatible-evolution scope.
- Semantic changes return according to the deterministic upstream-owner rule above.
- Exactly one Project Card executes at a time.
- Card identity is stable after materialization; execution order is explicit and total.
- Dependencies bind exact accepted Results and exist for validation/impact propagation, not scheduling.
- Before execution, the reviewed Plan/Execution Package must prove that total execution order, material-input dependencies and acceptance/Review gates are jointly satisfiable and cycle-free as semantic constraints; this is validation, not a parallel scheduler.
- Every materialized Card carries an objectively decidable Review obligation fixed by the reviewed Plan/Execution Package or another explicitly named durable authority. Missing or ambiguous Review applicability fails closed rather than being guessed at execution time.
- No product-level parallel Card scheduler, claims/fan-in state or parallel execution DAG is part of PWV3.

## Result, Review and revalidation

A Result records exact implementation subject, obligation/Card, material input Results, required evidence/readbacks, outcome and producing contract version.

Changed implementation creates a new Result.

Independent Review is required where risk/semantic authority warrants it. Low-risk Cards may complete from deterministic Result/tests/readback only when their exact durable Review obligation says independent Review is not required. A context that materially authored or repaired an exact subject is ineligible to independently approve that subject. Fresh context/runtime/model identity alone does not prove independence. An exact-scope owner waiver is allowed only when explicitly authorized and durably recorded, and the resulting outcome is not labeled independent GREEN.

Prior Review evidence is immutable. Reuse is an applicability decision.

Changed dependency, implementation/integration subject, shared contract or acceptance surface invalidates the exact transitive materially affected cone over declared material-input dependencies, acceptance/Review dependencies and relevant shared surfaces. Preserve evidence outside the proven cone. If the cone or impact cannot be bounded safely, widen revalidation to the full potentially affected current acceptance surface rather than assuming narrow applicability.

For OP-backed Plan Review and Execution Package Review:
- one full discovery wave covers the frozen subject;
- findings are integrated before ordinary repair;
- bounded repair is followed by fresh focused independent revalidation;
- another full wave is required only when applicability/coverage assumptions materially fail.

The exact mechanics of discovery breadth, lanes and focused revalidation remain OP Skill responsibility.

## Recovery and external effects

Recovery reconstructs durable truth and does not replay chat/session execution.

- Durable accepted Result suppresses replay.
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
- health;
- runtime/package doctor/handshake.

A missing, denied, unverifiable or incompatible capability required by the current obligation never counts as completion. It yields a durable blocker or a runtime-neutral handoff to a qualified supported runtime, which reconstructs canonical state and re-derives the same obligation before work continues.

No helper-local workflow DB, scheduler journal, agent registry or hidden durable semantic cache.

## Runtime realization

### ChatGPT

- Minimal Project Instructions + live GitHub discovery.
- Qualified locator-only bootstrap fallback.
- No static Project Source required.
- Resolve trusted release origin -> immutable package identity -> handshake -> helper -> canonical GitHub read/write/readback.
- Capabilities are probed rather than inferred.
- Required OP boundaries use the external Orchestration Protocol Skill in ChatGPT.

### Pi/Paseo

- One globally managed exact PWV3 package.
- PWV3 skill + shared helper core + thin typed adapter + CLI/debug + tiny bootstrap.
- Paseo owns runtime/child lifecycle; PWV3 owns semantics.
- Generic Workers may be used for ordinary bounded work where permitted.
- Generic Workers are bounded non-recursive workers in 3.0 and do not spawn/delegate to further Generic Workers.
- Generic Workers/child agents cannot substitute for mandatory OP.
- No mandatory MCP/Paseo semantic plugin.

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
- OP Targeted and Global Bug Hunt;
- fresh independent final acceptance;
- one qualified final integration method;
- target-side Close;
- safe compatible patch adoption within the 3.0.x line.

Before qualified 3.0.0 GA:
- mandatory host-neutral regression corpus is GREEN;
- live ChatGPT qualification is GREEN only when the exact frozen candidate demonstrates every applicable required ChatGPT realization semantic and declared blocker/failure behavior;
- live Pi/Paseo qualification is GREEN only when the exact frozen candidate demonstrates every applicable required Pi/Paseo realization semantic and declared blocker/failure behavior;
- at least one real cross-host continuation is proven;
- Targeted Bug Hunt runs;
- exactly one required full Global Bug Hunt runs on the frozen qualification subject;
- accepted findings are repaired/revalidated;
- representative PWV3-on-PWV3 dogfood reaches valid Close and exercises, at minimum, Research/Definition/Planning, independent Plan Review, Execution Prep, dependent sequential Cards, routine and independently reviewed Results, restart/host transition, guarded external effect/readback, ordinary Final Qualification, Targeted/Global Hunts, repair/revalidation, fresh acceptance, final integration/Close and fresh terminal reconstruction;
- the corrected exact final candidate QF first proves applicability of every required prior qualification item to QF/current acceptance, then receives fresh semantically independent final acceptance under the independence rule above;
- immutable publication/promotion and readback succeed.

An earlier bounded self-hosting cut is allowed only after an exact candidate proves the narrow SH0 safety spine on at least one complete real host path: verified package/helper identity; clean-runtime reconstruction of canonical truth and next obligation; Brainstorming Research/Definition/Planning; independent Plan Review; Execution Prep and sequential Results/Reviews; Recovery/no-replay; safe external effects; health/maintenance gating; Final Qualification semantics; managed final integration/target-side Close; and independent acceptance/readback. Dual-host/full-GA breadth that is not needed to govern continued development may complete after this cut.

## Product versioning and compatibility

Initial product release is `3.0.0`.

- `3.0.x`: bug-fix/maintenance line.
- `3.1.0`, `3.2.0`, ...: compatible product/contract evolution.
- major increment: genuinely breaking semantic/contract boundary that cannot safely preserve or interpret valid prior-lineage work.

Release labels do not prove compatibility.

Every durable artifact kind carries a producing contract version. Product/package version, helper/API contract, artifact contract version and runtime capability are separate axes.

A normal `3.0.x` patch preserves 3.0-line artifact contracts and reads valid earlier 3.0.x history without rewriting immutable Results/Reviews. An active workstream pinned to an exact 3.0.x package/helper identity may explicitly adopt a qualified compatible 3.0.x identity without rewriting immutable semantic history when durable artifact contracts remain compatible. The identity transition is freshness-fenced and positively read back, and prior evidence is reused only after current applicability is established. Richer generalized roll-forward UX/matrices remain later compatible-evolution scope. Invalid state created through an implementation defect may correctly enter Recovery/repair.

If a fix requires a genuinely new compatible durable contract, prefer the next minor release with explicit old+new reader/applicability support.

A genuinely breaking contract/semantic correction requires a major boundary rather than a disguised patch.

No automatic rollback controller. Prefer qualified forward repair. Blind downgrade after writing an unsupported newer contract is forbidden.

## Planned compatible evolution after 3.0

Expected 3.1-class work, only where real 3.0 history makes it useful:
- first real historical readers for changed 3.0 -> 3.1 artifact contracts;
- explicit safe active-workstream adopt-release/roll-forward;
- release/contract compatibility matrix and downgrade refusal;
- semantics-preserving JIT refinement improvements;
- semantic Review reuse optimization;
- richer affected-cone diagnostics;
- richer health/maintenance diagnostics and remediation guidance;
- better doctor/inspect/resume explanations;
- richer deterministic context packs;
- improved Pi/Paseo Generic Worker ergonomics/allow-lists;
- richer GitHub Issue mutation/reconciliation helpers;
- safe anomaly dedup/file-and-continue where evidence proves useful.

Potential later 3.2+ work, only if real use justifies it:
- multi-generation historical readers/conversion support;
- historical-reader retirement/compaction;
- generalized within-PWV3 migration helpers;
- material fingerprint optimization;
- branch cleanup automation.

Rich TUI/web dashboards and additional managed merge-queue/repository-policy product capabilities are outside the current PWV3 roadmap. They may return only through a future concrete owner product decision based on demonstrated need.

These are roadmap candidates, not guaranteed commitments.

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

## PWV2 construction bridge

PWV2 is only a temporary construction harness.

Accepted sequence:
1. this PWV3 Definition becomes accepted product authority;
2. perform bounded PWV2 doctorfix DF-0..DF-4;
3. qualify and freeze exact temporary bridge D0;
4. perform Strategic Planning/construction under that frozen bridge;
5. transfer semantic center of gravity to PWV3 at the bounded self-hosting cut;
6. retire PWV2 from the new-work path after qualified 3.0 promotion.

Do not broadly stabilize PWV2. If bounded doctorfix expands into a predecessor redesign, stop for an explicit OWNER_DECISION. The previously researched one-time bypass/bootstrap authority may be activated only after that owner authorization; the trigger itself does not automatically switch governing authority.

## Acceptance obligations for Planning

Strategic Planning must preserve this Definition and cover at least:
- native PWV3 checkpoint/artifact contracts;
- exact authority and derive-next kernel;
- donor extraction boundaries and non-authoritative provenance metadata;
- regression corpus;
- package/helper identity;
- ChatGPT and Pi/Paseo adapters;
- external OP Skill invocation/result contract and build dependency;
- mandatory OP boundary integration;
- Planning/Execution Package/Result/Review semantics;
- Recovery/external effects;
- versioning/patch adoption/evolution;
- health/maintenance;
- Final Qualification;
- one final integration/Close path;
- bridge -> self-host -> qualified 3.0.0 cutover.

Exact filenames, serialization, helper operation names, API schemas, package names and other representation choices remain Planning/implementation choices unless required by an external stable contract.

## Definition completion

No unresolved owner/product choice remains in this draft.

Definition revision 2 received a complete independent OP-backed review with overall RED and 20 canonical blocking findings. Revision 3 incorporates the bounded repair set without changing the accepted product outcome, lifecycle topology, supported runtimes, mandatory OP boundaries or release strategy. The original full discovery wave therefore remains applicable unless focused revalidation proves otherwise.

Before this Definition becomes GREEN, revision 3 requires fresh independent focused revalidation of the repaired and directly affected neighbor surfaces. A new full Definition Review wave is required only if repair materially changes the product outcome/lifecycle/runtime/OP/release/bridge/acceptance surface, introduces a new owner choice or authority, produces unbounded impact, reveals a materially new defect class, or otherwise invalidates applicability of the revision-2 discovery wave.

The external architecture Research for `elmakus/orchestration-protocol-skill` remains a separate product effort and is not a gate for this Definition revalidation.

No Strategic Planning or PWV3 implementation is authorized by this draft.
