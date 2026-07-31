#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example — set OPENAI_API_KEY before generating."
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

exec uvicorn app.main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8080}" --reload
