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

if test -f scripts/test-state-envelope.sh; then
  sh scripts/test-state-envelope.sh
fi

if test -f scripts/test-router.sh; then
  sh scripts/test-router.sh
fi

if test -f scripts/test-execution-contract.sh; then
  sh scripts/test-execution-contract.sh
fi

if test -f scripts/test-review-contract.sh; then
  sh scripts/test-review-contract.sh
fi

if test -f scripts/test-recovery-contract.sh; then
  sh scripts/test-recovery-contract.sh
fi

python3 -m unittest tests.test_close_contract tests.test_fork_release_contract tests.test_chatgpt_delivery tests.test_codex_delivery tests.test_v1_migration tests.test_migration_apply tests.test_migration_rehearsal

# Cumulative acceptance: discover every Python regression, compile all Python sources,
# then prove repository checks leave no diff or untracked execution artifacts behind.
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m compileall -q tools tests
find tools tests -type d -name '__pycache__' -prune -exec rm -rf {} +
git diff --check
test -z "$(git status --porcelain --untracked-files=all)"

printf 'M01 baseline checks: PASS\n'
