#!/usr/bin/env python3
"""
Production smoke tests — read-only HTTP checks against a deployed API.

Usage:
  export API_BASE_URL=https://ai-english-teacher-api.onrender.com
  export ADMIN_TOKEN=your_admin_jwt
  python3 scripts/production_smoke_test.py

Optional:
  API_PREFIX=/api/v1 (default)
  STUDENT_TOKEN=... (for RBAC negative checks)
  TIMEOUT_SECONDS=60
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass


REQUEST_ID_HEADER = "X-Request-ID"


@dataclass
class SmokeResult:
    name: str
    passed: bool
    status_code: int | None = None
    detail: str = ""


def _base_url() -> str:
    base = os.environ.get("API_BASE_URL", "http://localhost:8000").rstrip("/")
    prefix = os.environ.get("API_PREFIX", "/api/v1")
    if not prefix.startswith("/"):
        prefix = f"/{prefix}"
    return f"{base}{prefix}"


def _api_root() -> str:
    return os.environ.get("API_BASE_URL", "http://localhost:8000").rstrip("/")


def _timeout() -> int:
    return int(os.environ.get("TIMEOUT_SECONDS", "60"))


def _request(
    path: str,
    token: str | None = None,
    expect_status: int | tuple[int, ...] = 200,
    extra_headers: dict[str, str] | None = None,
    return_headers: bool = False,
) -> SmokeResult:
    url = f"{_base_url()}{path}" if path.startswith("/") else path
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if extra_headers:
        headers.update(extra_headers)

    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=_timeout()) as resp:
            code = resp.status
            body = resp.read().decode("utf-8", errors="replace")
            ok = code in expect_status if isinstance(expect_status, tuple) else code == expect_status
            detail = body[:200]
            if return_headers:
                rid = resp.headers.get(REQUEST_ID_HEADER, "")
                detail = f"request_id={rid} {detail[:120]}"
                if ok and not rid:
                    ok = False
                    detail = "missing X-Request-ID header"
            return SmokeResult(name=path, passed=ok, status_code=code, detail=detail)
    except urllib.error.HTTPError as exc:
        code = exc.code
        ok = code in expect_status if isinstance(expect_status, tuple) else code == expect_status
        detail = exc.read().decode("utf-8", errors="replace")[:200]
        if return_headers:
            rid = exc.headers.get(REQUEST_ID_HEADER, "")
            detail = f"request_id={rid} {detail[:120]}"
        return SmokeResult(name=path, passed=ok, status_code=code, detail=detail)
    except Exception as exc:
        return SmokeResult(name=path, passed=False, detail=f"{type(exc).__name__}: {exc}")


def _request_root_health(path: str, return_headers: bool = False) -> SmokeResult:
    url = f"{_api_root()}{path}"
    headers = {"Accept": "application/json"}
    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=_timeout()) as resp:
            code = resp.status
            ok = code == 200
            detail = ""
            if return_headers:
                rid = resp.headers.get(REQUEST_ID_HEADER, "")
                detail = f"request_id={rid}"
                if not rid:
                    ok = False
                    detail = "missing X-Request-ID header"
            return SmokeResult(name=path, passed=ok, status_code=code, detail=detail)
    except Exception as exc:
        return SmokeResult(name=path, passed=False, detail=str(exc))


def run_smoke_tests() -> list[SmokeResult]:
    admin = os.environ.get("ADMIN_TOKEN")
    student = os.environ.get("STUDENT_TOKEN")
    results: list[SmokeResult] = []

    for path in ("/health", "/health/auth", "/health/ai"):
        results.append(_request_root_health(path))

    results.append(_request_root_health("/health", return_headers=True))

    custom_rid = "smoke-test-request-id-001"
    results.append(
        _request(
            f"{_api_root()}/health",
            extra_headers={REQUEST_ID_HEADER: custom_rid},
            return_headers=True,
        )
    )
    propagated = results[-1]
    if propagated.passed and custom_rid not in propagated.detail:
        results[-1] = SmokeResult(
            name="/health (propagate request id)",
            passed=False,
            status_code=propagated.status_code,
            detail=f"expected {custom_rid} in response",
        )
    else:
        results[-1].name = "/health (propagate request id)"

    if not admin:
        results.append(
            SmokeResult(
                name="admin_token",
                passed=False,
                detail="ADMIN_TOKEN not set — skipping authenticated checks",
            )
        )
        return results

    # Operations
    results.append(_request("/operations/health", token=admin))
    results.append(_request("/operations/overview", token=admin))

    # Security
    results.append(_request("/security/summary", token=admin))
    results.append(_request("/security/rls", token=admin))
    results.append(_request("/security/auth", token=admin))
    results.append(_request("/security/authorization", token=admin))

    # Production readiness
    results.append(_request("/production/readiness", token=admin))

    # Reliability
    results.append(_request("/reliability/status", token=admin))
    results.append(_request("/reliability/logging", token=admin))
    results.append(_request("/reliability/backup", token=admin))
    results.append(_request("/reliability/performance", token=admin))

    # Analytics / governance sanity
    results.append(_request("/analytics/overview", token=admin))
    results.append(_request("/governance/summary", token=admin))

    if student:
        for path in (
            "/production/readiness",
            "/security/summary",
            "/reliability/status",
            "/operations/health",
        ):
            results.append(_request(path, token=student, expect_status=403))

    return results


def main() -> int:
    print(f"Smoke target: {_base_url()}")
    results = run_smoke_tests()
    failed = [r for r in results if not r.passed]

    for r in results:
        status = "PASS" if r.passed else "FAIL"
        code = r.status_code if r.status_code is not None else "-"
        print(f"[{status}] {r.name} (HTTP {code}) {r.detail[:80]}")

    summary = {
        "total": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
    }
    print(json.dumps(summary, indent=2))

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
