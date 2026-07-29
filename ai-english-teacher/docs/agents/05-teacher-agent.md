# 5. Teacher Agent

| Field | Value |
|-------|-------|
| **Wave** | 1 |
| **Priority** | P0 |
| **Status** | `implemented` |
| **LangGraph Node** | Teaching Node |
| **Primary Model** | GPT-4o / Copilot |

---

## Purpose

Core teaching: explanations, examples, questioning, role-play.

## Responsibilities

- Teaching & explanation
- Examples
- Socratic questioning
- Role-play scenarios

## Inputs

```json
{"scenario":"job_interview","message":"string","cefr_level":"B1","message_history":[]}
```

## Outputs

```json
{"response":"string","grammar_corrections":[],"vocabulary_introduced":[]}
```

## Tools

LLM, Memory Agent, Grammar Agent (inline)

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o / Copilot | See Cost Optimization Agent (#38) |

## Memory

Conversation DB + learner profile

## Prompt (Summary)

```
Expert English teacher; adapt to CEFR; correct gently inline.
```

## Workflows

Scenario select → Teach loop → Corrections

## KPIs

- Learning gain per session (survey)
- Correction acceptance rate

## Failure Handling

JSON parse fail → extract raw_response

## Observability

Provider, latency, correction count

## Security

Content moderation hook (Wave 6)

## Test Cases

- Job interview scenario
- Grammar correction on request

## Implementation Notes

`TeacherAgent` in `backend/app/agents/__init__.py`; API: `/conversations`.
