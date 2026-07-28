# 36. Policy Agent

| Field | Value |
|-------|-------|
| **Wave** | 6 |
| **Priority** | P1 |
| **Status** | `planned` |
| **LangGraph Node** | Safety Gate Node |
| **Primary Model** | Rules engine + GPT-4o-mini |
| **Owner** | AI Platform Team |

---

## Purpose

Enforce school policies, learning policies, and safety rules per tenant.

## Responsibilities

- Tenant policy rule evaluation
- Blocked topics and hours
- Allowed model/tool restrictions
- Policy violation responses

## Inputs

```json
{"tenant_id":"uuid","action":"teach","topic":"...","user_role":"student"}
```

## Outputs

```json
{"allowed":true,"violations":[],"message":null}
```

## Tools

Policy store (PostgreSQL), Admin API

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | Rules engine | GPT-4o-mini |

## Memory

PostgreSQL (policy versions)

## Prompt (Summary)

```
Explain policy violation neutrally with allowed alternative.
```

## Workflows

Orchestrator → Policy Agent → proceed or block

## KPIs

- Zero unauthorized policy bypass
- Evaluation < 50ms

## Failure Handling

Policy store down → deny by default for K-12 tenants

## Observability

Violation counts by rule ID

## Security

Immutable policy audit trail

## Test Cases

- Blocked topic rejected
- After-hours rule for minor

## Implementation Notes

Not implemented.
