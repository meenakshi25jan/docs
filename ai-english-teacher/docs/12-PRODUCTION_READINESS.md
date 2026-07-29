# Production Readiness Checklist

## Infrastructure

- [ ] AKS cluster provisioned with 3 node pools (system, app, ai-workers)
- [ ] PostgreSQL Flexible Server with HA enabled and pgvector extension
- [ ] Azure Cache for Redis (Premium tier) with persistence
- [ ] Azure Blob Storage with lifecycle management policies
- [ ] Azure Front Door with WAF rules configured
- [ ] Azure Key Vault for all secrets (no secrets in env files)
- [ ] cert-manager installed with Let's Encrypt ClusterIssuer
- [ ] DNS records configured and verified
- [ ] Terraform state stored in Azure Storage with locking

## Security

- [ ] JWT RS256 key pair generated and stored in Key Vault
- [ ] OAuth2 credentials configured (Google, Microsoft)
- [ ] Row-Level Security policies tested for all tenant tables
- [ ] Rate limiting enabled (100/min user, 1000/min tenant)
- [ ] Prompt injection protection active on all AI endpoints
- [ ] Input validation on all API endpoints (Pydantic)
- [ ] CORS restricted to production domains
- [ ] TLS 1.3 enforced on all endpoints
- [ ] PII fields encrypted at rest
- [ ] Audit logging enabled for all data mutations
- [ ] OWASP ZAP scan passed (0 critical, 0 high)
- [ ] Dependency vulnerability scan passed (Trivy/Snyk)
- [ ] RBAC tested for all roles (student, teacher, admin)

## Application

- [ ] All API endpoints documented in OpenAPI spec
- [ ] Health check endpoint responding (`/health`)
- [ ] Prometheus metrics exposed (`/metrics`)
- [ ] Application Insights instrumentation active
- [ ] Structured logging (JSON) with correlation IDs
- [ ] Graceful shutdown handling (SIGTERM)
- [ ] Database migrations tested (up and down)
- [ ] Seed data script for initial tenant/admin user
- [ ] AI fallback behavior tested (Azure OpenAI unavailable)
- [ ] Error responses follow RFC 7807 format

## AI & Scoring

- [ ] Azure OpenAI GPT-5.5 deployment verified
- [ ] Azure Speech Services connectivity tested
- [ ] All 11 AI agents tested with real LLM responses
- [ ] Scoring engine validated against sample assessments
- [ ] CEFR/IELTS/PTE mapping calibrated with test data
- [ ] Token usage monitoring and alerts configured
- [ ] AI rate limiting per tenant enforced

## Frontend

- [ ] Production build succeeds (`npm run build`)
- [ ] All dashboard pages render with API data
- [ ] Mobile responsive design verified (375px–1920px)
- [ ] Authentication flow end-to-end tested
- [ ] Error boundaries and loading states implemented
- [ ] Lighthouse performance score > 90
- [ ] Accessibility audit passed (WCAG 2.1 AA)

## DevOps & CI/CD

- [ ] GitHub Actions CI pipeline passing (lint, test, build)
- [ ] CD pipeline deploys to staging on merge to main
- [ ] Production deployment requires manual approval
- [ ] Docker images scanned for vulnerabilities
- [ ] Rollback procedure documented and tested
- [ ] Database backup schedule configured (daily + PITR)
- [ ] Disaster recovery runbook documented

## Monitoring & Alerting

- [ ] Application Insights dashboards configured
- [ ] Grafana dashboards for API latency, error rate, AI usage
- [ ] Alerts: API error rate > 1%, p95 latency > 1s
- [ ] Alerts: Database CPU > 80%, connections > 80%
- [ ] Alerts: AI token usage > 80% of monthly budget
- [ ] Alerts: Pod crash loop, OOM kills
- [ ] On-call rotation configured (PagerDuty/Opsgenie)
- [ ] Status page configured

## Performance

- [ ] Load test: 10K req/s sustained for 10 minutes
- [ ] AI assessment: 100 concurrent, p95 < 30s
- [ ] Database queries: dashboard < 100ms p95
- [ ] HPA tested: scales up under load, scales down after
- [ ] Connection pooling verified (PgBouncer)

## Compliance & Legal

- [ ] Privacy policy published
- [ ] Terms of service published
- [ ] GDPR data export endpoint implemented
- [ ] GDPR data deletion endpoint implemented
- [ ] Cookie consent banner (if applicable)
- [ ] Data processing agreement template for enterprise

## Documentation

- [ ] API documentation published (Swagger/ReDoc)
- [ ] Architecture diagrams up to date
- [ ] Runbook for common operations
- [ ] Onboarding guide for new developers
- [ ] Incident response playbook

## Go/No-Go Criteria

| Criteria | Threshold | Status |
|----------|-----------|--------|
| Test coverage | > 70% | Pending |
| Critical vulnerabilities | 0 | Pending |
| API p95 latency | < 500ms | Pending |
| Uptime (staging, 7 days) | > 99.9% | Pending |
| AI assessment accuracy | > 85% CEFR ±0.5 | Pending |
| Load test passed | 10K req/s | Pending |

**Sign-off required from:** Engineering Lead, Security, DevOps, Product
