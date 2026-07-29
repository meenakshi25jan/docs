# 25. Curriculum Agent

| Field | Value |
|-------|-------|
| **Wave** | 4 |
| **Priority** | P2 |
| **Status** | `planned` |
| **LangGraph Node** | Learning Node |
| **Primary Model** | GPT-4o |
| **Owner** | AI Platform Team |

---

## Purpose

Create lesson sequences, topic progression, and skill maps.

## Responsibilities

- Scope and sequence design
- Prerequisite mapping
- Skill map visualization data
- Align to standards (CEFR, IELTS)

## Inputs

```json
{"course_goal":"B2 conversation","weeks":12,"hours_per_week":3}
```

## Outputs

```json
{"sequence":[{"week":1,"topics":[],"skills":[]}],"skill_map":{}}
```

## Tools

RAG Agent, standards library

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o | template library |

## Memory

PostgreSQL (curriculum versions)

## Prompt (Summary)

```
Design pedagogically sound progression with spaced review.
```

## Workflows

Institution onboarding → Curriculum Agent → course publish

## KPIs

- Teacher approval > 85%
- Learning outcome lift vs unstructured

## Failure Handling

Overlong plan → compress with teacher review flag

## Observability

Curriculum version diff audit

## Security

Institution-owned IP protected

## Test Cases

- Prerequisites ordered correctly
- CEFR alignment tagged

## Implementation Notes

Not implemented.
