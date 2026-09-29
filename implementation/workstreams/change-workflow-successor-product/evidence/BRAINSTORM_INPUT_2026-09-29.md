# Workflow successor product — Brainstorming input

Date: 2026-09-29
Status: owner input / non-authoritative evidence
Scope subject: `workflow-successor-product@1`

## Product direction under investigation

Explore whether to stop feature-evolving PWv2/PWv2.2 after the required PWv2 stabilization baseline and instead build a clean successor product from scratch, using PWv2, PWv2.2 experiments, audits, bugs, tests and runtime experience as donors of knowledge rather than as code that must be preserved.

The successor's first usable release must be functionally complete enough to become its own workflow authority for subsequent development (dogfooding). It may intentionally omit nonessential advanced functionality, but it must support a complete real lifecycle rather than being an unusable kernel prototype.

Final product name is intentionally undecided. Do not assume "V3" is required.

## Owner constraints / preferences

1. **No product-level parallel execution/orchestration in the initial product design.**
   - Prefer one active mutating workflow owner/executor at a time.
   - Do not carry PWv2.2 parallel admission/claims/fan-in complexity into v1 merely because it exists.
   - Formal research itself may still use independent evidence lanes under the external orchestration protocol.

2. **Anomaly-to-Issue behavior should be first-class.**
   - If an agent executing the workflow discovers a workflow/product defect, invariant violation or reproducible anomaly, it should durably file/reconcile an official GitHub Issue immediately rather than leave the observation only in chat.
   - Research must define deduplication, readback, evidence, authority boundaries and anti-spam/false-positive behavior.
   - Filing an Issue must never itself authorize a repair.

3. **Backward-compatible versioned state semantics are a primary design goal.**
   - Durable records/artifacts should carry enough contract/schema/version identity to interpret them under the rules that were valid when they were created.
   - A record that was legal and passed acceptance under v1.0 should not become retrospectively illegal merely because v1.1 strengthens the canonical schema for newly created records.
   - Newer readers should distinguish historical legality from current-write requirements and should avoid forced history rewriting.
   - The #23 class of regression is a key counterexample: an older active workstream/state that was legal under its prior contract became invalid after canonical identity requirements were strengthened, causing Recovery/reroute behavior and renewed Premium-B progression.

4. **Use PWv2/PWv2.2 as evidence donors, not architectural obligations.**
   - Build a capability matrix and explicit disposition for each capability: initial product, later, policy, adapter/integration, or reject.
   - Preserve useful tests/invariants/adversarial cases even when implementation is replaced.

5. **Cross-harness usability matters.**
   - The successor should be usable from ChatGPT and Paseo.
   - Harness/runtime identity must not become semantic workflow authority.
   - Paseo's different execution behavior should be used as a qualification surface to expose hidden assumptions.

## Research deliverables sought

- semantic constitution candidate;
- capability/disposition matrix;
- adversarial corpus architecture;
- minimum complete v1 lifecycle and dogfooding release gate;
- state/schema evolution and backward-compatibility model;
- anomaly -> GitHub Issue contract;
- architecture boundaries between semantic core, workflow policy and external adapters/integrations;
- V2/V2.2 donor inventory including what to preserve, redesign, defer or reject;
- migration/cutover strategy from stabilized V2 without importing historical implementation complexity.
