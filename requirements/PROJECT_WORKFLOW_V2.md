# Project Workflow V2 Requirements

Revision: `R1`
Status: `approved`
Updated: `2026-09-22`
Definition subject: `project-workflow-v2@R1`
Source Brainstorming: `brainstorming/FINAL_V2_RECONCILIATION.md`
Coverage audit: `brainstorming/V1_TO_V2_COVERAGE_MATRIX.md`
Validation plan: `brainstorming/V2_VALIDATION_MATRIX.md`

## Goal / target state

Create a new clean `elmakus/project_workflow_v2` repository containing one semantic Project Workflow V2 that can be used interchangeably from normal ChatGPT and Codex without durable product-specific execution policy, duplicated workflow logic, or runtime-specific state conversion.

The workflow must preserve the proven V1 lifecycle/safety mechanisms that still add value, deliberately discard superseded V1 machinery, minimize Codex context consumption through progressive disclosure, and preserve explicit human control at product/strategy and issue-repair boundaries.

## Product / system requirements

| ID | Requirement | Priority | Source / decision | Status |
|---|---|---|---|---|
| PWV2-REQ-001 | V2 MUST have one canonical semantic workflow tree at `workflow/` in the new clean V2 repository. | MUST | ADR-PWV2-001 | accepted |
| PWV2-REQ-002 | V2 MUST NOT contain production semantic trees equivalent to `chatgpt_only`, `codex_only`, `legacy`, or redundant `workflow/v2/`. | MUST | ADR-PWV2-001 | accepted |
| PWV2-REQ-003 | New V2 durable project/workstream state MUST NOT use `execution_policy: chatgpt_only | codex_only | mixed` to select semantics. | MUST | ADR-PWV2-001 | accepted |
| PWV2-REQ-004 | Current runtime/product/model/session/worker identity MUST NOT be canonical Project Workflow state. | MUST | ADR-PWV2-001 | accepted |
| PWV2-REQ-005 | The same durable workstream MUST be continuable across ChatGPT and Codex durable boundaries without state conversion. | MUST | ADR-PWV2-001 | accepted |
| PWV2-REQ-006 | Project Workflow MUST own semantic obligations, authority, lifecycle, durable state, reviews, recovery, integration and close safety; runtime MUST own concrete worker/session/model topology and orchestration. | MUST | ADR-PWV2-001; ADR-PWV2-004 | accepted |
| PWV2-REQ-007 | ChatGPT MUST obtain V2 workflow authority from the V2 GitHub repository through user-owned Project Instructions/bootstrap. | MUST | ADR-PWV2-002 | accepted |
| PWV2-REQ-008 | Codex MUST obtain ordinary V2 workflow authority from the installed `pw` plugin bundle, not by fetching the remote workflow repository during normal operation. | MUST | ADR-PWV2-002 | accepted |
| PWV2-REQ-009 | Plugin namespace MUST remain `pw`; target V2 Skill name MUST be `project_workflow_v2`; implementation acceptance MUST verify explicit invocation `$pw:project_workflow_v2`. | MUST | ADR-PWV2-002 | accepted |
| PWV2-REQ-010 | The plugin MUST directly package the same canonical `workflow/` files; Skill/hook/plugin metadata MUST NOT maintain a second semantic copy. | MUST | ADR-PWV2-002 | accepted |
| PWV2-REQ-011 | Ordinary workflow semantic edits MUST NOT require editing Skill/hook/bootstrap files unless bootstrap/package behavior itself changes. | MUST | ADR-PWV2-002 | accepted |
| PWV2-REQ-012 | Repository-local plugin/MCP/Skill provisioning/pinning MUST remain outside V2 and owned by the separate `newproject-skill`. | MUST | ADR-PWV2-002 | accepted |
| PWV2-REQ-013 | V2 bootstrap and router MUST use progressive disclosure: thin bootstrap -> small router -> exact current module -> exact durable state -> exact authority/evidence refs. | MUST | ADR-PWV2-006 | accepted |
| PWV2-REQ-014 | Skill/hook/bootstrap MUST NOT preload or restate the complete workflow, neighboring stages, docs, templates, migration material, or historical guidance. | MUST | ADR-PWV2-006 | accepted |
| PWV2-REQ-015 | Durable artifacts SHOULD carry exact authority/evidence/result refs sufficient to avoid broad repository scans during ordinary continuation. | MUST | ADR-PWV2-006 | accepted |
| PWV2-REQ-016 | Every project using V2 MUST durably identify the common V2 contract, conceptually `project_workflow: v2`; exact schema is implementation-owned. | MUST | ADR-PWV2-001 | accepted |
| PWV2-REQ-017 | One project repository MUST remain the durable project source of truth from discovery through close; a second planning/state/control repository requires concrete technical justification and explicit user authority. | MUST | ADR-PWV2-003 | accepted |
| PWV2-REQ-018 | Managed changes MUST use stable branch-first, manifest-bound workstreams with workstream-local durable state/evidence/handoffs. | MUST | ADR-PWV2-003 | accepted |
| PWV2-REQ-019 | Correctness MUST NOT depend on a mutable repository-global workstream registry. | MUST | ADR-PWV2-003 | accepted |
| PWV2-REQ-020 | Stacked workstreams MUST be used only for genuine unmerged parent-only dependency and MUST preserve dependency/base/integration provenance. | MUST | ADR-PWV2-003 | accepted |
| PWV2-REQ-021 | Stable Task Cards MUST define bounded authority, scope, acceptance and tests; mutable execution/review/result state MUST remain in the selected workstream Task Board/state owner. | MUST | ADR-PWV2-004 | accepted |
| PWV2-REQ-022 | Exactly one Project Workflow Card MAY execute at a time in a selected workstream. | MUST | ADR-PWV2-004 | accepted |
| PWV2-REQ-023 | V2 MUST NOT carry Project-Card batch/lane/concurrent execution scheduler state, universal `active_execution`, ordinary `returned`, or `transfer_ready`. | MUST | ADR-PWV2-004 | accepted |
| PWV2-REQ-024 | Runtime-internal implementation MAY use zero, one or many subagents sequentially or concurrently without creating additional Project Workflow Cards or competing shared-state writers. | MUST | ADR-PWV2-004 | accepted |
| PWV2-REQ-025 | When a qualifying delegated implementation context is available, Main/coordinator MUST delegate Card implementation and retain routing/JIT/authority/validation/integration/review/recovery responsibility. | MUST | ADR-PWV2-004 | accepted |
| PWV2-REQ-026 | Worker/subagent output MUST NOT independently finalize shared Project Workflow state. | MUST | ADR-PWV2-004 | accepted |
| PWV2-REQ-027 | A runtime genuinely lacking delegated implementation capability MAY implement directly without changing Project Workflow semantics. | MUST | ADR-PWV2-004 | accepted |
| PWV2-REQ-028 | Execution Prep MUST materialize all currently well-defined useful Cards, preserve predecessor-dependent JIT triggers, and avoid speculative placeholder Cards. | MUST | accepted Brainstorming Stage 7 | accepted |
| PWV2-REQ-029 | Execution Prep MAY split/merge/reorder/refine not-yet-started Cards only within already accepted authority; strategy/requirements changes MUST route back to Planning/Definition as appropriate. | MUST | accepted Brainstorming Stage 7 | accepted |
| PWV2-REQ-030 | A Card may become READY based on legal authority/dependencies/prerequisites regardless of runtime implementation capability, and launch-time refresh/revalidation MUST occur before execution. | MUST | accepted Brainstorming Stage 7/8 | accepted |
| PWV2-REQ-031 | Recovery MUST reuse/reconcile an already durable completed result instead of replaying work solely because the previous worker/session disappeared. | MUST | accepted Brainstorming Stage 8 | accepted |
| PWV2-REQ-032 | An interrupted/uncertain external side effect MUST be read back before retry; if occurrence cannot safely be established, the workflow MUST fail closed rather than duplicate the side effect. | MUST | accepted Brainstorming Stage 8/10 | accepted |
| PWV2-REQ-033 | Material external mutations MUST follow ACTION/WRITE -> READBACK -> VERIFY EXPECTED STATE -> EVIDENCE when meaningful readback exists. | MUST | accepted V1 invariant | accepted |
| PWV2-REQ-034 | Independent implementation/final-integration review MUST use exact immutable subjects and append-only attempt history for changed subjects/verdicts. | MUST | ADR-PWV2-005 | accepted |
| PWV2-REQ-035 | A context that materially produced/repaired an exact subject MUST NOT independently review that subject. | MUST | ADR-PWV2-005 | accepted |
| PWV2-REQ-036 | REQUIRED and activated RECOMMENDED review gates MUST block completion until GREEN; RED evidence MUST remain durable for its failed subject. | MUST | ADR-PWV2-005 | accepted |
| PWV2-REQ-037 | Review provenance stored by Project Workflow MUST be semantic-only; concrete runtime worker/model/session/invocation identity is non-canonical unless a future explicit audit requirement justifies it. | MUST | ADR-PWV2-005 | accepted |
| PWV2-REQ-038 | Normal behavior/code workstreams MUST retain at least one independent final-integration review unless exact stronger review coverage fully covers the same final subject/acceptance surface. | MUST | ADR-PWV2-005 | accepted |
| PWV2-REQ-039 | Every new or materially revised Master Plan MUST receive independent Plan Review; only mechanical/editorial plan changes that do not alter strategy, milestone structure, requirement coverage or accepted gates may omit it. | MUST | ADR-PWV2-005 | accepted |
| PWV2-REQ-040 | Definition completion before material Strategic Planning MUST trigger premium stop A and MUST NOT automatically enter Planning. | MUST | ADR-PWV2-005 | accepted |
| PWV2-REQ-041 | Strategic Planning MUST be performed using the best available model/context as a human-facing recommendation, without hard-coding a product model name into canonical workflow. | MUST | ADR-PWV2-005 | accepted |
| PWV2-REQ-042 | After the exact Master Plan subject is frozen, premium stop B MUST require a fresh independent best-model context; the planner MUST NOT internally spawn Stage-6 Plan Review. | MUST | ADR-PWV2-005 | accepted |
| PWV2-REQ-043 | After GREEN Plan Review is durably approved, premium stop C MUST occur before Execution Prep, with recommendation to switch to a lighter/cheaper model. | MUST | ADR-PWV2-005 | accepted |
| PWV2-REQ-044 | Material later re-entry into Strategic Planning MUST repeat the full A -> Planning -> B -> Plan Review -> C premium block. | MUST | ADR-PWV2-005 | accepted |
| PWV2-REQ-045 | Qualified micro-fixes MAY bypass full Strategic Planning/premium planning block only after the mandatory issue diagnosis + user-alignment Brainstorming boundary. | MUST | ADR-PWV2-003; ADR-PWV2-005 | accepted |
| PWV2-REQ-046 | Adaptive grilling MUST be intrinsic to every Brainstorming scope; `#grill` MUST NOT be an active V2 operator command. | MUST | ADR-BGR-002; accepted V2 Brainstorming | accepted |
| PWV2-REQ-047 | Brainstorming questions MUST focus on genuine user/product/strategic choices, be thematic/numbered, include recommendations, and continue while another sensible round has material expected decision value. | MUST | ADR-BGR-002 | accepted |
| PWV2-REQ-048 | Agent-findable facts MUST remain agent-owned and use Research rather than being pushed to the user; Brainstorming completion MUST include a final challenge/completion audit. | MUST | ADR-BGR-002 | accepted |
| PWV2-REQ-049 | Every Research/diagnosis MUST perform a mandatory-but-proportional prior-art check across relevant official/upstream evidence, project/runtime evidence, issue/discussion trackers, and practitioner/community sources where available. | MUST | ADR-PWV2-006 | accepted |
| PWV2-REQ-050 | Research MUST explicitly distinguish source weight; community evidence may reveal practical failure modes/workarounds but MUST NOT be treated as authority merely because it is popular. | MUST | ADR-PWV2-006 | accepted |
| PWV2-REQ-051 | V2 MUST preserve global YAGNI/proportional design: every material extra complexity requires concrete current justification and YAGNI MUST NOT excuse missing correctness/security/testing/maintainability/compatibility/migration/observability obligations. | MUST | ADR-PWV2-006 | accepted |
| PWV2-REQ-052 | Every implementation change MUST have a precise bounded Task Card/fix contract; a separate technical-contract/OpenSpec artifact MUST be JIT/selective and created only when it adds material behavior/design-contract value beyond the Card. | MUST | ADR-PWV2-006 | accepted |
| PWV2-REQ-053 | `#issue` MUST authorize diagnosis/intake only, never automatic implementation. | MUST | ADR-PWV2-003 | accepted |
| PWV2-REQ-054 | After enough read-only `#issue` diagnosis exists to propose a repair, the workflow MUST present diagnosis, intended end state, material safety/side-effect considerations and a recommendation, then require at least one subsequent user response before any implementation mutation. | MUST | ADR-PWV2-003 | accepted |
| PWV2-REQ-055 | If the user asks for explanation, challenges safety, changes desired behavior or exposes alternatives, adaptive Brainstorming MUST continue until the repair outcome is sufficiently aligned. | MUST | ADR-PWV2-003 | accepted |
| PWV2-REQ-056 | Where GitHub Issues capability is available/enabled, `#issue` and `#feature` SHOULD create or recover an official GitHub Issue tracker after duplicate/recovery checks. | MUST | ADR-PWV2-003 | accepted |
| PWV2-REQ-057 | GitHub Issue tracker state MUST remain human-visible bookkeeping, not canonical Project Workflow authority or implementation authorization. | MUST | ADR-PWV2-003 | accepted |
| PWV2-REQ-058 | Workstream durable state MUST retain an exact tracker reference sufficient to reconnect GitHub Issue, workstream and final PR. | MUST | ADR-PWV2-003 | accepted |
| PWV2-REQ-059 | Intermediate PRs MUST NOT close a GitHub tracker unless they complete the whole accepted scope; the final scope-completing default-branch PR SHOULD use GitHub closing linkage when supported. | MUST | ADR-PWV2-003 | accepted |
| PWV2-REQ-060 | Close MUST read back expected GitHub Issue state and MAY explicitly close only after durable accepted completion when automatic close is unavailable/disabled. | MUST | ADR-PWV2-003 | accepted |
| PWV2-REQ-061 | Before final integration/publication, V2 MUST refresh current target truth, reconcile the smallest authorized target movement, run affected verification, decide review reuse only after refresh, and reread the target immediately before mutation when necessary. | MUST | accepted Brainstorming Stage 10 | accepted |
| PWV2-REQ-062 | Target commit/SHA movement alone MUST NOT invalidate GREEN when exact covered content/behavior and acceptance are unchanged and affected compatibility verification is GREEN. | MUST | accepted Brainstorming Stage 10 | accepted |
| PWV2-REQ-063 | Material behavior/content/acceptance reconciliation MUST create a new exact review subject. | MUST | accepted Brainstorming Stage 10 | accepted |
| PWV2-REQ-064 | Workstream terminal recovery MUST survive source-branch disappearance after merge; unique recovery artifacts MUST be durable independently of a soon-to-be-deleted source ref. | MUST | accepted Brainstorming Stage 10 | accepted |
| PWV2-REQ-065 | GitHub automatic deletion of merged head branches MUST be treated as valid normal cleanup realization; if a safe surviving branch cannot be deleted immediately, a minimal exact `safe_to_delete` fallback MAY be used with revalidation before deletion. | MUST | accepted Brainstorming Stage 10 | accepted |
| PWV2-REQ-066 | Deployment/live-write status alone MUST NOT create a human stop; only an explicit accepted authorization gate does. | MUST | accepted Brainstorming Stage 10/11 | accepted |
| PWV2-REQ-067 | Router MUST continue automatically whenever the next legal obligation is deterministic and already authorized, except for real human-owned stops and premium stops A/B/C. | MUST | accepted Brainstorming Stage 11 | accepted |
| PWV2-REQ-068 | Real stops MUST include unresolved user/product choice, explicit accepted authorization gate, non-remediable access/runtime/input blocker, explicit user stop, end of approved scope, and premium stops A/B/C. | MUST | accepted Brainstorming Stage 11 | accepted |
| PWV2-REQ-069 | V2 MUST NOT implement a Project Workflow Context Health/FRESH lifecycle; normal context/runtime replacement MUST recover from durable state. | MUST | accepted Brainstorming Stage 11 | accepted |
| PWV2-REQ-070 | At true end of approved scope the workflow MUST report durable completion and stop without inventing new work or requiring a workflow “what next?” prompt. | MUST | accepted Brainstorming Stage 11 | accepted |
| PWV2-REQ-071 | Fresh ChatGPT handoffs at genuine fresh-context gates MUST be ready-to-copy locator-only prompts containing the smallest project/branch/entry-obligation/durable-pointer data needed for recovery, not copied workflow narrative/evidence. | MUST | accepted V1 salvage | accepted |
| PWV2-REQ-072 | Legacy V1 support MUST be bounded migration tooling/readers only; V2 MUST NOT carry permanent legacy semantic routes into normal `workflow/`. | MUST | accepted V2 migration direction | accepted |
| PWV2-REQ-073 | Fork downstream release versioning MAY be preserved as a trigger-only optional module and MUST NOT load for ordinary non-fork work. | MUST | accepted V1 salvage | accepted |
| PWV2-REQ-074 | V2 implementation MUST provide automated validation for deterministic contracts/state/router/migration behavior and reserve manual tests for real ChatGPT/Codex/plugin/model-switch/GitHub integration behavior. | MUST | `brainstorming/V2_VALIDATION_MATRIX.md` | accepted |
| PWV2-REQ-075 | Deferred N-CAPABLE and N-CHATGPT orchestration-topology continuity scenarios MUST be executed against real V2 implementation before first production acceptance. | MUST | `brainstorming/V2_VALIDATION_MATRIX.md` | accepted |
| PWV2-REQ-076 | The V1->V2 coverage matrix MUST be used as a regression checklist so every V1 production surface remains explicitly kept, generalized, trigger-only, migration-only, bootstrap-only or dropped. | MUST | `brainstorming/V1_TO_V2_COVERAGE_MATRIX.md` | accepted |

## Constraints

- V2 production target is the new clean repository `elmakus/project_workflow_v2`, currently empty at Definition time.
- The current `elmakus/chatgpt-codex-project-workflow` repository remains development/history authority while V2 is being defined/planned/built.
- The V2 implementation should be smaller than the combined V1 policy-local system and MUST avoid abstractions/state that exist only for hypothetical extensibility.
- Codex context economy is a first-class constraint: workflow semantics must be progressively disclosed rather than injected broadly.
- Canonical workflow semantics MUST remain product-neutral except where a surface bootstrap/human UX contract inherently differs.
- The workflow must preserve human agency for issue repair/product/strategy decisions and must not infer user authorization from a marker alone.
- Exact V2 schema/file names/field names not fixed above are implementation details to choose during Planning/Execution under YAGNI.

## Non-goals

- Maintaining two independent ChatGPT/Codex Project Workflow products.
- Preserving V1 policy-local semantic duplication for compatibility.
- Persisting concrete model/worker/session/runtime orchestration telemetry in Project Workflow state.
- Reintroducing Project-Card parallel execution or scheduler machinery.
- Reproducing Context Health or forcing fresh chats for ordinary context hygiene.
- Creating a mandatory OpenSpec artifact for every trivial change.
- Making GitHub Issues the authoritative requirements/plan/execution state.
- Building a mutable global workstream registry, generic project DAG engine, or second project-control database.
- Pinning each project to an exact workflow patch version solely to handle plugin update lag.
- Owning repository provisioning/plugin/MCP pinning that belongs to `newproject-skill`.
- Copying complete workflow semantics into ChatGPT Project Instructions or Codex Skill/hook bootstrap.

## Global invariants

- Durable repository authority outranks chat recollection.
- Runtime portability must not weaken semantic correctness obligations.
- One active Project Workflow Card per selected workstream.
- Main/coordinator is the sole shared Project Workflow state reconciler/writer for delegated work.
- Exact authority references outrank summaries.
- Review independence is defined relative to the exact subject.
- External writes with meaningful readback use action/write -> readback -> verify -> evidence.
- User-owned product/strategy/repair decisions are not silently made by implementation agents.
- Adaptive grilling is the default Brainstorming interaction method.
- Research always performs a proportional external prior-art check.
- YAGNI rejects speculative complexity but never current quality obligations.
- The plugin is a delivery/bootstrap mechanism for the same workflow, not another semantic product.

## External contracts / dependencies

- GitHub repository/branch/PR/Issue behavior and connected GitHub capabilities.
- ChatGPT Project Instructions as user-owned bootstrap configuration.
- Codex plugin packaging, SessionStart hook, Skill invocation and installed package-root semantics.
- External `newproject-skill` for per-repository plugin/MCP/Skill provisioning.
- Existing `codex_workflow` or future runtime orchestration may realize internal Codex workers, but Project Workflow V2 must not depend on its concrete role/model/session schema.
- OpenSpec may be used as one realization of the optional technical-contract mechanism; V2 semantics must not require OpenSpec for every change.

## Data integrity / idempotency / security constraints

- Re-entering the same managed request MUST recover/deduplicate the exact workstream/GitHub Issue when it already exists rather than creating a duplicate.
- Recovery MUST never repeat accepted completed work merely because runtime/session state was lost.
- Review attempt subjects/verdict history MUST remain immutable per exact reviewed subject.
- Branch cleanup MUST never delete a ref whose current head no longer matches the exact verified safe head.
- External writes MUST not be blindly replayed after ambiguous interruption.
- User authorization boundaries MUST be durable/explicit where they affect mutation legality.
- Runtime-neutral state MUST retain all semantic properties required for correctness (for example reviewer independence or accepted authorization), even when concrete runtime telemetry is omitted.

## Acceptance-level requirements

Definition is accepted only if downstream implementation can demonstrate all of the following:

- ChatGPT and Codex enter the same common V2 semantics from different thin bootstraps.
- A V2 workstream can move ChatGPT -> Codex -> ChatGPT without state conversion.
- Codex plugin update receives changed canonical `workflow/` semantics without duplicate Skill/hook policy edits.
- `$pw:project_workflow_v2` resolves in the installed plugin and uses bundled local workflow authority.
- Adaptive grilling occurs automatically without `#grill`.
- A symptom-only `#issue` cannot autonomously proceed to implementation; at least one post-diagnosis user alignment response is required.
- `#issue` / `#feature` can create/recover a correlated GitHub Issue tracker and final accepted integration closes it only at the correct boundary.
- Research checks official/upstream, issue/discussion and community prior art proportionally rather than using official docs only.
- A trivial fix can be rigorously executed with Task Card contract alone; a materially contract-heavy change can trigger JIT technical-contract/OpenSpec handling.
- One Project Workflow Card executes at a time while Codex/runtime may internally delegate/parallelize its realization.
- Review attempt history, RED correction, new subject and independent GREEN work across runtime/context transitions.
- Premium stops A/B/C behave exactly as specified.
- Final integration handles target movement without needless re-review and creates new review subject only when covered content/acceptance actually changes.
- Completed work remains recoverable after source branch auto-deletion.
- V1 legacy constructs listed as DROP in the coverage matrix are absent from new V2 normal semantics.
- Automated and manual validation matrix scenarios reach GREEN before first production acceptance.

## Definition completeness

Definition Complete = GREEN:
- target state and all material MUST requirements are explicit;
- constraints/non-goals/global invariants are explicit;
- accepted architecture/product choices are captured in ADR-PWV2-001..006;
- no unresolved user/product choice remains that can materially alter Strategic Planning;
- no blocking Research obligation remains;
- V1 salvage/coverage and V2 validation matrices are complete;
- the production target repository exists and is ready for planned implementation;
- the next legal role is Strategic Planning, gated by premium stop A.

## Downstream coverage

Strategic Planning must map PWV2-REQ-001..076 into:
- V2 repository skeleton/bootstrap/plugin packaging;
- canonical common lifecycle modules;
- workstream/state/templates/migration model;
- GitHub Issue integration;
- automated test suites and live-test checkpoints;
- migration/deprecation handling;
- staged implementation order that preserves V1 historical reference and avoids premature cutover.
