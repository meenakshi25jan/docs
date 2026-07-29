# 26. Student Profile Agent

| Field | Value |
|-------|-------|
| **Wave** | 5 |
| **Priority** | P1 |
| **Status** | `planned` |
| **LangGraph Node** | Profile Node |
| **Primary Model** | GPT-4o-mini + SQL |
| **Owner** | AI Platform Team |

---

## Purpose

Maintain holistic learning profile, growth metrics, and behavior data.

## Responsibilities

- Unified learner profile
- Growth metrics aggregation
- Behavioral pattern summary
- Profile API for other agents

## Inputs

```json
{"student_id":"uuid","refresh":"full|incremental"}
```

## Outputs

```json
{"profile":{"level":"B1","strengths":[],"behaviors":{"sessions_per_week":4}}}
```

## Tools

PostgreSQL, Memory Agent, analytics

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o-mini | SQL only |

## Memory

PostgreSQL (profiles)

## Prompt (Summary)

```
Summarize learner in 3 bullets for teacher dashboard.
```

## Workflows

Nightly job → Student Profile → Dashboard Agent

## KPIs

- Profile freshness < 24h
- Dashboard load < 2s

## Failure Handling

Partial data → mark fields stale

## Observability

Profile completeness score

## Security

FERPA/GDPR field-level access

## Test Cases

- Profile merges assessment + conversation data
- PII fields masked for teachers without consent

## Implementation Notes

Not implemented. User table exists in DB.
