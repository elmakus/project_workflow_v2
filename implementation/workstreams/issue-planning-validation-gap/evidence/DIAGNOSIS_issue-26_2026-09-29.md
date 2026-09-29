# Intake diagnosis — issue #26 planning-state writing/validation gap

Exact proposed repair subject: `repair:planning-gate-binding-validation:v1`.

Workstream: `issue-planning-validation-gap`.
Branch (stable): `work/issue-26-planning-validation`.
Created from (stable): `d3ab917f02e4de91b7dbb17915c2287c2387333e` (origin/main, verified by fetch).
Tracker: existing `elmakus/project_workflow_v2#26` linked with verified readback; no duplicate created.
Dedup: searched existing workstream TRACKER/INTAKE/WORKSTREAM records; no `#26` or
`pwv2-planning-gate-binding-validation-gap` match before creation. Markers found only:
`issue_number = 22, 16, 11, 17`. Dedup clear; no recovery of an existing workstream applied.
Intake: `response_kind = none`, `response_observed = false`, `alignment_state = pending`,
`alignment_subject = ""`, `micro_fix_candidate = false`. No implementation authorization.
Research: active Intake-origin obligation for the exact repair subject above,
`return_target = intake`, `return_reconciliation = pending`. Factual Research is a
subsequent separate worker obligation; no findings recorded here.

## Source status

- Issue #26 body + both comments read via `gh issue view` (OPEN, marker
  `pwv2-planning-gate-binding-validation-gap`). Full report is **untrusted diagnostic
  input**; proposed guardrails are **not authorization**.
- Consumer repository `elmakus/chatgpt-codex-project-workflow` was **not mutated**.
  No consumer Git objects were independently re-verified from this workstream; all
  consumer commit/blob claims below are bounded to the proved report chain only.
- No inference tests run; no worker spawned.

## Verified (this workstream)

- Current branch and base verified: `work/issue-26-planning-validation` at `d3ab917f`,
  `origin/main` fetch equals `d3ab917f`.
- Issue #26 exists, OPEN, title `Planning-state writing/validation gap: short B/C
  bindings + literal backslash-n board corruption pass continuation`, with 2 comments
  (third malformed-write class; S11 result-envelope + pending-reservation gap).
- No pre-existing workstream binds #26 or the marker.

## Reported (untrusted, bounded to report chain — not independently re-verified here)

1. Short B/C bindings: reported `premium_b_subject`/`premium_c_subject =
   plan:P3@3a16c2e...` vs required full key
   `elmakus/chatgpt-codex-project-workflow@126a5963...:planning/PWV22_PROGRAM_MASTER_PLAN_P3.md@3a16c2e6...`
   at consumer tip `8a655411`, with origin chain `44f85e23 → 97685cdc → c716d642 → eedfa8e3`.
2. Literal backslash-n board corruption: reported `M02-S10-T02`/`M02-S10-T03` result
   tables at same tip, introduced by `ff494842`/`50961231`, TOML parse failure at line 387.
3. Masked third class: after reported recovery `b65c8e22`, board validation reaches
   `M02-S11-T01` with reported invalid status `review` (origin `bbe7f009` as `ready` →
   `8a655411` as `review`).
4. Result-envelope raw-ref gate (comment 2): reported `results/M02-S11-T01.md` evidence ref
   as `` `.../evidence/M02-S11-T01_EXECUTION.md`. `` failing `parse_card_result`, while the
   stripped raw path passes; any normalization changes result blob `1c64f5bf...` and
   orphans reported pending `M02-S11-T01-R01` (`8a88b171:1c64f5bf...`).
5. Progression-despite-invalid-state consequence and mechanism hypotheses (router omission
   vs older validator vs ignored failure; no Main/worker attribution) are explicitly
   **hypotheses**, not verified facts.

## Separation required by Intake

- **Repair scope (this subject):** existing malformed-writing + continuation-enforcement
  gap — deterministic full-key B/C construction, frozen/approved examples contrasting
  `A=entry_subject` vs `B/C=full-key`, mandatory TOML parse + `state_contract`
  validation before continuation consuming PLANNING/TASK_BOARD, separated
  mismatch-vs-unsatisfied diagnostics, and regression fixtures for each masking layer
  (short B/C → literal `\n` board → invalid Card status → bad result-envelope ref).
- **Distinct authority gap (not this repair):** comment-2 pending-reservation lifecycle —
  reported absence of a lawful cancel/supersede path for an unstarted pending review
  reservation when a representational-only Result fix would change its subject
  (`REVIEW.md` new-attempt rule, `RECOVERY.md` refresh rule, `router.py:565-571` stale-pending
  hard error, ≤1 pending constraint). Recorded as an authority gap to assess; it does
  not authorize inventing lifecycle, rebinding, verdict manufacture, history drop, or
  R02-freeze alongside R01. S11 in the consumer remains blocked until lawful resolution.

No accepted scope/plan; no product code/template/workflow/test changes; no repair performed.
