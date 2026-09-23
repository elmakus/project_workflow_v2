# V1 migration rehearsal boundary

Status: M06 disposable rehearsal only. This is **fixture-only** migration tooling, not production adoption.

## Rehearsed state classes

The finite V1 readers cover the three real-derived source classes frozen in
`tests/fixtures/migration/ORIGINS.toml`. The rehearsal demonstrates these outcomes:

| Source condition | M06 disposition |
| --- | --- |
| one active/in-progress Project Card | preserve the Card status/contract locator; never recreate V1 batch/lane scheduler state |
| completed Card/result | preserve it as a result to reconcile; never replay it as fresh execution |
| pending/RED/GREEN Card review | preserve exact append-only proof when supplied; otherwise create a blocking V2 review obligation rather than invent GREEN |
| legacy root terminal/unmerged state | map to a branch-local V2 destination; never revive the legacy root as live V2 state |
| source disappears after activation | destination readback remains self-verifying from its migration record |
| exploratory promotion / active Research / Plan Review or premium A/B/C-equivalent pre-execution state | fail closed and require explicit V2 reconstitution; M06 does not infer missing human authorization or translate V1 stage prose into V2 TOML |
| stacked unmerged parent dependency | retain it as an outstanding obligation and fail closed until the dependency is explicitly reconciled |
| parallel active Cards, racing source, unknown semantic field, ambiguous review subject, unresolved external effect | fail closed before automatic cutover |

The premium A/B/C line is deliberate: the bounded V1 manifest only exposes routing pointers,
not enough immutable semantic data to prove those human gates. Treating such a pointer as
authorization would be unsafe. A later explicit migration step may reconstitute the matching
V2 `DEFINITION.toml`, `PLANNING.toml` and `PLAN_REVIEW.toml` from exact evidence; this
fixture rehearsal does not guess them.

## Apply, rollback and recovery

Apply is allowed only after a GREEN exact dry run plus explicit authorization for that exact
source fingerprint. Generated state is staged, read back and verified before promotion.
Repeating the same exact migration is a verified no-op; changed source or destination state
conflicts instead of being overwritten.

An unactivated staging tree may be rolled back. Once activated, durable history is
**forward-repair** only. An uncertain external effect is read back before retry, and unknown
occurrence blocks. Activated destination readback does not depend on the V1 source branch
still existing.

There is exactly **one live owner** at a time. M06 does not transfer ownership of a real
project: the V1 fixture is read-only and the V2 destination is disposable. Any real ownership
transfer, production adoption, publication or cutover remains gated by M07 and separate
authorization.

## Ordinary V2 boundary

`workflow/ROUTER.md` and `tools/router.py` do not import the V1 reader or migration apply
module. Migration provenance lives under the migrated workstream's `migration/` directory.
No `execution_policy`, ChatGPT/Codex policy split, Context Health, batch/lane scheduler,
`active_execution`, `returned` or `transfer_ready` becomes canonical V2 state.

## Validation matrix readback

M06 exercises the migration-relevant validation rows without manufacturing live product tests:

- **A02** — ordinary V2 routing does not depend on legacy policy semantics.
- **A03** — exact manifest/Task Board/branch identity is validated and mismatch fails closed.
- **A05** — completed result stays a durable result instead of being replayed.
- **A06** — uncertain external effects require readback before retry.
- **A07** — review proof is exact and append-only; RED→corrected GREEN history is retained.
- **A10** — activated output remains readable after the source disappears.
- **A15** — finite real-derived V1 fixtures migrate into common V2 or fail closed explicitly.
- **A17** — the accepted V1→V2 coverage matrix remains the disposition authority.

## V1→V2 coverage disposition

The accepted coverage matrix is not copied into the runtime. Its categories remain explicit:

| Disposition | Rehearsal meaning |
| --- | --- |
| **KEEP CORE** | common semantic behavior remains represented by V2 modules/tests |
| **GENERALIZE** | useful semantics remain, product/policy-specific shape is not migrated |
| **TRIGGER-ONLY** | optional behavior is loaded only from its exact trigger |
| **MIGRATION-ONLY** | V1 readers/apply/provenance exist only for bounded migration |
| **DROP** | V1 execution-policy, orchestration/context-health and Project-Card scheduler state are intentionally absent |
| **BOOTSTRAP** | delivery/entry behavior stays thin and outside canonical project semantics |

The authoritative row-by-row classification remains
`brainstorming/V1_TO_V2_COVERAGE_MATRIX.md` in the Project Workflow construction repository;
M06 regression tests verify that migration-only code is not imported by ordinary routing and
that dropped scheduler/runtime-policy fields do not reappear in canonical conversion output.
