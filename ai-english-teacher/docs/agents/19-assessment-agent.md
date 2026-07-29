# 19. Assessment Agent

| Field | Value |
|-------|-------|
| **Wave** | 4 |
| **Priority** | P0 |
| **Status** | `planned` |
| **LangGraph Node** | Learning Node |
| **Primary Model** | GPT-4o |
| **Owner** | AI Platform Team |

---

## Purpose

Evaluate student understanding, retention, application, and analysis ability.

## Responsibilities

- Formative and summative assessment
- Rubric-based scoring
- Skill breakdown by domain
- Store results for Progress Agent

## Inputs

```json
{"student_id":"uuid","responses":[],"rubric":"CEFR","topic":"present perfect"}
```

## Outputs

```json
{"overall_score":78,"skills":{"grammar":80,"vocabulary":75},"gaps":["irregular verbs"]}
```

## Tools

Rubric engine, Memory Agent

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o | GPT-4o-mini |

## Memory

PostgreSQL (assessment results)

## Prompt (Summary)

```
Score against rubric with evidence quotes from student answers.
```

## Workflows

Quiz complete → Assessment Agent → Weak Topic Agent

## KPIs

- Inter-rater agreement with teachers > 0.8
- Assessment latency < 3s

## Failure Handling

Incomplete answers → partial credit with explanation

## Observability

Score distribution by topic

## Security

Assessment data tenant-isolated

## Test Cases

- Strong answer scores > 85
- Empty answer scores 0 with feedback

## Implementation Notes

Partial: `assessment` agent stub exists; frontend assessment page present.
