# 29. Parent Report Agent

| Field | Value |
|-------|-------|
| **Wave** | 5 |
| **Priority** | P2 |
| **Status** | `planned` |
| **LangGraph Node** | Report Node |
| **Primary Model** | GPT-4o |
| **Owner** | AI Platform Team |

---

## Purpose

Generate parent-friendly reports, recommendations, and improvement plans.

## Responsibilities

- Non-technical language summaries
- Strengths and areas to support at home
- Actionable parent tips
- PDF/email delivery

## Inputs

```json
{"student_id":"uuid","period":"month","parent_locale":"en"}
```

## Outputs

```json
{"report_html":"...","recommendations":["Practice 10 min daily"],"improvement_plan":{}}
```

## Tools

Progress Agent, Goal Tracker, email service

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o | GPT-4o-mini |

## Memory

PostgreSQL (sent reports archive)

## Prompt (Summary)

```
Write for parents: clear, positive, no jargon; include one home activity.
```

## Workflows

Monthly cron → Parent Report → email

## KPIs

- Parent satisfaction > 4/5
- Open rate > 50%

## Failure Handling

Missing parent email → queue for in-app notification

## Observability

Delivery and open tracking

## Security

COPPA parent consent required; no peer comparisons by default

## Test Cases

- Report excludes internal agent names
- Includes weekly study time

## Implementation Notes

Not implemented.
