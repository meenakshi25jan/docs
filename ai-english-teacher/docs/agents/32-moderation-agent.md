# 32. Moderation Agent

| Field | Value |
|-------|-------|
| **Wave** | 6 |
| **Priority** | P0 |
| **Status** | `planned` |
| **LangGraph Node** | Safety Gate Node |
| **Primary Model** | Moderation API + GPT-4o-mini |
| **Owner** | AI Platform Team |

---

## Purpose

Detect unsafe content, abuse, and age-sensitive material in inputs and outputs.

## Responsibilities

- Input and output moderation
- Abuse and harassment detection
- Age-appropriate filtering
- Block or sanitize with audit log

## Inputs

```json
{"text":"...","direction":"input|output","user_age":14}
```

## Outputs

```json
{"safe":false,"categories":["harassment"],"action":"block","sanitized":null}
```

## Tools

OpenAI Moderation, custom blocklists

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | omni-moderation-latest | keyword list |

## Memory

PostgreSQL (moderation events)

## Prompt (Summary)

```
Classify safety risk; prefer block over false negative for minors.
```

## Workflows

All messages → Moderation Gate → Orchestrator

## KPIs

- Recall on unsafe content > 95%
- False positive < 3%

## Failure Handling

API down → conservative keyword block + alert

## Observability

Moderation rate and category breakdown

## Security

First line of defense; integrates with Policy Agent

## Test Cases

- Profanity blocked for minors
- Educational violence context allowed

## Implementation Notes

Not implemented.
