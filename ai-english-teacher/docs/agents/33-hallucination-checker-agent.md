# 33. Hallucination Checker Agent

| Field | Value |
|-------|-------|
| **Wave** | 6 |
| **Priority** | P1 |
| **Status** | `planned` |
| **LangGraph Node** | Safety Gate Node |
| **Primary Model** | GPT-4o + RAG verification |
| **Owner** | AI Platform Team |

---

## Purpose

Verify facts, educational responses, and generated content against trusted sources.

## Responsibilities

- Claim extraction
- RAG cross-check
- Confidence scoring
- Flag or rewrite unsupported claims

## Inputs

```json
{"response":"...","sources":[],"subject":"grammar"}
```

## Outputs

```json
{"verified":false,"claims":[{"text":"...","supported":false}],"suggested_fix":"..."}
```

## Tools

RAG Agent, fact DB

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o | GPT-4o-mini |

## Memory

Qdrant (verified facts cache)

## Prompt (Summary)

```
List factual claims; mark supported only with source evidence.
```

## Workflows

Teacher Agent output → Hallucination Checker → user

## KPIs

- Hallucination rate < 2% on eval set
- Latency < 2s

## Failure Handling

No sources → add uncertainty disclaimer

## Observability

Unsupported claim rate by subject

## Security

Do not leak source content across tenants

## Test Cases

- False historical fact flagged
- Common grammar rule passes

## Implementation Notes

Not implemented.
