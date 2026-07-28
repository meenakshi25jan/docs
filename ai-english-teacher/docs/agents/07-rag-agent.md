# 7. RAG Agent

| Field | Value |
|-------|-------|
| **Wave** | 1 |
| **Priority** | P0 |
| **Status** | `planned` |
| **LangGraph Node** | RAG Node |
| **Primary Model** | Embeddings + GPT-4o |
| **Owner** | AI Platform Team |

---

## Purpose

Retrieve relevant books, courses, lessons, and knowledge assets for teaching.

## Responsibilities

- Vector search over curriculum content
- Chunk ranking and re-ranking
- Source attribution for citations
- Tenant-scoped knowledge isolation

## Inputs

```json
{"query":"Explain present perfect","student_id":"uuid","top_k":5,"filters":{"course_id":"optional"}}
```

## Outputs

```json
{"chunks":[{"text":"...","source":"Lesson 3","score":0.91}],"citations":["Course A / Unit 2"]}
```

## Tools

Qdrant, PostgreSQL metadata, embedding service

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | text-embedding-3-small | local embeddings |

## Memory

Qdrant (vectors), PostgreSQL (metadata)

## Prompt (Summary)

```
Retrieve top-k passages relevant to the student query and level.
```

## Workflows

Context Manager → RAG Agent → Teacher Agent

## KPIs

- Recall@5 > 85%
- P95 retrieval < 300ms

## Failure Handling

Qdrant unavailable → keyword SQL fallback; empty results → general knowledge disclaimer

## Observability

Log query, top scores, source IDs

## Security

Tenant filter on all queries; no cross-org leakage

## Test Cases

- Grammar query returns grammar lesson chunk
- Unknown topic returns empty with safe fallback

## Implementation Notes

Not implemented. Requires Qdrant collection per tenant.
