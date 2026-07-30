#!/usr/bin/env python3
"""Wait for Render service health endpoints before continuing deploy."""

from __future__ import annotations

import argparse
import os
import sys
import time
import urllib.error
import urllib.request

DEFAULT_PATHS = ["/health/live", "/health", "/"]


def probe(url: str, timeout: float) -> int:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except urllib.error.URLError:
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Wait until service responds healthy")
    parser.add_argument("--base-url", default=os.environ.get("WAIT_BASE_URL", ""))
    parser.add_argument(
        "--paths", default=os.environ.get("WAIT_PATHS", ",".join(DEFAULT_PATHS))
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=int(os.environ.get("WAIT_TIMEOUT", "600")),
    )
    parser.add_argument(
        "--interval", type=int, default=int(os.environ.get("WAIT_INTERVAL", "15"))
    )
    parser.add_argument("--per-request-timeout", type=int, default=30)
    args = parser.parse_args()

    if not args.base_url:
        print("FAIL: --base-url or WAIT_BASE_URL required")
        return 1

    base = args.base_url.rstrip("/")
    paths = [p.strip() for p in args.paths.split(",") if p.strip()]
    deadline = time.time() + args.timeout_seconds
    attempt = 0

    while time.time() < deadline:
        attempt += 1
        for path in paths:
            url = f"{base}{path}"
            code = probe(url, args.per_request_timeout)
            ready_path = path in ("/health/live", "/health", "/health/ready")
            if ready_path and code == 200:
                print(f"OK: {url} -> HTTP {code} (attempt {attempt})")
                return 0
            if path == "/" and code == 200:
                print(f"OK: {url} -> HTTP {code} (attempt {attempt})")
                return 0
            print(f"WAIT: {url} -> HTTP {code} (attempt {attempt})")
        time.sleep(args.interval)

    print(f"FAIL: service not healthy within {args.timeout_seconds}s")
    return 1


if __name__ == "__main__":
    sys.exit(main())
