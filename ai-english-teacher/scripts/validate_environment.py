#!/usr/bin/env python3
"""Validate deployment environment configuration (render.yaml + backend startup)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RENDER = REPO_ROOT / "render.yaml"

REQUIRED_MARKERS = [
    "name: ai-english-teacher-api",
    "name: ai-english-teacher-web",
    "rootDir: ai-english-teacher/backend",
    "rootDir: ai-english-teacher/frontend",
    "./start.sh",
    "requirements-render.txt",
    "JWT_SECRET",
    "DATABASE_URL",
    "XAI_API_KEY",
    "npm ci && npm run build",
    "npm start",
    "branch: main",
    "autoDeploy: true",
    "healthCheckPath: /health/live",
]


def main() -> int:
    errors: list[str] = []

    if not RENDER.is_file():
        return 1

    text = RENDER.read_text(encoding="utf-8")

    for needle in REQUIRED_MARKERS:
        if needle not in text:
            errors.append(f"missing required config: {needle}")

    if re.search(r"JWT_SECRET_KEY", text):
        errors.append("use JWT_SECRET (not JWT_SECRET_KEY) in render.yaml")

    start_sh = REPO_ROOT / "ai-english-teacher" / "backend" / "start.sh"
    if not start_sh.is_file():
        errors.append("backend/start.sh is missing")

    if errors:
        print("Environment validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"OK: {RENDER} environment configuration")
    return 0


if __name__ == "__main__":
    sys.exit(main())
