#!/usr/bin/env sh
set -eu
python3 -m unittest -v tests.test_policy_kernel
python3 - <<'PY'
from pathlib import Path
from tools.policy_kernel import PolicyKernel
root = Path.cwd()
kernel = PolicyKernel.from_path(root / "policy" / "mechanical_policy.json")
kernel.verify_projection(root / "workflow" / "POLICY_KERNEL.md")
print("PWv2.1 M01 mechanical policy checks: PASS")
PY
