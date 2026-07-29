# 2. Session Manager Agent

| Field | Value |
|-------|-------|
| **Wave** | 1 |
| **Priority** | P0 |
| **Status** | `planned` |
| **LangGraph Node** | Session Node |
| **Primary Model** | Rule-based |

---

## Purpose

Manage active session state across conversation, lesson, and audio.

## Responsibilities

- Conversation state
- Lesson state
- Audio state
- User context binding

## Inputs

```json
{"session_id":"uuid","action":"get|update|close","patch":{}}
```

## Outputs

```json
{"session":{"phase":"conversation","turn":5,"audio_active":false}}
```

## Tools

Redis, PostgreSQL sessions table

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | Rule-based | See Cost Optimization Agent (#38) |

## Memory

Redis (hot), PostgreSQL (cold archive)

## Prompt (Summary)

```
Persist and retrieve session snapshots atomically.
```

## Workflows

Start session → Update turns → Close session

## KPIs

- Session recovery rate > 99%
- Redis hit rate > 90%

## Failure Handling

Redis down → degrade to PostgreSQL read

## Observability

Session TTL metrics; orphan session alerts

## Security

Encrypt session payloads at rest

## Test Cases

- Resume session after refresh
- TTL expiry cleanup

## Implementation Notes

Redis in docker-compose; not wired to agents yet.
