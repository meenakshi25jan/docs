#!/usr/bin/env python3
"""Validate deployment environment configuration (render.yaml + required secrets)."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RENDER = REPO_ROOT / "render.yaml"

FORBIDDEN_PRODUCTION = [
    (r"SKIP_MIGRATIONS\s*\n\s*value:\s*[\"']?true", "SKIP_MIGRATIONS must be false"),
    (r"runtime:\s*docker", "Web service must not use Docker runtime"),
    (r"dockerfilePath:\s*backend/Dockerfile", "Web must not use backend Dockerfile"),
]

REQUIRED_MARKERS = [
    "name: ai-english-teacher-api",
    "name: ai-english-teacher-web",
    "rootDir: ai-english-teacher/backend",
    "rootDir: ai-english-teacher/frontend",
    "./start.sh",
    "SKIP_MIGRATIONS",
    '"false"',
    "npm ci && npm run build",
    "npm start",
    "branch: main",
    "autoDeploy: true",
]


def main() -> int:
    errors: list[str] = []

    if not RENDER.is_file():
        return 1

    text = RENDER.read_text(encoding="utf-8")
    web_section = text.split("ai-english-teacher-web", 1)
    web_text = web_section[1] if len(web_section) > 1 else ""

    for needle in REQUIRED_MARKERS:
        if needle not in text:
            errors.append(f"missing required config: {needle}")

    for pattern, msg in FORBIDDEN_PRODUCTION:
        if re.search(pattern, web_text if "docker" in pattern.lower() else text, re.I):
            errors.append(msg)

    # CI / deploy secret hints (non-fatal)
    if os.environ.get("CI") == "true":
        if (
            not os.environ.get("DATABASE_URL")
            and os.environ.get("CHECK_SECRETS") == "true"
        ):
            errors.append("DATABASE_URL secret not available in environment")

    if errors:
        print("Environment validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"OK: {RENDER} environment configuration")
    return 0


if __name__ == "__main__":
    sys.exit(main())
