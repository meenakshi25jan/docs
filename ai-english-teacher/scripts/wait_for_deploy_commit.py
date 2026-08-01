#!/usr/bin/env python3
"""Poll deployment until build-info reflects expected commit SHA."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request


def fetch_json(url: str, timeout: float) -> tuple[int, dict | None]:
  req = urllib.request.Request(url, headers={"Accept": "application/json"})
  try:
    with urllib.request.urlopen(req, timeout=timeout) as resp:
      return resp.status, json.loads(resp.read().decode())
  except urllib.error.HTTPError as exc:
    body = exc.read().decode("utf-8", errors="replace")
    try:
      return exc.code, json.loads(body)
    except json.JSONDecodeError:
      return exc.code, None
  except urllib.error.URLError:
    return 0, None


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument("--api-url", default=os.getenv("DEPLOY_API_URL", ""))
  parser.add_argument("--web-url", default=os.getenv("DEPLOY_WEB_URL", ""))
  parser.add_argument("--commit", default=os.getenv("EXPECTED_COMMIT", ""), required=True)
  parser.add_argument("--timeout", type=int, default=int(os.getenv("POLL_TIMEOUT", "600")))
  parser.add_argument("--interval", type=int, default=int(os.getenv("POLL_INTERVAL", "15")))
  args = parser.parse_args()

  if not args.api_url:
    print("FAIL: DEPLOY_API_URL / --api-url required")
    return 1

  deadline = time.time() + args.timeout
  attempt = 0
  while time.time() < deadline:
    attempt += 1
    api_status, api_body = fetch_json(f"{args.api_url.rstrip('/')}/build-info", timeout=10)
    api_commit = (api_body or {}).get("commit") if api_body else None
    web_commit = None
    if args.web_url:
      _, web_body = fetch_json(f"{args.web_url.rstrip('/')}/build-info.json", timeout=10)
      web_commit = (web_body or {}).get("commit") if web_body else None

    print(
      f"attempt={attempt} api_status={api_status} api_commit={api_commit} "
      f"web_commit={web_commit} expected={args.commit}"
    )

    api_ok = api_status == 200 and api_commit == args.commit
    web_ok = not args.web_url or web_commit == args.commit
    if api_ok and web_ok:
      print("OK: deployment reflects expected commit")
      return 0

    time.sleep(args.interval)

  print("FAIL: timed out waiting for deployment commit to match")
  return 1


if __name__ == "__main__":
  sys.exit(main())
