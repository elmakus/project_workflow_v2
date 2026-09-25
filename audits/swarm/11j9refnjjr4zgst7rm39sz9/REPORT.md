# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — READY dependency identity is metadata-only; mutated result content still launches

- Affected workflow contract/invariant: `workflow/EXECUTION_PREP.md` and `workflow/STATE.md` require each predecessor dependency to be bound as result path + immutable commit/blob identity and launch refresh to fail closed when that exact dependency is stale.
- Expected behavior: before a READY Card launches, the current dependency artifact must actually match the declared immutable blob/commit identity of the DONE predecessor. A same-path content mutation must fail closed.
- Actual behavior: `tools/router.py::refresh_ready_card` compares the dependency tuple only against the tuple stored on the DONE predecessor in `TASK_BOARD.toml`, then merely reads the dependency path. It never checks the current file's Git blob (or commit) against the declared identity. If both Card and Board retain the same stale tuple while the file contents change, launch refresh succeeds.
- Minimal reproduction: a DONE predecessor and READY successor both declare `results/M01-T01.md@aaaaaaaa...:bbbbbbbb...`; replace the result file contents without changing either metadata tuple. The production refresh logic accepts the dependency although the actual Git blob SHA is `411155663101521e759cf7b78a635350d2577962`, not `bbbb...`.
- Why this is materially load-bearing: downstream execution can consume a different predecessor result than the one its stable Card contract authorized, defeating immutable dependency binding and allowing stale/mutated state to pass a launch gate.
- Defect class / likely siblings: stale blob/commit/path identity; any refresh that checks locator metadata equality but does not bind it to repository object identity is suspect.
- Existing tests that failed to catch it: `test_ready_card_stale_dependency_fails_closed_before_launch` changes the Board result commit/blob tuple as well as the file, so it proves tuple mismatch detection, not actual blob verification when metadata remains unchanged.
- Reproduction artifact, if any: `repros/F1_dependency_blob_not_verified.py`.

### F2 — Card Result evidence references are accepted even when the evidence artifact does not exist

- Affected workflow contract/invariant: `workflow/EXECUTION.md` requires Main to validate returned implementation/evidence before normalizing an accepted semantic result; an accepted result must contain durable evidence refs.
- Expected behavior: a Card Result whose required evidence ref is missing/unreadable must fail closed before `result_reconciliation`, review freeze, or terminal finalization.
- Actual behavior: `tools/execution_contract.py::parse_card_result` validates only the syntax/prefix of `Evidence refs`. In the active-Card result path, `tools/router.py` reads the result file and Card contract but never reads any referenced evidence artifacts. A syntactically valid path to `.../evidence/DOES-NOT-EXIST.md` is accepted.
- Minimal reproduction: parse a valid Card Result with `Evidence refs: implementation/workstreams/sample-workstream/evidence/DOES-NOT-EXIST.md` while no such file exists. The production parser returns that ref successfully; the router contains no subsequent evidence read before result reconciliation/review routing.
- Why this is materially load-bearing: workflow state can treat an implementation as an accepted durable semantic result without the durable evidence the result contract says is required, permitting review/finalization to proceed on nonexistent proof.
- Defect class / likely siblings: negative-space durability validation; locators are syntax-validated but not dereferenced at the acceptance boundary. Review evidence locators deserve similar scrutiny.
- Existing tests that failed to catch it: result-routing tests create the referenced evidence file before routing; there is no negative case deleting/omitting the evidence while retaining the same Card Result.
- Reproduction artifact, if any: `repros/F2_missing_result_evidence.py`.

### F3 — Research routing preempts higher-precedence explicit/premium stops

- Affected workflow contract/invariant: `tools/router.py::PRIORITY_FOUNDATION` declares `explicit_human_or_premium_boundary` above `research_return`; `workflow/ROUTER.md` likewise defines explicit user/premium gates as real stops.
- Expected behavior: if a durable explicit user stop or due premium gate coexists with a Research obligation, the higher-precedence stop must win; if the combination is semantically contradictory, routing must fail closed rather than silently bypass the stop.
- Actual behavior: `select_route` loads `workstream.research` immediately after the manifest and returns for `active` or `complete` Research before it loads Brainstorming, Definition, Planning, or Plan Review. Therefore `brainstorm.explicit_user_stop = true`, premium A due, premium B due, or premium C due can be unreachable while Research is active/complete. The validators do not reject these cross-record combinations.
- Minimal reproduction: valid Research with `state = "active"`, `origin_role = "brainstorming"`, and a valid Brainstorm record with `explicit_user_stop = true`. Both records pass their individual validators; router control flow returns `route/research` before reading the explicit stop. The same ordering preempts later premium checks.
- Why this is materially load-bearing: the selector can continue work after an explicit human boundary or required premium boundary that its own precedence table says must dominate, violating deterministic authorization/stop semantics.
- Defect class / likely siblings: router precedence drift between declared precedence and executable ordering; especially early-return modules that run before higher-priority records are loaded.
- Existing tests that failed to catch it: tests cover Research routing and premium-stop routing separately and assert the precedence constant, but no interaction test combines Research with an explicit/premium boundary. There is no `explicit_user_stop = true` router case in the exact test file.
- Reproduction artifact, if any: `repros/F3_research_preempts_stop.py`.

## Non-blocking observations

No additional advisory item was promoted. Close/finalization helper semantics were inspected, including review reuse, external-effect readback, tracker closure, source-ref cleanup and `close_continuation`; no independent material defect was demonstrated there.

## Coverage

Audit subject remained bound to commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. I inspected canonical `workflow/ROUTER.md`, `CLOSE.md`, `PLANNING.md`, `PLAN_REVIEW.md`, `EXECUTION.md`, `EXECUTION_PREP.md`, and `STATE.md`; production `tools/router.py`, `close_contract.py`, `execution_contract.py`, `recovery_contract.py`, and relevant portions of `state_contract.py`; and exact-commit router tests around READY dependency refresh, Research, premium gates, result reconciliation, and Close. The four selected attack lenses were exercised: Close/finalization, helper-vs-documentation negative space, Planning/Premium/Execution precedence, and router precedence.

Executable falsification was performed with isolated reproductions copied from the exact production functions/order: F1 demonstrated acceptance of a dependency file whose actual Git blob differs from the declared blob; F2 demonstrated acceptance of a nonexistent evidence ref; F3 demonstrated the executable early-return ordering that selects Research before explicit-stop evaluation. Existing test coverage was inspected at the same immutable commit rather than moving `main`.

## Confidence and limitations

Confidence is high for F1 and F2 because the relevant production checks are local and the counterexamples directly exercise the exact acceptance logic. Confidence is high for F3 because both the declared precedence and executable early-return ordering are explicit and the state validators lack a cross-record exclusion for the counterexample.

A full checkout/test-suite execution was not available in the local container because outbound Git access is disabled, and the authorized Remote Desktop Commander had exhausted its monthly usage quota. I therefore used exact-commit GitHub reads plus isolated executable reproductions of the relevant production functions/order. No historical `audit/*` branch, swarm report, Issue, PR comment, or historical implementation evidence/review was inspected before freezing these findings.
