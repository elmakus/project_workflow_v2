# Issue #20 — Temporary Paseo create_agent readiness plan — P2

## Scope and implementation boundary

This is a temporary readiness/configuration repair for the current Paseo/Pi deployment only. The implementation target is the deployment repository `elmakus/pi-unraid`, not Project Workflow core semantics.

The repair MUST use only Paseo's official caller-scoped `create_agent` capability. It MUST NOT add a PWv2 child spawner, daemon/shell spawn bypass, alternate lifecycle/readback path, fallback delegation implementation, or the final PWv2.2 runtime-neutral helper.

No `workflow/*.md`, router, Review-independence, subject-binding, or Recovery semantics in `elmakus/project_workflow_v2` are changed by this repair. This workstream records/coordinates the repair because issue #20 was observed while running PWv2.

## Executable implementation targets

Execution Prep must materialize work only against these bounded `elmakus/pi-unraid` surfaces, refreshed from the then-current integration head:

1. `scripts/configure-paseo-runtime.sh`
   - Persist the supported Paseo setting `mcp.injectIntoAgents=true` through the official `paseo daemon config set ... --home /home/paseo/.paseo` path.
   - Extend the existing JSON readback in the same script to assert the persisted setting is exactly true.
   - Preserve the existing worktree-root and relay settings and unrelated Paseo config.

2. `tests/test_paseo_runtime_contract.py`
   - Add hermetic contract coverage that the runtime configurator sets and reads back `mcp.injectIntoAgents=true`.
   - Keep the existing invocation through `scripts/verify-compose-foundation.sh` as the repository-level static/disposable configuration verification surface.

3. `config/pi-agent/AGENTS.md`
   - Add one bounded temporary readiness rule for the current Paseo/Pi environment: when managed child delegation is required but the caller does not receive `create_agent`, fail closed with a specific `PASEO_CREATE_AGENT_NOT_READY` diagnostic identifying the missing agent-tool injection/readiness prerequisite and instructing the operator to verify `mcp.injectIntoAgents=true` and retry from a fresh Pi caller.
   - Explicitly forbid treating absence of the tool as proof that Paseo lacks child delegation and forbid daemon/shell/fallback spawning.

4. The existing live Paseo/Pi deployment surface
   - Apply the repository-managed configurator to the intended Paseo HOME using the existing deployment mechanism.
   - Any real LLM inference used for qualification must follow the existing `config/pi-agent` real-test policy; no alternate model fallback is introduced by this plan.

No additional implementation surface may be chosen by Execution Prep unless a concrete blocker proves one of the targets above cannot realize the accepted Definition. Such a change is material replanning, not JIT architecture selection.

## Milestones and gates

### M1 — Persisted injection readiness

Implement the `configure-paseo-runtime.sh` and `test_paseo_runtime_contract.py` changes.

**Gate G1 — configuration contract GREEN**
- shell/script syntax checks pass;
- the Paseo runtime contract suite passes;
- repository foundation verification still invokes the configurator;
- readback proves `cfg["mcp"]["injectIntoAgents"] is True`;
- existing `worktrees.root` and `daemon.relay.enabled=false` assertions remain GREEN.

G1 failure blocks all live qualification.

### M2 — Fail-closed missing-capability behavior

Implement the bounded `config/pi-agent/AGENTS.md` readiness diagnostic.

**Gate G2 — diagnostic/no-fallback GREEN**
- the instruction plane contains the exact `PASEO_CREATE_AGENT_NOT_READY` fail-closed diagnostic;
- the remediation points to supported agent-tool injection and a fresh caller;
- no PWv2 spawner, direct daemon child spawn, shell spawn, alternate lifecycle/readback, or fallback delegation path is added;
- Project Workflow routing/review semantics remain untouched.

G2 failure blocks deployment.

### M3 — Live caller-scoped create_agent qualification

After G1 and G2 are GREEN, apply the configuration through the existing `pi-unraid` deployment path and start a **fresh** Pi caller so tool injection is not inferred from a stale session.

**Gate G3 — live readiness GREEN**
Durable evidence must show all of the following on the same qualified deployment:
- persisted Paseo config reads `mcp.injectIntoAgents=true`;
- the fresh Pi caller is actually delivered the caller-scoped `create_agent` capability;
- one bounded end-to-end native child launch through `create_agent` completes with a deterministic sentinel;
- the child is visible through Paseo's managed parent/child identity and normal completion/status readback;
- no daemon/shell/fallback launch path is used.

If `create_agent` is absent, the gate is RED with `PASEO_CREATE_AGENT_NOT_READY`; execution stops on readiness/configuration and does not substitute another child mechanism.

### M4 — Evidence reconciliation

Record the exact `elmakus/pi-unraid` implementation commit/PR and G1-G3 evidence in this workstream before issue closure/integration.

**Gate G4 — scope-preservation GREEN**
- the repair is demonstrably configuration/readiness-only;
- Project Workflow independence and exact subject binding are unchanged;
- the evidence does not claim the final PWv2.2 helper was implemented;
- the future helper remains free to consume official Paseo `create_agent` without inheriting a temporary spawn workaround.

## Acceptance mapping

- **Correctly configured Paseo/Pi path is recognized as capable of official delegation:** G1 + G3.
- **Disabled/unavailable injection path is rejected with actionable readiness diagnosis:** G2 + G3 RED behavior.
- **No fallback child-launch implementation:** G2 + G4.
- **PWv2 independence and subject binding unchanged:** implementation boundary + G4.
- **Temporary repair does not constrain final runtime-neutral helper:** scope boundary + G4.

## Planner challenge audit

GREEN.

The P1 RED findings are resolved as follows:
- the executable target is no longer implicit: the exact `pi-unraid` files and live deployment surface are named;
- milestone/gate strategy is explicit in M1-G1 through M4-G4;
- verification is split into hermetic configuration/diagnostic checks and a fresh-caller live `create_agent` E2E that directly proves the previously failing `mcp.injectIntoAgents` prerequisite.

The plan remains intentionally narrow: it repairs readiness for the already-proven official Paseo capability instead of inventing a second orchestration mechanism.
