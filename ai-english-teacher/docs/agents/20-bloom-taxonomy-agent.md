# 20. Bloom Taxonomy Agent

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

Measure cognitive levels: Remember, Understand, Apply, Analyze, Evaluate, Create.

## Responsibilities

- Classify question and answer cognitive level
- Balance lesson across Bloom levels
- Recommend higher-order tasks
- Track cognitive growth

## Inputs

```json
{"questions":[],"answers":[],"lesson_id":"uuid"}
```

## Outputs

```json
{"levels":{"remember":2,"understand":3,"apply":1},"dominant":"understand","recommendation":"add apply task"}
```

## Tools

Bloom classifier, curriculum metadata

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o | GPT-4o-mini |

## Memory

PostgreSQL (Bloom history)

## Prompt (Summary)

```
Map each interaction to Bloom level with brief justification.
```

## Workflows

Assessment Agent → Bloom Agent → Curriculum Agent

## KPIs

- Classification accuracy > 85% on gold set

## Failure Handling

Ambiguous task → mark as understand default

## Observability

Bloom mix per course

## Security

N/A

## Test Cases

- Recall question → remember
- Essay critique → evaluate

## Implementation Notes

Not implemented.
