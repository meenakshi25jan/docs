# 1. Orchestrator Agent

| Field | Value |
|-------|-------|
| **Wave** | 1 |
| **Priority** | P0 |
| **Status** | `mvp` |
| **LangGraph Node** | Root Node |
| **Primary Model** | GPT-4o-mini |

---

## Purpose

Master controller routing all agent workflows.

## Responsibilities

- Workflow routing
- Agent execution
- State management
- Retry handling
- Failure recovery

## Inputs

```json
{"session_id":"uuid","student_id":"uuid","message":"Explain gravity","intent_hint":"optional"}
```

## Outputs

```json
{"next_agent":"TeacherAgent","intent":"teaching","confidence":0.92}
```

## Tools

LangGraph, Agent Registry, Redis state

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o-mini | See Cost Optimization Agent (#38) |

## Memory

Redis (session graph state)

## Prompt (Summary)

```
Route student intent to the correct specialist agent. Prefer minimal latency.
```

## Workflows

Student → Orchestrator → Sub-Agent → Response

## KPIs

- Routing accuracy > 95%
- P95 latency < 500ms (routing only)

## Failure Handling

Retry 2x with backoff; fallback to ConversationAgent

## Observability

Trace ID per request; log agent path

## Security

Tenant isolation; no PII in routing logs

## Test Cases

- Greeting routes to ConversationAgent
- Assessment request routes to AssessmentAgent

## Implementation Notes

Implemented in `backend/app/orchestration/orchestrator.py` and `graph.py`. Routes greetings → ConversationAgent, teaching → TeacherAgent. LangGraph root node with moderation gate.
