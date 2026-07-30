#!/usr/bin/env python3
"""Validate expected Next.js routes appear in build output."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

FRONTEND = Path(__file__).resolve().parents[1] / "frontend"

EXPECTED_ROUTES = [
    "/",
    "/conversation",
    "/grammar-class",
    "/login",
    "/register",
    "/assessment",
    "/dashboard/student",
    "/dashboard/teacher",
    "/dashboard/admin",
]


def main() -> int:
    if not (FRONTEND / "package.json").is_file():
        print(f"FAIL: frontend not found at {FRONTEND}")
        return 1

    log = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        check=False,
    )
    combined = log.stdout + log.stderr
    if log.returncode != 0:
        print(combined[-3000:])
        print("FAIL: npm run build failed")
        return 1

    missing: list[str] = []
    for route in EXPECTED_ROUTES:
        # Next.js route table uses ○ or ƒ prefix
        pattern = re.escape(route)
        if not re.search(rf"[○ƒ]\s+{pattern}\s", combined):
            missing.append(route)

    if missing:
        print("FAIL: routes missing from build output:")
        for r in missing:
            print(f"  - {r}")
        return 1

    print(f"OK: {len(EXPECTED_ROUTES)} routes verified in build output")
    return 0


if __name__ == "__main__":
    sys.exit(main())
