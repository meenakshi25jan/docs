#!/usr/bin/env python3
"""Validate root render.yaml for AI English Teacher Render deployment."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RENDER_FILE = REPO_ROOT / "render.yaml"

REQUIRED_WEB = {
    "name: ai-english-teacher-web",
    "runtime: node",
    "rootDir: ai-english-teacher/frontend",
    "npm ci && npm run build",
    "npm start",
}

REQUIRED_API = {
    "name: ai-english-teacher-api",
    "rootDir: ai-english-teacher/backend",
    "./start.sh",
    "healthCheckPath: /health/live",
    "JWT_SECRET",
    "XAI_API_KEY",
    "DATABASE_URL",
}


def main() -> int:
    if not RENDER_FILE.is_file():
        print(f"FAIL: missing {RENDER_FILE}")
        return 1

    text = RENDER_FILE.read_text(encoding="utf-8")
    errors: list[str] = []

    for needle in REQUIRED_API:
        if needle not in text:
            errors.append(f"API config missing: {needle}")

    for needle in REQUIRED_WEB:
        if needle not in text:
            errors.append(f"Web config missing: {needle}")

    if "branch: main" not in text:
        errors.append("Blueprint must deploy branch: main")

    if not re.search(r"name:\s*ai-english-teacher-api", text):
        errors.append("Missing api service name")
    if not re.search(r"name:\s*ai-english-teacher-web", text):
        errors.append("Missing web service name")

    start_sh = REPO_ROOT / "ai-english-teacher" / "backend" / "start.sh"
    if not start_sh.is_file():
        errors.append(f"missing backend start script: {start_sh}")
    elif "alembic upgrade head" not in start_sh.read_text(encoding="utf-8"):
        errors.append("start.sh must run alembic upgrade head")

    if errors:
        print("render.yaml validation FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"OK: {RENDER_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
