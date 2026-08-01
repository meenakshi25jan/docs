#!/usr/bin/env python3
"""Post-deploy verification for AI English Teacher MVP API."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime

API_BASE = os.environ.get(
    "DEPLOY_API_URL", "https://ai-english-teacher-api.onrender.com"
).rstrip("/")
WEB_BASE = os.environ.get(
    "DEPLOY_WEB_URL", "https://ai-english-teacher-web.onrender.com"
).rstrip("/")
TIMEOUT = int(os.environ.get("TIMEOUT_SECONDS", "90"))
REPORT_PATH = os.environ.get("POST_DEPLOY_REPORT", "post_deploy_report.json")
REGISTER_VERIFY = os.environ.get("POST_DEPLOY_REGISTER_USER", "true").lower() in (
    "1",
    "true",
    "yes",
)


def http_request(
    url: str,
    method: str = "GET",
    headers: dict | None = None,
    body: bytes | None = None,
) -> tuple[int, str]:
    hdrs = {"Accept": "application/json, text/html", **(headers or {})}
    req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        return 0, str(exc.reason)


def register_test_user() -> tuple[str | None, str]:
    if not REGISTER_VERIFY:
        return None, "skipped"
    email = f"postdeploy_{int(time.time())}@example.com"
    payload = json.dumps(
        {
            "name": "Post Deploy",
            "email": email,
            "password": "PostDeployVerify1!",
            "teacher_voice": "female",
        }
    ).encode()
    code, body = http_request(
        f"{API_BASE}/register",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=payload,
    )
    if code not in (200, 201):
        return None, f"register failed HTTP {code}: {body[:200]}"
    data = json.loads(body)
    token = data.get("access_token")
    if not token:
        return None, "register response missing access_token"
    return token, "ok"


def main() -> int:
    checks: list[dict] = []
    failed = 0

    static_checks: list[tuple[str, str, int | set[int]]] = [
        ("api_health", f"{API_BASE}/health", 200),
        ("api_live", f"{API_BASE}/health/live", 200),
        ("api_ready", f"{API_BASE}/health/ready", {200, 503}),
        ("api_home", f"{API_BASE}/home", 200),
        ("api_openapi", f"{API_BASE}/openapi.json", 200),
        ("web_home", f"{WEB_BASE}/", {200, 301, 302, 307, 308}),
    ]

    for name, url, expect in static_checks:
        code, body = http_request(url)
        if isinstance(expect, set):
            ok = code in expect
            expected_display = sorted(expect)
        else:
            ok = code == expect
            expected_display = expect
        if not ok:
            failed += 1
        checks.append(
            {
                "name": name,
                "url": url,
                "expected": expected_display,
                "status": code,
                "passed": ok,
                "detail": body[:250],
            }
        )
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: HTTP {code}")

    token, reg_msg = register_test_user()
    checks.append(
        {
            "name": "auth_register",
            "passed": token is not None or not REGISTER_VERIFY,
            "detail": reg_msg,
        }
    )
    if REGISTER_VERIFY and not token:
        failed += 1
        print(f"[FAIL] auth_register: {reg_msg}")
    elif REGISTER_VERIFY:
        print("[PASS] auth_register: token obtained")

    if token:
        code, body = http_request(
            f"{API_BASE}/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        ok = code == 200
        if not ok:
            failed += 1
        checks.append(
            {
                "name": "users_me",
                "url": f"{API_BASE}/users/me",
                "expected": 200,
                "status": code,
                "passed": ok,
                "detail": body[:250],
            }
        )
        print(f"[{'PASS' if ok else 'FAIL'}] users_me: HTTP {code}")

    report = {
        "timestamp": datetime.now(UTC).isoformat(),
        "web_base": WEB_BASE,
        "api_base": API_BASE,
        "failed": failed,
        "passed": len(checks) - failed,
        "checks": checks,
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print(f"\nReport: {REPORT_PATH}")
    print(json.dumps({"failed": failed, "total": len(checks)}, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
