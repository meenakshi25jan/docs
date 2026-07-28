# 3. Context Manager Agent

| Field | Value |
|-------|-------|
| **Wave** | 1 |
| **Priority** | P0 |
| **Status** | `planned` |
| **LangGraph Node** | Context Node |
| **Primary Model** | GPT-4o-mini |

---

## Purpose

Build optimal prompts by merging all context sources.

## Responsibilities

- Merge conversation history
- Student profile
- Long-term memory
- RAG chunks
- Current lesson

## Inputs

```json
{"student_id":"uuid","task":"teach|assess","raw_message":"string"}
```

## Outputs

```json
{"system_prompt":"string","user_prompt":"string","token_count":1842}
```

## Tools

Memory Agent, RAG Agent, Profile service

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o-mini | See Cost Optimization Agent (#38) |

## Memory

Ephemeral (per request)

## Prompt (Summary)

```
Assemble context within token budget; prioritize recent + weak areas.
```

## Workflows

Fetch context → Rank → Truncate → Emit prompt package

## KPIs

- Context relevance score > 4/5 (human eval)
- Token budget compliance 100%

## Failure Handling

Missing memory → proceed with profile only

## Observability

Log token counts and sources used

## Security

Strip PII from logs; tenant-scoped retrieval

## Test Cases

- Budget 8k tokens truncates oldest turns
- Weak area injected when relevant

## Implementation Notes

Partial: TeacherAgent flattens history in `agents/__init__.py`.
