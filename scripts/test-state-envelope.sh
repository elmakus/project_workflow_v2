#!/usr/bin/env sh
set -eu
python3 -m unittest -v tests.test_state_contract
python3 tools/state_contract.py \
  tests/fixtures/state/valid/PROJECT.md \
  tests/fixtures/state/valid/WORKSTREAM.toml \
  tests/fixtures/state/valid/TASK_BOARD.toml \
  tests/fixtures/state/valid/REVIEW_ATTEMPT.toml \
  tests/fixtures/state/valid/EXTERNAL_EFFECT.toml \
  --expect-revision 7
