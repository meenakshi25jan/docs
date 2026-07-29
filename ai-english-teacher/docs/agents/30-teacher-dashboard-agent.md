# 30. Teacher Dashboard Agent

| Field | Value |
|-------|-------|
| **Wave** | 5 |
| **Priority** | P1 |
| **Status** | `planned` |
| **LangGraph Node** | Report Node |
| **Primary Model** | GPT-4o-mini + SQL |
| **Owner** | AI Platform Team |

---

## Purpose

Support teacher insights, class analytics, and performance analytics.

## Responsibilities

- Class-level aggregates
- At-risk student flags
- Lesson effectiveness signals
- Natural language class summary

## Inputs

```json
{"teacher_id":"uuid","class_id":"uuid","date_range":{"from":"...","to":"..."}}
```

## Outputs

```json
{"summary":"...","at_risk":[{"student_id":"...","reason":"low engagement"}],"charts":{}}
```

## Tools

Analytics Agent, Student Profile Agent

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o-mini | SQL aggregates |

## Memory

PostgreSQL (cached dashboards)

## Prompt (Summary)

```
Highlight 3 class insights and 3 students needing attention.
```

## Workflows

Teacher opens dashboard → Teacher Dashboard Agent

## KPIs

- Dashboard P95 < 3s
- At-risk precision > 70%

## Failure Handling

Large class → paginate and pre-aggregate

## Observability

Dashboard query performance

## Security

Teacher sees only assigned classes

## Test Cases

- Class of 30 loads under 3s
- At-risk flag on zero sessions

## Implementation Notes

Not implemented.
