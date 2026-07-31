---
type: Reference
title: Service Dependencies
description: Downstream services the payment platform depends on.
tags: [architecture, dependencies]
service: payment-service
security_level: internal
---

# Service Dependencies

| Service | Purpose | Owner |
|---------|---------|-------|
| [Identity Provider](identity-provider.md) | JWT validation | Security |
| Stripe Adapter | Card processing | Payments |
| Ledger Service | Financial records | Finance |
| Notification Service | Customer emails | Platform |

The [Payment Gateway](payment-gateway.md) must reach all dependencies within the production VPC.
