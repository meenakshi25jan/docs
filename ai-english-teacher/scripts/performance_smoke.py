#!/usr/bin/env python3
"""Post-deploy API latency smoke (no auth required for public endpoints)."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

API_BASE = os.environ.get(
    "DEPLOY_API_URL", "https://ai-english-teacher-api.onrender.com"
).rstrip("/")
WEB_BASE = os.environ.get(
    "DEPLOY_WEB_URL", "https://ai-english-teacher-web.onrender.com"
).rstrip("/")
TIMEOUT = int(os.environ.get("TIMEOUT_SECONDS", "60"))
MAX_LATENCY_MS = float(os.environ.get("MAX_LATENCY_MS", "8000"))


def timed_get(url: str) -> tuple[bool, float, int]:
    start = time.perf_counter()
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            elapsed_ms = (time.perf_counter() - start) * 1000
            return resp.status == 200, elapsed_ms, resp.status
    except urllib.error.HTTPError as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return False, elapsed_ms, exc.code
    except urllib.error.URLError:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return False, elapsed_ms, 0


def main() -> int:
    checks = [
        ("api_health", f"{API_BASE}/health"),
        ("api_live", f"{API_BASE}/health/live"),
        ("api_ready", f"{API_BASE}/health/ready"),
        ("api_grammar", f"{API_BASE}/api/v1/grammar/grades"),
        ("web_home", f"{WEB_BASE}/"),
    ]

    results = []
    failed = 0
    for name, url in checks:
        ok, ms, code = timed_get(url)
        slow = ms > MAX_LATENCY_MS
        passed = ok and not slow
        if not passed:
            failed += 1
        results.append(
            {
                "name": name,
                "url": url,
                "status": code,
                "latency_ms": round(ms, 1),
                "passed": passed,
            }
        )
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}: HTTP {code} in {ms:.0f}ms")

    print(
        json.dumps(
            {"failed": failed, "max_latency_ms": MAX_LATENCY_MS, "checks": results},
            indent=2,
        )
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
