# Issue #32 Intake diagnosis and proportional prior art

Research subject: `repair:intake-relational-closure:v1`

This record supports issue diagnosis and later user alignment only. It is not
repair authorization, accepted Definition authority, an implementation plan, a
Task Card, or proof that a repair passes.

## Current baseline and tracker readback

- Repository/default branch checked: `elmakus/project_workflow_v2`,
  `main@d3ab917f02e4de91b7dbb17915c2287c2387333e` (equal to
  `origin/main` at the check).
- Diagnosis branch entry commit:
  `5c327eaa8d22fdb292e2ba6c104aa5c3c7e153b5`.
- GitHub Issue #32 was read back at `2026-09-29T11:12:14Z`: OPEN,
  `Intake can emit an empty repair alignment stop and disagree with manifest
  kind`, with dedup marker `pwv2-intake-relational-closure-gap`.
- A repository issue-list readback found #32 as the sole title-level Intake /
  repair-subject / relational match among the current issues inspected. The
  tracker is bookkeeping and diagnosis input, never authorization.

## Reproduced current behavior

Two current-schema cases were run directly through production
`tools.router.select_route` from the default-branch implementation.

1. An active issue Intake with `repair_subject = ""`, no response and pending
   alignment validates, then returns:

   `stop / issue_alignment / subject=''`

   with reason `Issue diagnosis has a proposed repair but no subsequent user
   alignment response yet`.
2. A manifest with `kind = "change"` pointing to a separately valid Intake with
   `kind = "issue"`, a concrete repair subject and its prior-art binding returns:

   `stop / issue_alignment / subject='repair:v1'`

   instead of failing closed on the stable-identity contradiction.

`python3 -m unittest tests.test_state_contract tests.test_router` passed all 71
current tests, demonstrating that the regressions are absent from the default
suite rather than already rejected by it. Code inspection confirms:

- `validate_workstream` and `validate_intake` validate each record separately,
  but no selected-state relation requires `WORKSTREAM.kind == INTAKE.kind`;
- the router's concrete-subject prior-art block is conditional on truthiness of
  `repair_subject`, after which active pending issue Intake unconditionally
  enters alignment handling.

The two failures are related at the Intake boundary but retain separate
negative controls: one is missing subject closure and one is contradictory
cross-record identity.

## Existing implementation prior art

Repository history contains commit
`c94a348a0490b11c014f02d57931a5829046f1a9` (`Gate issue alignment on concrete
repair subject`) on `origin/work/pwv21-policy-kernel`. It adds a router guard and
empty/blank-subject tests for the first failure. The branch diverges from the
current accepted default baseline at an older common ancestor and carries a
much broader unaccepted policy-kernel change set. It is evidence of a useful
candidate behavior, not an accepted Result and not safe to merge or cherry-pick
as repair authority.

A search of that branch's production and test sources found no relational check
between manifest kind and Intake kind, so it does not close the second failure.
Issue #23 remains broader producer/consumer schema compatibility and historical
reconciliation work; its current OPEN tracker description does not absorb this
current-schema-valid relational defect.

## Concrete bounded repair outcome proposed for alignment

For `repair:intake-relational-closure:v1`:

### Included

- an active issue with an empty or whitespace-only repair subject remains with
  Intake diagnosis and cannot emit an issue-alignment stop or enter any
  alignment-response path;
- selected-state consumption verifies that the stable manifest kind and Intake
  kind agree before Intake semantics are selected, and fails closed on a
  contradiction;
- focused production-contract tests cover empty/blank issue subjects across
  response classes, manifest/Intake kind contradictions, and lawful positive
  controls with consistent identity and a concrete exact repair subject;
- canonical Intake/state wording may be clarified only as needed to state these
  two existing invariants.

### Excluded

- #33 explicit-stop precedence, #36 orphan Planning state, schema migration or
  supported-legacy-profile design;
- review/history/Close behavior, Task Board/Card semantics, runtime
  orchestration, tracker mutation, issue closure, merge or deployment;
- changing feature/change discovery semantics beyond rejecting contradictory
  selected identity;
- adopting the broad `work/pwv21-policy-kernel` branch or widening #23.

### Qualification required by a later accepted repair contract

- reproduce both failures on the exact current baseline before modification;
- exercise production validation and routing, not a test-only helper;
- prove empty and whitespace-only subjects remain diagnosis for every allowed
  response class without turning a premature `authorization` value into repair
  permission;
- reject manifest/Intake kind disagreement for issue/feature/change pairings,
  while preserving lawful consistent positive controls;
- run cumulative Intake/router/state-contract tests and committed readback from
  a clean consumer;
- independently review the exact immutable implementation subject against the
  accepted repair scope.

The exact placement/API of the relational check remains a later Definition and
Planning decision. No code write scope is granted by this diagnosis.

## Source accounting and conflicts

- **Official/upstream — checked, controlling:** canonical `workflow/INTAKE.md`,
  `workflow/WORKSTREAMS.md`, `workflow/STATE.md`, `workflow/AUTHORITY.md` and
  `workflow/ROUTER.md` require a concrete repair outcome before alignment and
  fail-closed exact workstream-local binding.
- **Actual project/runtime — checked, highest defect weight:** both production
  reproducers, current validator/router inspection, the 71-test baseline, and
  historical partial commit `c94a348...`.
- **Issue/discussion tracker — checked, supporting diagnosis/dedup only:** #32 is
  the exact open tracker; #23 documents a different broader schema-evolution
  problem. Neither tracker authorizes repair.
- **Practitioner/community — not relevant:** this is an internal deterministic
  state relation with direct canonical and executable evidence; general
  community practice cannot outweigh those sources.

No material source conflict remains. The historical partial implementation
agrees with the empty-subject diagnosis but lacks the kind relation and has no
accepted status on current main. The canonical contracts and current
reproducers agree on the bounded outcome above.

## Limitations

No repair was implemented, no accepted requirements/decisions were authored,
no clean-clone post-repair qualification exists, and no independent
implementation review was performed. The program-level P1 recommendation at
`work/pwv2-stabilization-program@2a7e134...` selected this issue for admission
only; it does not supply issue-repair authorization.
