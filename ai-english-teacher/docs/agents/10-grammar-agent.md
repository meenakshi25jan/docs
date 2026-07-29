# 10. Grammar Agent

| Field | Value |
|-------|-------|
| **Wave** | 2 |
| **Priority** | P1 |
| **Status** | `planned` |
| **LangGraph Node** | Language Analysis Node |
| **Primary Model** | GPT-4o |
| **Owner** | AI Platform Team |

---

## Purpose

Detect grammar, tense, articles, and sentence structure errors in speech and text.

## Responsibilities

- Error detection and classification
- Correction with explanation
- Pattern tracking per student
- Severity scoring

## Inputs

```json
{"text":"I goed to school yesterday","student_id":"uuid","mode":"speech|writing"}
```

## Outputs

```json
{"errors":[{"type":"verb_tense","original":"goed","correction":"went","rule":"..."}],"score":72}
```

## Tools

LanguageTool (optional), LLM grammar checker

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o | GPT-4o-mini |

## Memory

Memory Agent (mistake patterns)

## Prompt (Summary)

```
Identify grammar errors; explain briefly; suggest one practice exercise.
```

## Workflows

Conversation → Grammar Agent → inline correction

## KPIs

- Precision > 90% on labeled set
- False positive rate < 5%

## Failure Handling

Ambiguous sentence → ask clarifying question instead of correcting

## Observability

Error type histogram per tenant

## Security

No storage of offensive content beyond moderation pipeline

## Test Cases

- Article omission detected
- Correct sentence returns zero errors

## Implementation Notes

Partial: `grammar` agent stub in AGENT_REGISTRY.
