#!/usr/bin/env python3
"""Production health monitoring — database, API, frontend, migrations."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out.strip()


def main() -> int:
    results: dict = {"components": []}
    failed = 0

    steps = [
        (
            "validate_render",
            [sys.executable, str(SCRIPTS / "validate_render_config.py")],
        ),
        (
            "validate_environment",
            [sys.executable, str(SCRIPTS / "validate_environment.py")],
        ),
        (
            "check_migrations_disk",
            [sys.executable, str(SCRIPTS / "check_migrations.py")],
        ),
    ]

    if os.environ.get("DATABASE_URL"):
        steps.append(
            (
                "check_migrations_db",
                [sys.executable, str(SCRIPTS / "check_migrations.py")],
            )
        )
        steps.append(
            (
                "verify_tables",
                [
                    sys.executable,
                    str(
                        SCRIPTS.parent
                        / "backend"
                        / "scripts"
                        / "verify_migrations_applied.py"
                    ),
                ],
            )
        )

    api_url = os.environ.get(
        "DEPLOY_API_URL", "https://ai-english-teacher-api.onrender.com"
    ).rstrip("/")
    os.environ["WAIT_BASE_URL"] = api_url
    os.environ.setdefault("WAIT_PATHS", "/health/live,/health")
    steps.append(
        ("api_health_wait", [sys.executable, str(SCRIPTS / "wait_for_healthy.py")])
    )
    steps.append(
        ("production_probe", [sys.executable, str(SCRIPTS / "post_deploy_verify.py")])
    )

    for name, cmd in steps:
        code, out = run(cmd)
        ok = code == 0
        if not ok:
            failed += 1
        results["components"].append({"name": name, "passed": ok, "output": out[-500:]})
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")

    results["failed"] = failed
    print(json.dumps(results, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
