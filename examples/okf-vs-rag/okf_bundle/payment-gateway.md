---
type: Service
title: Payment Gateway
description: Core service that routes payment requests to processors.
tags: [payments, gateway, api]
service: payment-service
security_level: internal
---

# Payment Gateway

The payment gateway is the public entry point for all payment operations. It terminates TLS, enforces [Payment Authentication](authentication.md), and routes requests to downstream processors.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/charges` | Create a charge |
| POST | `/v1/refunds` | Initiate a [Refund Workflow](refund-workflow.md) |
| GET | `/v1/health` | Health check (no auth required) |

## Dependencies

- [Identity Provider](identity-provider.md) for JWT validation keys
- [Service Dependencies](service-dependencies.md) for downstream processor routing
