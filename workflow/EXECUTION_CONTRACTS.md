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

The obligation is derived and disposable. It is not a second project-state store.

`obligation_id` is content-derived from the registered rule, exact role, exact subject and current relevant freshness fingerprint. Equivalent determining inputs serialize byte-identically. Unrelated repository state is excluded from the fingerprint rather than hashed for convenience.

## Authority resolution

PW supplies exact authority locators. Every authority locator must contain repository, 40-hex commit, repo-relative path and 40-hex blob. Materialization reads that exact source and verifies its Git blob identity before including it in the bounded authority bundle.

The transport/execution runtime receives the resolved bundle. It does not add, drop or reinterpret authority.

## Execution Result

The canonical JSON shape is `schemas/EXECUTION_RESULT.schema.json`; executable validation is in `tools/obligation_contract.py`.

A result contains only PW-relevant semantic data:
- exact obligation and original freshness binding;
- exact result subject and changed-artifact refs;
- semantic status/outcome;
- tests, evidence and readback observations;
- a real blocker when status is blocked.

Provider, model, worker, session, retry, worktree, scheduler, invocation and runtime identity are non-canonical and rejected as fields.

## Freshness and stale-result reconciliation

Before acceptance, PW validates the result against the exact obligation and recomputes the relevant freshness fingerprint from current canonical inputs.

- unchanged fingerprint -> `accept`;
- stale without a bounded safety proof -> `reexecute`;
- stale with exact old/new fingerprint binding, an explicit materially-unchanged proof and durable basis -> explicit `reuse`, `rebase`, or `reconcile`.

A stale result is never silently accepted. Reuse, rebase, or reconcile is allowed only when safety is positively proven.

## Governed mutation and readback

The kernel emits mutation preconditions/postconditions in the obligation. The coordinator/owning workflow role performs any canonical write and then verifies the required postconditions through readback. OR/Paseo does not finalize canonical PW state directly.

For external effects whose occurrence is unknown, existing exact-target readback semantics remain authoritative:
- pending occurrence -> read back the exact target before deciding;
- uncertain occurrence -> fail closed without retry;
- verified no-effect -> retry may be allowed;
- verified expected effect -> reconcile without replay;
- verified unexpected effect -> reconcile the discrepancy.

Blind duplicate external effects are forbidden.

## Kernel seams

`PolicyKernel.compile_obligations()`, `validate_results()`, and `reconcile()` are the M02 entry points. Compilation accepts only an existing registered rule ID; it does not create a second rule vocabulary or general workflow DSL.
