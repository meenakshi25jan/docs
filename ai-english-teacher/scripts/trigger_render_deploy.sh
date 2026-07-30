#!/usr/bin/env bash
# Trigger Render redeploy via deploy hooks (set in environment or GitHub secrets).
set -euo pipefail

trigger() {
  local name="$1"
  local url="$2"
  if [ -z "$url" ]; then
    echo "SKIP: $name hook not set"
    return 0
  fi
  echo "Triggering $name..."
  curl -fsS -X POST "$url"
  echo "OK: $name deploy hook accepted"
}

trigger "RENDER_DEPLOY_HOOK_API" "${RENDER_DEPLOY_HOOK_API:-}"
trigger "RENDER_DEPLOY_HOOK_WEB" "${RENDER_DEPLOY_HOOK_WEB:-}"

if [ -z "${RENDER_DEPLOY_HOOK_API:-}" ] && [ -z "${RENDER_DEPLOY_HOOK_WEB:-}" ]; then
  echo "No deploy hooks configured."
  echo "Set RENDER_DEPLOY_HOOK_API and RENDER_DEPLOY_HOOK_WEB or use Render Dashboard Manual Deploy."
  exit 1
fi
