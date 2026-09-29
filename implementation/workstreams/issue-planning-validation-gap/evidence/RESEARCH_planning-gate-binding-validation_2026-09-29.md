# Research evidence — repair:planning-gate-binding-validation:v1

Workstream `issue-planning-validation-gap`, branch `work/issue-26-planning-validation`.
Base `d3ab917f`; HEAD tools/workflow/templates/tests identical to base (empty diff).
Read-only; no consumer mutation; no inference tests; no workers spawned.

## Verified (project_runtime, in-memory probes vs canonical production code)

- B/C key: `_git_blob_subject_key` (`tools/state_contract.py`) = `repo@commit:path@blob`.
  Short `plan:P3@blob` != full key. `validate_planning` with short B/C FAILS
  (`planning: frozen subject requires exact premium B gate subject`) for frozen AND
  approved; full-key form PASSES. Diagnostic names the frozen path even when
  `state="approved"` and does not separate format-mismatch from unsatisfied gate.
- Board: literal backslash-n after a closing quote fails `tomllib` with
  `Expected newline or end of document after a statement (... column 92)` — same error
  class/column as reported (line 387 col 92).
- Card status: `CARD_STATUSES` = `{planned, ready, in_progress, blocked, done}`
  (never `review`); `validate_board` rejects `review`.
- Result envelope: `parse_card_result` (`tools/execution_contract.py`) FAILS backticked
  ref and trailing-period ref with `card_result.evidence[0]: invalid workstream
  evidence ref`; clean raw `implementation/workstreams/<ws>/evidence/*.md` path PASSES.
- Router fail-closed when invoked: `validate_planning` (`tools/router.py:352`),
  `validate_board` (`:482`), active-Card `parse_card_result` (`:531`) +
  `validate_review_history` + stale-pending hard error (`:565-571`) all route
  `recovery_boundary` on violation. Validator precedence (planning gate before board
  parse before card-schema) is consistent with the reported layer-masking order.
- No writer-side deterministic B/C key helper exists: only the private validator-side
  `_git_blob_subject_key`; `migration_apply._render_toml` is generic TOML rendering.
  Tests construct the full key correctly (`tests/test_router.py` gate_key,
  `tests/test_state_contract.py`). Docs gap confirmed: `workflow/PLANNING.md` (48 lines)
  says "exact subject" without serialized B/C format or A-vs-B/C contrast;
  `templates/PLANNING.toml` is draft-only; `templates/CARD_RESULT.md` has a generic
  evidence-refs placeholder; `workflow/EXECUTION.md` shows no raw-ref examples.
- Prior art: #23 is adjacent (producer/consumer schema drift, invalid status class) but
  covers neither short B/C keys, literal-backslash-n boards, continuation enforcement,
  nor result-envelope refs. Open #25/#27/#28/#30/#31/#33 are neighboring state topics;
  none covers this subject. Dedup clear.

## Report-only (tracker_discussion, untrusted per ROUTER/GITHUB_ISSUES)

Issue #26 OPEN (+2 comments, marker `pwv2-planning-gate-binding-validation-gap`) read via
`gh issue view`. All consumer commit/blob chains (tip `8a655411`, origins `44f85e23`...,
board corruption `ff494842`/`50961231`, recovery `b65c8e22`, `778c371c`, tip `dbece127`,
pending R01 `8a88b171:1c64f5bf...`), status transitions, and recurrence notes are bounded
to the report chain — NOT independently re-verified here (no consumer clone).

## Hypotheses (not facts)

Continuation mechanism (omitted validation vs older validator vs ignored failure);
any Main/worker attribution (consumer history is not attribution nor proof of mechanism).

## Source classes

- official_upstream (primary): checked — stdlib `tomllib` TOML decode behavior + Git
  40-hex commit/blob identity semantics. No external framework dependency.
- project_runtime (direct): checked — probes above at base-equivalent tree.
- tracker_discussion (supporting): checked as untrusted input/bookkeeping only.
- practitioner_community (supporting): unavailable — no community source consulted;
  in-repo search found none relevant; per `workflow/RESEARCH.md` it could not override
  canonical validators by popularity regardless.

## Conflicts

None material. Tracker guardrail direction aligns with canonical fail-closed behavior;
comment-2 reviewer posture (verdict withheld, fail-closed to Recovery) aligns with
`workflow/REVIEW.md`, `workflow/RECOVERY.md`, and router precedence.

## Scope boundary (not authorized for repair)

The comment-2 pending-reservation lifecycle gap (no lawful cancel/supersede path for an
unstarted pending R01 when a representational-only Result fix changes its subject) is a
distinct authority gap recorded for assessment only. This subject covers only
malformed-writing/validation/continuation enforcement (B/C bindings, literal
backslash-n board, invalid Card status, result evidence-ref layer). No lifecycle
invented, no verdict/rebind/history change authorized. Consumer S11 remains blocked
until a lawful solution. Proposed subject stands — research does not contradict or
expand it.
