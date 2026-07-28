# 34. Citation Agent

| Field | Value |
|-------|-------|
| **Wave** | 6 |
| **Priority** | P2 |
| **Status** | `planned` |
| **LangGraph Node** | Safety Gate Node |
| **Primary Model** | GPT-4o-mini |
| **Owner** | AI Platform Team |

---

## Purpose

Add references, sources, and attributions to teaching content.

## Responsibilities

- Map claims to RAG sources
- Format citations (APA simple)
- Inline reference links
- Bibliography generation

## Inputs

```json
{"response":"...","rag_chunks":[{"source":"Lesson 2","id":"..."}]}
```

## Outputs

```json
{"cited_response":"... [1]","references":[{"id":1,"title":"Lesson 2"}]}
```

## Tools

RAG Agent metadata

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o-mini | template |

## Memory

N/A

## Prompt (Summary)

```
Insert minimal inline citations without disrupting readability.
```

## Workflows

RAG + Teacher → Citation Agent → student

## KPIs

- Citation accuracy > 95%
- Added latency < 500ms

## Failure Handling

No chunks → skip citations

## Observability

Citation coverage rate

## Security

Only cite tenant-approved sources

## Test Cases

- Two sources → two references
- No sources → unchanged text

## Implementation Notes

Not implemented.
