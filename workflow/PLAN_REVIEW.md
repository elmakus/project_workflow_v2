# Project Workflow V2 — Independent Plan Review

Status: M02-T03 Stage-6 exception.

Plan Review judges one exact immutable frozen Master Plan subject against its accepted Definition/requirements/decisions and planning acceptance surface.

## Independence

Plan Review requires a fresh independent best-available context. The context that materially authored or repaired the exact plan subject cannot issue its verdict. The planner must not spawn its own Stage-6 reviewer internally.

Canonical review provenance is semantic only; model/session/runtime identity is not durable workflow state.

## Attempt lifecycle

Each `PLAN_REVIEW.toml` attempt owns:
- exact workstream + plan revision/cycle;
- immutable Git-blob subject;
- exact acceptance authority;
- semantic independence proof;
- pending / green / red verdict;
- concise evidence locator when verdict is terminal.

Any other verdict — including the generic Card Review `in_progress` state — is invalid for Plan Review and fails closed to Recovery/validation; it never routes as RED correction.

A changed material plan subject requires a new attempt. RED history remains attached to its failed subject. The only omission is the Planning-owned `editorial_exempt` case: it must point to a prior exact GREEN-reviewed subject from the same cycle with satisfied C and an exact immutable independent classification record. Free-text basis is not proof. The record must bind exact prior/changed plan subjects, record inspected diff/evidence, be GREEN and `editorial_only`, explicitly show strategy, milestone topology, requirement coverage, gates and acceptance semantics unchanged, and prove classifier independence from materially producing or repairing the changed subject.

## GREEN

GREEN returns to Planning for deterministic approval consumption. Planning then sets premium stop C due. GREEN does not itself authorize Execution Prep.

## RED

RED returns to Planning for correction classification. Material strategy/milestone/coverage/gate correction creates a new planning cycle and repeats A/B/C. Accepted Definition contradictions route back to Definition; missing facts route to Research. The review role does not silently repair its own subject.
