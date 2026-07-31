#!/usr/bin/env python3
"""
Full production verification — health, routes, authenticated student/analytics APIs.

Exit 1 if any check fails. Writes JSON report to POST_DEPLOY_REPORT path.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

WEB_BASE = os.environ.get(
    "DEPLOY_WEB_URL", "https://ai-english-teacher-web.onrender.com"
).rstrip("/")
API_BASE = os.environ.get(
    "DEPLOY_API_URL", "https://ai-english-teacher-api.onrender.com"
).rstrip("/")
TIMEOUT = int(os.environ.get("TIMEOUT_SECONDS", "90"))
REPORT_PATH = os.environ.get(
    "POST_DEPLOY_REPORT",
    os.path.join(os.path.dirname(__file__), "post_deploy_report.json"),
)
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
            "email": email,
            "password": "PostDeployVerify1!",
            "first_name": "Post",
            "last_name": "Deploy",
        }
    ).encode()
    code, body = http_request(
        f"{API_BASE}/api/v1/auth/register",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=payload,
    )
    if code not in (200, 201):
        return None, f"register failed HTTP {code}: {body[:200]}"
    data = json.loads(body)
    token = data.get("tokens", {}).get("access_token")
    if not token:
        return None, "register response missing access_token"
    return token, "ok"


def main() -> int:
    checks: list[dict] = []
    failed = 0

    static_checks: list[tuple[str, str, int]] = [
        ("api_health", f"{API_BASE}/health", 200),
        ("api_live", f"{API_BASE}/health/live", 200),
        ("api_ready", f"{API_BASE}/health/ready", 200),
        ("api_openapi", f"{API_BASE}/openapi.json", 200),
        ("api_grammar_grades", f"{API_BASE}/api/v1/grammar/grades", 200),
        ("web_home", f"{WEB_BASE}/", 200),
        ("web_build_info", f"{WEB_BASE}/build-info.json", 200),
        ("web_grammar_class", f"{WEB_BASE}/grammar-class", 200),
        ("web_conversation", f"{WEB_BASE}/conversation", 200),
        ("web_api_proxy", f"{WEB_BASE}/api/v1/grammar/grades", 200),
    ]

    for name, url, expect in static_checks:
        code, body = http_request(url)
        if name == "api_ready" and code == 503:
            ok = False
        else:
            ok = code == expect
        if not ok:
            failed += 1
        checks.append(
            {
                "name": name,
                "url": url,
                "expected": expect,
                "status": code,
                "passed": ok,
                "detail": body[:250],
            }
        )
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: HTTP {code}")

    # build-info must list /grammar-class (stale deploy detection)
    _, build_info_body = http_request(f"{WEB_BASE}/build-info.json")
    try:
        build_info = json.loads(build_info_body)
        routes = build_info.get("routes") or []
        has_grammar = "/grammar-class" in routes
        checks.append(
            {
                "name": "web_build_info_grammar_class",
                "passed": has_grammar,
                "detail": f"commit={build_info.get('commit', '?')[:12]} nextBuildId={build_info.get('nextBuildId')}",
            }
        )
        if not has_grammar:
            failed += 1
            print(
                "[FAIL] web_build_info_grammar_class: /grammar-class not in routes list"
            )
        else:
            print(
                "[PASS] web_build_info_grammar_class: route listed in build-info.json"
            )
    except json.JSONDecodeError:
        failed += 1
        checks.append(
            {
                "name": "web_build_info_grammar_class",
                "passed": False,
                "detail": "invalid JSON",
            }
        )
        print("[FAIL] web_build_info_grammar_class: invalid build-info.json")

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
        auth_paths = [
            ("student_summary", f"{API_BASE}/api/v1/student-intelligence/summary", 200),
            ("student_profile", f"{API_BASE}/api/v1/student-intelligence/profile", 200),
            ("analytics_overview", f"{API_BASE}/api/v1/analytics/overview", 200),
            ("analytics_progress", f"{API_BASE}/api/v1/analytics/progress", 200),
        ]
        for name, url, expect in auth_paths:
            code, body = http_request(url, headers={"Authorization": f"Bearer {token}"})
            ok = code == expect
            if not ok:
                failed += 1
            checks.append(
                {
                    "name": name,
                    "url": url,
                    "expected": expect,
                    "status": code,
                    "passed": ok,
                    "detail": body[:250],
                }
            )
            print(f"[{'PASS' if ok else 'FAIL'}] {name}: HTTP {code}")

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
