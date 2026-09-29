# Issue #33 — Explicit stop precedence decisions

Status: `accepted`
Definition revision: `D1`
Source scope: `brainstorm-explicit-stop-precedence@1`

## I33-D1 — Preserve the real stop rather than classify Recovery

**Decision:** A locally valid selected Brainstorm record with `explicit_user_stop = true` selects the canonical Brainstorm stop. The promoted/Definition combination is not declared invalid merely because later state exists.

**Why:** Brainstorming defines the flag as an orthogonal durable real stop. Later records do not own authority to clear it.

## I33-D2 — Evaluate after Brainstorm validation and before Definition consumption

**Decision:** Keep local record validation, then enforce explicit-stop precedence immediately after the exact Brainstorm record is available and before reading or dispatching Definition and later pre-execution owners.

**Why:** This closes the demonstrated ordering defect, preserves malformed Brainstorm Recovery, and avoids treating downstream state as stop authority.

## I33-D3 — Do not consume downstream state while stopped

**Decision:** A valid active stop need not load or validate later Definition/Planning/Board records in order to stop. Those records remain untouched and are validated when the Brainstorm owner lawfully clears the stop.

**Why:** Progressive disclosure should not let later malformed or valid state bypass an earlier human boundary. Deferred validation does not approve the deferred records.

## I33-D4 — Preserve exact existing stop delivery

**Decision:** Reuse the existing `stop / explicit_user_stop` result, exact scope subject, Brainstorm owner, and USER_STOP rendering path. Add no new stop type, handoff schema, or durable key.

**Why:** Detection exists and works without later Definition. The defect is precedence, not delivery format.

## I33-D5 — Leave Research precedence outside this repair

**Decision:** Do not reorder manifest or Task-Board Research handling under #33. Enforce the bounded stop before downstream Definition/Planning/pre-execution dispatch once the router reaches selected Brainstorm state.

**Why:** Execution Research shadowing is separately tracked by #28, and widening this repair would change accepted program boundaries.

## I33-D6 — Use direct production ordering, not a generic policy engine

**Decision:** Prefer the smallest direct production selector change. A new policy registry/priority abstraction is unjustified unless Planning proves a current technical need.

**Why:** One explicit owner boundary is sufficient and independently testable.

## I33-D7 — Test both stop preservation and resumed routing

**Decision:** Qualification must prove the exact stop in active/GREEN Definition variants and prove that clearing the flag restores unchanged Definition/premium behavior. Read-set assertions must distinguish stop-time deferral from post-clear validation.

**Why:** A test that only observes one stop could hide a permanent downstream-routing regression.

## Consequences

- Definition and later pre-execution records are not read while a valid Brainstorm explicit stop is active.
- Clearing the stop exposes those records to their existing validation/routing rules.
- Existing active/complete Research precedence remains unchanged by this bounded repair.
- No state schema, migration, or new authority owner is introduced.
