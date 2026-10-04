# PWV3 D10 A01 RED — pending owner decision

Date: 2026-10-04
Subject: workflow-successor-product@6 / D10
Review result: RED
Blocking findings: D10-F01..D10-F09
Owner decision required only for: D10-F02

## D10-F02 question

R5 owner authority established both:
- an applicable Global CLEAR normally continues automatically to terminal acceptance without a routine CONTINUE / RUN OP AGAIN stop; and
- an explicit same-binding repeat Global remains possible when the owner asks for one.

D10 must define one exact durable precedence rule so Recovery cannot reconstruct both the prior CLEAR-derived closure path and a newer repeated Global as current.

### Option A — repeat allowed until final integration begins — RECOMMENDED

After Global CLEAR, terminal acceptance may proceed automatically.

Until the durable final-integration intent/cut begins, the owner may explicitly request another same-binding Global. That request is one durable single-use transition which:
- revalidates exact candidate/acceptance applicability;
- supersedes any pending or already accepted terminal-acceptance result derived from the predecessor CLEAR for forward authority;
- creates and positively reads back exactly one successor Global attempt frontier;
- makes the predecessor CLEAR and any superseded closure evidence immutable history only;
- blocks final integration until the successor Global and a fresh applicable terminal acceptance complete.

Once final integration has durably begun, a same-binding repeat is no longer part of that qualification epoch.

Tradeoff: preserves automatic CLEAR continuation and a genuinely usable explicit repeat right, at the cost of one bounded supersession rule.

### Option B — repeat allowed only before terminal acceptance becomes accepted

Global CLEAR automatically establishes/runs terminal acceptance. An explicit repeat is legal only while that terminal-acceptance frontier has not yet produced an accepted result. The repeat supersedes the pending frontier and creates one successor Global attempt.

Once terminal acceptance is accepted, same-binding repeat is no longer legal in that qualification epoch.

Tradeoff: simpler than A, but the usable repeat window may be very short because terminal closure is designed to run automatically.

### Option C — no same-binding semantic Global repeat after CLEAR

Global CLEAR automatically proceeds to terminal acceptance and there is no same-binding repeat transition in canonical PWV3. A new Global is required only when repair changes the exact candidate/acceptance surface. Any extra human-requested Global on an unchanged candidate is supplemental evidence outside canonical advancement.

Tradeoff: simplest semantics, but explicitly abandons the previously preserved owner ability to ask for another same-binding Global.

## Recommendation

Choose **A**.

It best preserves both accepted R5 goals:
- no routine post-Global owner gate;
- explicit owner-requested repeat remains truly usable.

All other A01 findings are bounded Definition corrections and need no product choice unless repair unexpectedly expands beyond the reviewed scope.
