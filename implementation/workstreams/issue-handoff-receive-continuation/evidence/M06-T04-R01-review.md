# M06-T04-R01 Independent Review Evidence

Verdict: RED.

Reviewed exact subject blob `f96fa3b6d2ab82360a4e3dc8ac7c8f0df21636b9` at commit `2a35843e2b8fc4bfe33d7db053f5314acecf6547` against `implementation/workstreams/issue-handoff-receive-continuation/cards/M06-T04.md` and its named authority.

Independence:
- This fresh review context did not materially produce or repair the exact M06-T04 subject.

Acceptance-blocking findings:
1. The required durable-state advancement / duplicate-receipt qualification is not exercised. `test_stale_wrong_forged_and_duplicate_receipt_fail_closed` only varies the expected repository, branch, entry obligation, durable pointer, or transferability and asserts a first-call `ReceiveContractError`. It never performs a successful receipt, advances durable state, then submits the old locator again to prove that duplicate/stale receipt after advancement fails closed without replay.
2. The required end-of-approved-scope stop is not qualified. `test_producer_locator_receiver_continues_until_new_real_stop` checks a generic `authorization_boundary` stop only. No case exercises the durable end-of-scope stop required by the Card, accepted plan, and Issue #17 requirement 8.

Additional review note:
- The adapter check verifies shared bootstrap marker text and the four-line template, but does not itself execute two adapter-specific receive paths. This is weaker than the Card's end-to-end wording; however, the two concrete missing matrix cases above are independently sufficient for RED.

The exact subject therefore does not cover the complete accepted Issue #17 qualification matrix required by M06-T04. Repair must create a new immutable subject and a new review attempt; this failed attempt remains durable history.
