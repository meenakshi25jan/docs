# 27. Goal Tracker Agent

| Field | Value |
|-------|-------|
| **Wave** | 5 |
| **Priority** | P1 |
| **Status** | `planned` |
| **LangGraph Node** | Profile Node |
| **Primary Model** | Rules + GPT-4o-mini |
| **Owner** | AI Platform Team |

---

## Purpose

Track English fluency, IELTS, exam prep, and communication goals.

## Responsibilities

- Goal CRUD and milestones
- Progress percent calculation
- Deadline reminders
- Goal attainment prediction

## Inputs

```json
{"student_id":"uuid","goal":{"type":"IELTS","target_band":7,"deadline":"2026-12-01"}}
```

## Outputs

```json
{"progress_pct":42,"on_track":true,"milestones":[{"name":"Band 6.5 mock","done":false}]}
```

## Tools

Progress Agent, Assessment Agent

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o-mini | linear projection |

## Memory

PostgreSQL (goals)

## Prompt (Summary)

```
Explain goal progress in plain language with next milestone.
```

## Workflows

Student sets goal → Goal Tracker → Motivation Agent

## KPIs

- Goal completion rate > 40%
- Reminder open rate > 25%

## Failure Handling

Unrealistic goal → suggest adjusted target

## Observability

Goal type distribution

## Security

Goals visible to student and linked parent account

## Test Cases

- IELTS goal tracks band progress
- Past deadline flags off-track

## Implementation Notes

Not implemented.
