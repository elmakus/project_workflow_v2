# Project Research — Universal Coordinator Protocol

Status: ACTIVE
Authority: non-authoritative orchestration convention for this research archive
Repository: elmakus/project-research
Applies to: formal Research swarms, Targeted/Global bug hunts, bounded Repair swarms, post-repair Revalidation swarms, and equivalent reusable multi-chat orchestration
Does not replace: consumer Project Workflow authority, Review semantics, implementation authorization, or project-specific overlays

## 1. Purpose

This protocol defines how a long-lived ChatGPT Main coordinator should organize substantial multi-chat Research, discovery, repair and revalidation work while minimizing user choreography and preserving independence, coverage, reproducibility, bounded mutation and durable recovery.

The default architecture is:

Main coordinator
-> independent evidence lanes
-> ONE post-wave integration chat
-> owner-ready durable result

Fresh chats are used where independence, contamination control, isolation or context reset materially improves quality. They are not created merely because a mechanical stage has a different name.

## 2. Coordinator role

Main is the coordinator, not the default worker.

Main owns:
- recovering current durable state and applicable workflow authority;
- framing the question;
- freezing the common evidence baseline / analysis subject;
- decomposing the topic into lanes;
- ensuring coverage of the full problem;
- deciding which overlap is epistemically useful;
- defining independence and contamination rules;
- writing the durable orchestration package;
- consuming the final integrated result;
- deciding the next global obligation.

Main MAY perform bounded deterministic tool/repository work directly when that avoids an unnecessary user handoff and does not materially impair later judgment.

Optimization target:

> minimize total user choreography and coordinator cognitive load, subject to required independence, evidence quality, recoverability and semantic correctness.

## 3. ChatGPT research economics

Worker token/model/computation cost is NOT an optimization target.

Do not reduce useful lane count, overlap or falsification just to save worker tokens.

The scarce resources are:
- Main's usable context/attention;
- the user's manual chat choreography;
- contamination/independence risk;
- fragmentation caused by unnecessary handoffs.

## 4. Formal research swarm shape

The 1 + 1 + minimum-8 rule applies ONLY to substantial FORMAL RESEARCH.

Every substantial formal Research wave uses at least:

1. ONE whole-scope/generalist worker;
2. ONE independent red-team/falsification worker;
3. at least EIGHT targeted research workers.

Therefore a normal formal research swarm has at least TEN independent workers before integration.

The coordinator MAY use more than eight targeted workers whenever the topic needs finer coverage.

Small ad-hoc lookups or bounded questions are not automatically a formal research wave. Once Main chooses formal/swarm Research, the minimum above applies unless the owner explicitly overrides it.

This minimum does NOT apply to bug-hunt/red-team swarms.

### 4.1 Whole-scope worker

The whole-scope worker independently analyzes the complete research question end-to-end.

Purpose:
- produce one coherent global model;
- catch omissions introduced by decomposition;
- give synthesis an independent full-scope baseline.

It must not read targeted-lane or red-team outputs before committing its own result.

### 4.2 Red-team worker

The red-team worker independently attempts to falsify:
- the framing;
- hidden assumptions;
- proposed decomposition;
- likely conclusions;
- rollout/cutover/rollback logic;
- evidence sufficiency;
- negative-space and counterexamples.

It must not read sibling outputs before committing its own result unless the research design explicitly defines a later adversarial pass.

### 4.3 Minimum eight targeted workers

At least eight targeted workers must collectively cover the entire material subject.

Before launch, Main writes a COVERAGE MATRIX mapping:
- material subtopics/questions;
- owning targeted lane(s);
- cross-cutting seams;
- expected evidence classes;
- known blind spots.

Coverage rule:
- every material subtopic must have at least one targeted owner;
- important cross-boundary/high-risk seams SHOULD be covered by at least two lanes from different angles;
- modest overlap is desirable where it tests framing or boundary assumptions;
- avoid overlap only when it is pure duplication with no distinct epistemic value.

The eight-lane minimum is a floor, not a target ceiling.


### 4.4 Finite heterogeneous auto-lane allocation

For any **finite heterogeneous swarm** whose distinct work units are known before launch, the preferred low-choreography realization is one identical reusable launcher plus one immutable lane/unit manifest.

Default validated mechanism: `finite_branch_claim`.

This applies, when the work is actually finite and heterogeneous, to:
- formal Research lanes such as W00/R00/L01...;
- Targeted Bug Hunt lanes derived from a frozen risk/coverage matrix;
- bounded Repair Units produced only after findings have been integrated/deduplicated and the coordinator has frozen their scopes/conflict relations;
- post-repair Revalidation/impact lanes when multiple distinct affected surfaces require independent fresh judgment;
- equivalent future finite heterogeneous worker sets.

It does **not** replace the monotonic run-ID/CAS allocator for homogeneous/open-ended swarms where every worker executes the same prompt, such as the Global identical-prompt Bug Hunt.

The package defines, for every lane/unit:
- exact lane/unit ID;
- exact worker prompt path;
- exact result branch;
- exact output path;
- one common exact frozen base / analysis-or-mutation subject;
- any scope/admission metadata required by that swarm type.

Path-resolution invariant:
- every package prompt that references this universal protocol MUST use the repository-root path `/COORDINATOR_PROTOCOL.md` or explicitly say `repository-root COORDINATOR_PROTOCOL.md`;
- a bare `COORDINATOR_PROTOCOL.md` MUST be resolved from the repository root, never relative to the topic/package directory;
- launchers/integration prompts SHOULD use the explicit repository-root wording so a fresh worker cannot reinterpret the path;
- before declaring the protocol missing, a worker MUST check the repository root on the instructed/default ref.

Each fresh worker:
1. reads the same immutable manifest and launcher;
2. scans unclaimed lanes/units strictly sequentially in deterministic manifest order and attempts at most one branch creation at a time;
3. atomically attempts to create that lane/unit's exact result branch from the exact frozen base;
4. owns it only after successful branch creation followed by exact branch-head readback;
5. on the **first** successful create + readback, records exactly one claimed lane/unit and **immediately exits the claim loop**;
6. after a successful claim, MUST NOT inspect, create or claim any later lane/unit branch in the same invocation;
7. treats an existing-ref/conflict response as a lost race only while it has not yet claimed anything, then tries the next lane/unit;
8. stops as `EXHAUSTED` only when this invocation acquired **zero** claims and every finite lane/unit was already claimed;
9. after claiming, reads only its assigned prompt, executes exactly that one assignment and writes only its assigned output on that branch.

Hard invariant: **one worker invocation may successfully claim at most one finite heterogeneous lane/unit**. Pre-creating, reserving or probing later claim branches after the first successful claim is a protocol violation.

Reference algorithm:

```text
claimed = none
for unit in manifest_order:
  result = try_create(unit.branch, frozen_base)
  if result == success:
    require(readback_head(unit.branch) == frozen_base)
    claimed = unit
    break
  if result == existing_ref_or_conflict:
    continue
  fail_closed()

if claimed == none:
  return EXHAUSTED

execute_exactly(claimed)
```

The result branch itself is the claim lock. Do not add a mutable central allocator merely to assign finite heterogeneous work.

#### Repair-swarm constraint

`finite_branch_claim` allocates only **pre-authorized frozen Repair Units**. Before launch, the coordinator/integrator must already have:
- integrated/deduplicated the findings;
- frozen the exact repair base;
- grouped shared-root/shared-owner findings where required;
- recorded each unit's included/excluded scope;
- recorded write, semantic/invariant and external-effect claims;
- classified pairwise relations conservatively as GROUP, SERIALIZE or PARALLEL.

A repair worker MUST NOT invent a sibling repair, widen its scope, change conflict classification, merge sibling work or self-accept. Workers prove their bounded repair on their own branch; one integration owner later proves composition on the shared candidate.

#### Revalidation-swarm constraint

A finite Revalidation/impact swarm allocates only **predefined affected surfaces/questions**. A worker may gather evidence and return the assigned disposition/recommendation, but it MUST NOT rewrite canonical dependency/acceptance authority, silently invalidate unrelated Results, or authorize downstream repair outside its assignment. Deterministic cheap reruns should not be turned into fresh-chat lanes merely to use the allocator.

#### Crash and reclaim behavior

- a branch claimed at the frozen base with no result commit is durably `CLAIMED_INCOMPLETE`;
- it MUST NOT be silently reassigned by elapsed time;
- reclaim requires explicit owner/coordinator authorization after exact branch/base/output readback;
- ordinary V1 reclaim deletes only the abandoned disposable claim branch, then a fresh worker may recreate the same exact branch from the same frozen base;
- when the allocator/launcher itself is defective or branch deletion is unavailable, an explicitly authorized **claim-generation reset** MAY be used instead: verify every affected old-generation branch has no result commit/output, publish a new package/manifest control-plane generation, assign fresh generation-specific branch names, and make only that new generation current;
- superseded generation branches remain durable non-current recovery evidence and MUST NOT count as active claims for the new generation;
- **partial reclaim MUST preserve the wave's original `research_base`** for every replacement lane/unit. Publishing a repaired launcher/manifest does not change the evidence base;
- distinguish `package_revision` (the live/main commit containing orchestration fixes) from `research_base` (the immutable branch start for evidence lanes). They may differ after a control-plane repair;
- if a proposed repair truly requires a different `research_base`, Main MUST either reset the entire wave onto that new common base or finish the existing wave; it MUST NOT retain completed lanes from the old base while launching only a subset from the new base;
- integration validates each accepted lane against the single wave `research_base`, not against the latest package publication commit;
- a generation reset MUST record the superseded generation/reason and the unchanged wave `research_base` in the manifest/package;
- autonomous timeout reclaim is forbidden unless a later design adds explicit generations/fencing.

Allocation state is orchestration metadata only and never consumer workflow authority.

Validated evidence:
- `experiments/identical-multilane-v1/RESULT.md`.

Per-lane launchers remain the fallback for small waves, read-only environments, or when branch creation is unavailable.

### 4.5 Allocator selection rule

Choose the allocator from the shape of the frozen work, not from the workflow phase name:

- **finite + heterogeneous work units** -> `finite_branch_claim`;
- **homogeneous/open-ended repeated identical prompt** -> monotonic `RUN_ID` allocation via `NEXT_RUN_ID.txt` + compare-and-swap;
- **single independent reviewer / Plan Review / one-off final reviewer** -> no swarm allocator;
- **small finite wave where explicit launchers are simpler** -> per-lane launchers remain valid fallback.

The user's interaction goal is the same whenever a reusable swarm is used: one exact launcher that can be pasted repeatedly without editing lane IDs, run IDs, branch names or output paths.

Allocator choice is non-semantic orchestration policy and MUST NOT alter consumer Project Workflow legality, authority, scope or acceptance.

## 5. Bug-hunt / red-team swarm mode

For this protocol, **bug hunt** and **red-team swarm** are the same swarm pattern: many independent fresh workers attack the same bounded subject with the same adversarial prompt, then one integration pass deduplicates and clusters findings.

This is different from the single red-team/falsification worker used inside a formal Research wave. To avoid ambiguity:

- **Research R00 red-team worker** = one adversarial lane inside the 1 + 1 + minimum-8 Research design.
- **Bug-hunt / red-team swarm** = N repetitions of ONE identical adversarial worker prompt.

### 5.1 User-controlled swarm size

There is no fixed minimum or maximum worker count for a bug-hunt/red-team swarm.

The coordinator prepares ONE reusable universal worker prompt.

The user may paste the exact same launcher into:
- 5 fresh chats;
- 10 fresh chats;
- 50 fresh chats;
- or any other number the user chooses.

The user MUST NOT need to edit a letter, run number, branch name, output path or any other per-worker field before pasting.

### 5.2 Automatic run identity allocation

The reusable prompt must allocate its own unique run identity.

Default durable mechanism:

- package contains `NEXT_RUN_ID.txt`;
- each fresh worker reads the allocator value and current blob SHA;
- it atomically claims the next ID using compare-and-swap / expected-SHA update;
- if the claim loses a race, the worker rereads the allocator and retries;
- after successful claim, that worker owns exactly one `RUN_ID`.

Suggested IDs:

`R100`, `R101`, `R102`, ...

The counter value is allocation metadata only. It is never workflow or research semantic authority.

### 5.3 Per-run isolation

After claiming `RUN_ID`, the worker creates its own isolated branch from the wave's frozen analysis/research base.

Recommended branch:

`bughunt/<scope_slug>-<RUN_ID>`

Recommended output:

`<bughunt_root>/runs/<RUN_ID>/FINDINGS.md`

Each worker:
- reads the same universal prompt;
- analyzes the same frozen subject;
- does NOT read sibling run findings/branches;
- does NOT modify another run's output;
- records exact evidence/reproduction details;
- commits and pushes its own findings;
- stops.

The swarm is intentionally repetitive. Different workers may independently find the same defect; deduplication happens later.

### 5.4 Universal prompt package

A bug-hunt package should normally contain:

```text
<bughunt_root>/
  BUG_HUNT_PLAN.md
  AUTO_PROMPT.md
  NEXT_RUN_ID.txt
  runs/
    <RUN_ID>/FINDINGS.md
  INTEGRATION_PROMPT.md
  FINAL_FINDINGS.md
```

The coordinator gives the user the same launcher every time:

```text
Repo: elmakus/project-research

Przeczytaj i wykonaj dokładnie:
<bughunt_root>/AUTO_PROMPT.md
```

No manual substitution is permitted.

### 5.5 Bug-hunt worker scope

Unless explicitly authorized otherwise, bug-hunt/red-team workers:
- investigate;
- reproduce;
- localize;
- collect evidence;
- classify likely root-cause families;
- identify negative-space/failure-mode cases;
- propose regression tests;
- do NOT implement fixes.

The integration chat later:
- discovers all valid allocated/completed runs;
- validates branch/output integrity;
- deduplicates findings;
- clusters shared root causes;
- resolves contradictory reproductions where possible;
- identifies cross-run causal families;
- persists the durable bug-hunt result.

Implementation/repair then follows the consumer project's normal authority.

### 5.6 No per-worker launch choreography

The coordinator must not generate 5/10/50 unique prompts for a bug-hunt swarm.

One `AUTO_PROMPT.md` is the contract.

The only repeated human action is opening another fresh chat and pasting the exact same launcher again.

## 6. Repository and durable package location

This repository is the default durable archive:

`elmakus/project-research`

Project-specific research:

`projects/<primary-consumer>/<horizon-or-topic>/<topic_slug>/`

Cross-project research with no single primary consumer:

`shared/<cross-project-domain>/<topic_slug>/`

A typical FORMAL RESEARCH package:

```text
<topic_slug>/
  RESEARCH_PLAN.md
  COVERAGE_MATRIX.md
  prompts/
    W00_WHOLE_SCOPE.md
    R00_RED_TEAM.md
    L01_<slug>.md
    ...
    L08_<slug>.md
    ...more if needed
  lanes/
    W00_WHOLE_SCOPE.md
    R00_RED_TEAM.md
    L01_<slug>.md
    ...
  INTEGRATION_PROMPT.md
  FINAL_SYNTHESIS.md
```

Bug-hunt/red-team swarm packages use the reusable `AUTO_PROMPT.md` + allocator design from Section 5 instead of per-worker Hxx prompts.

Essential orchestration state must be durable before worker launch.

## 7. Branch naming

Each wave starts from one exact frozen `project-research/main` commit.

Formal research branches:

- whole-scope: `research/<scope_slug>-W00-whole-scope`
- red-team: `research/<scope_slug>-R00-redteam`
- targeted: `research/<scope_slug>-L<nn>-<lane_slug>`
- integration: `research/<scope_slug>-integration`

Bug-hunt/red-team swarm branches:

- worker run: `bughunt/<scope_slug>-<RUN_ID>`
- integration: `bughunt/<scope_slug>-integration`

`RUN_ID` is allocated automatically by the shared allocator; the user never edits it.

Project-specific overlays MAY impose a more specific prefix, but must preserve one-branch-per-logical-lane.

Do not reuse a branch for a different logical worker.

## 8. Frozen baseline and common analysis subject

Before launch Main freezes:

1. `research_base`: exact `project-research/main` commit from which every evidence lane branch starts;
2. `analysis_subject`: exact immutable repository/ref/commit set the lanes analyze, when applicable;
3. `package_revision`: the current control-plane revision containing the launcher/manifest. At initial launch it may equal or follow `research_base`; later orchestration-only repairs may advance it without changing `research_base`.

`research_base` is wave identity, not "latest package commit". Once any lane has completed, a partial reclaim or launcher repair MUST NOT move it.

All independent lanes in the same wave analyze the SAME immutable subject.

Workers may read live routing/authority required by the consumer workflow, but must not silently replace the pinned subject with a later moving HEAD.

If live state drifts:
- record the drift;
- continue against the pinned subject unless the assignment says the drift invalidates the wave;
- reconcile material drift once, during integration.

## 9. Durable wave design before launch

Before showing the user launchers for FORMAL RESEARCH, Main must persist:

- `RESEARCH_PLAN.md`;
- `COVERAGE_MATRIX.md`;
- exact research base and analysis subject;
- whole-scope prompt;
- red-team prompt;
- at least eight targeted prompts;
- expected branch + artifact for every worker;
- sibling-independence rules;
- one `INTEGRATION_PROMPT.md`;
- stop conditions and forbidden mutations;
- any project-specific overlay references.

Before launching a BUG-HUNT/RED-TEAM SWARM, Main instead persists:
- `BUG_HUNT_PLAN.md`;
- exact frozen subject/base;
- one reusable `AUTO_PROMPT.md`;
- `NEXT_RUN_ID.txt`;
- output/branch naming rules derived from claimed `RUN_ID`;
- one `INTEGRATION_PROMPT.md`;
- stop conditions and forbidden mutations.

Do not generate per-run prompts for bug hunt.

Do not leave required merge/synthesis choreography only in Main's chat.

## 10. Lane contract

Each worker is a bounded fresh assignment.

Unless explicitly authorized otherwise, each lane:
- validates its frozen base and analysis subject;
- reads only evidence required for its assignment;
- does not read sibling outputs/branches before its own commit;
- does not select the next global obligation;
- does not modify production/consumer authority;
- writes only assigned durable artifacts;
- commits and pushes only its assigned branch;
- returns a compact result and stops.

Compact result should include:
- branch;
- commit SHA;
- artifact path;
- exact subject actually analyzed;
- key findings;
- anomalies/blockers/drift;
- intentionally unverified scope.

Compact results are for visibility; Git is the durable transport.

## 11. Handoff budget

Every additional fresh chat after the evidence lanes needs a concrete justification.

Valid reasons:
- true independent judgment is required;
- contamination would invalidate the result;
- mutation isolation is required;
- context size materially threatens quality;
- a separately independent reviewer/falsifier is itself part of the evidence design.

Invalid reasons:
- merge is a separate phase;
- readback is a separate phase;
- drift reconciliation is a separate phase;
- synthesis has a different name;
- final reconciliation has a different name;
- the protocol happens to contain a separate file.

Default after all lanes finish:

> ONE fresh integration chat performs all mechanical and integrative follow-up that does not require separate independence.

## 12. User interaction

Main returns short launcher blocks only.

### 12.1 Launcher presentation contract

When Main presents one or more launchers to the user:

1. every launcher MUST have a sequential human-facing number;
2. every launcher MUST have a short descriptive title;
3. the number and title MUST be outside the code block;
4. every launcher MUST be in its own separate fenced code block;
5. each code block MUST contain only the exact copy/paste launcher text;
6. multiple launchers MUST NEVER be combined into one code block;
7. do not require the user to delete labels, numbering, commentary or sibling launchers before pasting.

Required presentation shape:

**1. Whole-scope**

```text
Repo: elmakus/project-research

Przeczytaj i wykonaj dokładnie:
<durable prompt path>
```

**2. Red-team**

```text
Repo: elmakus/project-research

Przeczytaj i wykonaj dokładnie:
<durable prompt path>
```

The numbering is presentation-only and does not replace durable worker IDs such as W00, R00 or L01. A short title SHOULD make the worker's purpose recognizable without opening the prompt.

For any finite heterogeneous swarm covered by section 4.4, use explicit per-lane launchers only for small waves/fallbacks; otherwise prefer the validated `finite_branch_claim` mode. Main presents ONE numbered/titled reusable launcher block, and the user pastes that exact same launcher into as many fresh chats as needed. This includes formal Research, Targeted Bug Hunt, eligible Repair swarms and eligible Revalidation swarms.

For bug-hunt/red-team swarm mode, Main presents ONE numbered/titled launcher block for the reusable `AUTO_PROMPT.md`. The user then pastes that exact same block into as many fresh chats as desired; do not generate per-run launchers.

When the user says the Research lane set is complete, or says the bug-hunt swarm is large enough/finished, that signal is sufficient to start the prewritten integration path.

Do not require the user to paste every compact result.
Do not make Main manually enumerate and reread every branch first.

## 13. One-chat integration by default

The default integration chat may sequentially:

1. harvest/validate all expected branches and artifacts;
2. validate base/scope/independence metadata;
3. perform clean mechanical merges;
4. run validators/tests/reproductions;
5. target-side readback;
6. reconcile material live drift against the pinned subject;
7. read all merged lane evidence;
8. deduplicate findings;
9. resolve evidence conflicts;
10. synthesize cross-lane conclusions;
11. compare with authorized prior/preliminary research;
12. perform final reconciliation;
13. persist the owner-ready result;
14. update the durable continuation/handoff.

It should do all of that in ONE chat unless a valid fresh-context reason arises.

It stops and escalates rather than continuing when:
- substantive merge conflict requires semantic choice;
- evidence was materially rewritten/contaminated;
- independence of the next judgment would be invalid;
- unresolved contradictions require a separately independent evaluator;
- the context has become unreliable for the final judgment.

A separate mechanical "final merge worker" after a completed final synthesis is normally unnecessary: the same integration assignment should publish/read back its own final durable artifact when that publication is deterministic and authorized.

## 14. Synthesis rules

Synthesis is evidence-weighted, not vote-counted.

Agreement among many lanes increases confidence only when the lanes were meaningfully independent.

Resolve conflicts using:
- applicable authority;
- source quality;
- direct reproducibility;
- causal explanation;
- counterexamples;
- explicit owner decisions;
- negative evidence.

Preserve material disagreement when evidence does not resolve it.

## 15. Main drill-down rule

Main normally consumes the integrated result, exact durable locators and reported anomalies.

Main drills into raw lane reports only when:
- outputs conflict materially;
- the integration reports an anomaly;
- a finding is surprising or high-impact;
- information needed for the next owner decision was omitted;
- Main itself must form a semantic judgment.

## 16. Anti-patterns

Do not:
- apply the Research 1 + 1 + minimum-8 rule to bug-hunt/red-team swarms;
- generate unique manual prompts/letters/IDs for bug-hunt workers;
- require the user to edit RUN_ID, lane ID, branch or output path before launching a reusable swarm worker;
- combine multiple user launchers into one code block or omit their sequential number/short title;
- make every mechanical noun a fresh chat;
- split merge -> readback -> drift -> synthesis -> reconciliation -> final merge into a chain of user handoffs;
- require the user to relay compact results that are already durable in Git;
- optimize away independent lanes to save ChatGPT tokens;
- allow different workers in one wave to silently analyze different moving subjects;
- let workers self-select downstream/global work or invent their own Repair/Revalidation unit;
- let research or bug-hunt artifacts become consumer workflow authority by accident;
- let derived caches/session/runtime identity become semantic truth.

## 17. Project-specific overlays

A project/topic MAY define an overlay with:
- exact consumer repository;
- applicable canonical workflow;
- topic package root;
- branch prefix;
- evidence sources;
- forbidden mutations;
- runtime realization constraints;
- owner decisions specific to that project.

The overlay may narrow or add constraints, but SHOULD NOT duplicate the universal protocol.

If overlay and universal protocol conflict, the explicit project/owner instruction for that topic wins, while consumer Project Workflow authority remains supreme for workflow semantics.

## 18. Fresh coordinator bootstrap

A fresh coordinator:

1. reads applicable live consumer workflow/router first;
2. recovers exact current consumer state required by that router;
3. reads this universal protocol;
4. reads the topic/project overlay;
5. reads the exact continuation handoff/plan;
6. recovers durable research state from `project-research/main`;
7. does not replay already durable work;
8. continues from the next real evidence/coordinator obligation.

This protocol governs evidence orchestration only. It is not Project Workflow authority.
