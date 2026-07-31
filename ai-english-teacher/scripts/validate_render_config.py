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
    "bash ./start.sh",
}

FORBIDDEN_API_START = [
    re.compile(r"startCommand:\s*\./start\.sh\s*$", re.M),
    re.compile(r"startCommand:\s*sh\s+\./start\.sh", re.M),
]

FORBIDDEN_WEB = [
    "dockerfilePath: backend/Dockerfile",
    "runtime: docker",
]


def main() -> int:
    if not RENDER_FILE.is_file():
        print(f"FAIL: missing {RENDER_FILE}")
        return 1

    text = RENDER_FILE.read_text(encoding="utf-8")
    errors: list[str] = []

    for needle in REQUIRED_API:
        if needle not in text:
            errors.append(f"API config missing: {needle}")

    web_section = text.split("ai-english-teacher-web", 1)
    web_text = web_section[1] if len(web_section) > 1 else ""
    for needle in REQUIRED_WEB:
        if needle not in text:
            errors.append(f"Web config missing: {needle}")

    for needle in FORBIDDEN_WEB:
        if needle in web_text:
            errors.append(f"Web service must not use: {needle}")

    if "branch: main" not in text:
        errors.append("Blueprint must deploy branch: main")

    if not re.search(r"name:\s*ai-english-teacher-api", text):
        errors.append("Missing api service name")
    if not re.search(r"name:\s*ai-english-teacher-web", text):
        errors.append("Missing web service name")
    api_part = text.split("ai-english-teacher-web", 1)[0]
    for pattern in FORBIDDEN_API_START:
        if pattern.search(api_part):
            errors.append(
                "API startCommand must be bash ./start.sh (not ./start.sh or sh ./start.sh)"
            )
    if "SKIP_MIGRATIONS" in api_part:
        mig_section = api_part.split("SKIP_MIGRATIONS", 1)[1][:60]
        if re.search(r"value:\s*[\"']?true", mig_section, re.I):
            errors.append("SKIP_MIGRATIONS must be false (never true in production)")
        if '"false"' not in mig_section and "'false'" not in mig_section:
            errors.append("API should set SKIP_MIGRATIONS: false")

    if errors:
        print("render.yaml validation FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"OK: {RENDER_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
