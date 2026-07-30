#!/usr/bin/env python3
"""Generate migration validation report (ordering, duplicates, rollback hints)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = REPO_ROOT / "ai-english-teacher" / "database" / "migrations"

EXPECTED = [
    "001_initial_schema.sql",
    "002_pgvector.sql",
    "003_auth_rls.sql",
    "004_fix_rls_policies.sql",
    "005_knowledge_and_voice.sql",
    "006_curriculum_intelligence.sql",
    "007_security_rls_hardening.sql",
]


def migration_number(name: str) -> int | None:
    match = re.match(r"^(\d+)_", name)
    return int(match.group(1)) if match else None


def main() -> int:
    if not MIGRATIONS_DIR.is_dir():
        print(f"FAIL: {MIGRATIONS_DIR} missing")
        return 1

    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    names = [f.name for f in files]
    errors: list[str] = []

    print("Migration Report")
    print("================")
    for name in names:
        num = migration_number(name)
        size = (MIGRATIONS_DIR / name).stat().st_size
        rollback_hint = "manual rollback via down SQL not automated"
        print(f"  {name} (#{num}) — {size} bytes — rollback: {rollback_hint}")

    for expected in EXPECTED:
        if expected not in names:
            errors.append(f"missing: {expected}")

    extra = [n for n in names if n not in EXPECTED]
    if extra:
        errors.append(f"unexpected files: {extra}")

    numbers = [migration_number(n) for n in names]
    if any(n is None for n in numbers):
        errors.append("invalid migration filename pattern (use NNN_name.sql)")

    sorted_nums = sorted(n for n in numbers if n is not None)
    if sorted_nums != list(range(1, len(sorted_nums) + 1)):
        errors.append(f"ordering gap or duplicate numbers: {sorted_nums}")

    dup_check = {}
    for n in numbers:
        if n is not None:
            dup_check[n] = dup_check.get(n, 0) + 1
    dups = [k for k, v in dup_check.items() if v > 1]
    if dups:
        errors.append(f"duplicate migration numbers: {dups}")

    print(f"\nTotal: {len(names)} files, expected {len(EXPECTED)}")

    if errors:
        print("\nFAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("\nOK: migration report passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
