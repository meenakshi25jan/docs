#!/usr/bin/env python3
"""
Trigger Render deployments for AI English Teacher.

Methods (first match wins per service):
  1. Deploy hook URL (RENDER_DEPLOY_HOOK_API / RENDER_DEPLOY_HOOK_WEB)
  2. Render API (RENDER_API_KEY + RENDER_SERVICE_ID_API / RENDER_SERVICE_ID_WEB)

Environment:
  RENDER_DEPLOY_HOOK_API, RENDER_DEPLOY_HOOK_WEB
  RENDER_API_KEY
  RENDER_SERVICE_ID_API, RENDER_SERVICE_ID_WEB
  CLEAR_WEB_BUILD_CACHE=true  — clear cache on web deploy (recommended for /grammar-class)
  DEPLOY_TARGET=api|web|both   — deploy one service or both (default: both)
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

RENDER_API = "https://api.render.com/v1"


def post_hook(url: str, label: str) -> bool:
    print(f"Triggering deploy hook: {label}")
    req = urllib.request.Request(url, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            print(f"OK: {label} hook accepted (HTTP {resp.status})")
            return True
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"FAIL: {label} hook HTTP {exc.code}: {body[:300]}")
        return False
    except urllib.error.URLError as exc:
        print(f"FAIL: {label} hook: {exc.reason}")
        return False


def api_deploy(service_id: str, label: str, clear_cache: bool = False) -> bool:
    api_key = os.environ.get("RENDER_API_KEY", "")
    if not api_key:
        print(f"SKIP: {label} — no RENDER_API_KEY")
        return False
    payload: dict = {}
    if clear_cache:
        payload["clearCache"] = "clear"
    data = json.dumps(payload).encode() if payload else b""
    url = f"{RENDER_API}/services/{service_id}/deploys"
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    print(f"Triggering Render API deploy: {label} (clear_cache={clear_cache})")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            print(f"OK: {label} deploy started (HTTP {resp.status})")
            if body:
                print(body[:500])
            return True
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"FAIL: {label} API HTTP {exc.code}: {body[:500]}")
        return False
    except urllib.error.URLError as exc:
        print(f"FAIL: {label} API: {exc.reason}")
        return False


def deploy_service(
    label: str,
    hook_env: str,
    service_id_env: str,
    clear_cache: bool = False,
) -> bool:
    hook = os.environ.get(hook_env, "").strip()
    if hook:
        return post_hook(hook, label)
    service_id = os.environ.get(service_id_env, "").strip()
    if service_id:
        return api_deploy(service_id, label, clear_cache=clear_cache)
    print(f"SKIP: {label} — set {hook_env} or {service_id_env} (+ RENDER_API_KEY)")
    return False


def main() -> int:
    target = os.environ.get("DEPLOY_TARGET", "both").strip().lower()
    clear_web = os.environ.get("CLEAR_WEB_BUILD_CACHE", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    api_ok = True
    web_ok = True
    if target in ("both", "api"):
        api_ok = deploy_service(
            "ai-english-teacher-api",
            "RENDER_DEPLOY_HOOK_API",
            "RENDER_SERVICE_ID_API",
            clear_cache=False,
        )
    if target in ("both", "web"):
        web_ok = deploy_service(
            "ai-english-teacher-web",
            "RENDER_DEPLOY_HOOK_WEB",
            "RENDER_SERVICE_ID_WEB",
            clear_cache=clear_web,
        )
    if target not in ("both", "api", "web"):
        print(f"FAIL: invalid DEPLOY_TARGET={target!r} (use api, web, or both)")
        return 1
    if not api_ok and not web_ok:
        print("\nNo Render deploy triggered.")
        print("Configure GitHub secrets or export:")
        print("  RENDER_DEPLOY_HOOK_API, RENDER_DEPLOY_HOOK_WEB")
        print("  or RENDER_API_KEY + RENDER_SERVICE_ID_API + RENDER_SERVICE_ID_WEB")
        print(
            "\nBlueprint: Manual sync in Render dashboard if services are out of date."
        )
        return 1
    if not api_ok or not web_ok:
        print("\nWARN: One service was not triggered — check secrets above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
