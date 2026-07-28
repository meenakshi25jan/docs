# 18. Motivation Agent

| Field | Value |
|-------|-------|
| **Wave** | 3 |
| **Priority** | P1 |
| **Status** | `planned` |
| **LangGraph Node** | Affective Node |
| **Primary Model** | GPT-4o |
| **Owner** | AI Platform Team |

---

## Purpose

Deliver encouragement, goal reinforcement, and positive feedback adapted to student state.

## Responsibilities

- Personalized praise
- Goal reminder linkage
- Streak and milestone celebration
- Re-engagement messaging

## Inputs

```json
{"student_id":"uuid","emotion":"frustrated","goals":[],"recent_wins":[]}
```

## Outputs

```json
{"message":"You improved fluency 12% this week!","tone":"warm","cta":"Try one more minute"}
```

## Tools

Goal Tracker, Progress Agent, Memory Agent

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o | GPT-4o-mini |

## Memory

PostgreSQL (motivation history)

## Prompt (Summary)

```
Be genuine and specific; tie encouragement to real progress data.
```

## Workflows

Negative affect detected → Motivation Agent → Conversation Agent

## KPIs

- Student satisfaction +10% when active
- Repeat session rate uplift

## Failure Handling

No progress data → generic but honest encouragement

## Observability

Motivation message acceptance rate

## Security

Avoid manipulative dark patterns

## Test Cases

- Frustrated student gets empathy first
- Milestone triggers celebration

## Implementation Notes

Not implemented.
