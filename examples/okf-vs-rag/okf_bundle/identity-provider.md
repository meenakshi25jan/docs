---
type: Service
title: Identity Provider
description: Corporate IdP that issues JWT tokens for internal services.
tags: [security, identity, sso]
service: identity-service
security_level: confidential
---

# Identity Provider

Issues short-lived JWT access tokens used by [Payment Authentication](authentication.md).

## Token claims

- `sub` — user or service principal ID
- `scope` — space-separated list (e.g. `payments:charge payments:refund`)
- `exp` — expiry (Unix timestamp)

## Key rotation

Signing keys rotate every 90 days. The payment gateway fetches JWKS from `/.well-known/jwks.json`.
