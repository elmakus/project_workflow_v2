# Issue #17 — Accepted decisions

Scope subject: `handoff-receive-continuation@1`.

## Receive consumption

Valid receipt consumes only the exact transferable handoff/context-selection boundary and immediately enters the canonically selected obligation.

## Canonical authority and fail-closed safety

The router and durable owner state outrank locator prose. Invalid or stale bindings fail closed and cannot manufacture authority.

## Composition with Issue #16

Build on the accepted terminal Issue #16 continuation/restart baseline on `main`; do not create parallel continuation or runtime-specific authority state.

## Qualification

Require producer-to-locator-to-fresh-receiver end-to-end evidence, including Premium A/B/C, independent Review, invalid locator rejection, replay/readback safety, deterministic continuation, supported adapter equivalence, and preservation of genuine stops.
