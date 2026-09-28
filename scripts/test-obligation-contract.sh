#!/usr/bin/env sh
set -eu
python3 -c 'import jsonschema' >/dev/null 2>&1 || { echo 'Missing test dependency: python3 -m pip install -r requirements-test.txt' >&2; exit 1; }
python3 -m unittest -v tests.test_obligation_contract
echo "PWv2.1 M02 typed execution contract checks: PASS"
