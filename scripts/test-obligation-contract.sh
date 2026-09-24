#!/usr/bin/env sh
set -eu
python3 -m unittest -v tests.test_obligation_contract
echo "PWv2.1 M02 typed execution contract checks: PASS"
