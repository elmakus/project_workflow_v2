# PWV3 Brainstorm revision 5 — final challenge: owner decisions required

Date: 2026-10-02
Subject: `workflow-successor-product@5`
Status: **OWNER DECISIONS REQUIRED BEFORE GREEN**

## Inputs challenged

- owner direction for R5 goal execution, mandatory subagents and 3.x→3.0 consolidation;
- integrated 20-lane Research:
  - repository: `elmakus/project-research`
  - commit: `0bdfccd332b78caa0795283ec64d366def01b511`
  - result blob: `94753f446542d03171f81a2827cb188420cf1df2`;
- prior accepted PWV3 Definition/owner invariants from revision 4 / D09.

## Findings

Most of the integrated Research is compatible with owner direction and can be carried forward without a new choice:

- one provider-neutral semantic workflow;
- one shared reviewed Execution Package for native and goal modes;
- late execution-mode selection after Package Review;
- provider qualification instead of hard-coding a package name;
- mandatory real subagent/delegated-worker use for goal mode;
- provider-neutral Goal Launch Envelope / Goal Execution Report;
- exact runtime bundle conformance testing;
- goal-owned implementation, tests, bounded implementation repair and non-independent qualification;
- external independent Global Bug Hunt;
- exact-subject repair/requalification after Global findings;
- provider-independent recovery/currentness/external-effect safety.

However, the synthesis made several product/strategy choices that Research evidence alone cannot authorize because they alter earlier owner-fixed lifecycle semantics or answer questions the owner explicitly sent to Research for recommendation.

## OD-R5-01 — launch boundary and common artifact

Research recommendation:

**A — launch goal only after GREEN Execution Package Review; the exact reviewed Execution Package is the one common semantic artifact for both `native_pwv3` and `goal`. Mode is selected only at launch.**

Alternative:
**B — launch from reviewed Plan and allow goal to perform Execution-Prep-like materialization.**

Recommendation: **A**.

Reason: Execution Prep fixes semantic Card/scope/dependency/acceptance facts. Letting goal create them privately would either duplicate canonical Execution Prep or make provider-local state semantic authority.

## OD-R5-02 — Targeted qualification boundary

Prior PWV3 owner authority made both Targeted Bug Hunt and Global Bug Hunt mandatory OP boundaries.

Research recommendation:

**A — remove the universal external Targeted Bug Hunt OP boundary. Replace it with a mandatory non-independent Targeted Qualification Campaign inside goal/native Final Qualification. Keep an external specialty targeted review only when an exact risk specifically requires independent treatment. Global remains the mandatory independent external OP hunt.**

Alternative:
**B — retain mandatory external OP Targeted Bug Hunt and Global Bug Hunt as two separate independent boundaries.**

Recommendation: **A**, because the owner's R5 intent is for goal to deliver all routine work up to the one independent Global hunt.

This is a material lifecycle change and needs explicit owner acceptance.

## OD-R5-03 — post-Global GREEN owner gate

Prior owner-fixed PWV3 invariant:
after every advance-permitting accepted OP result, stop for **CONTINUE / RUN OP AGAIN**.

Research recommendation for the R5 "user manually does only Global Bug Hunt" experience:

**A — Global CLEAR does NOT create a routine CONTINUE/RUN OP AGAIN stop. The user launches Global; once its exact result is CLEAR and applicable, canonical routing automatically continues to terminal closure acceptance. RUN OP AGAIN remains available only when explicitly requested or when another accepted policy creates that choice.**

Alternative:
**B — preserve the universal post-OP CONTINUE / RUN OP AGAIN gate after Global, so after launching Global the owner must still explicitly select CONTINUE before closure.**

Recommendation: **A** if the desired meaning of "goal dowozi do końca, ja robię tylko Global Bug Hunt" is literal.

This explicitly supersedes the earlier universal post-OP owner-gate rule for the Global boundary and therefore requires owner authority.

## OD-R5-04 — terminal closure after Global

Research recommendation:

**A — preserve fresh terminal acceptance as a PWV3 semantic predicate, but allow a qualified semantically independent, read-only, non-authoring closure reviewer to execute it automatically after applicable Global CLEAR.**

Alternative:
**B — require a separate manual/fresh terminal-acceptance handoff or owner waiver after Global.**

Recommendation: **A**, consistent with minimizing manual choreography while preserving semantic independence.

## OD-R5-05 — all later 3.x work in 3.0

Owner direction was categorical: everything previously planned for later PWV3 3.x belongs in initial 3.0.

The Research synthesis classified performance-oriented material-fingerprint optimization as genuinely future-only. That classification conflicts with owner authority and is therefore **not accepted**.

Final-challenge reconciliation:
- every previously planned later-3.x capability must be included in 3.0 either as the concrete capability or, where a literal future instance cannot yet exist (for example a reader for a not-yet-created future schema), as the complete framework/contract/harness needed so the later instance is only data/adapter work;
- material-fingerprint optimization is included in 3.0 as well;
- only truly unknowable future instances, not their supporting capability, may naturally arise later.

No owner choice is required for this item because the owner already decided it.

## Recommended owner disposition

Approve the Research architecture as one package:

- **OD-R5-01 = A**
- **OD-R5-02 = A**
- **OD-R5-03 = A**
- **OD-R5-04 = A**
- OD-R5-05 follows prior owner authority: all previously planned later-3.x capability is part of 3.0.

If approved, Brainstorm revision 5 can complete its final challenge as GREEN and become ready for explicit Definition promotion. If any item differs, revision 5 remains active and the selected alternative is reconciled before another final challenge.
