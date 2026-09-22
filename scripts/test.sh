#!/usr/bin/env sh
set -eu

test -f README.md
test -f docs/CONSTRUCTION_AUTHORITY.md
test -f .github/workflows/test.yml

test ! -e implementation/TASK_BOARD.yaml
test ! -e implementation/workstreams/feature-common-preexecution-core/TASK_BOARD.yaml

test ! -d workflow/chatgpt_only
test ! -d workflow/codex_only

if test -f scripts/test-plugin-probe.sh; then
  sh scripts/test-plugin-probe.sh
fi

printf 'M01 baseline checks: PASS\n'
