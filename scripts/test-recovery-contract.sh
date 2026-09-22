#!/usr/bin/env sh
set -eu

python3 -m unittest -v tests.test_recovery_contract
echo "M03-T04 recovery contract checks: PASS"
