# 17. Stress Detection Agent

| Field | Value |
|-------|-------|
| **Wave** | 3 |
| **Priority** | P2 |
| **Status** | `planned` |
| **LangGraph Node** | Affective Node |
| **Primary Model** | GPT-4o-mini + prosody |
| **Owner** | AI Platform Team |

---

## Purpose

Detect exam anxiety, fear, frustration, and burnout signals.

## Responsibilities

- Stress level classification
- Trigger identification
- Escalation to human support when severe
- Calming intervention suggestions

## Inputs

```json
{"transcript":"...","audio_features":{},"context":{"upcoming_exam":true}}
```

## Outputs

```json
{"stress_level":"moderate","type":"exam_anxiety","intervention":"breathing exercise","escalate":false}
```

## Tools

Prosody analyzer, crisis keyword list

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o-mini | keyword rules |

## Memory

PostgreSQL (stress events, encrypted)

## Prompt (Summary)

```
Detect stress compassionately; never diagnose medical conditions.
```

## Workflows

Emotion Agent → Stress Detection → Motivation Agent

## KPIs

- Severe stress recall > 90%
- False escalation < 2%

## Failure Handling

Crisis keywords → immediate safe response template + human alert

## Observability

Anonymized stress trend reports

## Security

Crisis protocol; regional helpline numbers in responses

## Test Cases

- Exam panic language triggers moderate stress
- Crisis language escalates

## Implementation Notes

Not implemented.
