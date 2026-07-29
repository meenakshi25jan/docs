---
type: Playbook
title: Deployment
description: How payment services are deployed to production.
tags: [devops, deployment]
service: payment-service
security_level: internal
---

# Deployment

The [Payment Gateway](payment-gateway.md) deploys via blue/green on Kubernetes.

## Pre-deploy checklist

- Run integration tests against staging
- Verify [Service Dependencies](service-dependencies.md) health
- Confirm [Monitoring](monitoring.md) dashboards are green

## Rollback

Revert the deployment manifest and notify on-call per [Incident History](incident-history.md) procedures.
