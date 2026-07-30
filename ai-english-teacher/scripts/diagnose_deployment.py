#!/usr/bin/env python3
"""Diagnose build and deployment errors — local + production comparison."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
WEB_BASE = os.environ.get(
    "DEPLOY_WEB_URL", "https://ai-english-teacher-web.onrender.com"
).rstrip("/")
API_BASE = os.environ.get(
    "DEPLOY_API_URL", "https://ai-english-teacher-api.onrender.com"
).rstrip("/")
TIMEOUT = int(os.environ.get("TIMEOUT_SECONDS", "90"))

FRONTEND_ROUTES = [
    "/",
    "/conversation",
    "/grammar-class",
    "/login",
    "/register",
    "/assessment",
    "/dashboard/student",
]

API_ROUTES = [
    "/",
    "/health",
    "/health/live",
    "/health/ready",
    "/docs",
    "/openapi.json",
    "/api/v1/grammar/grades",
]


def probe(url: str) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json, text/html"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            build_id = None
            if "<!--" in body:
                m = re.search(r"<!--([^>]+)-->", body)
                if m:
                    build_id = m.group(1).strip()
            return {
                "url": url,
                "status": resp.status,
                "ok": resp.status < 400,
                "build_id": build_id,
            }
    except urllib.error.HTTPError as exc:
        return {"url": url, "status": exc.code, "ok": False, "build_id": None}
    except urllib.error.URLError as exc:
        return {"url": url, "status": 0, "ok": False, "error": str(exc.reason)}


def check_local_build() -> list[str]:
    issues: list[str] = []
    standalone = FRONTEND / ".next/standalone/frontend/server.js"
    if not standalone.is_file():
        issues.append(
            "Local frontend not built — run: cd frontend && npm ci && npm run build"
        )
        return issues
    if not (FRONTEND / ".next/standalone/frontend/.next/static").is_dir():
        issues.append("Standalone static assets missing — postbuild may have failed")
    return issues


def check_source_routes() -> list[str]:
    issues: list[str] = []
    for route in ["/grammar-class", "/conversation"]:
        rel = route.lstrip("/")
        page = FRONTEND / "src/app" / rel / "page.tsx"
        if not page.is_file():
            issues.append(f"Missing source page: {page}")
    return issues


def main() -> int:
    report: dict = {"issues": [], "production": {}, "diagnosis": []}

    print("=== Source & build checks ===")
    for fn in (check_source_routes, check_local_build):
        found = fn()
        report["issues"].extend(found)
        for i in found:
            print(f"  FAIL: {i}")

    if not report["issues"]:
        print("  OK: source routes and local build artifacts")

    print("\n=== Production web ===")
    web_build_ids: set[str] = set()
    for path in FRONTEND_ROUTES:
        r = probe(f"{WEB_BASE}{path}")
        report["production"][path] = r
        status = "PASS" if r["ok"] else "FAIL"
        bid = r.get("build_id") or ""
        if bid:
            web_build_ids.add(bid)
        print(f"  [{status}] {path} -> HTTP {r['status']} build={bid}")

    print("\n=== Production API ===")
    for path in API_ROUTES:
        r = probe(f"{API_BASE}{path}")
        report["production"][f"api:{path}"] = r
        status = "PASS" if r["ok"] else "FAIL"
        print(f"  [{status}] {path} -> HTTP {r['status']}")

    grammar = report["production"].get("/grammar-class", {})
    if grammar.get("status") == 404:
        report["diagnosis"].append(
            "ROOT CAUSE: /grammar-class 404 — production web build is stale or wrong runtime. "
            "Source and local standalone serve 200. Fix: Render web Manual Deploy + Clear cache, "
            "Node runtime, rootDir ai-english-teacher/frontend, branch main."
        )

    if report["production"].get("api:/health/live", {}).get("status") == 404:
        report["diagnosis"].append(
            "API missing /health/live — production API not deployed from latest main/CI branch. "
            "Redeploy API from render.yaml with start.sh migrations."
        )

    if len(web_build_ids) == 1:
        print(f"\nProduction web build ID: {web_build_ids.pop()}")

    print("\n=== Diagnosis ===")
    for d in report["diagnosis"]:
        print(f"  • {d}")
    if not report["diagnosis"] and not report["issues"]:
        print("  No repository-controlled deployment errors detected.")

    out_path = ROOT / "scripts" / "diagnose_deployment_report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport written: {out_path}")

    failed = bool(report["issues"]) or any(
        not r.get("ok") for r in report["production"].values()
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
