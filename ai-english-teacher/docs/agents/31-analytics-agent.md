# 31. Analytics Agent

| Field | Value |
|-------|-------|
| **Wave** | 5 |
| **Priority** | P1 |
| **Status** | `planned` |
| **LangGraph Node** | Analytics Node |
| **Primary Model** | Python analytics service |
| **Owner** | AI Platform Team |

---

## Purpose

Produce learning, behavioral, and trend analytics for institution dashboards.

## Responsibilities

- Learning outcome trends
- Behavioral cohort analysis
- Funnel and retention metrics
- Export to BI tools

## Inputs

```json
{"tenant_id":"uuid","metric":"retention","granularity":"week","filters":{}}
```

## Outputs

```json
{"series":[],"insights":["Retention up 8% MoM"],"anomalies":[]}
```

## Tools

PostgreSQL, ClickHouse (optional), Python pandas

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | Python service | SQL |

## Memory

Warehouse tables

## Prompt (Summary)

```
N/A — primarily deterministic analytics
```

## Workflows

ETL → Analytics Agent → institution admin UI

## KPIs

- Query SLA < 10s for standard reports
- Data freshness < 1h

## Failure Handling

Heavy query → async job + email when ready

## Observability

Query cost and cache hit rate

## Security

Tenant isolation; k-anonymity for small cohorts

## Test Cases

- Retention cohort correct
- Small cohort suppressed

## Implementation Notes

Not implemented.
