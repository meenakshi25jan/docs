# 15. Confidence Agent

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

Measure student confidence, self-belief, and communication courage on a 0–100 scale.

## Responsibilities

- Linguistic confidence markers
- Hesitation vs assertion patterns
- Longitudinal confidence tracking
- Actionable confidence boosts

## Inputs

```json
{"transcript":"...","history":[],"fluency_score":84}
```

## Outputs

```json
{"confidence":67,"trend":"improving","factors":["fewer fillers"],"encouragement":"..."}
```

## Tools

Fluency Agent output, historical metrics

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o-mini | weighted rules |

## Memory

PostgreSQL (confidence time series)

## Prompt (Summary)

```
Score confidence 0–100 with evidence; one specific praise and one gentle challenge.
```

## Workflows

Post-session → Confidence Agent → Progress Agent

## KPIs

- Score correlates with teacher ratings r > 0.6

## Failure Handling

Insufficient history → session-only estimate with wide band

## Observability

Confidence trend dashboards

## Security

Individual scores visible only to student and authorized teachers

## Test Cases

- Hesitant speech → lower score
- Assertive answers → higher score

## Implementation Notes

Not implemented.
