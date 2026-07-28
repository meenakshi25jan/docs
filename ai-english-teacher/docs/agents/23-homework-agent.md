# 23. Homework Agent

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

Generate assignments, projects, and exercises aligned to lesson outcomes.

## Responsibilities

- Exercise generation by skill
- Estimated completion time
- Differentiation by level
- Submission rubric

## Inputs

```json
{"lesson_id":"uuid","student_id":"uuid","weak_topics":[],"duration_min":30}
```

## Outputs

```json
{"homework":{"title":"...","tasks":[],"rubric":{},"due_in_days":3}}
```

## Tools

RAG Agent, Curriculum Agent

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o | GPT-4o-mini |

## Memory

PostgreSQL (homework assignments)

## Prompt (Summary)

```
Create achievable homework linked to today's lesson and weak areas.
```

## Workflows

Lesson end → Homework Agent → notify student

## KPIs

- Completion rate > 60%
- Teacher edit rate < 20%

## Failure Handling

Content policy block → simplify task

## Observability

Homework completion funnel

## Security

Age-appropriate content checks via Moderation Agent

## Test Cases

- Homework references lesson topic
- Rubric included

## Implementation Notes

Not implemented.
