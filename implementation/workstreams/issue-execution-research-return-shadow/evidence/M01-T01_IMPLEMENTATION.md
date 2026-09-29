# M01-T01 implementation evidence

Implementation subject: `elmakus/project_workflow_v2@716a4b62b5409ddbe3e6a2d2da0b42e4b5f03dcc`

Production change:
- `tools/router.py` blob `bec68c428343582bf8cdbe6ccf4b7c9de58024bb`
- `tests/test_router.py` blob `3297cc24da59483110f53593170a21f766288cc1`

Acceptance evidence:
- A shared Research return resolver now maps manifest-level and Task-Board completed Research to identical owners for `execution_resolution:<subject>`, `execution_prep:<subject>`, and `execution:<subject>`.
- Dual-locator complete/pending and complete/applied coverage is present for all three execution prefixes.
- Dual-locator consumed/applied remains `research_cleanup` only.
- Manifest Intake/Brainstorming/Definition return controls remain covered.
- Missing execution return subject fails closed.

Exact-subject verification:
- GitHub Actions run `36599654808` for `716a4b62b5409ddbe3e6a2d2da0b42e4b5f03dcc`: terminal `success`.
- Clean detached checkout of `716a4b62b5409ddbe3e6a2d2da0b42e4b5f03dcc` ran the Card commands:
  - `python3 -m unittest tests.test_router tests.test_state_contract` — 75 tests, OK.
  - `python3 -m unittest tests.test_continuation_contract tests.test_user_stop_contract` — 26 tests, OK.
  - `python3 -m unittest discover -s tests -v` — 279 tests, OK.
  - `git diff --check` — PASS.
- Clean-tree readback remained empty after testing.
