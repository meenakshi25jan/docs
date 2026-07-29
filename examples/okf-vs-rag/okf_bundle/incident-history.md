---
type: Playbook
title: Incident History
description: Record of past production incidents affecting payments.
tags: [incidents, postmortem]
service: payment-service
security_level: internal
---

# Incident History

## INC-2025-0412 — Auth outage (2025-04-12)

**Impact:** 23% of payment requests returned 401 for 18 minutes.

**Root cause:** [Identity Provider](identity-provider.md) JWKS endpoint returned stale keys after rotation.

**Resolution:** Rolled back key rotation; updated [Payment Authentication](authentication.md) runbook to cache-bust JWKS on rotation events.

**Follow-up:** Added `auth_failures_total` alert in [Monitoring](monitoring.md).
