# Definition — Project Workflow V3 successor product

Status: GREEN  
Subject: `workflow-successor-product@1`  
Definition revision: 1

## Product outcome

Build PWV3 as a clean successor to Project Workflow V2: a deterministic, runtime-neutral workflow for long-lived software/project work that preserves exact durable authority in Git/GitHub, survives fresh contexts and host changes, supports ChatGPT and Pi/Paseo, and remains materially simpler than V2/V2.2.

PWV3 must optimize for reconstructibility, exact evidence, safe continuation and low semantic machinery rather than maximal orchestration features.

## Accepted lifecycle

The semantic lifecycle is:

1. entry/resume health + freshness admission;
2. Brainstorming for genuine owner/product choices;
3. mandatory proportional Research/prior art;
4. Definition;
5. Strategic Planning, with optional Technical Design inside the Plan Package;
6. independent Plan Review;
7. Execution Prep;
8. sequential Project Card execution;
9. Result + proportional Review/revalidation;
10. Final Qualification;
11. one final integration PR;
12. Close from durable target-side evidence.

Named lifecycle steps do not imply a user stop at each stage. Only explicit authorization/independence/blocker/end-of-scope boundaries stop.

## Core authority invariants

- There is one semantic workflow and one legal current/next obligation.
- GitHub remote durable state is canonical across runtimes.
- Runtime/model/session/worker/local-worktree state is never semantic authority.
- One small versioned current/recovery checkpoint stores only non-derivable routing facts and exact pointers.
- Immutable/revisioned artifacts carry semantic history; helper-derived projections do not become parallel authority.
- Exact Git object identity is part of correctness where acceptance, reuse or non-replay depends on it.
- Results are immutable.
- Review attempts are append-only and bind exact subject + exact acceptance surface.
- Canonical publication is freshness-fenced and followed by positive remote readback.
- UNKNOWN semantic/effect state fails closed.

## Planning and execution model

- Plan Package owns strategy, ordered logical work, acceptance coverage, dependencies/material inputs, Review topology and risk/qualification expectations.
- Technical Design is optional and Plan-owned, never a separate lifecycle authority.
- The reviewed Plan may describe logical work slots rather than every final concrete Card.
- Execution Prep materializes the concrete Execution Package and stable Cards as refinements of the exact reviewed Plan.
- Semantics-preserving splits of unstarted logical work do not mutate the reviewed Plan.
- A refinement that changes strategy, scope, acceptance intent, dependency meaning or product outcome returns to the proper semantic owner.
- Exactly one Project Card executes at a time.
- Card identity is stable after materialization; execution order is explicit and total.
- Human-facing initial IDs should reflect planned order; later legal splits use insertion-safe child identity/order rather than renumbering later Cards.
- Dependencies bind exact accepted Results and exist for validation/impact propagation, not runtime scheduling.
- No product-level scheduler, claim system, fan-in state or parallel Card DAG executor is part of PWV3 v1.

## Result, Review and revalidation

A Result records the exact implementation subject, Card/obligation, material input Results, required evidence/readbacks, outcome and producing contract version.

A changed implementation creates a new Result.

Independent Review is required for:
- Plan Review;
- fresh final acceptance;
- implementation surfaces where risk/semantics justify it, including security/trust, migration/evolution, external effects/recovery, shared/public contracts, workflow authority and integration composition.

Ordinary low-risk Cards may complete from deterministic Result/tests/readback without blanket independent Review.

Review reuse is an applicability decision over immutable prior Review evidence; old Review artifacts are never rewritten.

When dependencies/target/acceptance change, revalidate only the provably affected cone. If impact cannot be bounded safely, widen revalidation.

## Recovery and external effects

Recovery reconstructs durable truth; it does not replay chat/session execution.

- Durable Result means the completed semantic obligation is not replayed.
- Local unpublished progress may continue only while the verified remote base is unchanged.
- If remote advanced and local WIP diverges, remote wins; do not automatically merge/rebase/cherry-pick stale semantic work.
- Ordinary WIP publication is not mandatory.
- Before a materially duplicable external effect, exact intent must be durably bound.
- External-effect flow is intent -> attempt -> exact readback -> verified outcome.
- UNKNOWN occurrence never authorizes blind retry.

## Helper and state boundary

The deterministic helper is a stateless executor/projection over explicit canonical inputs, not a workflow engine or second state store.

Expected capabilities include:
- inspect/resume / derive-next;
- validate identities/contracts/dependencies/acceptance;
- classify freshness and local-vs-remote state;
- assemble deterministic context packs;
- derive version/evolution impact;
- guarded publish/checkpoint/readback;
- external-effect reconciliation;
- health query;
- runtime/package doctor/handshake.

Losing helper process/cache must not lose workflow truth.

No helper-local workflow database, scheduler journal, agent registry or durable hidden cache is required.

## Runtime realization

### Pi/Paseo

PWV3 v1 uses one globally managed exact package containing:
- PWV3 skill;
- deterministic helper core;
- thin native Pi typed-tool adapter;
- CLI/debug adapter;
- tiny managed global AGENTS bootstrap.

Paseo owns runtime/child-agent lifecycle; PWV3 owns workflow semantics.

One owner-configured Generic Worker profile is sufficient. Exact assignment envelopes supply bounded roles such as planner-reviewer, reviewer, executor/repairer or evidence worker. Generic Workers do not choose global continuation and do not recursively delegate in v1.

No mandatory MCP/Paseo semantic plugin is required.

### ChatGPT / Android

Default bootstrap is minimal Project Instructions + live GitHub discovery.

Qualified fallback is handoff/locator-only bootstrap + GitHub.

No static PWV3 Project Source is required for v1.

Normal helper path:
bootstrap -> trusted discovery channel -> immutable release/ref -> identity verification -> runtime/contract handshake -> helper execution -> canonical GitHub operation/readback.

Required capability is probed, not inferred from host name. If a write-required obligation lacks the qualified write surface, it must block/handoff rather than fabricate completion.

## Helper implementation default

Planning should prefer a plain ESM JavaScript execution artifact targeting the qualified Node runtime because live ChatGPT/Pi-facing research showed the simplest no-build cross-host path.

TypeScript may be used for authoring if the released execution artifact remains immutable plain JS. This is an implementation default, not semantic authority; Planning may choose another implementation only if later evidence shows a material advantage without violating the Definition.

## Package trust — owner simplification

PWV3 v1 introduces no trust service, PKI, signing hierarchy, trust database or separate credential authority.

Each supported host/bootstrap has one fixed owner-controlled canonical PWV3 package/release origin.

Consumer/workstream state may request/select a compatible PWV3 release within that origin but may not redefine or expand the executable origin.

Moving channel metadata is discovery only. Execution resolves to an immutable Git/release identity and verifies the exact artifact identity/hash.

This is a bootstrap constant plus immutable identity verification, not a new subsystem.

## GitHub Issues and health

GitHub Issues remain bookkeeping/tracker evidence and are not general Definition/Plan/Result/Review authority.

One narrow exception is accepted for PWV3 self-health:

- the canonical PWV3 repository has one reserved confirmed-defect classification, simplest v1 realization being a dedicated label such as `pwv3-confirmed-defect`;
- zero open confirmed-defect Issues => HEALTHY;
- one or more => BLOCKED for ordinary consumer work;
- unreliable query/auth/pagination/identity => UNKNOWN and therefore not healthy;
- a dedicated PWV3 maintenance workstream may proceed to repair the exact blocking defect(s).

No second health database/cache is required.

## Final Qualification

- Freeze one exact Q0 qualification/global-hunt candidate.
- Run risk-driven Targeted Bug Hunt coverage.
- Run exactly one mandatory full Global Bug Hunt on Q0.
- Bug hunts discover findings; they do not vote or accept.
- Deduplicate findings by root cause/trigger/repair obligation while preserving material dissent/provenance.
- Repairs execute sequentially.
- Each repair receives impact-bounded revalidation with broad fallback when uncertainty remains.
- Do not automatically run a second full Global Bug Hunt solely because repairs changed content.
- After all in-scope findings are resolved, freeze the corrected candidate and perform fresh independent final acceptance on that exact subject.

Flaky required evidence is unresolved evidence, not GREEN-by-rerun.

PWV3 v1 readiness requires:
- implementation-independent regression coverage for historical V2/V2.2 failure classes;
- live qualification on ChatGPT and Pi/Paseo;
- one representative PWV3-on-PWV3 dogfood workstream through valid Close.

## Integration and Close

Normal PWV3 integration uses one final PR.

Before merge:
- freeze exact source head, target/base, integrated candidate/tree, final acceptance and required checks;
- refresh source/target/integration context;
- classify target movement by material impact rather than invalidating Review from SHA movement alone;
- satisfy native GitHub base-freshness protection / required checks for the managed path.

Simplest v1 managed integration should prefer merge-commit semantics because exact post-merge identity/readback is clearest. Other merge methods may remain available for unrelated repository work; adding them as managed PWV3 modes later requires method-aware Close proof.

Do not create a second Close/cleanup PR.

Close is derived from:
- durable pre-merge close-ready/terminal evidence;
- verified PR merge;
- verified target containment/integration;
- resolved required effects/tracker evidence.

Source-branch survival/deletion is non-semantic.

## Evolution and cutover

- PWV3 is a clean lineage and does not natively interpret V1/V2/V2.2 state.
- Per-artifact contract versions evolve independently.
- Historical artifacts are read under their producing contracts.
- Compatible PWV3.x roll-forward preserves unaffected evidence and revalidates only materially affected use.
- Helper/runtime/package version is separate from semantic artifact version.
- Moving release channels are discovery only; exact execution uses immutable verified package identity.
- Existing V2/V2.2 work may be migrated only by explicit one-off extract -> validate -> initialize; old lifecycle/Review/Card state is not automatically imported.
- First PWV3 release uses staged bootstrap and PWV3-on-PWV3 dogfood before designation as qualified.

## Explicit v1 exclusions

PWV3 v1 must not require:
- permanent V1/V2/V2.2 compatibility adapters;
- product-level parallel Card scheduling/claims/fan-in;
- cross-runtime lock/lease/takeover machinery;
- separate workflow database/event store;
- LangGraph/Temporal as canonical state;
- mandatory MCP;
- RAG as authority;
- Jev/System-One/formal orchestration core;
- fixed semantic repair-attempt counts;
- stacked workstreams;
- separate OpenSpec lifecycle;
- mandatory continuous WIP publication;
- a second Close PR;
- Gauntlet stage, Gauntlet skill, quality-bar comparator or loop-until-win mechanism.

Gauntlet prior-art remains historical research only and may be reconsidered in a future independent use case without changing PWV3 v1.

## Acceptance obligations for downstream Planning

Strategic Planning must preserve all Definition invariants and produce an executable strategy covering at least:

- checkpoint/artifact schemas and exact authority ownership;
- helper semantic contract and host adapters;
- Pi/Paseo packaging/bootstrap/update path;
- ChatGPT bootstrap/discovery/helper execution and qualified write behavior;
- Generic Worker assignment envelopes and independence boundaries;
- Result/Review/evolution contracts;
- recovery/external-effect safety;
- health/self-repair path;
- regression corpus and live host qualification;
- Final Qualification;
- GitHub freshness/protection/integration/Close;
- staged PWV3 v1 dogfood/cutover.

Planning may choose exact filenames, serialization, helper operation names/schema details, package names, component registration, Project Instructions wording and other implementation representation as long as this Definition is preserved.

## Completeness

Completeness audit: GREEN.

No unresolved owner/product choice remains for this exact scope.

## Authority

Promoted Brainstorming:
`implementation/workstreams/change-workflow-successor-product/BRAINSTORM.toml` subject `workflow-successor-product@1`.

Research return:
`implementation/workstreams/change-workflow-successor-product/RESEARCH.toml`.

Integrated Research:
`elmakus/project-research@research/workflow-successor-v1-integration-g3:projects/project_workflow_v2/successor-product/architecture-v1/FINAL_SYNTHESIS.md`
(blob `18e5e8de80db2fcdbda0e065016457b517b7bfc6`).

Owner Research reconciliation:
`implementation/workstreams/change-workflow-successor-product/evidence/PWV3_RESEARCH_RECONCILIATION_OWNER_2026-09-30.md`.

Final Brainstorming challenge:
`implementation/workstreams/change-workflow-successor-product/evidence/PWV3_BRAINSTORM_FINAL_CHALLENGE_POST_RESEARCH_2026-09-30.md`.

No implementation is authorized by this Definition.
