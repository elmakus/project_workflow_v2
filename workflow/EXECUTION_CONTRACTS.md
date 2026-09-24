# PWv2.1 — Typed Execution Obligation and Result contracts

Status: M02 transport-neutral contract.

Project Workflow owns authority resolution, obligation derivation, result acceptance and canonical state reconciliation. A runtime such as ChatGPT or OR/Paseo may transport or realize an already-derived obligation, but runtime topology never becomes Project Workflow authority.

## Execution Obligation

The canonical JSON shape is `schemas/EXECUTION_OBLIGATION.schema.json`; executable validation/derivation is in `tools/obligation_contract.py`.

An obligation binds:
- schema version and deterministic `obligation_id`;
- the registered mechanical rule and semantic role;
- one exact subject as repository + commit + path + blob;
- only the exact authority sources selected by PW, including immutable locators and verified content;
- prerequisites, mechanically safe constraints, and completion/test/evidence requirements;
- a freshness fingerprint over only the canonical inputs that materially determined this obligation;
- expected canonical mutation preconditions and postconditions.

The obligation is derived and disposable. It is not a second project-state store. Canonical JSON serialization rejects non-finite numeric values and any value that cannot be represented as standard JSON.

`obligation_id` is content-derived from the registered rule, exact role, exact subject and current relevant freshness fingerprint. The production kernel derives the rule-owned determining inputs from the registered rule's declared canonical input paths and the current canonical state; callers cannot substitute an arbitrary determining-input projection or a role that disagrees with the registered outcome. Equivalent determining inputs serialize byte-identically. Unrelated repository state is excluded from the fingerprint rather than hashed for convenience.

## Authority resolution

PW supplies exact authority locators. Every authority locator must contain repository, 40-hex commit, canonical repo-relative POSIX path spelling and 40-hex blob. Path aliases such as duplicate separators, `.`/`..` segments, leading or trailing separators are rejected. Materialization reads that exact source and verifies its Git blob identity before including it in the bounded authority bundle.

The transport/execution runtime receives the resolved bundle. It does not add, drop or reinterpret authority.

## Execution Result

The canonical JSON shape is `schemas/EXECUTION_RESULT.schema.json`; executable validation is in `tools/obligation_contract.py`.

A result contains only PW-relevant semantic data:
- exact obligation, original obligation-subject, and original freshness binding;
- a distinct exact immutable result/implementation subject plus changed-artifact refs;
- semantic status/outcome;
- tests, evidence and readback observations;
- a real blocker when status is blocked.

Provider, model, worker, session, retry, worktree, Paseo, scheduler, invocation and runtime identity are non-canonical and rejected as fields. Those telemetry terms reserve their field-name families as well as their exact spellings (for example, `model_name`, `session_uuid`, and `retry_count` are also forbidden), so runtime identity cannot enter freshness material under an alias.

`changed_artifacts` describes implementation artifacts only. For the obligation-subject repository, a Result that reports direct mutation of canonical Project Workflow durable state such as `PROJECT.md` or `implementation/workstreams/**` fails closed; runtime execution returns semantic results for coordinator-owned persistence instead.

## Freshness and stale-result reconciliation

Before acceptance, PW validates the result against the exact obligation and recomputes the relevant freshness fingerprint from current canonical inputs.

- unchanged fingerprint -> eligible for `accept`, subject to any mandatory governed-mutation readback;
- stale without a bounded safety proof -> `reexecute`;
- stale with exact old/new fingerprint binding, an explicit materially-unchanged proof and durable basis -> explicit `reuse`, `rebase`, or `reconcile`.

A stale result is never silently accepted. Reuse, rebase, or reconcile is allowed only when safety is positively proven.

The Result's `subject` remains the exact original obligation subject used for binding validation. Its separate `result_subject` is the exact immutable Git implementation subject produced by execution (repository + commit), matching the implementation-subject meaning that Main persists in the durable Card Result.

## Governed mutation and readback

The kernel emits mutation preconditions/postconditions in the obligation. Equality is checked over canonical JSON bytes, so JSON types cannot coerce across the boundary (for example, boolean `true` never satisfies integer `1`). The coordinator/owning workflow role performs any canonical write and then verifies the required postconditions through readback. When postconditions are non-empty, a fresh Result cannot reach terminal `accept` until the observed canonical state satisfies those postconditions and the Result carries verified readback evidence; missing, failed or mismatching readback fails closed. Staleness is classified first so a stale result is reconciled/re-executed rather than being mistaken for a fresh mutation acceptance. OR/Paseo does not finalize canonical PW state directly.

For external effects whose occurrence is unknown, existing exact-target readback semantics remain authoritative:
- pending occurrence -> read back the exact target before deciding;
- uncertain occurrence -> fail closed without retry;
- verified no-effect -> retry may be allowed;
- verified expected effect -> reconcile without replay;
- verified unexpected effect -> reconcile the discrepancy.

Blind duplicate external effects are forbidden.

## Kernel seams

`PolicyKernel.compile_obligations()`, `validate_results()`, and `reconcile()` are the M02 entry points. Compilation accepts only an existing registered rule ID that matches current canonical state, binds the registered semantic obligation/role, and derives the rule's declared canonical determining inputs itself; it does not create a second rule vocabulary or general workflow DSL. Reconciliation refreshes those registered rule inputs from current canonical state before recomputing freshness.
