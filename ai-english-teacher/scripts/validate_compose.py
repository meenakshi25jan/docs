#!/usr/bin/env python3
"""Validate docker-compose.yml structure and healthchecks."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "docker-compose.yml"

REQUIRED_SERVICES = ("postgres", "redis", "backend", "frontend")


def main() -> int:
    if not COMPOSE.is_file():
        print(f"FAIL: missing {COMPOSE}")
        return 1

    text = COMPOSE.read_text(encoding="utf-8")
    errors: list[str] = []

    for svc in REQUIRED_SERVICES:
        if f"{svc}:" not in text:
            errors.append(f"missing service: {svc}")

    if "pgvector/pgvector" not in text:
        errors.append("postgres should use pgvector image")

    if "healthcheck:" not in text:
        errors.append("services should define healthchecks")

    if "backend/Dockerfile" not in text:
        errors.append("backend should reference backend/Dockerfile")

    if errors:
        print("docker-compose validation FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"OK: {COMPOSE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
