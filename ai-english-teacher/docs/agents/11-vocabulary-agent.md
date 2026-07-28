# 11. Vocabulary Agent

| Field | Value |
|-------|-------|
| **Wave** | 2 |
| **Priority** | P1 |
| **Status** | `planned` |
| **LangGraph Node** | Language Analysis Node |
| **Primary Model** | GPT-4o-mini |
| **Owner** | AI Platform Team |

---

## Purpose

Analyze vocabulary range, word repetition, and lexical complexity.

## Responsibilities

- Unique word count and diversity
- Repetition and overuse detection
- CEFR level estimation
- Suggest richer alternatives

## Inputs

```json
{"text":"...","student_id":"uuid","target_level":"B1"}
```

## Outputs

```json
{"unique_words":42,"repetitions":["good"],"cefr_estimate":"B1","suggestions":["excellent","wonderful"]}
```

## Tools

Lexical database, n-gram analyzer

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o-mini | frequency lists |

## Memory

Memory Agent (vocabulary gaps)

## Prompt (Summary)

```
Highlight 2–3 words to upgrade; keep tone supportive.
```

## Workflows

Writing/speaking analysis → Vocabulary Agent → report

## KPIs

- CEFR estimate within ±1 level
- Suggestion relevance > 80%

## Failure Handling

Very short input → skip complexity analysis

## Observability

Track vocabulary growth over time

## Security

Student text not used for model training

## Test Cases

- Repeated 'nice' flagged
- Advanced essay rated B2+

## Implementation Notes

Partial: `vocabulary` agent stub in AGENT_REGISTRY.
