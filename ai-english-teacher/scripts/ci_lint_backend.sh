#!/usr/bin/env bash
# Backend quality gates for CI.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"

echo "==> Ruff (app/)"
python3 -m ruff check app

echo "==> Flake8 critical errors (app/)"
python3 -m flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics

echo "Backend quality checks passed"
