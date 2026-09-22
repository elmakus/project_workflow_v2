#!/usr/bin/env sh
set -eu

python3 -m unittest -v tests.test_review_contract
echo "M03-T03 review contract checks: PASS"
