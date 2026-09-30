# Workflow successor product — Research orchestration binding

Date: 2026-09-29
Brainstorming subject: `workflow-successor-product@1`

Formal Research archive:
- repository: `elmakus/project-research`
- package root: `projects/project_workflow_v2/successor-product/architecture-v1`
- initial research base: `193e6f38572a680ba2cabe3897021a44a9d2d8f1`
- package publication commit: `2e5211456518b715094a80cdfdce1f0bdd979cc9`
- allocator: `finite_branch_claim`
- lane set: W00, R00, L01-L10 (12 independent evidence lanes)
- integration artifact: `projects/project_workflow_v2/successor-product/architecture-v1/FINAL_SYNTHESIS.md`

The package is evidence orchestration only. It does not authorize Definition, implementation, migration, merge, issue closure or product naming.

Owner-fixed inputs carried into the package:
- no product-level parallel execution/orchestration in initial successor design;
- automatic durable anomaly -> GitHub Issue behavior is desired, without repair authorization leakage;
- versioned backward-compatible durable-state semantics are a primary goal;
- first release must be complete enough to develop its next release using itself;
- ChatGPT and Paseo are required qualification surfaces, not workflow authority.


## Pre-launch refresh — 2026-09-30

Status: **prepared / not launched**

The formal Research package was refreshed after the extended owner Brainstorming and 60-item V2/V2.2 capability disposition review.

Current package:
- repository: `elmakus/project-research`
- package root: `projects/project_workflow_v2/successor-product/architecture-v1`
- owner disposition: `FEATURE_DISPOSITION_1_60.md`
- package refresh commit: `68eb220352f95255b9f1ed1342aee8027b14655f`
- launch-manifest commit: `cd1a3c294e775574d6149fbf4cccc20fd394544e`
- claim generation: `2`
- research base: `68eb220352f95255b9f1ed1342aee8027b14655f`
- analysis subject: `workflow-successor-product-architecture-v1@2`
- integration branch: `research/workflow-successor-v1-integration-g2`

Generation 2 treats the owner decisions and the 1–60 disposition as fixed product constraints. Research is asked to falsify feasibility, find simpler prior art, expose contradictions, and determine implementation architecture; it must not casually reopen settled owner choices.

No generation-2 lane branch has been launched or claimed as part of this preparation step. The consumer `RESEARCH.toml` remains active/pending and no Research finding has been reconciled back into Brainstorming yet.


## Rich-wave expansion — 2026-09-30

Status: **prepared / not launched**

After owner clarification that the formal Research should use the full orchestration protocol with many independent lanes, the earlier 12-lane generation-2 package was superseded before any lane was claimed.

Current Research wave:
- protocol: repository-root `/COORDINATOR_PROTOCOL.md`
- allocator: `finite_branch_claim`
- claim generation: `3`
- package root: `projects/project_workflow_v2/successor-product/architecture-v1`
- research base: `1c1516ebdb675f0bfce61a52980d0ca91a50d8d8`
- manifest publication: `6ac4fc3e3831042bab93130b1b06b123a06da25a`
- analysis subject: `workflow-successor-product-architecture-v1@3`
- lane shape: 1 whole-scope + 1 independent red-team + 30 targeted lanes = 32 independent workers before integration
- integration branch: `research/workflow-successor-v1-integration-g3`

The 30 targeted lanes are grouped across lifecycle/planning, durable state/evidence/recovery, runtime/GitHub/helpers/workers, qualification/self-maintenance/anomalies, and donor/prior-art/cutover. Owner-marked “research needed” questions from Brainstorming are assigned explicitly rather than hidden inside broad generalist lanes.

Generation 2 was never launched; no generation-2 evidence is accepted into generation 3. Generation 3 is the only current launch package.

No generation-3 lane is launched by this preparation update. Consumer `RESEARCH.toml` remains active with pending return reconciliation and no finding.


## Supplemental runtime-integration deep-dive — 2026-09-30

A separate formal Research wave is prepared because the main generation-3 wave had already been fully claimed before the owner requested deeper investigation of helper/runtime integration.

Package:
- repository: `elmakus/project-research`
- root: `projects/project_workflow_v2/successor-product/architecture-v1/runtime-integration-deepdive`
- protocol: repository-root `/COORDINATOR_PROTOCOL.md`
- allocator: `finite_branch_claim`
- research base: `79017df50f402fdbdfde1621e72084982fafc068`
- manifest publication: `22715fc208af4014b7a4d7fd63a13297950b733b`
- lane shape: 1 whole-scope + 1 red-team + 12 targeted lanes = 14 workers before integration

The wave specifically researches:
- Pi/Paseo extension/bootstrap/helper packaging;
- native extension tools vs CLI vs MCP;
- Pi/Paseo live tests;
- ChatGPT Project/repo/bootstrap options;
- ChatGPT helper execution strategies;
- Android/mobile constraints;
- ChatGPT live tests;
- MCP value/cost;
- contract/helper/runtime version handshakes;
- performance/context economics;
- failure/trust boundaries.

The parent generation-3 integration prompt now requires the completed supplemental `FINAL_SYNTHESIS.md` before it may finalize the overall PWV3 architecture Research.

This preparation does not itself launch any supplemental lane or consume a Research result.


## Main-wave claim recovery and overflow fallback — 2026-09-30

A mechanical audit of generation 3 found:
- 32 declared/claimed lane branches;
- 13 valid completed lane outputs;
- 19 branches still exactly at the immutable research base with no declared output, therefore `CLAIMED_INCOMPLETE`.

Valid completed g3 lanes:
`W00, R00, L01, L02, L03, L08, L12, L18, L19, L20, L21, L22, L23`.

Reclaimed/fenced incomplete lanes:
`L04, L05, L06, L07, L09, L10, L11, L13, L14, L15, L16, L17, L24, L25, L26, L27, L28, L29, L30`.

The research package now uses partial reclaim generation 4 on the same original research base for those 19 lanes. Old empty g3 claims remain as non-current evidence and are not deleted.

The universal orchestration protocol and this wave launcher now also support opt-in overflow research after finite-lane exhaustion. Once all current finite lanes are claimed, an additional fresh worker receives a unique supplemental overflow run instead of immediately returning `EXHAUSTED`. Overflow evidence is supplemental and never substitutes for required lane completion.

Protocol/package repair publication in `elmakus/project-research`: `6222c2b35bbf0e3a940d7da807e83cd5ac19774b`.


## Generation-5 reclaim + claim-race hardening — 2026-09-30

A fresh audit after generation-4 execution showed:
- 17/19 reclaimed generation-4 lanes completed with declared outputs;
- 2 lanes remained empty at exact research_base with no output: `L07 durable-state` and `L17 helper-architecture`.

Generation 5 reclaims only L07 and L17 on new fenced branch names while preserving the same immutable research base.

A real L14 dual-writer race was also observed: two workers produced independent L14 reports on the same g4 branch. Both reports remain recoverable in Git history. The first report has been preserved as supplemental evidence in the research package; the later branch-HEAD report remains the required canonical L14 output.

The universal orchestration protocol now requires a unique fenced claim commit after branch reservation. Branch creation/readback at research_base alone no longer proves lane ownership. Competing workers create sibling claim commits; only one non-force ref update can win.

Research package hardening publication: `29726931662cc456682a893fd85ca0d2d9b2d754`.
