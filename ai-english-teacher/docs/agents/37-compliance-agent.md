# 37. Compliance Agent

| Field | Value |
|-------|-------|
| **Wave** | 6 |
| **Priority** | P1 |
| **Status** | `planned` |
| **LangGraph Node** | Governance Node |
| **Primary Model** | Rules + documentation |
| **Owner** | AI Platform Team |

---

## Purpose

Support GDPR, FERPA, COPPA, SOC2, and ISO27001 compliance workflows.

## Responsibilities

- Consent tracking
- Data retention enforcement
- Compliance report generation
- Cross-agent compliance checks

## Inputs

```json
{"request_type":"dsar_export|delete|audit","subject_id":"uuid","regulation":"GDPR"}
```

## Outputs

```json
{"status":"completed","artifacts":["export.zip"],"audit_id":"..."}
```

## Tools

Privacy Agent, PostgreSQL, object storage

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | Rules engine | N/A |

## Memory

Compliance audit store

## Prompt (Summary)

```
N/A — procedural agent
```

## Workflows

Admin request → Compliance Agent → coordinate deletes/exports

## KPIs

- DSAR SLA < 30 days
- 100% delete propagation

## Failure Handling

Partial delete → rollback and alert DPO

## Observability

Compliance request queue depth

## Security

Highest privilege; MFA required

## Test Cases

- GDPR export includes all student tables
- Delete removes Qdrant vectors

## Implementation Notes

Not implemented.
