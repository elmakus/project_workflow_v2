# Issue #20 — Temporary Paseo create_agent readiness plan

Frozen scope: temporary readiness/configuration repair only.

## Strategy

1. Add the smallest runtime/deployment-facing readiness check at the existing Paseo/Pi integration boundary used by this project.
2. Treat the official caller-scoped Paseo child-delegation capability as the only acceptable child-launch path for this temporary repair.
3. Verify the prerequisites that caused the observed failure, including agent-tool injection/readiness sufficient for create_agent to be delivered to Pi.
4. When the capability is unavailable, fail closed with a specific diagnostic that identifies readiness/configuration rather than claiming Paseo lacks child delegation.
5. Add bounded regression coverage for both ready and unavailable states.
6. Do not add a PWv2 child spawner, daemon/shell spawn bypass, alternate lifecycle/readback, fallback delegation, or the final PWv2.2 helper.

## Acceptance

- A correctly configured Paseo/Pi path is recognized as capable of official create_agent delegation.
- A disabled/unavailable injection path is rejected with an actionable readiness diagnostic.
- No fallback child-launch implementation is introduced.
- Existing PWv2 independence and subject-binding semantics are unchanged.
- The temporary repair does not constrain the final runtime-neutral helper API; the later Paseo realization can use official create_agent.
