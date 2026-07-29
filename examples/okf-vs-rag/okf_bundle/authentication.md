---
type: API Security
title: Payment Authentication
description: How the payment service authenticates incoming API requests.
tags: [payments, security, api]
service: payment-service
security_level: internal
---

# Payment Authentication

All requests to the payment service must include a valid JWT bearer token issued by the corporate identity provider.

## Flow

1. Client obtains a token from [Identity Provider](identity-provider.md).
2. Client sends `Authorization: Bearer <token>` on every request.
3. The [Payment Gateway](payment-gateway.md) validates the token signature and expiry.
4. Scopes are checked against the requested operation (e.g. `payments:charge`, `payments:refund`).

## Failure modes

- Missing token → `401 Unauthorized`
- Expired token → `401 Unauthorized` with `token_expired` error code
- Insufficient scope → `403 Forbidden`

## Related

- [Monitoring](monitoring.md) tracks authentication failure rates.
- [Incident History](incident-history.md) documents past auth outages.
