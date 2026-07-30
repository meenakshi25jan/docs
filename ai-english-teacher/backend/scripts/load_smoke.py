#!/usr/bin/env python3
"""
Lightweight load smoke — sequential + small concurrency only (not stress testing).

Checks:
  - /health
  - /api/v1/production/readiness (admin token)
  - /api/v1/operations/health (admin token)

Usage:
  export API_BASE_URL=https://ai-english-teacher-api.onrender.com
  export ADMIN_TOKEN=your_admin_jwt
  python3 scripts/load_smoke.py

Optional:
  CONCURRENCY=3 (default 2, max 5)
  ROUNDS=2 (default 1)
  TIMEOUT_SECONDS=60
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field


@dataclass
class LatencyStats:
    count: int = 0
    failures: int = 0
    total_ms: float = 0.0
    min_ms: float = field(default_factory=lambda: float("inf"))
    max_ms: float = 0.0

    def record(self, elapsed_ms: float, ok: bool) -> None:
        self.count += 1
        if not ok:
            self.failures += 1
        self.total_ms += elapsed_ms
        self.min_ms = min(self.min_ms, elapsed_ms)
        self.max_ms = max(self.max_ms, elapsed_ms)

    def summary(self) -> dict:
        avg = self.total_ms / self.count if self.count else 0.0
        return {
            "count": self.count,
            "failures": self.failures,
            "latency_ms": {
                "avg": round(avg, 2),
                "min": round(self.min_ms if self.count else 0, 2),
                "max": round(self.max_ms, 2),
            },
        }


def _base() -> str:
    return os.environ.get("API_BASE_URL", "http://localhost:8000").rstrip("/")


def _prefix() -> str:
    p = os.environ.get("API_PREFIX", "/api/v1")
    return p if p.startswith("/") else f"/{p}"


def _timeout() -> int:
    return int(os.environ.get("TIMEOUT_SECONDS", "60"))


def _fetch(url: str, headers: dict[str, str] | None = None) -> tuple[bool, int, float]:
    hdrs = {"Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, headers=hdrs, method="GET")
        with urllib.request.urlopen(req, timeout=_timeout()) as resp:
            elapsed_ms = (time.perf_counter() - start) * 1000
            return resp.status == 200, resp.status, elapsed_ms
    except urllib.error.HTTPError as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return False, exc.code, elapsed_ms
    except Exception:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return False, 0, elapsed_ms


def run_load_smoke() -> dict:
    base = _base()
    prefix = _prefix()
    admin = os.environ.get("ADMIN_TOKEN")
    concurrency = min(5, max(1, int(os.environ.get("CONCURRENCY", "2"))))
    rounds = max(1, int(os.environ.get("ROUNDS", "1")))

    targets: list[tuple[str, dict[str, str] | None]] = [
        (f"{base}/health", None),
    ]
    if admin:
        auth = {"Authorization": f"Bearer {admin}"}
        targets.extend(
            [
                (f"{base}{prefix}/production/readiness", auth),
                (f"{base}{prefix}/operations/health", auth),
            ]
        )

    stats = LatencyStats()
    jobs: list[tuple[str, dict[str, str] | None]] = []
    for _ in range(rounds):
        jobs.extend(targets)

    # Sequential first pass
    for url, hdrs in targets:
        ok, code, ms = _fetch(url, hdrs)
        stats.record(ms, ok)
        print(f"[sequential] {url} -> HTTP {code} ({ms:.1f} ms)")

    # Small concurrency on public health only
    health_url = f"{base}/health"
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(_fetch, health_url, None) for _ in range(concurrency)]
        for fut in as_completed(futures):
            ok, code, ms = fut.result()
            stats.record(ms, ok)
            print(f"[concurrent] {health_url} -> HTTP {code} ({ms:.1f} ms)")

    result = {
        "base_url": base,
        "admin_token_set": bool(admin),
        "concurrency": concurrency,
        "rounds": rounds,
        **stats.summary(),
    }
    if not admin:
        result["warning"] = "ADMIN_TOKEN not set — authenticated endpoints skipped"
    return result


def main() -> int:
    summary = run_load_smoke()
    print(json.dumps(summary, indent=2))
    failed = summary.get("failures", 0)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
