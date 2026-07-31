---
type: Metric
title: Payment Monitoring
description: Dashboards and alerts for the payment platform.
tags: [payments, monitoring, observability]
service: payment-service
security_level: internal
---

# Monitoring

## Key metrics

- `auth_failures_total` — spikes may indicate [Identity Provider](identity-provider.md) issues
- `charge_latency_p99` — gateway performance
- `refund_error_rate` — [Refund Workflow](refund-workflow.md) health

## Dashboards

- Payment Gateway overview
- Authentication failures (linked to [Incident History](incident-history.md))

## Alerts

Page on-call when `auth_failures_total` exceeds 50/min for 5 minutes.
