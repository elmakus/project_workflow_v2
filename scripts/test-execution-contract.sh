#!/usr/bin/env sh
set -eu

python3 -m unittest -v tests.test_execution_contract
echo "M03-T02 execution contract checks: PASS"
