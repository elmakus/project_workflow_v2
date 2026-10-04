# PWV3 3.0.0 — portable Execution Package EP1

Artifact kind: construction-execution-package; producing contract: EP1/1.
Workstream: `change-workflow-successor-product`; recipient: `elmakus/pwv3`.

**Review candidate only. Not accepted, not a launch authorization, and not a PWV2 Task Board.** Mandatory independent OP Execution Package Review and the exact human owner CONTINUE remain required. The P1 construction Plan Review waiver is not reusable here.

## 1. Authority and portable contents

EP1 refines exactly P1 at `elmakus/project_workflow_v2@c67645f7cd0a0887003da178bc8eaaf44357668b:planning/PWV3_3_0_MASTER_PLAN.md@ba2990d773cdd30673f2ce23a6bc74700c6c56cf`. D12 controls over all historical prose. No Definition, strategic order, gate, host, integration method or scope is changed.

Read, in order:
1. `snapshots/authority/DEFINITION.md` in full, with acceptance proved by the archived D12 state, review and owner disposition;
2. `snapshots/authority/DEFINITION.toml` and its 43 ordered decisions, resolved through `SNAPSHOTS.json` (not their old live paths);
3. `snapshots/plan/P1.md`, including its Technical Design, C01–C26 coverage, G0–G7 gates and all section-8 oracles;
4. this file, `CONTRACTS.json`, `QUALIFICATION.md`, `COVERAGE.json`, `DONORS.json`, `DEPENDENCIES.md` and the exact supporting snapshots referenced by those files.

`SNAPSHOTS.json` maps every copied source repository/commit/path/blob to byte-identical package-local bytes. Read the local copy; mutable historical paths are not required inputs. Historical references not selected in this map are provenance only, not transitive construction dependencies. All necessary current D12/decision/P1 authority and its acceptance proof are included. Prior review investigations and donor implementation sources are historical provenance, not required execution lookups. R5/corpus/donor research is evidence, never authority to restore superseded optional OP, execution-mode, delayed evolution, unconditional terminal independence or SH0 construction governance.

The frozen source Definition intentionally contains DRAFT/pending text. Its accepted state and owner CONTINUE, not historical status prose, control. Archived PWV2 TOML records are inert acceptance/provenance snapshots, not native PWV3 checkpoints. The 43-decision ordering and supersession are preserved without re-authoring them.

### Equivalence and identity

Run `python3 verify.py` inside this directory. It checks the complete inventory, byte hashes, original Git blob identities, the exact ordered decision closure, P1/D12 pins, stable Card order, composed graph and mandatory coverage. It needs no donor checkout, network, model or product installation. `python3 -B -m unittest test_verify` exercises rejection controls. These are **package construction checks**, not product acceptance or independent Package Review.

`MANIFEST.json` inventories every payload file except itself; an immutable Git commit plus the EP1 subtree tree ID binds the manifest too. Each package-authored artifact is produced under EP1/1. Snapshots preserve original bytes and identify their actual historical/unversioned producing format rather than inventing native PWV3 versions. All native product artifacts must carry explicit producing versions from S01 onward. Hash verification proves export byte equivalence, not review, remote freshness or authorization; those are independently admitted.

After review, freeze a separate handoff envelope binding the immutable EP1 subtree, the exact OP terminal result, its applicability, explicit published/read-back owner CONTINUE and publication proof. The envelope does not modify the reviewed subtree. This separation avoids self-reference: EP1 cannot contain a review of its own final bytes. A candidate without that closure envelope is not accepted/exportable for launch. Future amendments produce a new package subject and applicable review; never rewrite EP1 under an old verdict.

## 2. Construction governance and admission

PWV2 governs pre-execution only. Do not create a PWV2 Task Board, mark these Cards in_progress under PWV2, or use its Result/Review loop to build PWV3. Package acceptance plus final handoff is an explicit construction-governance boundary. The receiving external invocation executes the accepted contracts, not the PWV2 router. No partial-native SH0 checkpoint takes over construction. A native dogfood workstream is created only for qualification after a runnable candidate exists.

Before launch the receiver must positively verify:
- exact reviewed package tree, complete inventory, accepted P1/D12/decision authority, current applicable OP review and its single-use owner CONTINUE;
- canonical source/handoff and recipient remote freshness, safe branch/worktree and complete required immutable objects; no branch-only, stale local or dirty-path identity substitution;
- sufficient supported host capabilities for the **current** obligation, verified package/helper/runtime baseline where applicable, read/write/effect/readback transport and exact review-independence realization; later production dependencies remain explicit gates, not assumed present;
- exact actual executing runtime/executor/provider bundle, observed after invocation, durably published with positive readback as provenance **before the first material Card write or currentness-sensitive effect**. It is not a semantic execution-mode choice;
- any initial recipient creation/ref effect has exact intent, expected absence/base, bounded write set and authoritative readback. An empty repository observation is not blanket permission to overwrite later content. Do not write an integration/main branch for ad-hoc construction. Establish a legal construction branch, observing host/repository policy; if initial repository policy requires an owner action, stop for it rather than weaken policy.

The package names no executor/provider/model, install recipe or extension. The same bytes work across supported invocations. Capability absence prefers exactly one positively qualified safe receiver that reconstructs the same obligation; zero, ambiguous or UNKNOWN qualified receivers is a blocker. Never infer capability from a tool/product name. Environment real-inference test policy must be obeyed; fixtures and metadata cannot impersonate live qualification.

## 3. Stable Card contract and inputs

`CONTRACTS.json` contains exactly 13 immutable stable Cards `PWV3-S01` through `PWV3-S13`, one-to-one refinements of P1 S01–S13. No placeholder Cards or parallel scheduler. Its S14–S16 records are typed qualification/integration obligations, not Cards. The JSON is a static contract, not mutable execution status.

All Cards inherit these mandatory fields by the explicit `common_contract` reference:
- **Authority:** complete local D12/decision/P1 snapshots plus this package and its post-review closure envelope. The optional technical contract is P1 section 3, not a new OpenSpec lifecycle.
- **Scope/non-goals:** only the stated deliverable and named interfaces/tests. No other Card, product scope, OP internals, host administration, unqualified release, new host/tracker or removed machinery is implicitly included.
- **Writes:** only that Card's `writes` in the recipient, plus its assigned regression/guard/seam test facets in `COVERAGE.json`, its specification/provenance and coordinator-owned Result/Review/readback evidence. No donor writes, repository-rule changes, secrets, accepted package edits, currentness overrides or completed-predecessor rewrites. Evidence paths are `construction/results/<Card>/<unique>.json`, `construction/reviews/<Card>/<unique>.json`, `construction/evidence/<Card>/<unique>/`; stable package import is `construction/package/EP1/`. These are external construction evidence, not PWV2 or partial-native workflow state. Existing evidence is append-only.
- **Inputs:** each `material_inputs` edge is a logical Result output locator, not a future hash. Before running, resolve `construction/results/<predecessor>/<accepted-unique>.json` to repository + immutable commit + path + blob, its exact implementation subject, acceptance/Review and published readback. Bind these in the new Result. Order-only predecessors must also be accepted, but are not invented material dependencies. Missing, stale, unaccepted or same-path-changed inputs forbid launch. No future SHA or accepted-output placeholder is supplied by EP1.
- **Acceptance:** bounded exit tests, positive and independently targeted negative controls, resolved required evidence and ordinary complete-surface Review. All 13 main Cards require ordinary independent Review after checks. An explicit durable exact-scope owner independence waiver is eligible under D12, but is never inferred. For these ordinary Card boundaries only, honest WAIVED_ACCEPTANCE is sufficient when the exact waiver is verified and all non-independence checks pass. Never label it independent GREEN or apply it to OP/QF. Missing/ambiguous Review disposition blocks.
- **Result:** immutable exact Card/package/implementation/input-Result/producing-contract identities, test commands and exit/readback evidence; no completion-text authority. Result suppresses implementation replay but cannot release an unresolved acceptance gate. Changed implementation requires a new Result and newly applicable checks/Review.
- **Tests:** `node --test test/slots/sNN.test.mjs` is required for each Card. `COVERAGE.json` additionally assigns exact family facet test paths. S01 establishes the test harness. Later Cards add their assigned runnable facets, never fake future checks. Every facet includes positive control, isolated negative controls, expected semantic outcomes and source provenance. No skipped/TODO expected-required test counts as accepted. S13 runs the complete host-neutral suite; S14–S16 supply live/release gates separately.
- **Upstream/stop:** unchanged bounded implementation repair stays on the same stable Card; changed package detail returns to Execution Prep and applicable re-review; changed strategy/order/dependency meaning to Planning; changed requirements/acceptance to Definition; product choice to Brainstorming; missing facts to the exact Research owner. OP, human authority, qualified transfer, explicit pause and genuine non-remediable capability/input blockers are real stops. Worker/Card/milestone completion is not.

Earlier component acceptance uses the interface/fixture contract deliverable already available, not unfinished later implementations or Final Qualification. S10 exercises external OP with S09 helper envelopes, not the later S11 ChatGPT bootstrap. S11/S12 real capability exits remain required, while S14 reruns on the exact integrated candidate. This is not a deferral of those exits.

### Combined graph proof

For each Card N the contract graph is `start:N -> result:N -> checks:N -> review:N -> accepted:N`. Every preceding Card acceptance orders the next start. Material Result acceptance edges also enter the consumer start. Post-implementation chain is `accepted:S13 -> S14 -> S15 -> S16`; their evidence is not an early Card prerequisite. `verify.py` builds and topologically validates that composed graph, including explicit extra acceptance edges. A negative control adds `S14 -> accepted:S13` and must fail. External exit gates are capability prerequisites, not edges from future Cards. Their unavailability blocks the frontier, not a reason to skip it. This is a mechanical proof over the declared contracts, not independent confirmation that every material prerequisite was declared; mandatory OP Package Review must inspect semantic completeness and hidden-cycle risk across the full bounded surface.

Shared-impact relations in `CONTRACTS.json` are for revalidation, not scheduling. Any changed shared surface invalidates the declared materially affected cone; outside-cone preservation requires proof. UNKNOWN widens conservatively. Repair reopens the earliest affected stable Card and revisits affected Cards in total order with new Results/acceptance, then resumes the outstanding qualification gate. No second repair schedule or package-level repair object.

## 4. Bounded delegation

For a goal-capable Pi/Paseo invocation, S02 verified identity/publication and S06 impact computation have designated delegation-required bounded implementation units. Their exact read/write/evidence envelopes are in `CONTRACTS.json`. Capability must be positively qualified, and the accepted output must prove actual useful child implementation—not an idle child or a capability bit. Other invocations retain the same semantic Cards without provider-specific variants.

A Generic Worker receives only the exact current unit, accepted package/input Result locators, allowed read/write/test envelope and stop conditions. One delegation edge only; no recursive children, global continuation choice, authority edits or package/OP review substitution. Worker edits may be isolated; only the coordinator consumes exact outputs, verifies tests/publication, reconciles Result/acceptance and advances the current Card. Material independence is checked separately for ordinary review.

## 5. Receiver return contract

Return only positively published immutable deliverables and exact Result/Review/check/readback locators, impacted-surface classification, outstanding accepted gates and any genuine blocker/owner question. Do not claim progress from provider completion or fabricate a GREEN for unavailable dependencies. Resume by reconstructing accepted evidence; never replay completed material work just because a runtime disappeared.

`QUALIFICATION.md` fixes repair, Q0/QF, Global, terminal, integration and GA predicates. `DEPENDENCIES.md` records present observations separately from required future qualification. `DONORS.json` chooses native reimplementation and scenario reuse, not wholesale module copying. This package is not an authorization to install third-party executors, change host policy, manufacture OP evidence or publish an unqualified product.
