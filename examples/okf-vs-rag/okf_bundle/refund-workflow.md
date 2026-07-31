---
type: Playbook
title: Refund Workflow
description: Step-by-step process for processing customer refunds.
tags: [payments, refunds, workflow]
service: payment-service
security_level: internal
---

# Refund Workflow

Refunds require the `payments:refund` scope. See [Payment Authentication](authentication.md) for scope details.

## Steps

1. Validate the original charge exists and is refundable.
2. Call the processor refund API via [Service Dependencies](service-dependencies.md).
3. Update ledger and notify the customer.
4. Emit metrics to [Monitoring](monitoring.md).

## SLA

Refunds must complete within 24 hours for standard cards.
