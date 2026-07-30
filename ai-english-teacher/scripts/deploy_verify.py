#!/usr/bin/env python3
"""Post-deploy smoke verification for Render production URLs."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

WEB_BASE = os.environ.get(
    "DEPLOY_WEB_URL", "https://ai-english-teacher-web.onrender.com"
).rstrip("/")
API_BASE = os.environ.get(
    "DEPLOY_API_URL", "https://ai-english-teacher-api.onrender.com"
).rstrip("/")
TIMEOUT = int(os.environ.get("TIMEOUT_SECONDS", "90"))
OLD_BUILD_PREFIX = os.environ.get("EXPECT_BUILD_ID_CHANGE_FROM", "")
GRAMMAR_REQUIRED = os.environ.get("DEPLOY_VERIFY_GRAMMAR_CLASS", "true").lower() in (
    "1",
    "true",
    "yes",
)


def probe(
    url: str, accept: str = "application/json, text/html"
) -> tuple[int, str, str | None]:
    req = urllib.request.Request(url, headers={"Accept": accept})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            build_id = None
            if "<!--" in body:
                start = body.find("<!--") + 4
                end = body.find("-->", start)
                if end > start:
                    build_id = body[start:end]
            return resp.status, body[:300], build_id
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, body[:300], None
    except urllib.error.URLError as exc:
        return 0, str(exc.reason), None


def main() -> int:
    checks: list[tuple[str, str, int]] = [
        ("web_home", f"{WEB_BASE}/", 200),
        ("web_conversation", f"{WEB_BASE}/conversation", 200),
        ("web_login", f"{WEB_BASE}/login", 200),
        ("web_register", f"{WEB_BASE}/register", 200),
        ("web_assessment", f"{WEB_BASE}/assessment", 200),
        ("api_root", f"{API_BASE}/", 200),
        ("api_health", f"{API_BASE}/health", 200),
        ("api_live", f"{API_BASE}/health/live", 200),
        ("api_ready", f"{API_BASE}/health/ready", 200),
        ("api_docs", f"{API_BASE}/docs", 200),
        ("api_openapi", f"{API_BASE}/openapi.json", 200),
        ("api_grammar_grades", f"{API_BASE}/api/v1/grammar/grades", 200),
        ("web_api_proxy", f"{WEB_BASE}/api/v1/grammar/grades", 200),
    ]

    if GRAMMAR_REQUIRED:
        checks.insert(3, ("web_grammar_class", f"{WEB_BASE}/grammar-class", 200))

    results: list[dict] = []
    failed = 0
    grammar_build_id: str | None = None

    for name, url, expect in checks:
        code, detail, build_id = probe(url)
        ok = code == expect
        # ready endpoint may be 503 when DB down — still report
        if name == "api_ready" and code == 503:
            ok = False
        if not ok:
            failed += 1
        if name == "web_grammar_class":
            grammar_build_id = build_id
        results.append(
            {
                "name": name,
                "url": url,
                "expected": expect,
                "status": code,
                "passed": ok,
                "detail": detail,
                "build_id": build_id,
            }
        )
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}: HTTP {code} (expected {expect})")

    if OLD_BUILD_PREFIX and grammar_build_id:
        if grammar_build_id == OLD_BUILD_PREFIX:
            print(f"FAIL: build ID still {grammar_build_id} (expected change)")
            failed += 1
        else:
            print(f"Build ID changed: {OLD_BUILD_PREFIX} -> {grammar_build_id}")

    report = {"failed": failed, "checks": results}
    print(json.dumps(report, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
