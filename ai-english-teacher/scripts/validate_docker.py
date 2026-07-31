#!/usr/bin/env python3
"""Validate Dockerfiles for AI English Teacher (structure, security, health)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BACKEND_DOCKER = ROOT / "backend" / "Dockerfile"
FRONTEND_DOCKER = ROOT / "frontend" / "Dockerfile"


def check_backend(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing {path}"]
    text = path.read_text(encoding="utf-8")
    if "FROM python:3.12" not in text:
        errors.append(f"{path}: expected python 3.12 base image")
    if "EXPOSE" not in text:
        errors.append(f"{path}: missing EXPOSE")
    if re.search(r"USER\s+\w+", text) is None:
        print(
            f"NOTE: {path}: no USER directive (Render native Python runtime does not use this Dockerfile)"
        )
    if "requirements-render.txt" not in text and "requirements.txt" not in text:
        errors.append(f"{path}: missing requirements install")
    if re.search(r"CMD\s*\[\s*['\"]\./start\.sh['\"]", text):
        errors.append(f"{path}: CMD must be [\"bash\", \"./start.sh\"] not [\"./start.sh\"]")
    if "chmod +x start.sh" not in text:
        errors.append(f"{path}: missing RUN chmod +x start.sh")
    return errors


def check_frontend(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing {path}"]
    text = path.read_text(encoding="utf-8")
    stages = len(re.findall(r"^FROM ", text, re.MULTILINE))
    if stages < 2:
        errors.append(f"{path}: expected multi-stage build (found {stages} stages)")
    if "USER nextjs" not in text:
        errors.append(f"{path}: missing non-root USER nextjs")
    if "standalone" not in text:
        errors.append(f"{path}: expected Next.js standalone output")
    if "HEALTHCHECK" not in text:
        print(
            f"NOTE: {path}: no HEALTHCHECK (acceptable; Render uses service healthCheckPath)"
        )
    return errors


def main() -> int:
    errors: list[str] = []
    errors.extend(check_backend(BACKEND_DOCKER))
    errors.extend(check_frontend(FRONTEND_DOCKER))

    if errors:
        print("Docker validation FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"OK: Dockerfiles validated ({BACKEND_DOCKER.name}, {FRONTEND_DOCKER.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
