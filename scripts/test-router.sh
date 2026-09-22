#!/usr/bin/env sh
set -eu

python3 -m unittest -v tests.test_router
python3 -m tools.router \
  tests/fixtures/router/valid-project \
  --workstream implementation/workstreams/sample-workstream/WORKSTREAM.toml \
  | grep -q '"obligation": "execution"'

echo "M01-T04 router checks: PASS"
