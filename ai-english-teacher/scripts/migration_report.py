#!/usr/bin/env python3
"""Report Alembic migration files for AI English Teacher backend."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERSIONS_DIR = REPO_ROOT / "ai-english-teacher" / "backend" / "alembic" / "versions"


def parse_revision(path: Path) -> tuple[str | None, str | None]:
    text = path.read_text(encoding="utf-8")
    rev = re.search(r'^revision:\s*str\s*=\s*["\']([^"\']+)["\']', text, re.M)
    down = re.search(r'^down_revision:\s*[^=]*=\s*["\']([^"\']*)["\']', text, re.M)
    down_rev = down.group(1) if down and down.group(1) else None
    return (rev.group(1) if rev else None, down_rev)


def main() -> int:
    if not VERSIONS_DIR.is_dir():
        print(f"FAIL: {VERSIONS_DIR} missing")
        return 1

    files = sorted(VERSIONS_DIR.glob("*.py"))
    print("Alembic Migration Report")
    print("========================")
    for path in files:
        revision, down_revision = parse_revision(path)
        size = path.stat().st_size
        print(f"  {path.name}")
        print(f"    revision={revision} down_revision={down_revision} size={size}B")

    print(f"\nTotal: {len(files)} migration(s)")
    print("OK: migration report passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
