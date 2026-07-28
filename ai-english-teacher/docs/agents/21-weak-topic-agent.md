# 21. Weak Topic Agent

| Field | Value |
|-------|-------|
| **Wave** | 4 |
| **Priority** | P1 |
| **Status** | `planned` |
| **LangGraph Node** | Learning Node |
| **Primary Model** | GPT-4o-mini |
| **Owner** | AI Platform Team |

---

## Purpose

Identify knowledge gaps, skill gaps, and misconceptions from assessment and conversation data.

## Responsibilities

- Aggregate errors across agents
- Rank weak topics by impact
- Detect persistent misconceptions
- Feed Recommendation and Curriculum agents

## Inputs

```json
{"student_id":"uuid","assessments":[],"grammar_errors":[],"memory_snapshot":{}}
```

## Outputs

```json
{"weak_topics":[{"topic":"articles","severity":0.8,"evidence_count":12}],"misconceptions":["a vs an rule"]}
```

## Tools

Memory Agent, Assessment Agent, analytics SQL

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o-mini | SQL aggregates |

## Memory

PostgreSQL + Memory Agent

## Prompt (Summary)

```
Prioritize top 3 weak areas with evidence counts.
```

## Workflows

Post-assessment → Weak Topic → Recommendation Agent

## KPIs

- Top-3 weak topics match teacher review > 75%

## Failure Handling

Sparse data → return exploratory topics from level defaults

## Observability

Weak topic heatmap per cohort

## Security

Student-level data access controls

## Test Cases

- Repeated article errors surface articles
- New student gets level defaults

## Implementation Notes

Not implemented.
