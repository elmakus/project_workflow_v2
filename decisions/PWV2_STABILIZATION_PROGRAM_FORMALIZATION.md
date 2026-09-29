# Accepted decisions — PWV2 stabilization program formalization

**Definition R1, source `pwv2-stabilization-program@1`: authority for bounded program formalization ONLY. No individual repair Definition or implementation is approved by this document.**

- Formalization subject (bounded): exact promoted revision
  `pwv2-stabilization-program@1` (source `PWV2-STAB-P1`).
- Canonical decision authority: `decisions/PWV2_STABILIZATION_PROGRAM_FORMALIZATION.md`, companion to `requirements/PWV2_STABILIZATION_PROGRAM_FORMALIZATION.md`.
- These dispositions challenge the P1 proposal under U01/U02 and the consumed
  prior art. Unsafe alternatives are rejected with rationale. Nothing here
  approves any individual repair Definition (see D7), freezes a Master Plan, or
  creates Cards.

Boundary note: distinguish the current U01/U02 stage limit from scope exclusions and canonical prohibitions (requirements R6). Later Strategic Planning requires explicit premium-A continuation and durable satisfaction; later repairs require their own lawful scope/gates. Phase advancement never silently admits PR #9, feature expansion or a different #20/#23 subject, and never permits history rewrite, manufactured GREEN, invalid approval transfer or a second workflow store. No approval transfers by this formalization.

## D1 — Dedicated ownership (fixed constraint)

Keep the U01-authorized dedicated workstream
(`issue-pwv2-stabilization-program`, branch `work/pwv2-stabilization-program`);
do NOT adopt either stopped audit workstream and do NOT expand #23/#20.
Rationale: resumption would inherit stopped/active subjects, violate #23/#20
boundaries, and launder audit completion into repair authority.

## D2 — Separate issue invariants; shared infrastructure is reuse only

Maintain every R4 invariant and acceptance separately. Shared
constructors/resolvers/history primitives are capability reuse; no
duplicate/closing/scope-subsumption verdict by similarity. In particular: #26
serialization counterexamples may QUALIFY #23's producer boundary without
changing #23's subject and without declaring #26 a duplicate; #34/#38/#39/#30
share machinery with four role-separated acceptance predicates (no mutual
subsumption); #18/#31/#37 are not duplicates (invalid-terminal / Stage-6
storage / valid-terminal-overwrite); #27 does not subsume #29.

## D3 — Immutable bound Git bytes; role-separated identities; non-self-referential publication

Prefer explicitly bound immutable Git bytes (repo@commit:path@blob), never a
mixed mutable/historical subject. Keep implementation / normalized Result /
Review / acceptance roles distinct with role-separated identity predicates and
non-self-referential publication sequencing (implementation → Result → Review
freeze). Define exact mechanisms in Definition/Planning without weakening
existing subject authority.

## D4 — Lawful history: preserve invalid records; separate pending replacement

Preserve invalid historical raw records/evidence immutably and define their
lawful successor separately (invalidity + exact-bound successor disposition)
— distinct from unstarted pending-reservation replacement (old reservation
preserved, prevented from verdicting the new subject). Do not fabricate
GREEN/RED, rebind attempts (no R01 rebinding), rewrite terminal evidence, or
leave two active attempts. Independence is recomputed for every repaired
subject; a repairing context never independently approves its own repaired
subject.

## D5 — Minimal Close-owned completion proof

Prefer a minimal Close-owned durable completion proof (reconstructing
in-progress Close, accepted completion, end-of-scope from target-side state +
immutable integration evidence) over a universal event-log redesign, which is
unbounded, unowned, and reinvents lifecycle state.

## D6 — #14 proposed inclusion retained; exclusion is a scope change

Retain P1's PROPOSED #14 inclusion in this candidate scope for explicit program
consideration (U02 authorizes promotion with that membership). Excluding #14
instead requires a revised scope/challenge with a stated qualification gap
(strategic combined-gate-cycle coverage lost; PWv2.2.1 deferral remains sole
owner) — never a silent deferral. Inclusion does not lift the consumer
PWv2.2.0 deferral and does not authorize #14 implementation.

## D7 — #25 formal Research gate retained unresolved; NO waiver, NO repair approval

Keep #25's formal 1+1+8 Research unresolved and blocking BEFORE #25's
Definition/repair authorization; audit import is not completion. A future owner
must establish the actual required evidence (full wave + integration pass +
Intake return + Brainstorming alternatives per #25 items 7–8) before claiming
that gate satisfied. **This program formalization — even if GREEN — does not
approve #25's individual repair Definition and does not waive its
prerequisite.** The current formalization subject (program-scope preparation)
and later repair authorization (individual issue repair approval) are distinct;
Definition must keep that distinction durable.

## D8 — W0–W7 refinements validated; NO scope/wave boundary change required

The SCOPE_REVISION_1 §5 refinements are accepted as carried constraints:
dedicated ownership already decided (D1); #32/#33/#36 early guards and
#28/#40 early research/preparation with W4 as preferred shared-router
integration checkpoint (not fabricated hard dependencies); W2 predicates before
credible GREEN reuse; W3 replacement laws before normalization changing a bound
pending/terminal subject; W1's #23 writer capability is not whole-issue
completion (full #23 qualification at W5); #14 combined-gate check applies to
this program's own eventual strategy; semantic requirements independent of
runtime realization (no helper/model/session identity or parallel queue as
authority). Definition-level consistency check: hard vs non-hard classification
holds against the preserved invariants; provisional wave order needs no
reordering; **no necessary scope or wave-boundary change surfaced** — any
material reordering/boundary change discovered by Definition/Planning must be
surfaced explicitly through applicable owning gates (substantive scope change
increments the exploratory revision and renews subject-bound gates).

## D9 — Early-guard split retained; full qualification deferred to owning gates

Land #32/#33/#36 + #28/#40 analysis early (W1/W4-split) rather than gating all
safety work behind W2/W3; declare full #23 qualification at W5, not at W1;
keep runtime-adapter gaps separately owned/scoped (reject importing the final
PWv2.2 helper or a second queue to make tests pass). Per-wave qualification
discipline (R10) is Planning/implementation-design for owning gates (A/B/C +
independent reviews), not bounded-formalization choice.

## D10 — Alternatives disposition register (challenged, unsafe rejected)

A1 dedicated vs resume-audit/#23/#20 — FIXED per D1. A2 absorb #26 into #23 vs
separate — RETAIN separation (U01 anti-absorption; pending-reservation gap
would be destroyed). A3 one shared fix vs four acceptances for #34/#38/#39/#30
— RETAIN shared machinery + four predicates (single-format checks proven
insufficient per distinct role bindings). A4 minimal Close proof vs event log —
RETAIN minimal proof (D5). A5 preserve+successor vs rewrite-invalid-valid —
RETAIN preserve + lawful successor (D4). A6 include #14 vs defer — RETAIN
proposed inclusion with explicit consequence of exclusion (D6). A7 early guards
vs gate-everything — RETAIN split (D9). A8 full #23 at W5 vs declare-fixed-at-W1
— RETAIN W5 qualification (D8). A9 import helper/queue vs scope gaps separately
— REJECT import (D9). A10 audit-import-satisfies-#25 vs retain gate — REJECT
waiver (D7).
