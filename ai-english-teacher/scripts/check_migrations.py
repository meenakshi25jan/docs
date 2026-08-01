#!/usr/bin/env python3
"""Validate Alembic migrations for AI English Teacher backend."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERSIONS_DIR = REPO_ROOT / "ai-english-teacher" / "backend" / "alembic" / "versions"
ALEMBIC_INI = REPO_ROOT / "ai-english-teacher" / "backend" / "alembic.ini"


def main() -> int:
    errors: list[str] = []

    if not ALEMBIC_INI.is_file():
        errors.append(f"missing alembic.ini: {ALEMBIC_INI}")
    if not VERSIONS_DIR.is_dir():
        errors.append(f"missing versions dir: {VERSIONS_DIR}")
    else:
        files = sorted(VERSIONS_DIR.glob("*.py"))
        if not files:
            errors.append("no Alembic migration files found")
        revisions: list[str] = []
        for path in files:
            text = path.read_text(encoding="utf-8")
            match = re.search(r'^revision:\s*str\s*=\s*["\']([^"\']+)["\']', text, re.M)
            if not match:
                errors.append(f"could not parse revision in {path.name}")
                continue
            revisions.append(match.group(1))
        if len(revisions) != len(set(revisions)):
            errors.append("duplicate Alembic revision ids detected")

    if errors:
        print("Alembic migration check FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    count = len(list(VERSIONS_DIR.glob("*.py")))
    print(f"OK: Alembic migrations ({count} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
