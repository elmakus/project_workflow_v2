# Project Workflow V2 — Master Plan

Plan revision: `PWV2-P2`
Status: `approved`
Date: `2026-09-23`
Definition subject: `project-workflow-v2@R1`
Independent Plan Review: `REQUIRED`
Plan Review record: `planning/reviews/PWV2-P2.md`
Planner-side audit: `planning/audits/PWV2-P2.md`
Control workstream: `feature-common-preexecution-core`
Control branch: `feat/common-preexecution-core`
Implementation destination: `elmakus/project_workflow_v2`

## 1. Authority, scope and current boundary

This is an execution strategy for the accepted V2 Definition, not a new Definition and not permission to implement during the planning session. All packages below are planned work, not executable Task Cards. This revision remains draft until independent review and deterministic approval.

The controlling process is Project Workflow V1, `elmakus/chatgpt-codex-project-workflow` current `main`, resolved for this planning boundary to `7aa7512ead67a86256089d1af0171e2e655e700d`. The selected project policy remains **`chatgpt_only`**. A premium model/context does not change it. V1 supplies recovery, authority handling, planning, review-record ownership and Git handoff mechanics. It does not supply target V2 architecture by inheritance.

The V2 Definition baseline is source-repository commit `8055ed00acdb708c79919d470217fd87c920973a`. Read these exact artifacts at that commit for the accepted target:

| Authority/input | Exact path |
|---|---|
| Approved requirements R1, PWV2-REQ-001..076 | `requirements/PROJECT_WORKFLOW_V2.md` |
| Accepted ADR-PWV2-001 | `decisions/ADR_PROJECT_WORKFLOW_V2_SINGLE_SEMANTIC_CORE.md` |
| Accepted ADR-PWV2-002 | `decisions/ADR_PROJECT_WORKFLOW_V2_DELIVERY_BOOTSTRAP.md` |
| Accepted ADR-PWV2-003 | `decisions/ADR_PROJECT_WORKFLOW_V2_MANAGED_CHANGE_LIFECYCLE.md` |
| Accepted ADR-PWV2-004 | `decisions/ADR_PROJECT_WORKFLOW_V2_EXECUTION_BOUNDARY.md` |
| Accepted ADR-PWV2-005 | `decisions/ADR_PROJECT_WORKFLOW_V2_REVIEW_AND_PREMIUM_PLANNING.md` |
| Accepted ADR-PWV2-006 | `decisions/ADR_PROJECT_WORKFLOW_V2_CONTEXT_RESEARCH_YAGNI.md` |
| Mandatory salvage/regression input | `brainstorming/V1_TO_V2_COVERAGE_MATRIX.md` |
| Mandatory validation input | `brainstorming/V2_VALIDATION_MATRIX.md` |
| Definition GREEN/start boundary | `implementation/workstreams/feature-common-preexecution-core/handoffs/DEFINITION_COMPLETE_2026-09-22.md` |

The manifest selects those six ADRs and requirements. Old root project pointers describe the integrated V1 project; historical exploratory conclusions and V1 experiments cannot overrule the selected V2 Definition. The old exploratory locator can be cleared because Definition completion is durable. No production V2 implementation, Task Board or Cards exist at this boundary.

**PWV2-P2 correction boundary:** P2 preserves the accepted Definition, M01–M04 results and M05-T01..T03 delivery work. It changes only the remaining M05 qualification strategy after user-driven live evidence proved the core ChatGPT control path and package/runtime evidence proved the Codex delivery mechanics. Full L03 final-PR/tracker closure and any still-missing ordinary model-backed L04 completion remain mandatory before first production acceptance in M07; they are no longer hard blockers for the M05 delivery checkpoint. The active M05-T04 Card remains blocked on this replan and must be reconciled by Execution Prep only after P2 is independently reviewed and approved.

**Session completion contract:** planner completeness/challenge audit → freeze this exact draft → separate pending V1 Plan Review record + manifest locator → `premium_stop_B`. The planner must neither perform nor spawn Stage-6 review and must not enter Execution Prep. In the next independent context, GREEN may be consumed into plan approval, but the explicitly accepted premium block requires **`premium_stop_C` before Execution Prep**. A plan-only RED correction creates a new revision and a new B boundary; a Definition-owned contradiction returns to Definition. Material re-entry into Strategic Planning repeats A/B/C. These explicit workstream boundaries constrain the V1 default automatic continuation without changing its execution policy.

## 2. Verified baseline and planning assumptions

- The source workstream is `planning`, Intake is complete, Research and plan-review locators are null, Task Board and plan authority are null. The Definition handoff records GREEN and stop A. This context is the requested continuation from A.
- GitHub readback on 2026-09-22 confirms `elmakus/project_workflow_v2` exists, is private and empty, with no default-branch commit. Its emptiness must be rechecked before initialization; no overwrite is authorized if another actor has populated it.
- V1 already has packaging, hook and branch/review examples. They are prior art only. In particular the V1 Skill invocation uses a different name and its historical live evidence does **not** prove `$pw:project_workflow_v2` works.
- The V1 topology scenarios remain deferred. Neither their synthetic state nor their old `active_execution` fields are a V2 schema template. Preserve the semantic BAD → GOOD and independence/continuation oracles only.
- There is no need for a daemon, database, durable runtime dispatcher, universal event ledger, new MCP server or generic DAG engine. Markdown contracts plus small validated structured records, Git and focused validation/migration utilities satisfy the current scope.

### 2.1 Proportional external evidence check

Checked 2026-09-22. These sources constrain verification order, not accepted product choices:

| Source and weight | Finding / planning consequence |
|---|---|
| [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins), primary platform documentation | The supported Codex compatibility manifest, bundled hooks, package-root paths and hook trust provide a viable packaging direction. Recheck the installed host contract in M01; trust and installed-file readback belong in M05 acceptance. Do not add an updater to V2. |
| [OpenAI skills](https://learn.chatgpt.com/docs/build-skills), primary documentation | Skill metadata and progressive loading are platform concepts. The exact accepted namespaced V2 invocation still needs a real installed-surface test; descriptive docs alone are insufficient. |
| [GitHub Issue/PR linking](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue), primary service documentation | Closing-keyword behavior is tied to the default branch. M04 tests intermediate versus final PRs, including commit-message closing keywords, then reads back actual Issue state. |
| [openai/codex issue 30993](https://github.com/openai/codex/issues/30993), first-person practitioner report in an upstream tracker; not a platform guarantee | Reports stale cached Skill resolution after switching plugin sources. This supplies a practical failure case for M01/M05 source disambiguation and update readback; do not assume it affects the current installation or adopt its workaround blindly. |
| Source baseline `implementation/workstreams/feature-project-workflow-codex-plugin/evidence/M01-T01-runtime-contract-2026-09-20.md`, local historical runtime evidence | Earlier package-root, hook-trust and installation observations justify a small early feasibility probe. They cannot discharge V2 invocation, delivery or portability tests. |

Official/upstream, actual project evidence and community/practitioner evidence from the upstream issue tracker were checked proportionally. No material conflict requiring a new product decision was established. Exact supported packaging syntax, name acceptance and cache/update behavior are M01/M05 empirical checks, not claims of completed acceptance. Any contrary current evidence routes to Research/Definition; never silently rename the accepted Skill.

The deferred scenario inputs are the three exact baseline files `brainstorming/live-tests/ORCHESTRATION_TOPOLOGY_N_AUTHORITY.md`, `brainstorming/live-tests/ORCHESTRATION_TOPOLOGY_N_CAPABLE.md` and `brainstorming/live-tests/ORCHESTRATION_TOPOLOGY_N_CHATGPT.md`. Their target semantics are selected by the accepted validation matrix. Preserve their oracles, not their V1 harness/runtime wrappers. The optional fork algorithm is salvage evidence from `workflow/common/FORK_RELEASE_VERSIONING.md` at the controlling-main commit above, only within the accepted matrix's trigger-only disposition.

## 3. Target shape and complexity limits

V2 is one semantic workflow at `workflow/`. ChatGPT reads it from the V2 GitHub repository; Codex reads the same bytes delivered in an installed `pw` package. Neither runtime identity nor delivery-source identity selects workflow semantics in project state. One workstream can move between runtimes at a durable boundary unchanged.

The proposed repository layout is an implementation starting point; names not fixed by Definition may be refined within L1/L2. Ownership, boundaries and acceptance below are fixed by this plan. Create a file only when its milestone needs it.

```text
workflow/
  ROUTER.md                  small common obligation selector
  AUTHORITY.md               authority domains + global proportionality
  STATE.md                   owners, bindings and legal durable transitions
  WORKSTREAMS.md             branch identity, dependency and terminal package
  INTAKE.md                  managed intent, diagnosis and tracker entry
  BRAINSTORMING.md           intrinsic adaptive grilling + promotion
  RESEARCH.md                source breadth/weight + exact return ownership
  DEFINITION.md              accepted intent and completion
  PLANNING.md                strategy/coverage + premium window
  PLAN_REVIEW.md             fresh exact-plan review exception
  EXECUTION_PREP.md          bounded Cards + predecessor-driven JIT
  EXECUTION.md               serial Card, delegation, reconciliation
  REVIEW.md                  common implementation/integration attempts
  CLOSE.md                   refresh, integration, publication, cleanup
  RECOVERY.md                exact durable obligation recovery
  USER_STOP.md               real stops + locator-only handoffs
  TECHNICAL_CONTRACT.md      loaded only for a material extra contract
  GITHUB_ISSUES.md           loaded for supported tracker operations
  FORK_RELEASE_VERSIONING.md loaded only on declared fork release trigger
templates/                  small artifact templates, instantiated JIT
schemas/                    workstream, board, review and related validation
skills/project_workflow_v2/SKILL.md
.codex-plugin/plugin.json   pw compatibility packaging, subject to M01 probe
.agents/plugins/marketplace.json
hooks/hooks.json
hooks/session-start.py      bounded installed-root bootstrap only
prompts/CHATGPT_PROJECT_INSTRUCTIONS.md
prompts/CHATGPT_FRESH_SESSION.md
tests/                      deterministic contract/scenario/integration tests
tools/                      only needed validation and migration helpers
migration/                  bounded V1 readers/fixtures/instructions
docs/                       installation, adoption and maintained user guidance
README.md
```

`requirements/`, `decisions/`, `planning/` and `implementation/workstreams/` hold this product's own authority/history only according to the custody boundary in §4. Consumer project state stays in each consumer's repository. Fixtures are clearly test data and are never selected as active state. A plugin package includes canonical `workflow/` directly; there is no second `skills/.../references/` policy copy. If distribution requires a build artifact, it is a deterministic byte-preserving package verified against canonical files, not a second editable tree.

No separate runtime-policy directories, redundant `workflow/v2/`, root live Task Board, runtime registry, Card scheduler, policy-selection field, context-health lifecycle, plugin updater, telemetry database or per-project workflow patch pin is planned. Test utilities do not become an autonomous execution engine. Ordinary semantic changes touch canonical modules; bootstrap files change only when bootstrap behavior changes. The optional fork module does not make the new V2 repository itself a downstream fork.

### 3.1 Durable ownership and schema envelope

M01 settles the minimum interoperable envelope before downstream modules. Later milestones extend only their owned fields with valid fixtures and explicit compatibility checks; this plan does not freeze a speculative full JSON/YAML API.

| Artifact/owner | Semantic contents and exclusions | First useful slice |
|---|---|---|
| Consumer `PROJECT.md` | Common V2 marker (conceptually `project_workflow: v2`), identity, repository, high-level authority/navigation, workstream-root convention. No live Card/phase registry, runtime selector, policy or installed plugin path. | M01 |
| Selected workstream manifest | Stable ID/kind, original branch, exact creation base, final target, genuine parent dependency/provenance; exact Intake/Research/plan-review/board/authority locators; tracker correlation; workstream integration/cleanup ownership. Pointed artifacts own their contents and lifecycle. | Binding M01; owning slices M02/M04 |
| Intake/Brainstorming record | Exact scope/revision, diagnosis and intended repair, material decisions, unresolved questions, explicit alignment/promotion evidence sufficient for restart. A reply asking about safety is not acceptance. No raw chat transcript requirement. | M02 |
| Research record | Question, origin/subject, source classes/weight, finding/limits, exact return target and durable reconciliation result. Final target consumes findings once; interruption must not cause a new plan/Card/result merely to clear a pointer. | M02; execution returns M03 |
| Definition and Master Plan | Accepted requirements/ADRs; revisioned plan with milestone outcomes, coverage, JIT triggers and gates. Plan lifecycle/review record separate from reviewed body. | M02 |
| Selected Task Board | Binding to manifest identity/original branch; current milestone, serial Card status, result/evidence, review references, execution Research/blocker pointers and cumulative checkpoint. Main is the sole reconciler of shared execution state. | M01 envelope; M03 transitions |
| Stable Task Card | Bounded scope/non-scope, exact authority/dependencies, acceptance/tests, required evidence and external/readback/review obligations; optional technical-contract ref. No mutable worker/status mirror. | M03 |
| Review record/attempt | Exact immutable subject AND acceptance surface; classification, semantic independence proof, verdict/evidence, append-only attempts for new subjects/verdicts. Board locates Card/milestone review; manifest locates final review; plan record owns plan review. Never duplicate the active verdict in competing owners. | M01 identity; M02/M03 lifecycle |
| Checkpoint/handoff | Minimal cumulative accepted results, outstanding obligation and exact refs, workstream-local collision-free path. Exists when checkpoint adds recovery value even if continuation is immediate. | M03/M04 |
| External-effect evidence | Intended operation, exact affected object/content and expected state, readback/proof and uncertainty if unresolved. Owned by affected obligation; no universal action ledger. Secrets excluded. | M01 envelope; M02/M04 operations |
| Terminal/cleanup package | Authority/board/contract/review/result/evidence refs needed without source branch; exact integration result and optional surviving-ref safe-delete proof. Original branch remains provenance. | M04 |

Choose the smallest standard serialization/schema toolchain in M01 (prefer existing interpreter/standard validation facilities; add a schema library only for demonstrated checks). Runtime invocations, worker/model/session IDs, scheduling lanes and ordinary `returned`/`transfer_ready`/`active_execution` are prohibited in new canonical state. Historical migration fixtures may contain them solely as input. Semantic evidence that a reviewer did not produce the subject is required even though runtime telemetry is not canonical.

### 3.2 Router and progressive disclosure

Use one small obligation selector, with owning modules carrying detailed transitions. Freeze the precedence needed for correctness, not a general orchestration engine:

1. Resolve project contract and exact requested workstream/entry. A new `#issue`/`#feature` or new managed intent routes to Intake instead of adopting an unrelated active board. Read-only exploration does not manufacture a workstream.
2. Validate selected manifest/locator class and binding before trusting mutable state. Inconsistent or ambiguous identity routes to Recovery, never fallback to a global/default board. Terminal entry resolves exact target-side package plus merge/closure evidence.
3. Honor explicit user stop, due accepted authorization/alignment/promotion gates and premium A/B/C. Recovery cannot consume a human gate without its exact authorized entry/response. No durable model identity or new context-health gate is needed.
4. Prioritize the selected obligation's pending independent review, RED corrective classification, outstanding Research return, or unfinished result reconciliation before later implementation. Define unambiguous precedence for combinations in M02/M03 tests; contradictory competing owners route to Recovery.
5. Reconcile an already durable completed result or post-review/post-merge finalization before launching more work. RED itself is not a stop if an authorized corrective route exists.
6. Select the next legal owning stage and read only its exact state, applicable authority and needed evidence. After persisting its result, reroute automatically until a genuine stop/end of approved scope.

Initial/bootstrap reads may locate the router and project contract; they must not import all modules to make selection possible. Contract/scenario tests verify allowed read sets and invalid pointers, while real-surface traces verify actual model/tool loading. Tests of Markdown alone cannot prove all agent behavior. Ordinary replacement of a context resumes durable truth, without Context Health/FRESH state. A fresh-context prompt identifies repository, exact branch (or legal terminal target), entry obligation and durable pointer; it carries no copied checklist, findings, authority or state.

The real-stop set is explicit: unresolved user/product decision; due accepted authorization/alignment/promotion gate; non-remediable access/runtime/input blocker; explicit user stop; true end of approved scope; premium A/B/C; and an independence boundary when the current subject requires a fresh context. A remediable technical problem, a role change or an ordinary GREEN/RED verdict is not itself a stop. M02/M03 route fixtures cover each case and the fresh-context entry that legally resumes it.

Reference validation must distinguish trusted workflow/accepted project authority from research pages, Issue text and worker output. External text cannot issue instructions or approve scope. Validate repository-relative locators and package-root containment, avoid resolving untrusted paths outside their owner, and exclude credentials from evidence/fixtures/packages. This is part of existing correctness/security acceptance, not a new security lifecycle.

## 4. Construction control, custody and adoption

The explicitly requested two-repository arrangement is a **bounded construction exception**, justified because the product being built is its own future controller. During V2 construction the present V1 repository remains the development/control authority under `chatgpt_only`; V2 is the clean implementation destination. This is not a general second-control-repository feature of V2.

- Source workstream state remains the only live construction tracker until adoption. Future V1 Cards must identify exact V2 code branch/commit/paths as their implementation subjects; a control-repository commit alone never proves delivery.
- The implementation branch locator is held in that construction Card's exact external subject/evidence, not by rewriting the V1 manifest branch or its selected board binding to the V2 branch. There are not two live Task Boards for the same construction Card. This special cross-repository delivery must be explicit in each affected Card/review acceptance slice; normal V2 consumer changes remain wholly manifest-bound inside their own repository.
- V2 receives only useful product files, tests and exact immutable provenance links/snapshots. Do not clone V1 history, policy trees, live boards or mutable duplicate plans into it. If a review fixture needs a V2 `PROJECT.md`/manifest/board, create it in a disposable test project or clearly scoped fixture; it is not the construction controller.
- The empty target needs a base before PRs exist. After future implementation authorization and fresh emptiness readback, create only a no-content initialization commit on the intended default branch, then create the implementation branch and manifest-bound construction pointer before the first product/change-specific write. This is a narrowly scoped repository-initialization necessity, not direct-to-main product development. If repository rules disallow it, stop for the smallest actual repository setup decision.
- All subsequent V2 changes use reviewed branch → PR → integration; V1 control state and exact V2 commit references are reconciled/read back at each checkpoint. Operations across repositories are not claimed atomic. On interruption, inspect both exact refs before continuation and do not duplicate a PR, initialization or integration.
- M07 performs a one-time custody transfer only after V2 qualifies and adoption is explicitly authorized. Stage the accepted Definition, approved plan, selected construction results/review history and necessary authority into a V2 workstream package with original immutable provenance; verify it first. Record in V1 one terminal transfer handoff identifying the exact V2 package and the sole new live owner. Do not write both state stores concurrently.
- If transfer is interrupted or ownership is ambiguous, hold subsequent mutations and recover from the transfer handoff plus exact readback; do not guess the live owner. Keep the V1 source as immutable development/history evidence after transfer, not a second mutable control plane.

This session only plans that procedure and writes the source planning handoff. It does not initialize the new repo, install a plugin, change Project Instructions, migrate consumer projects or authorize production adoption. Future V1 execution remains `chatgpt_only` until the explicit adoption boundary retires that controller; V2 adoption is use of the new common contract, not selection of `codex_only`/`mixed`.

## 5. Milestones and executable work-package order

Dependencies are **M01 → M02 → M03 → M04**, then **M05** delivery qualification and **M06** migration rehearsal, then **M07** full-system acceptance/adoption. M05 package design uses an early M01 feasibility check to avoid a late architectural surprise. M06 reader analysis can use settled M01 schemas, but its accepted migration output requires M02–M04 transitions. These are dependency opportunities, not authorization for concurrent Project Cards. Execution Prep serializes Cards; runtime-internal work inside one Card may be concurrent.

At every milestone: acceptance uses exact delivered V2 subject and applicable authority, affected automated tests pass, required review is GREEN, and a durable checkpoint records actual results/outstanding limitations. An incomplete/live-test-blocked milestone is not GREEN. Source changes cannot silently widen Definition or the authorization scope.

### M01 — Clean foundation, durable envelope and early delivery feasibility

**Outcome:** one coherent common core can bind a project/workstream, reject invalid state and identify its next obligation without runtime selection. A real packaging probe has retired the highest-risk naming/root assumptions before full module construction.

**Dependencies:** approved PWV2 plan, completed premium C, future implementation authorization; revalidated target baseline (§4). Inherits ADR-001/002/003/004/006.

**Packages:**

- **M01.P1 — Clean repo and custody baseline.** Apply §4, establish minimal README/layout/test command/CI and exact source authority pointers. Preserve private visibility. No copied V1 bootstrap or entire repository; new product work occurs on an implementation branch.
- **M01.P2 — Authority/state/router minimum.** Implement §3 owner boundaries, common marker, manifest/board binding, exact reference validation, single-Card invariant, semantic-only review identity and external-result envelope. Create project/workstream/board/review skeleton templates and valid/invalid fixtures. Router skeleton routes only implemented obligations; an unimplemented route is explicitly unavailable, never guessed or advertised as production-ready.
- **M01.P3 — Early package compatibility probe.** Use an isolated installation/test project to verify plugin `pw`, Skill `project_workflow_v2`, exact `$pw:project_workflow_v2`, installed root containing sibling canonical `workflow/`, and supported SessionStart/trust discovery. Preserve the accepted names. Failed exact invocation or unavailable needed platform contract creates bounded Research/Definition evidence before dependent packaging proceeds. Do not change the user's live plugin or install a parallel `pw` globally during a probe.
- **M01.P4 — Test foundation.** Add deterministic schema/binding/route fixtures and checks that positive production paths cannot select V1 policy fields, runtime identity or scheduler state. Cover actual parsed fixtures, not only textual substring checks. Adopt small read-only validation helpers; no new execution service.

**Checkpoint / acceptance:** A01/A02/A03/A04 foundations GREEN; valid same-state fixtures select the same semantic route regardless of realization; malformed/missing/cross-workstream locators fail closed; project templates do not contain prohibited fields. Record exact package/invocation proof or a real unresolved blocker. V2 remains a development slice, not adopted.

**JIT:** choose schema syntax, helper language and minimal supported packaging representation using actual host evidence. Review/runtime state field names may be refined while retaining settled owners. Do not implement all downstream fields merely to fill an empty template. Primary requirement ownership is listed in Appendix A.

### M02 — Intake through Definition and premium planning

**Outcome:** the common discovery/authority path is usable and cannot turn a symptom-only issue into implementation. Material planning and its independent review reach A/B/C exactly.

**Dependencies:** M01 envelope/router and identity tests. Inherits ADR-003/005/006; no target changes to accepted Definition.

**Packages:**

- **M02.P1 — Intake and human alignment.** Implement exact recovery/dedup, `#feature` discovery, neutral managed changes and read-only `#issue` diagnosis. Establish branch/workstream before durable change-specific records; Intake/tracker bookkeeping is distinguishable from implementation mutation. Present diagnosis, intended outcome, material safety/side effects and recommendation. A subsequent user response is necessary but not by itself sufficient: a question, concern or alternate outcome continues Brainstorming; persist explicit aligned repair authorization before implementation. Changed repair scope invalidates stale alignment. Qualified micro-fix is selected only after this gate and retains bounded Card/tests/review; no fabricated full milestone or plan.
- **M02.P2 — Adaptive Brainstorming/Research/Definition.** Implement thematic numbered recommendations, agent-owned fact gathering, material-value continuation, explicit user stop and final challenge audit; no `#grill`. Preserve explicit promotion of an exact exploratory revision to Definition. Research records source classes, weights/conflicts, exact origin/return and single-consumption reconciliation; no popularity-as-authority. Keep optional open-question/support/prototype artifacts proportional. Definition produces approved requirement/ADR authority with a GREEN completeness criterion and stop A.
- **M02.P3 — Planning and Stage-6 exception.** Implement plan revisions, coverage, planner audit, immutable draft freeze and separate plan-review lifecycle. A: recommend best available context. B: require fresh independent best-context reviewer, never internal spawn by planner. GREEN is consumed into approval and C is persisted before Execution Prep; recommend a lighter/cheaper context. Re-entry cannot loop or bypass stops. Material replans repeat A/B/C; editorial-only changes and aligned micro-fixes have their accepted bounded exemptions.
- **M02.P4 — GitHub tracker opening/correlation.** Implement a small capability-aware operation contract using available connector/CLI; no custom bot/server. Discover an exact existing Issue/workstream before creating anything. Persist repository + Issue identity and workstream/PR references, read back writes and reconnect after interruption. Tracker capability absence is recorded honestly and does not turn the Issue into authority or silently authorize repair. Ambiguous duplicate matches require bounded recovery, never create another tracker to escape ambiguity.

**Checkpoint / acceptance:** A13/A14 plus extended input/premium fixtures GREEN. Test initial symptom only, safety-question reply, explicit agreement, changed diagnosis, stale alignment and fresh restart; no implementation route before aligned authorization. Test Research return interrupted before/after application; no double consumption. Test fresh reviewer entry and premium-stop re-entry, material replan, editorial exemption and micro-fix path. Stage-relevant templates are present; no templates are blanket-loaded.

**JIT:** exact connector operation syntax/permissions from the enabled GitHub surface, repair evidence sufficient for the current symptom, optional Research prototype branches only when an actual comparison requires them. UI proof waits for M05/M07; deterministic gate validation does not require manual driving.

### M03 — JIT execution, delegated results and common independent review

**Outcome:** one bounded Card can be prepared, implemented, reviewed/corrected and finalized with portable state, including interrupted delegated work and the two allowed review topologies.

**Dependencies:** M01 state and M02 authority/Research/gates. Inherits ADR-004/005/006.

**Packages:**

- **M03.P1 — Cards/JIT/technical contracts.** Materialize all currently well-defined useful Cards; retain predecessor-dependent triggers rather than placeholders. Stable Card contains complete authority slice, scope, acceptance/tests and readback/review obligations. READY depends on authority/prerequisites, not whether a worker currently exists. Launch refresh rereads exact state/authority/dependencies/result and prevents stale work. L1/L2 changes may refine unstarted Cards only within approved scope; strategy → Planning, product/global intent → Definition, missing facts → Research. Technical-contract/OpenSpec module is loaded only when it materially adds cross-component behavior/API/schema/idempotency/security/migration detail; simple Card-only case remains rigorous. OpenSpec never replaces Definition, plan or Card.
- **M03.P2 — Implementation and reconciliation.** Exactly one Card in progress in the selected workstream. Determine qualifying delegation from available capability, bounded authority/context access and a valid return path; when available Main delegates substantive implementation/debugging/testing and keeps state/authority/routing/validation/integration responsibility. Internal multiple workers must not mutate shared board/manifest or create additional Cards. Main normalizes and validates returned evidence. A bad result with still-valid contract stays in progress for correction; only a real blocker becomes blocked. Without genuine delegation capability the same common contract permits direct implementation.
- **M03.P3 — Exact-subject common review.** Implement REQUIRED and activated RECOMMENDED gates, exact immutable content plus acceptance identity, semantic independence qualification and durable evidence. Append new attempts for changed subject/verdict; completed RED/GREEN history never mutates into another subject. Capability-first independent implementation/final review may continue internally when a qualifying context exists; if the current context produced the subject and cannot obtain an independent context, freeze and emit locator-only fresh-review handoff. Stage-6 premium review is the deliberate exception. Record stronger exact coverage only after final refresh; normal behavior work retains final integration review unless coverage is complete.
- **M03.P4 — Recovery/continuation proof.** Reconcile a durable completed result before replay; normalize semantic evidence without worker IDs. Recheck exact result/subject before terminal finalization. Classify RED into bounded correction, planning, Definition, Research or real stop. Returning from review/correction is not itself a stop. Implement durable checkpoints and proportional blocker/evidence templates.

**Checkpoint / acceptance:** A04/A05/A07/A11/A12 GREEN, plus route combinations, stale subject, duplicated result, invalid independence and no-capability fixtures. Tests cover internal worker concurrency while one Card remains active and Main retains sole state ownership. Automated N semantic traces prove expected transitions; **they do not substitute for L08/L09**. Risk-based review frequency is proportional, with required gates never weakened and final integration coverage mandatory.

**JIT:** first real predecessor result determines concrete Card boundaries and optional contracts. No runtime role catalog, model preference, worker adapter API or persisted invocation schema is added. Review serialization is chosen to make immutable-subject/history validation straightforward, not to reproduce the V1 wrappers.

### M04 — Integration, tracker closure, publication and terminal recovery

**Outcome:** a workstream can close safely against a moving target, with external effect readback and recovery independent of the source branch.

**Dependencies:** M03 result/review semantics and M02 tracker references. Inherits ADR-003/005 plus accepted Stage-10 requirements.

**Packages:**

- **M04.P1 — Refresh before review reuse and integration.** Compare current target and exact covered subject/acceptance; perform the smallest authorized reconciliation and affected semantic/compatibility verification. SHA/ancestry-only movement may retain GREEN if unchanged content/behavior/acceptance and compatibility are proven. Material change freezes a new subject/attempt; the correcting context cannot review it. Refresh precedes first final-review freeze/reuse, and reread target immediately before the actual mutation when it can move. Clean textual merge alone is insufficient.
- **M04.P2 — External effects and final tracker lifecycle.** For merge/publication/Issue changes follow write → readback → expected-state verification → evidence. On timeout/unknown occurrence inspect the exact external object before any retry; if still uncertain stop that action. Intermediate PRs/commits reference the tracker without closing keywords or closing linkage; final scope-completing default-branch PR may close it. Read back Issue state after accepted completion; explicit closure only when automatic closure did not occur and the whole accepted scope is durably complete. Unexpected closure before completion is reconciliation evidence, never approval.
- **M04.P3 — Target-side closure and cleanup.** Put every unique knowable recovery artifact in the merge subject before merge. Recover merge-result-dependent bookkeeping from target package and immutable PR/merge evidence even if GitHub deleted the head immediately; never recreate the source just for bookkeeping. Preserve original branch/base/parent provenance. Final readback verifies refs resolve independently. For surviving safe refs use minimal `safe_to_delete` only when needed, exact current-head revalidation before deletion, absence readback afterward. Terminal unmerged/superseded closure preserves recovery-only artifacts independently without importing rejected implementation. Stacked children either fold into parent or integrate after proof the genuine dependency is accepted in target; no parent branch survival assumption.
- **M04.P4 — Optional fork publication and end of scope.** Implement trigger-only lineage rules for durably declared downstream fork releases: accepted upstream repo/tag/SHA, baseline-local numeric `private.N`, canonical cross-baseline numeric ordering, immutable historical releases, native optional latest alias pointing to the same accepted stable artifact, quality separate from lineage. No ordinary non-fork loading, no synthetic `vlatest`, no automatic sync/tag/deploy authorization. Close reports completed scope and stops without inventing follow-up work. Deployment/live-write alone never adds a human gate; an explicit accepted authorization boundary still does.

**Checkpoint / acceptance:** A06/A08/A09/A10/A16 GREEN. Use disposable Git repos and controlled external-operation fixtures to test target races, semantic conflicts, stronger-coverage reuse, immediate head deletion, surviving-head movement, unmerged closure, both stacked paths and interrupted writes. Final Issue closure oracle is ready for L03. Repeated close/recovery must produce no duplicate external action and no lost unique evidence.

**JIT:** current target movement determines the affected checks; actual supported publication surface determines readback. Fork helper details activate only for a declared fork-version operation. Broader integration-intent changes escalate instead of being hidden in reconciliation.

### M05 — Thin ChatGPT/Codex delivery with verified update propagation

**Outcome:** both supported products enter the same finished semantics through their intended thin delivery surface.

**Dependencies:** M01 compatibility proof and M02–M04 modules. Inherits ADR-002/006; external `newproject-skill` retains provisioning responsibility.

**Packages:**

- **M05.P1 — ChatGPT bootstrap and prompts.** Provide minimal user-owned Project Instructions template for the V2 repository and common router; entry recovers the consumer's repository and exact workstream. Provide locator-only fresh-gate prompt. A start prompt is optional convenience, not a policy copy. Explain actual required access without requiring a second project store.
- **M05.P2 — Codex package.** Package canonical `workflow/` directly with `pw` + `project_workflow_v2`; Skill and SessionStart locate local installed root and router only. Verify package contents/path containment, malformed/missing root/router failure, expected startup/resume/compaction behavior and normal hook trust. Missing bundled authority fails closed; no remote workflow fetch or memory reconstruction. Avoid duplicate V1/V2 `pw` activation and source ambiguity in the test environment. Runtime compaction support does not create a V2 Context Health lifecycle.
- **M05.P3 — Semantic update readback.** Use an isolated candidate distribution and one harmless observable canonical module change; retain unchanged Skill/hook/bootstrap hashes, update via the supported external installer, start a fresh session and read back installed module bytes and observed behavior. Record source/version/hash in package test evidence, not canonical project execution state. No project patch pin, update daemon or alternate semantic route is introduced.
- **M05.P4 — Real surface checkpoints.** At M05, require enough real-surface evidence to prove each delivery surface and the highest-risk human-control/runtime boundaries without forcing full end-to-end repetition. ChatGPT live qualification requires L01 GREEN, L02 human-control GREEN, and continuation of the same issue flow through blocker recovery, implementation, required-review freeze and the fresh-independence stop. The final PR/default-branch tracker-close portion of L03 remains a mandatory M07/first-production acceptance obligation. Codex M05 qualification uses the real installed CLI/package evidence for exact `$pw:project_workflow_v2` resolution, bundled local router authority, thin Skill/hook, missing-router fail-closed/no-V1 behavior and the supported update/readback path; an additional ordinary model-backed completion is not an M05 blocker when that package/runtime evidence is already exact. Any still-missing full model-backed L04 completion remains mandatory before first production acceptance in M07. Reuse exact evidence only with an explicit compatibility assessment after later semantic edits.

**Checkpoint / acceptance:** A01/A02/A17 package/context regression stays GREEN; L01 and L02 are GREEN on the real ChatGPT surface; the combined L02/L03 issue flow has demonstrated durable recovery from a real input blocker, implementation with GREEN regression tests, and correct stop at a required independent-review boundary; Codex delivery has exact installed-package/CLI evidence for explicit Skill resolution, bundled local authority, thin bootstrap, missing-router/no-V1 fail-closed behavior, plus L05 supported update/readback GREEN. Full L03 final integration/tracker closure and any still-missing ordinary model-backed L04 completion are deferred, not waived: both remain mandatory before first production acceptance in M07. Later semantic edits require affected regression plus a documented compatibility assessment for retained evidence.

**JIT:** supported installer command/manifest details, hook trust setup, package version and observed read traces. Do not freeze those from old V1 evidence. If exact accepted invocation cannot work, return to Definition; do not silently substitute hyphens, another namespace or another Skill.

Update lag is handled by an explicit supported package update and readback at delivery/portability checkpoints, not a per-operation remote policy comparison. Ordinary Codex entry must not fetch remote workflow policy. If the installed contract cannot safely read a project's current schema/obligation, fail closed with the concrete compatibility evidence; do not convert state, silently select V1 or introduce a permanent version-negotiation service. Compatible updates preserve existing durable obligations and immutable review subjects.

### M06 — Bounded V1 migration and cutover rehearsal

**Outcome:** supported V1 states migrate once into valid common V2 state without losing authority/results/review/authorization or retaining live legacy routes.

**Dependencies:** M01–M04 settled ownership/transition contracts; M05 delivery available for a rehearsal. Inherits ADR-001/003/004/005/006 and migration/non-goal requirements.

**Packages:**

- **M06.P1 — Bounded input readers and dry run.** Inventory representative V1 `chatgpt_only`, `codex_only` and legacy/mixed-shaped states as migration input only; support a documented finite set of recognized shapes. Preserve immutable source refs and original artifacts. Dry run reports exact destination, mapping, outstanding obligations and unsupported/ambiguous fields; it makes no live mutation. Historical root state is never a V2 live destination.
- **M06.P2 — Safe conversion.** Map accepted authority, stable Card scope, branch/base/parent/target identity, unresolved Research/authorization, results and exact review history to common owners. Remove runtime binding/policy/scheduler fields from output; removal must not erase semantic review independence or pending effects. A V1 ordinary returned result becomes a result to reconcile, not a new V2 state. Concurrent V1 Cards must first be durably quiesced/serialized under the V1 controller; migration must not choose a winner or mark the others done. Missing exact review subject/independence proof blocks relying on that verdict and creates a review obligation, not invented evidence.
- **M06.P3 — Apply/readback/restart.** Apply only after dry-run validity and explicit migration/adoption authorization for the selected project. Use exact source identity and destination readback so repeated apply either proves the same result/no-op or reports conflicting divergence. Test crash points before/after record, ref and external-write reconciliation. Preserve source recovery independently and support rollback of unactivated changes without rewriting published history.
- **M06.P4 — Rehearsal and documentation.** Rehearse on disposable cloned fixtures; document supported input boundaries, blocked cases, rollback/forward-repair choices and the one-live-owner transfer. Consumers never load V1 readers during ordinary V2 routing. Preserve historical metadata as read-only provenance outside normal semantic routes; no permanent V1 interpreter or dual-write compatibility layer.

**Checkpoint / acceptance:** A15 plus A02/A03/A05/A06/A07/A10/A17 migration regressions GREEN. Fixture set includes pre-execution promotion/Research/plan review at A/B/C-equivalent obligations, active/in-progress/result-complete Card, pending/RED/GREEN review, stacked work, terminal deleted-source and terminal unmerged state. Unknown schema, ambiguous authorization/subject, racing source, parallel-active inputs and unresolved effects fail closed. Repeated conversion is idempotent and preserves all outstanding semantic obligations. Real-project migration is optional if fixtures suffice; production adoption is still M07-gated.

**JIT:** select exact supported V1 schema variants from real samples, not hypothetical backward compatibility. A discovered unhandled semantic obligation returns to its authority owner before migration. No migration machinery is imported into `workflow/` beyond an exact bounded entry pointer for a requested migration.

### M07 — System qualification and first production-ready adoption

**Outcome:** a pinned acceptance candidate satisfies all R1 requirements, salvage dispositions and validation scenarios, with demonstrated portability and safe adoption/rollback.

**Dependencies:** M01–M06 checkpoints, L01–L05 evidence applicable to final candidate, explicit real-surface access. Inherits every accepted ADR/invariant.

**Packages:**

- **M07.P1 — Full automated qualification.** Reconcile Appendix A and B with implemented artifacts/evidence; run all A01–A17 and supplemental gate/ownership/authorization cases. Every requirement has actual acceptance evidence, not just a plan link. Validate negative/drop assertions semantically with fixtures/read-sets as well as static checks. Review the exact final content/acceptance surface independently after refresh.
- **M07.P2 — Cross-runtime and premium live proof.** Run L06 ChatGPT → Codex → ChatGPT without state conversion, retaining the same obligation/review and reusing completed results. Run L07 on actual V2 model/context switching, including recovery at A/B/C; no current model name becomes workflow authority. Reuse existing live sequence only where it actually exercises those boundaries.
- **M07.P3 — Deferred topology live proof.** Execute L08 N-CAPABLE on actual V2: one capable invocation independently REDs S1, delegates bounded S2 correction when capable, obtains independent GREEN on S2 and finalizes without an artificial stop. Execute L09 N-CHATGPT: fresh reviewer RED → same-chat authorized correction → freeze S2 → stop only for new independence; next fresh reviewer GREEN → same-chat finalization. Exact oracle is `topology-n: BAD\n` rejected then `topology-n: GOOD\n` accepted. Use clean V2 test-project entry and V2 state; never wrap with production V1 routing or transplant the old harness schema. No planner Stage-6 review is confused with these Stage-9 scenarios.
- **M07.P4 — Controlled adoption.** Apply §8 acceptance/cutover, immutable release/package identity and user-owned bootstrap adoption. Complete the construction custody transfer (§4), then adopt only the specifically authorized pilot project(s) at safe durable boundaries. Verify production-source/package readback and locator recovery; retain exact rollback inputs. Wider rollout is separate scope, not automatic follow-up work.

**Checkpoint / acceptance:** all mandatory A01–A17 and L01–L09 GREEN with exact subjects, provenance and applicable readback; no missing acceptance for PWV2-REQ-001..076; final independent integration review GREEN or exact stronger complete coverage; no unresolved semantic blocker/P0/P1 defect; approved adoption gates satisfied. A blocked live test blocks first production acceptance instead of becoming an unearned waiver. Finish scope durably; do not synthesize new features.

**JIT:** concrete live fixtures, eligible actual independent/delegated contexts and harmless test changes depend on implemented candidate and available surfaces. A missing capable topology means L08 remains blocked, not replaced by another no-capability test. Record product versions in test observations if needed, never in canonical semantic state.

## 6. Verification design and evidence rules

Prefer deterministic automated tests for schemas, ownership/binding, routing precedence, gates, subject/history invariants, crash/retry handling, migration, content equality and Git topology. Exercise real parsers/helpers and disposable Git histories; use fake external-operation responses to force timeout/ambiguous/readback branches reproducibly. Contract tests should prove expected input → allowed/rejected route/outcome, not merely count keywords. Small static checks still protect package content and forbidden positive routes. Do not build a second test-only workflow interpreter whose passing behavior says nothing about production contracts: share machine-readable constraints where justified and connect each scenario to exact module/validator implementation.

Agent judgment such as research adequacy, semantic compatibility and independence cannot be guaranteed by a substring assertion. Use scenario oracles, adversarial fixtures, focused independent review and the specified real-surface tests for that residual risk. No extra manual suite substitutes for automatable checks. Broad manual repetition is unnecessary; after a change rerun affected tests and explicitly justify reuse of unchanged exact evidence.

### 6.1 Mandatory validation input mapped to delivery

| ID | Owner / prerequisite | Concrete automated acceptance path |
|---|---|---|
| A01 | M01.P4, M05.P2/P3 | Allowed bootstrap/router/module read sets, exact refs and unrelated-module exclusions; package trace corroboration. |
| A02 | M01.P4, M06.P2, M07.P1 | Parse new templates/state and normal route reachability; reject all legacy selectors/schedulers/context-health/runtime bindings. |
| A03 | M01.P2/P4, M04.P3 | Valid exact bindings; wrong branch/ID/class/path/missing record; legal target-side terminal exception. |
| A04 | M03.P2/P4 | Reject two active Cards in one board; allow concurrent runtime workers inside one Card with sole Main reconciliation. |
| A05 | M03.P4, M06.P3 | Result already durable after worker loss; validate/reconcile once, never replay solely for missing runtime. |
| A06 | M04.P2, M06.P3 | Inject timeout after successful write and indeterminate readback; inspect first, no blind retry, fail closed if uncertain. |
| A07 | M03.P3/P4 | Immutable S1/RED retained, correction S2/new attempt, independence and GREEN exact result match. |
| A08 | M04.P1 | New target SHA with identical covered content/acceptance + passing compatibility retains exact valid GREEN. |
| A09 | M04.P1 | Reconciliation changes behavior/acceptance; old coverage invalid, new immutable subject/review required. |
| A10 | M04.P3 | Merge then delete source before bookkeeping; recover target package, reconcile/read back without recreating source. |
| A11 | M03.P1 | Trivial aligned fix uses precise Card alone; complex schema/API/idempotency/security/migration adds material JIT contract. |
| A12 | M02.P2, M03.P1 | Reject hypothetical extension/registry; retain needed current correctness/security/maintenance/test obligations. |
| A13 | M02.P2 | Research fixture includes proportional official/upstream, project and issue/community check with weights/conflicts/limits; no official-only shortcut. |
| A14 | M02.P4, M04.P2 | Exact existing Issue/workstream wins; ambiguous match/creation timeout cannot create duplicate; intermediate tracker remains open. |
| A15 | M06.P1–P3 | Finite V1 fixture conversions, unsupported input rejection, obligations preserved and repeat/crash idempotency. |
| A16 | M04.P4 | Only declared downstream release loads lineage module; numeric lane/tuple cases, historical tag immutability and optional alias identity. |
| A17 | M07.P1, each earlier milestone | Every Appendix B source row/disposition has assertion or explicit non-code disposition; DROP has no positive normal route. |

Supplement A01–A17 with deterministic cases for **issue alignment/promotion**, **premium A/B/C/replan**, **end-of-scope versus role completion**, **authorization before live writes**, **stacked dependencies**, **source-head change before cleanup**, **read-only diagnosis boundary**, **Research return crash points**, **package missing authority/trust** and **custody transfer interruption**. These close gaps between the matrix's concise scenarios and the full requirement acceptance surface without inventing additional manual gates.

### 6.2 Staged real-surface checkpoints

| ID | Earliest complete slice / combination | Required live evidence |
|---|---|---|
| L01 | M05 after M02; Android Project | V2 GitHub bootstrap, nontrivial feature, correlated tracker, automatic numbered/recommended grilling, agent-owned Research when needed, no implementation. |
| L02 | M05 after M02/M03; combine L03 | Symptom-only Android issue; diagnosis; safety-question response continues discussion; only later explicit aligned repair proceeds; one correlated Issue. |
| L03 | Partial continuity evidence in M05; full completion required in M07 before first production acceptance | M05 may stop after the same real L02 issue flow proves blocker recovery, implementation and a correct fresh independent-review boundary. Full acceptance still requires: intermediate PR does not close tracker; final default-branch PR has correct linkage; post-merge Issue readback and accepted-completion-only fallback close; no duplicate after recovery. |
| L04 | Delivery mechanics qualified in M05; full ordinary model-backed completion required in M07 before first production acceptance if not already obtained | Exact `$pw:project_workflow_v2` resolution on the real installed CLI/package, bundled local authority path, thin Skill/hook, failed missing-router case and no V1 route are sufficient for the M05 delivery checkpoint. The full ordinary model-backed semantic continuation remains part of first-production live acceptance. |
| L05 | M05 paired L04 | Harmless canonical module update with unchanged bootstrap hashes; installed updated files observed in fresh session; exact source disambiguated. |
| L06 | M07 after both bootstraps and complete lifecycle | Same workstream ChatGPT → Codex → ChatGPT, identical state schema/authority and completed-result reuse. |
| L07 | M07; may reuse pilot planning sequence | Actual A → best-context Planning → B → fresh independent review → approved GREEN → C → cheaper-context Prep; restart at gates re-presents them. |
| L08 | M07 after M03/M04 and capable runtime | Actual N-CAPABLE RED → delegated correction → independent GREEN → finalization in one invocation, no artificial stop. |
| L09 | M07 after M03/M04; two fresh ChatGPT contexts | RED → same-chat correction → stop for new subject; next GREEN → same-chat finalization, with no verdict-only stops. |

User-driven work is limited to actual surface/model/context interactions and genuine human decisions. Agents prepare disposable fixtures, inspect evidence and run automatable checks. Optional exploratory smoke scenarios from validation section C are not additional first-release blockers if equivalent automated coverage is strong. The missing/broken router failure remains mandatory delivery evidence and is already exercised in M05; P2 only defers the still-missing full model-backed L04 continuation and L03 final integration/closure to M07. This changes milestone timing, not first-production acceptance: §8 still requires all mandatory L01–L09 GREEN.

Evidence must identify exact candidate content, test setup, expected/actual outcome, durable results and limitations. Runtime-specific observational metadata may live in surface test reports where necessary; it must not become canonical workflow routing/state/provenance. A V1 or synthetic run cannot be relabeled as a V2 live PASS. A later material change invalidates only affected evidence, with an explicit compatibility decision for reused evidence.

## 7. JIT, risk and escalation register

| Trigger | Owner / evidence required | Permitted downstream decision |
|---|---|---|
| First valid state/router slice | M01 valid/invalid fixtures | Minimal schema/tool syntax and field encoding within §3 owners; no runtime selector or generic state engine. |
| First installed V2 probe | M01.P3 actual discovery/invocation/root evidence | Packaging mechanism refinement; accepted name failure routes to Research/Definition, never implicit rename. |
| Diagnosis reaches repair proposal | M02 diagnosis + current intended outcome | Human alignment before mutation; micro-fix eligibility only after alignment, never marker-based permission. |
| Research findings complete | Owning stage exact origin/return/result | Consume once; strategy change → Planning, accepted intent change → Definition; do not treat research as a decision. |
| Useful current milestone scope known | M03 exact predecessor results | Create/refine unstarted Cards, acceptance and necessary technical contract; no placeholder Cards for unknown work. |
| Material technical ambiguity remains beyond Card | M03 demonstrable API/schema/behavior/security/migration interaction | Load optional technical-contract/OpenSpec; add only contract value that is actually missing. |
| Delegation/review capability at launch | M03 current available capability + subject provenance | Choose runtime realization; preserve common state. No worker availability field in durable schema. |
| Target movement or new final subject | M04 exact target/content/acceptance/compatibility | Small integration repair/reuse or new review; strategic/intent change escalates. |
| Real fork release/version operation | M04 exact declared upstream lineage | Optional version helper/policy only; no blanket fork policy or release automation. |
| Actual legacy source selected | M06 immutable source + dry-run mapping | Bounded supported conversion; unresolved semantic fields or concurrent Cards block apply. |
| Delivered candidate ready for real surfaces | M05/M07 exact package/implementation | Instantiate minimal live fixtures and user interactions; access failure remains a test blocker. |
| First production adoption | M07 complete evidence + explicit project adoption scope | Transfer one live owner and update user-owned bootstrap; no mass migration or permanent dual-write. |

Principal risks and controls: hidden V1 import (row-by-row salvage plus negative tests); duplicate ownership (single-owner schemas and crash fixtures); stale user approval (exact scope/revision alignment); package naming/cache/trust (early actual probe then live update readback); runtime identity leaking into state (schema negatives + evidence normalization); review reuse without acceptance equivalence (exact subject plus compatibility); premature branch deletion (target package before merge); two-repository divergence (bounded custody and no dual writes); fake automated confidence in agent behavior (scenario/independent review plus mandatory live tests). No known unresolved product choice blocks this plan. Future contrary evidence is an escalation trigger, not a silently preapproved requirement change.

## 8. First production-ready criteria and safe cutover

The first production-ready candidate must satisfy all of the following:

1. Every PWV2-REQ-001..076 has implemented acceptance evidence; every salvage row has its accepted disposition; all mandatory A01–A17 and L01–L09 are GREEN. Documentation accurately identifies supported migration boundaries and runtime prerequisites. There is no production waiver for deferred N scenarios.
2. One canonical common tree and runtime-neutral consumer state are actually delivered. Thin ChatGPT bootstrap and installed Codex package resolve that same accepted content. Exact invocation and update propagation are proven without semantic duplication or project patch pinning.
3. Input human-control, review independence/history, A/B/C, direct/delegated portability, target refresh, uncertain-effect recovery, tracker close and deleted-branch recovery work together. No unresolved semantic blocker or P0/P1 defect remains. Lower-severity findings must have a concrete acceptance rationale that does not waive a MUST.
4. Final candidate has independent final-integration GREEN (or exact stronger full coverage), affected checks after target refresh and immediate pre-mutation readback as needed. No self-review. Release/package identity is immutable and read back; ordinary V2 release numbering is chosen proportionally in JIT and is not automatically the optional fork lineage policy.
5. A named pilot/adoption scope, safe boundary, source recovery snapshot and expected target/package/bootstrap state are durable. Explicit authorization is required for adopting/migrating the user's actual projects and changing user-owned instructions/installations; classification as deployment alone adds no gate. Routine already-authorized deterministic writes are not re-confirmed.

**Cutover sequence:** keep V1 controlling production projects → qualify V2 in disposable fixtures/candidate delivery → rehearse migration and rollback → freeze/read back acceptance candidate → obtain the explicit scoped adoption action when due → stage and verify the full V2 custody package → retire V1 live control with exact terminal transfer pointer → enable the V2 bootstrap/package for that selected pilot → read back both delivery surfaces and recover the exact workstream → close the adoption scope. If an existing `pw` source conflicts, resolve the installed source explicitly; do not rely on cache precedence. Provisioning/configuration is performed by its external owner, not by V2 growing a provisioning subsystem.

**Rollback:** before activation, revert an unaccepted candidate/migration branch or restore the prior installation/Project Instructions while the V1 source remains the sole controller. After V2 has produced new live state or effects, do not feed that state to V1 or blindly reset commits: hold affected work, read back external effects, retain the V2 state and exact evidence, and choose bounded forward correction or an explicitly authorized reverse migration from verified facts. No force-push or rewrite of published review/release history. Installing an older compatible package is delivery rollback only; it cannot undo accepted project effects. This avoids promising a generic inverse converter.

Completion is scoped: first production-ready V2 and specifically authorized pilot adoption. Further projects, features, infrastructure or runtime products require new scope; Close does not manufacture a next assignment.

## Appendix A — Complete requirement ownership and execution path

Each row names a primary owner, concrete package and acceptance oracle. Supporting milestone references do not create a second owner. All requirements receive Cards from future Execution Prep before implementation. The JIT register (§7) constrains deferred implementation detail; no requirement is deferred indefinitely.

| Requirement | Primary owner / package | Outcome-level acceptance / validation |
|---|---|---|
| PWV2-REQ-001 | M01.P1/P2 | Sole canonical `workflow/`; A01/A02/A17. |
| PWV2-REQ-002 | M01.P2/P4 | No normal fixed-policy/legacy/redundant V2 tree; A02/A17. |
| PWV2-REQ-003 | M01.P2/P4 | New state never selects execution policy; A02/A15. |
| PWV2-REQ-004 | M01.P2/P4 | No canonical runtime/model/session/worker identity; A02, L06. |
| PWV2-REQ-005 | M07.P2 | Same durable state across ChatGPT/Codex boundaries; L06. |
| PWV2-REQ-006 | M01.P2 | Explicit semantic/runtime ownership; M03.P2 realizes it, A04/L08. |
| PWV2-REQ-007 | M05.P1 | ChatGPT reads V2 GitHub authority through user bootstrap; L01. |
| PWV2-REQ-008 | M05.P2 | Codex normal policy reads stay in installed bundle; L04/A01. |
| PWV2-REQ-009 | M05.P2 | Exact `$pw:project_workflow_v2`; early M01.P3 gate, L04. |
| PWV2-REQ-010 | M05.P2/P3 | Installed canonical workflow bytes, no semantic copy; L05/A17. |
| PWV2-REQ-011 | M05.P3 | Semantic update leaves Skill/hook/bootstrap hashes unchanged; L05. |
| PWV2-REQ-012 | M05.P2 | Provisioning remains external `newproject-skill`; A17 boundary check. |
| PWV2-REQ-013 | M01.P2/P4 | Thin bootstrap → router → current module/state/refs; A01/L04. |
| PWV2-REQ-014 | M05.P1/P2 | No bootstrap blanket preload or stage restatement; A01/A17. |
| PWV2-REQ-015 | M01.P2 | Exact resolvable artifact refs prevent routine broad scans; A01/A03. |
| PWV2-REQ-016 | M01.P2 | Consumer project common V2 marker validated; A02/A03. |
| PWV2-REQ-017 | M01.P1 | One consumer repo; bounded authorized construction custody §4, transfer M07.P4. |
| PWV2-REQ-018 | M01.P1/P2 | Branch first + manifest/local state before managed write; A03/A10. |
| PWV2-REQ-019 | M01.P2/P4 | No correctness-critical global registry; A02/A03/A17. |
| PWV2-REQ-020 | M04.P3 | Only real parent dependency; provenance and legal stacked integration tests. |
| PWV2-REQ-021 | M03.P1/P2 | Stable contract versus selected mutable owner; A03/A04/A07. |
| PWV2-REQ-022 | M03.P2 | One executing Card per workstream; A04. |
| PWV2-REQ-023 | M01.P2/P4 | No Card scheduler or removed wrapper/statuses; A02/A04/A15. |
| PWV2-REQ-024 | M03.P2 | Runtime worker concurrency inside one Card; A04/L08. |
| PWV2-REQ-025 | M03.P2 | Qualifying capability mandates implementation delegation; A04/L08. |
| PWV2-REQ-026 | M03.P2/P4 | Worker returns evidence, Main alone reconciles state; A04/A05. |
| PWV2-REQ-027 | M03.P2 | Genuine no-delegation realization uses same direct execution contract; L06/L09. |
| PWV2-REQ-028 | M03.P1 | All knowable useful Cards + exact predecessor JIT triggers, no placeholders. |
| PWV2-REQ-029 | M03.P1 | L1/L2 bounded refinement; strategy/intent escalation fixtures. |
| PWV2-REQ-030 | M03.P1/P2 | READY independent of capability; launch refresh rejects stale prerequisites. |
| PWV2-REQ-031 | M03.P4 | Durable result reused after worker loss; A05/L06. |
| PWV2-REQ-032 | M04.P2 | Readback before uncertain-effect retry or fail closed; A06. |
| PWV2-REQ-033 | M04.P2 | Every material readable external write verified/evidenced; A06/L03. |
| PWV2-REQ-034 | M03.P3 | Exact subject/acceptance and append-only attempts; A07/L08/L09. |
| PWV2-REQ-035 | M03.P3 | Producer/repairer cannot independently review same subject; A07/L08/L09. |
| PWV2-REQ-036 | M03.P3 | Activated REQUIRED/RECOMMENDED blocks until GREEN; durable RED retained. |
| PWV2-REQ-037 | M03.P3/P4 | Semantic provenance with no canonical runtime telemetry; A02/A07/L06. |
| PWV2-REQ-038 | M04.P1 | Independent final review or exact stronger whole-surface coverage; A08/A09. |
| PWV2-REQ-039 | M02.P3 | Every new/material plan independently reviewed; editorial-only exception tested. |
| PWV2-REQ-040 | M02.P3 | Durable A after Definition, no automatic Planning; premium fixtures/L07. |
| PWV2-REQ-041 | M02.P3 | Best-context recommendation without model constant; L07. |
| PWV2-REQ-042 | M02.P3 | Frozen exact plan → B, no planner internal Stage-6 review; L07. |
| PWV2-REQ-043 | M02.P3 | Approved GREEN → C before Prep; recovery fixtures/L07. |
| PWV2-REQ-044 | M02.P3 | Material replan repeats A/B/C, not an L2 bypass; premium fixtures. |
| PWV2-REQ-045 | M02.P1/P3 | Qualified micro-fix skips full plan only after alignment; A11/L02. |
| PWV2-REQ-046 | M02.P2 | Intrinsic grilling, `#grill` inactive; L01/A17. |
| PWV2-REQ-047 | M02.P2 | Material thematic numbered choices with recommendations/value-based rounds; L01. |
| PWV2-REQ-048 | M02.P2 | Agent-owned facts, Research and final challenge audit; A13/L01. |
| PWV2-REQ-049 | M02.P2 | Proportional official/upstream + local + tracker/community prior art; A13. |
| PWV2-REQ-050 | M02.P2 | Source weights/conflicts explicit; community not authority by popularity; A13. |
| PWV2-REQ-051 | M01.P2 | Global complexity justification with quality intact; A12, M03 audit. |
| PWV2-REQ-052 | M03.P1 | Every change bounded Card; extra contract JIT/value-triggered; A11. |
| PWV2-REQ-053 | M02.P1 | Initial `#issue` permits diagnosis/intake only; input fixtures/L02. |
| PWV2-REQ-054 | M02.P1 | Proposal/safety/recommendation then subsequent aligned authorization; L02. |
| PWV2-REQ-055 | M02.P1/P2 | Safety question/alternative continues grilling; no auto-fix; L02. |
| PWV2-REQ-056 | M02.P4 | Supported issue/feature tracker created/recovered after dedup; A14/L01/L02. |
| PWV2-REQ-057 | M02.P4 | Tracker never requirements/authorization/state authority; A14 negative cases. |
| PWV2-REQ-058 | M02.P4 | Exact repo/Issue/workstream/final-PR correlation durable; A14/L03. |
| PWV2-REQ-059 | M04.P2 | Intermediate references only, final default-branch closing linkage; L03. |
| PWV2-REQ-060 | M04.P2 | Issue readback, explicit close only after accepted whole scope; A06/L03. |
| PWV2-REQ-061 | M04.P1 | Refresh/reconcile/affected tests before coverage, target reread before write; A09. |
| PWV2-REQ-062 | M04.P1 | SHA-only motion preserves proven coverage + compatibility; A08. |
| PWV2-REQ-063 | M04.P1 | Material content/behavior/acceptance change requires new subject; A09. |
| PWV2-REQ-064 | M04.P3 | Unique artifacts pre-merge, target-side terminal recovery; A10. |
| PWV2-REQ-065 | M04.P3 | Auto-delete normal; surviving-ref fallback checks exact head; A10/cleanup cases. |
| PWV2-REQ-066 | M04.P2/P4 | Live write alone no stop; explicit accepted gate honored; authorization cases. |
| PWV2-REQ-067 | M01.P2 | Deterministic authorized continuation; M03.P4 realization, premium/human exceptions; L08/L09. |
| PWV2-REQ-068 | M02.P3 | Complete real-stop set and recoverable stop state; L07/route cases. |
| PWV2-REQ-069 | M01.P2/P4 | No Context Health/FRESH lifecycle; durable recovery; A02/L06. |
| PWV2-REQ-070 | M04.P4 | True approved-scope completion reports and stops, no invented next work. |
| PWV2-REQ-071 | M05.P1 | Ready-to-copy locator-only real-gate handoff; L07/L09/A01. |
| PWV2-REQ-072 | M06.P1–P4 | Finite readers/conversion only, no permanent legacy route; A15/A02. |
| PWV2-REQ-073 | M04.P4 | Fork version module concrete declared trigger only; A16. |
| PWV2-REQ-074 | M07.P1 | A01–A17 automated; only actual surfaces manual; §6 evidence. |
| PWV2-REQ-075 | M07.P3 | Actual V2 N-CAPABLE and N-CHATGPT both GREEN before production; L08/L09. |
| PWV2-REQ-076 | M07.P1 | Every salvage row reconciled; explicit DROP regression; A17/Appendix B. |

## Appendix B — Mandatory V1 salvage/regression accounting

The row-by-row mapping below is part of this immutable plan. Dispositions are copied from the accepted matrix; implementation references are planned destinations/assertions, not imported V1 authority. Each source row must retain an implemented assertion or explicit non-code disposition in A17. Support/optional/out-of-scope rows are included as well as KEEP/GENERALIZE/BOOTSTRAP/DROP. Migration-only support is further specified in M06 for all removed V1 state: old representation is input/provenance only, never a positive production route.

| Row | Exact V1/source surface | Accepted disposition | Planned owner / assertion or non-code disposition |
|---|---|---|---|
| S001 | `workflow/BRAINSTORMING.md` + fixed-policy Brainstorming copies | KEEP CORE | M02.P2; common Brainstorming; L01 intrinsic grilling, A17 no active #grill. |
| S002 | `workflow/common/BRAINSTORMING.md` | KEEP CORE | M02.P2; Brainstorming authority/promotion; final challenge and exact revision fixtures. |
| S003 | `workflow/chatgpt_only/INTAKE.md` + `codex_only/INTAKE.md` | GENERALIZE | M02.P1/P4; common Intake; A03/A14 binding/dedup and L02 aligned issue. |
| S004 | automatic V1 `#issue -> micro_fix` fast path | DROP | M02.P1; reject initial-issue autonomous micro-fix; input negative cases/L02. |
| S005 | V1 micro-fix contract | GENERALIZE | M02.P1 + M03.P1; aligned proportional fix with Card/tests/review; A11/L02. |
| S006 | `workflow/RESEARCH.md` + `workflow/common/RESEARCH.md` + fixed-policy Research | KEEP CORE | M02.P2; common Research; A13 breadth/weight and exact once-only return. |
| S007 | `workflow/common/DEFINITION.md` + fixed-policy Definition | KEEP CORE | M02.P2; common Definition; exact user promotion and approved authority tests. |
| S008 | `workflow/PLANNING.md` + fixed-policy Planning | KEEP CORE | M02.P3; common Planning; coverage plus A before material planning, L07. |
| S009 | fixed-policy `PLAN_REVIEW.md` | GENERALIZE | M02.P3; plan review record/immutable draft; B/C and no internal Stage-6, L07. |
| S010 | `workflow/EXECUTION_PREP.md` + fixed-policy prep | GENERALIZE | M03.P1; Prep/JIT/readiness; complete known Cards, predecessor triggers, A04/A11. |
| S011 | root/shared `workflow/EXECUTION.md` + fixed-policy Execution | GENERALIZE | M03.P2/P4; common execution/delegation; A04/A05/L06/L08. |
| S012 | fixed-policy `REVIEW.md` | GENERALIZE | M03.P3; exact-subject append-only common review; A07/L08/L09. |
| S013 | fixed-policy `CLOSE.md` | KEEP CORE | M04.P1-P4; close/readback/terminal safety; A06/A08-A10/L03. |
| S014 | fixed-policy `RECOVERY.md` | GENERALIZE | M03.P4 + M04.P3; common recovery; completed result/terminal ref cases. |
| S015 | fixed-policy `ROUTER.md` + root `CONTEXT_ROUTING.md` | GENERALIZE | M01.P2/P4; small common router; A01/A02 exact read-set and no policy selection. |
| S016 | `workflow/common/USER_STOP.md` | GENERALIZE | M02.P3 + M05.P1; real stops and locator-only prompts; L07/L09, no Context Health variant. |
| S017 | `workflow/common/AUTHORITY.md` | KEEP CORE | M01.P2; authority domains and global YAGNI; A12/A17. |
| S018 | `workflow/contracts/PROJECT_REPOSITORY.md` / fixed-policy `REPOSITORY.md` | GENERALIZE | M01.P1/P2; project marker/index and state separation; A02/A03, bounded custody section 4. |
| S019 | one project = one repository | KEEP CORE | M01.P1; consumer single-repo invariant; construction exception is bounded and explicitly scoped in section 4. |
| S020 | branch-first manifest-bound workstreams | KEEP CORE | M01.P2; exact manifest/local state; A03 and pre-write branch tests. |
| S021 | mutable repository-global workstream registry | DROP | M01.P4; reject authoritative global registry; A02/A03. |
| S022 | stacked parent/child workstreams | KEEP CORE | M04.P3; real dependency/provenance and two legal integration paths; stacked/deleted-parent fixtures. |
| S023 | `WORKSTREAM.yaml` final-integration/cleanup ownership | GENERALIZE | M04.P1/P3; manifest-owned final review/cleanup pointers; A08-A10. |
| S024 | `TASK_BOARD.yaml` mutable state | KEEP CORE | M03.P2; selected board mutable owner; A03/A04/A05. |
| S025 | stable Task Card vs mutable Task Board | KEEP CORE | M03.P1/P2; stable Card/board separation; reject mirrored mutable status/results. |
| S026 | root/default legacy Task Board as live destination | DROP | M06.P1/P2; root board migration input only; A02/A15 reject live fallback. |
| S027 | execution-policy field | DROP | M01.P4 + M06.P2; reject new policy field, read old field only in migration; A02/A15. |
| S028 | runtime/model/session/worker identity in canonical state | DROP | M01.P4 + M03.P4; reject canonical runtime telemetry, retain semantic proof; A02/A07. |
| S029 | durable orchestration binding | DROP | M01.P4 + M06.P2; no new orchestration binding; old input mapped without semantic loss. |
| S030 | universal `active_execution` / `transfer_ready` | DROP | M01.P4 + M06.P2; reject universal active_execution/transfer_ready (and ordinary returned); A02/A15. |
| S031 | Project-Card parallel batch/lane scheduler | DROP | M01.P4 + M03.P2; reject Card batches/lanes/frozen-members/scheduler scopes; A02/A04. |
| S032 | runtime-internal parallel subagents | KEEP OUTSIDE PW | M03.P2; runtime-owned topology only; A04/L08 prove one Card and one shared-state writer. |
| S033 | cumulative milestone handoff/checkpoint | KEEP CORE | M03.P4 + M04.P3; cumulative exact checkpoint/handoff; recovery without transcript. |
| S034 | terminal target-side workstream package | KEEP CORE | M04.P3; complete target package before branch loss; A10. |
| S035 | branch cleanup `safe_to_delete` fallback | KEEP CORE | M04.P3; only needed surviving-ref fallback, head reread then absence readback; cleanup fixtures. |
| S036 | `workflow/contracts/TASK_CARDS.md` + fixed-policy `TASK_CARDS.md` | GENERALIZE | M03.P1; one stable bounded Card contract; scope/authority/tests/readback/review checks. |
| S037 | `workflow/contracts/TASK_EXECUTION.md` | GENERALIZE | M03.P1/P2/P4; refresh/start/DoD/blocker/review; READY not capability-dependent. |
| S038 | `workflow/contracts/GITHUB_STATE.md` | GENERALIZE / SHRINK | M01.P2 + M04.P2/P3; Git/ref/evidence recovery only; A03/A06/A10, no scheduler machinery. |
| S039 | `workflow/common/OPENSPEC.md` + `workflow/contracts/OPENSPEC.md` | TRIGGER-ONLY / GENERALIZE | M03.P1; tool-neutral selective technical contract; A11 simple no-extra-artifact and material trigger. |
| S040 | speculative distant OpenSpec | DROP | M03.P1; no speculative distant OpenSpec; JIT predecessor/contract-value fixtures. |
| S041 | OpenSpec as replacement for requirements/plan/Card | DROP | M03.P1; technical artifact cannot override requirements/plan/Card; authority-negative fixture. |
| S042 | REQUIRED / RECOMMENDED exact-subject implementation review | KEEP CORE | M03.P3; both activated review classes block until GREEN; A07. |
| S043 | product-specific reviewer identities | DROP | M03.P3/P4; independence is per exact subject, not product/worker name; A07/L06. |
| S044 | Stage-6 planner spawning internal reviewer | DROP | M02.P3; reject planner internal Stage-6 dispatch; B fresh context required; L07. |
| S045 | Stage-9 internal independent reviewer when capability exists | KEEP CORE | M03.P3; capability-first Stage-9 independent realization; L08 while preserving independence. |
| S046 | locator-only fresh ChatGPT handoff | KEEP CORE | M05.P1; repository/branch/obligation/pointer only; L07/L09 handoff inspection. |
| S047 | Context Health / FRESH lifecycle | DROP | M01.P4; no Context Health/FRESH lifecycle or automatic hygiene stops; A02/L06. |
| S048 | issue auto-implementation from initial `#issue` | DROP | M02.P1; no mutation from initial issue alone; L02 and alignment fixtures. |
| S049 | user stop at deployment/live-write merely because it is deployment/live-write | DROP | M04.P2/P4; no deployment-only stop, honor accepted explicit authorization; route fixtures. |
| S050 | GitHub as durable commit/PR/evidence source | KEEP CORE | M01.P1 + M04.P2; exact immutable Git/PR/result evidence and readback; A06/A10. |
| S051 | coherent commits / branch-PR managed changes | KEEP CORE | M01.P1 + M04.P1; cohesive branch/PR checkpoints; section 4 empty-root exception only. |
| S052 | never force-push main as normal remediation | KEEP CORE | M04.P1; no force-push main or published-history rewrite as remediation; integration safety tests. |
| S053 | integration refresh against current target | KEEP CORE | M04.P1; refresh before review reuse/freeze and integration; A08/A09. |
| S054 | textual merge cleanliness = semantic compatibility | DROP | M04.P1; reject clean-merge-only compatibility proof; affected semantic verification required. |
| S055 | external `ACTION/WRITE -> READBACK -> VERIFY -> EVIDENCE` | KEEP CORE | M04.P2; operation/readback/verify/evidence chain; A06/L03. |
| S056 | uncertain interrupted external side effect -> blind retry | DROP | M04.P2; reject blind retries after ambiguous effect; A06. |
| S057 | GitHub auto-delete merged branch | KEEP CORE | M04.P3; automatic head deletion is normal, not recovery failure; A10. |
| S058 | `workflow/common/FORK_RELEASE_VERSIONING.md` | TRIGGER-ONLY | M04.P4; module loaded only for declared downstream release/version operation; A16. |
| S059 | `vX.Y.Z-private.N` lineage rules | TRIGGER-ONLY | M04.P4; accepted upstream tuple/private numeric lanes/immutable history/native latest; A16. |
| S060 | competing research/prototype branches | TRIGGER-ONLY | M02.P2 JIT; optional A/B prototype evidence only for real alternatives, not lifecycle scheduler. |
| S061 | `BLOCKER.md` durable blocker record/template | KEEP SUPPORT | M03.P4; optional blocker artifact only when recovery needs it; no mandatory boilerplate. |
| S062 | acceptance evidence template | KEEP SUPPORT | M03.P4; optional acceptance evidence template with exact subject/results; A07. |
| S063 | `workflow/chatgpt/CAPABILITY_GATE.md` | DROP as product gate | M01.P4; no mixed/product capability gate; capability decisions remain within common obligations. |
| S064 | `workflow/chatgpt/EXECUTION.md` | GENERALIZE/MINIMIZE | M05.P1 + M03.P2; only ChatGPT entry/UX differences; no separate execution semantics. |
| S065 | `workflow/codex/CODEX_ORCHESTRATION.md` | GENERALIZE/MINIMIZE | M03.P2; semantic/runtime boundary without binding or Card scheduler; A04/L08. |
| S066 | `workflow/codex/EXECUTION.md` | GENERALIZE/MINIMIZE | M05.P2 + M03.P2; local bootstrap plus common execution, no Codex policy tree. |
| S067 | `workflow/codex/HANDOFF.md` | MOSTLY DROP | M05.P1 + M03.P4; drop cross-product task transfer lifecycle; retain exact locator/recovery evidence only. |
| S068 | named Codex Main/Executor/Tester/Investigator in canonical policy | DROP | M03.P2/P3; no canonical named runtime role catalog; generic semantic responsibilities only. |
| S069 | `.codex-plugin/plugin.json` | BOOTSTRAP | M05.P2; thin pw metadata, M01.P3 validates supported packaging; no workflow copy. |
| S070 | marketplace metadata | BOOTSTRAP | M05.P2/P3; distribution metadata only; source disambiguation and update readback. |
| S071 | `skills/project-workflow/SKILL.md` | BOOTSTRAP | M05.P2; Skill renamed project_workflow_v2; exact invocation L04, no embedded stage policy. |
| S072 | `hooks/session-start.py` + `hooks.json` | BOOTSTRAP | M05.P2; tiny installed-root SessionStart pointer, trust/path/missing-router checks; L04. |
| S073 | Codex fetching remote workflow repo in normal operation | DROP | M05.P2; reject ordinary remote workflow acquisition; L04 local-path/read-set evidence. |
| S074 | `prompts/CHATGPT_PROJECT_INSTRUCTIONS.md` | BOOTSTRAP | M05.P1; minimal recommended user-owned GitHub bootstrap; L01. |
| S075 | `prompts/CHATGPT_START.md` | SHRINK / OPTIONAL | M05.P1 JIT; omit redundant start prompt unless manual recovery needs a locator; no new policy. |
| S076 | `prompts/CHATGPT_FRESH_SESSION.md` | KEEP SUPPORT | M05.P1; locator-only actual-gate prompt template; L07/L09. |
| S077 | `prompts/CODEX_START.md` | DROP / DEBUG-ONLY | M05.P2; omit normal CODEX_START semantics; debug guidance, if needed, is locator-only. |
| S078 | duplicate semantic policy inside plugin Skill/hook | DROP | M05.P2/P3; no duplicate policy in Skill/hook; unchanged-bootstrap hash proof L05. |
| S079 | project-local plugin/MCP/Skill provisioning | OUT OF SCOPE | M05.P2; explicit external newproject-skill boundary; no V2 provisioner/pinning subsystem. |
| S080 | `templates/PROJECT.md` | GENERALIZE | M01.P2; minimal common-contract PROJECT template; A02. |
| S081 | `templates/BRAINSTORM.md` | KEEP SUPPORT | M02.P2; concise decisions/promoted subject, no transcript dump; L01/fixture checks. |
| S082 | `templates/OPEN_QUESTIONS.md` | KEEP SUPPORT | M02.P2 JIT; optional material unresolved questions only; no fabricated decision registry. |
| S083 | `templates/RESEARCH.md` | KEEP SUPPORT | M02.P2; Research origin/return/sources/weights/reconciliation template; A13. |
| S084 | `templates/REQUIREMENTS.md` | KEEP SUPPORT | M02.P2; approved requirements/revision/acceptance authority template. |
| S085 | `templates/DECISION.md` | KEEP SUPPORT | M02.P2; accepted decision/rationale/consequences authority template. |
| S086 | `templates/MASTER_PLAN.md` | KEEP SUPPORT | M02.P3; revision/coverage/milestone/gates/JIT plan template; L07. |
| S087 | `templates/MILESTONE.md` | KEEP SUPPORT / OPTIONAL | M03.P1 JIT; optional milestone extension only when plan lacks useful acceptance detail. |
| S088 | `templates/TASK_CARD.md` | KEEP SUPPORT | M03.P1; precise bounded stable scope/authority/tests contract; A11. |
| S089 | `templates/TASK_BOARD.yaml` | GENERALIZE | M01.P2 + M03.P2; manifest-bound common board, no runtime/scheduler fields; A03/A04. |
| S090 | `templates/ACCEPTANCE_EVIDENCE.md` | KEEP SUPPORT | M03.P4; optional concise actual/expected result evidence, no redundant form requirement. |
| S091 | `templates/BLOCKER.md` | KEEP SUPPORT | M03.P4; optional recoverable blocker evidence and exact owning obligation. |
| S092 | `templates/HANDOFF.md` | GENERALIZE | M03.P4 + M05.P1; minimal cumulative checkpoint and locator-only fresh entry, distinct functions. |
| S093 | Official GitHub Issue for `#issue` | KEEP SUPPORT / DEFAULT TRACKER | M02.P4; supported issue tracker after exact recovery/dedup, no repair authorization; A14/L02. |
| S094 | Official GitHub Issue for `#feature` | KEEP SUPPORT / DEFAULT TRACKER | M02.P4; supported feature tracker and refinement in Brainstorming; A14/L01. |
| S095 | Workstream -> GitHub Issue exact reference | KEEP CORE POINTER | M02.P4; exact Issue/repo/workstream/PR correlation durable; A14/L03. |
| S096 | Final PR closing keyword | KEEP SUPPORT | M04.P2; only final scope-completing default-branch PR closes; intermediate linkage negative tests/L03. |
| S097 | Post-merge Issue readback | KEEP CORE CLOSE CHECK | M04.P2; verify Issue state and accepted-completion-only explicit fallback; A06/L03. |

The accepted matrix's standalone **Explicit V1 drops checklist** is also normative input to A17: no fixed ChatGPT/Codex/legacy trees; no execution policy or mixed Capability Gate; no Context Health/FRESH lifecycle; no parallel Cards/batch/lane/frozen-member/scheduler write-scope metadata; no universal active-execution or transfer-ready wrapper; no durable orchestration/runtime identity; no named product-specific implementation/reviewer roles; no automatic issue repair; no planner-spawned Stage-6 review; no unconditional live-write stop; no duplicate plugin policy; no ordinary Codex remote-policy fetch; no source-ref prerequisite for terminal recovery. The additional explicit `ordinary returned` prohibition in R1 is tested too. Negative assertions are scoped to new normal semantics; quoted requirements, migration fixtures and drop documentation may name a forbidden term without enabling it.

## Appendix C — Planning completion and review boundary

Planner-side completeness/challenge audit is recorded separately at `planning/audits/PWV2-P1.md`. Its GREEN means this strategy is ready for independent review, **not** that the plan is approved or V2 is implemented/tested. Coverage here is planned coverage; actual evidence remains future milestone work.

The exact plan blob/commit is frozen in `planning/reviews/PWV2-P1.md`; that record alone owns the V1 review lifecycle. The selected manifest `routing.plan_review` points to it and `authority.plan` points to this draft; root `PROJECT.md` remains the integrated-project router and does not mirror workstream state. Keep Task Board null at this boundary. Review must use the frozen subject and exact Definition inputs, not this planning conversation. Stop B remains the current real stop until a fresh independent context is entered.
