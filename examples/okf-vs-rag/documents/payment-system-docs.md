# Payment System Documentation

This document covers authentication, the payment gateway, refunds, monitoring, identity, dependencies, incidents, and deployment for the payment platform.

## Payment Authentication

All requests to the payment service must include a valid JWT bearer token issued by the corporate identity provider.

### Flow

1. Client obtains a token from the Identity Provider.
2. Client sends `Authorization: Bearer <token>` on every request.
3. The Payment Gateway validates the token signature and expiry.
4. Scopes are checked against the requested operation (e.g. `payments:charge`, `payments:refund`).

### Failure modes

- Missing token → `401 Unauthorized`
- Expired token → `401 Unauthorized` with `token_expired` error code
- Insufficient scope → `403 Forbidden`

Monitoring tracks authentication failure rates. Incident History documents past auth outages.

## Payment Gateway

The payment gateway is the public entry point for all payment operations. It terminates TLS, enforces authentication, and routes requests to downstream processors.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/charges` | Create a charge |
| POST | `/v1/refunds` | Initiate a refund workflow |
| GET | `/v1/health` | Health check (no auth required) |

### Dependencies

The gateway depends on the Identity Provider for JWT validation keys and on Service Dependencies for downstream processor routing.

## Refund Workflow

Refunds require the `payments:refund` scope. See Payment Authentication for scope details.

### Steps

1. Validate the original charge exists and is refundable.
2. Call the processor refund API via Service Dependencies.
3. Update ledger and notify the customer.
4. Emit metrics to Monitoring.

Refunds must complete within 24 hours for standard cards.

## Monitoring

### Key metrics

- `auth_failures_total` — spikes may indicate Identity Provider issues
- `charge_latency_p99` — gateway performance
- `refund_error_rate` — refund workflow health

### Dashboards

Payment Gateway overview and authentication failures (linked to Incident History).

Page on-call when `auth_failures_total` exceeds 50/min for 5 minutes.

## Identity Provider

Issues short-lived JWT access tokens used by Payment Authentication.

### Token claims

- `sub` — user or service principal ID
- `scope` — space-separated list (e.g. `payments:charge payments:refund`)
- `exp` — expiry (Unix timestamp)

Signing keys rotate every 90 days. The payment gateway fetches JWKS from `/.well-known/jwks.json`.

## Service Dependencies

| Service | Purpose | Owner |
|---------|---------|-------|
| Identity Provider | JWT validation | Security |
| Stripe Adapter | Card processing | Payments |
| Ledger Service | Financial records | Finance |
| Notification Service | Customer emails | Platform |

The Payment Gateway must reach all dependencies within the production VPC.

## Incident History

### INC-2025-0412 — Auth outage (2025-04-12)

**Impact:** 23% of payment requests returned 401 for 18 minutes.

**Root cause:** Identity Provider JWKS endpoint returned stale keys after rotation.

**Resolution:** Rolled back key rotation; updated Payment Authentication runbook to cache-bust JWKS on rotation events.

**Follow-up:** Added `auth_failures_total` alert in Monitoring.

## Deployment

The Payment Gateway deploys via blue/green on Kubernetes.

### Pre-deploy checklist

- Run integration tests against staging
- Verify Service Dependencies health
- Confirm Monitoring dashboards are green

Revert the deployment manifest and notify on-call per Incident History procedures on rollback.
