# 16. Engagement Agent

| Field | Value |
|-------|-------|
| **Wave** | 3 |
| **Priority** | P1 |
| **Status** | `planned` |
| **LangGraph Node** | Affective Node |
| **Primary Model** | GPT-4o-mini |
| **Owner** | AI Platform Team |

---

## Purpose

Detect attention, participation, and interest during learning sessions.

## Responsibilities

- Response latency and length analysis
- Participation rate
- Topic interest signals
- Disengagement alerts

## Inputs

```json
{"session_id":"uuid","turns":[{"role":"student","text":"...","ts":0}],"duration_sec":600}
```

## Outputs

```json
{"engagement":72,"attention":"medium","alerts":[],"suggestions":["ask opinion question"]}
```

## Tools

Session Manager, turn analytics

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o-mini | heuristics |

## Memory

Redis (live session), PostgreSQL (aggregates)

## Prompt (Summary)

```
Identify engagement drops; suggest one re-engagement tactic.
```

## Workflows

Live session monitoring → Engagement Agent → Orchestrator

## KPIs

- Disengagement detected within 2 turns
- Alert precision > 70%

## Failure Handling

Sparse turns → mark engagement unknown

## Observability

Engagement heatmaps by lesson type

## Security

No biometric inference without consent

## Test Cases

- Monosyllabic replies → low engagement
- Active Q&A → high engagement

## Implementation Notes

Not implemented.
