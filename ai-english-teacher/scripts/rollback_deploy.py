#!/usr/bin/env python3
"""Rollback helper — re-trigger last known-good deploy hooks and fail loudly."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path


def post_hook(url: str, label: str) -> None:
  if not url:
    print(f"SKIP: {label} hook not configured")
    return
  req = urllib.request.Request(url, method="POST")
  with urllib.request.urlopen(req, timeout=60) as resp:
    print(f"OK: triggered {label} rollback hook HTTP {resp.status}")


def vercel_rollback() -> None:
  token = os.getenv("VERCEL_TOKEN")
  if not token:
    print("SKIP: VERCEL_TOKEN not set for CLI rollback")
    return
  cmd = ["npx", "vercel@latest", "rollback", "--yes", "--token", token]
  subprocess.run(cmd, check=False)


def main() -> int:
  state_path = Path(os.getenv("DEPLOY_STATE_PATH", "deploy-state.json"))
  previous_commit = os.getenv("ROLLBACK_COMMIT", "")
  if state_path.is_file():
    data = json.loads(state_path.read_text())
    previous_commit = previous_commit or data.get("last_good_commit", "")

  print("=" * 60)
  print("ROLLBACK INITIATED — production verification failed")
  print(f"Re-deploying last known-good commit: {previous_commit or 'unknown'}")
  print("=" * 60)

  post_hook(os.getenv("RENDER_ROLLBACK_HOOK", os.getenv("RENDER_DEPLOY_HOOK", "")), "Render API")
  post_hook(os.getenv("VERCEL_ROLLBACK_HOOK", ""), "Vercel")
  vercel_rollback()

  print(
    "Manual fallback: Render Dashboard → service → Rollback | "
    "Vercel Dashboard → Deployments → Promote previous"
  )
  return 1


if __name__ == "__main__":
  sys.exit(main())
