# 6. Memory Agent

| Field | Value |
|-------|-------|
| **Wave** | 1 |
| **Priority** | P0 |
| **Status** | `planned` |
| **LangGraph Node** | Memory Node |
| **Primary Model** | Embeddings + rules |

---

## Purpose

Store and retrieve learner mistakes, preferences, weak areas, progress.

## Responsibilities

- Mistake tracking
- Preferences
- Weak areas
- Progress snapshots

## Inputs

```json
{"student_id":"uuid","action":"store|recall","payload":{}}
```

## Outputs

```json
{"memories":[{"type":"mistake","text":"...","weight":0.8}]}
```

## Tools

PostgreSQL, Redis cache, Qdrant vectors

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | Embeddings + rules | See Cost Optimization Agent (#38) |

## Memory

Redis (recent), PostgreSQL (structured), Qdrant (semantic)

## Prompt (Summary)

```
Store durable learning signals; recall top-k relevant memories.
```

## Workflows

Write after assessment → Recall before teach

## KPIs

- Recall precision > 80%
- Write latency < 100ms

## Failure Handling

Vector DB down → SQL fallback

## Observability

Memory write audit trail

## Security

GDPR delete propagates to all stores

## Test Cases

- Store article error → recall in next lesson

## Implementation Notes

DB tables exist; agent not implemented.
