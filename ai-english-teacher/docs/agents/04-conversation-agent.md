# 4. Conversation Agent

| Field | Value |
|-------|-------|
| **Wave** | 1 |
| **Priority** | P0 |
| **Status** | `partial` |
| **LangGraph Node** | Dialogue Node |
| **Primary Model** | GPT-4o-mini |

---

## Purpose

Natural dialogue, question handling, and context preservation.

## Responsibilities

- Natural dialogue
- Question handling
- Response generation
- Context preservation

## Inputs

```json
{"message":"string","history":[],"student_profile":{}}
```

## Outputs

```json
{"response":"string","follow_up_question":"string"}
```

## Tools

LLM (Copilot/Groq/Ollama), Context Manager

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o-mini | See Cost Optimization Agent (#38) |

## Memory

Session history (Redis)

## Prompt (Summary)

```
Be warm, concise, and encourage the learner to speak more.
```

## Workflows

User message → Context → LLM → Response

## KPIs

- Student satisfaction > 4/5
- Avg turns per session > 6

## Failure Handling

LLM timeout → cached fallback response

## Observability

Latency, tokens, provider

## Security

Prompt injection guard (`prompt_guard.py`)

## Test Cases

- Handles greetings
- Handles off-topic redirect

## Implementation Notes

Merged into TeacherAgent today; split in V2.
