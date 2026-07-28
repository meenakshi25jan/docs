# 24. Recommendation Agent

| Field | Value |
|-------|-------|
| **Wave** | 4 |
| **Priority** | P1 |
| **Status** | `planned` |
| **LangGraph Node** | Learning Node |
| **Primary Model** | GPT-4o |
| **Owner** | AI Platform Team |

---

## Purpose

Generate daily and weekly learning plans and course suggestions.

## Responsibilities

- Daily micro-plans
- Weekly study schedules
- Course and resource recommendations
- Balance skills across week

## Inputs

```json
{"student_id":"uuid","goals":[],"weak_topics":[],"available_min_per_day":20}
```

## Outputs

```json
{"daily_plan":[{"day":"Mon","tasks":[]}],"courses":["IELTS Prep B1"]}
```

## Tools

Weak Topic Agent, Goal Tracker, RAG Agent

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o | GPT-4o-mini |

## Memory

PostgreSQL (plans)

## Prompt (Summary)

```
Build realistic plans respecting time budget and goals.
```

## Workflows

Weekly cron → Recommendation Agent → student dashboard

## KPIs

- Plan adherence > 50%
- Goal progress correlation

## Failure Handling

Missing goals → default skill-balanced plan

## Observability

Recommendation click-through rate

## Security

N/A

## Test Cases

- 20 min/day respected
- Weak topic appears in plan

## Implementation Notes

Partial: `planner` agent stub in AGENT_REGISTRY.
