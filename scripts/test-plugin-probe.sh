#!/bin/sh
set -eu

test -f .codex-plugin/plugin.json
test -f .agents/plugins/marketplace.json
test -f skills/project_workflow_v2/SKILL.md
test -f hooks/hooks.json
test -f hooks/session-start.py
test -f workflow/ROUTER.md

grep -q '"name": "pw"' .codex-plugin/plugin.json
grep -q '^name: project_workflow_v2$' skills/project_workflow_v2/SKILL.md
grep -q '\$pw:project_workflow_v2' skills/project_workflow_v2/SKILL.md
grep -q 'workflow/ROUTER.md' skills/project_workflow_v2/SKILL.md
grep -q 'SessionStart' hooks/hooks.json
grep -q 'fail closed' workflow/ROUTER.md

if find workflow -maxdepth 2 -type d \( -name chatgpt_only -o -name codex_only \) | grep -q .; then
  echo "legacy policy tree present" >&2
  exit 1
fi

echo "M01-T02 package probe checks: PASS"
