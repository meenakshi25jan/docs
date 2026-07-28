# 28. Progress Agent

| Field | Value |
|-------|-------|
| **Wave** | 5 |
| **Priority** | P1 |
| **Status** | `planned` |
| **LangGraph Node** | Profile Node |
| **Primary Model** | SQL + GPT-4o-mini |
| **Owner** | AI Platform Team |

---

## Purpose

Create weekly, monthly, and yearly progress reports.

## Responsibilities

- Time-bucketed metrics
- Skill trend charts data
- Comparison to personal baseline
- Export for Parent Report Agent

## Inputs

```json
{"student_id":"uuid","period":"week|month|year","end_date":"2026-07-26"}
```

## Outputs

```json
{"period":"week","metrics":{"fluency_delta":5,"sessions":4},"narrative":"..."}
```

## Tools

PostgreSQL analytics, chart data API

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o-mini | template narrative |

## Memory

PostgreSQL (progress snapshots)

## Prompt (Summary)

```
Write concise progress narrative highlighting wins and one focus area.
```

## Workflows

Scheduled job → Progress Agent → Parent Report / Dashboard

## KPIs

- Report generation < 5s
- Narrative accuracy per teacher review

## Failure Handling

No activity in period → encouragement + suggested restart plan

## Observability

Report generation success rate

## Security

Reports respect parent visibility settings

## Test Cases

- Week report includes session count
- Year report aggregates monthly

## Implementation Notes

Partial: `progress` agent stub in AGENT_REGISTRY.
