#!/bin/sh
set -eu

test -f .codex-plugin/plugin.json
test -f .agents/plugins/marketplace.json
test -f skills/project_workflow_v2/SKILL.md
test -f hooks/hooks.json
test -f hooks/session-start.py
test -f workflow/ROUTER.md

grep -q '"name": "pw"' .codex-plugin/plugin.json
grep -q '"version": "0.2.1"' .codex-plugin/plugin.json
grep -q '"name": "project-workflow-v2"' .agents/plugins/marketplace.json
grep -q '^name: project_workflow_v2$' skills/project_workflow_v2/SKILL.md
grep -q '\$pw:project_workflow_v2' skills/project_workflow_v2/SKILL.md
grep -q '<plugin-root>/workflow/ROUTER.md' skills/project_workflow_v2/SKILL.md
grep -q 'SessionStart' hooks/hooks.json
grep -q 'Canonical bundled router' hooks/session-start.py
grep -q 'Production selector: `tools/router.py`.' workflow/ROUTER.md
grep -q 'fail closed' workflow/ROUTER.md

if find workflow -maxdepth 2 -type d \( -name chatgpt_only -o -name codex_only \) | grep -q .; then
  echo "legacy policy tree present" >&2
  exit 1
fi

python3 -m unittest tests.test_codex_delivery

echo "M05-T02 package bootstrap checks: PASS"
