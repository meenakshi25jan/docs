#!/usr/bin/env bash
# Backend quality gates for CI — critical syntax + type safety on core modules.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"

echo "==> Flake8 (syntax / undefined names)"
python3 -m flake8 app scripts --count --select=E9,F63,F7,F82 --show-source --statistics

echo "==> Ruff (E/F on scripts only)"
python3 -m ruff check ../scripts --select E,F --ignore E501

echo "==> Mypy (app/core, app/schemas)"
python3 -m mypy app/core app/schemas

echo "==> Black (scripts only)"
python3 -m black --check ../scripts

echo "Backend quality checks passed"
