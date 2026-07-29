# 9. Fluency Agent

| Field | Value |
|-------|-------|
| **Wave** | 2 |
| **Priority** | P1 |
| **Status** | `planned` |
| **LangGraph Node** | Voice Analysis Node |
| **Primary Model** | Rules + GPT-4o-mini |
| **Owner** | AI Platform Team |

---

## Purpose

Detect pauses, hesitations, speaking speed, and confidence markers.

## Responsibilities

- Measure words per minute
- Detect long pauses and fillers
- Compute fluency index 0–100
- Trend fluency over sessions

## Inputs

```json
{"transcript":"...","timestamps":[],"audio_metrics":{}}
```

## Outputs

```json
{"fluency":84,"wpm":128,"pauses":3,"fillers":2,"confidence":"medium"}
```

## Tools

Timestamp analyzer, statistical scorer

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o-mini | rule-based |

## Memory

PostgreSQL (fluency history)

## Prompt (Summary)

```
Summarize fluency patterns in one encouraging sentence plus one improvement tip.
```

## Workflows

Pronunciation Agent output → Fluency Agent → Speaking report

## KPIs

- Fluency score stability ±5 across re-runs
- Report generation < 1s

## Failure Handling

Missing timestamps → estimate from transcript length

## Observability

Track WPM distribution by CEFR level

## Security

Aggregate metrics only in dashboards

## Test Cases

- Hesitation-heavy transcript scores < 60
- Smooth speech scores > 75

## Implementation Notes

Not implemented.
