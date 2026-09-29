# M01-T01 — exact implementation verification

Immutable implementation subject: `elmakus/project_workflow_v2@8328e1aedced70c4c321128f00bf6e3c90d1a2fd`.

Changed production/readback blobs: `tools/router.py@bb0b69b61d6060479d88073ab656079e4c08e6d7`, `workflow/ROUTER.md@cfae3e3c3068f34d05f69415903772b274d1e3eb`, `tests/test_router.py@402d11d13844031d20190cd560b1e4106659cd89`. The commit changes only those three files. The stop is now dispatched after local Brainstorm validation, ahead of Definition and later state; the late duplicate is removed. Earlier Intake/Research/tracker selection remains unchanged.

Verification of exact committed implementation:

- `python3 -m unittest tests.test_router -v`: 50 tests, OK.
- `python3 -m unittest tests.test_router tests.test_state_contract`: 78 tests, OK.
- `python3 -m unittest tests.test_user_stop_contract tests.test_continuation_contract tests.test_m05_trajectory`: 95 tests, OK.
- `python3 -m unittest discover -s tests -v`: 285 tests, OK.
- `git diff --check`: clean.
- Clean detached worktree at `8328e1a`: production `tools.router` import, focused 50, cumulative 78/95 and full 285 tests passed; detached worktree removed after readback.
- Independent local readback of the same commit's three blob IDs matched above; combined focused/state/stop/continuation/trajectory run: 173 tests, OK; full suite: 285 tests, OK.

The production-selector matrix exercises active Definition, GREEN Definition A due/satisfied, later Planning/Plan Review/Board read-set deferral, stop-only and active/ready Brainstorm controls, stop-cleared lawful routes, malformed owner/downstream Recovery, and preserved earlier Research precedence. Exact subject/owner/reason/USER_STOP and no downstream read are asserted. This is implementation evidence, not an independent review verdict or integration approval.
