# 14. Emotion Detection Agent

| Field | Value |
|-------|-------|
| **Wave** | 3 |
| **Priority** | P1 |
| **Status** | `planned` |
| **LangGraph Node** | Affective Node |
| **Primary Model** | Multimodal classifier + GPT-4o-mini |
| **Owner** | AI Platform Team |

---

## Purpose

Detect student emotional state from voice, conversation, and optional facial cues.

## Responsibilities

- Classify happy, confused, frustrated, excited, bored
- Fuse voice prosody and text sentiment
- Optional webcam emotion (with consent)
- Emit confidence scores

## Inputs

```json
{"transcript":"...","audio_features":{},"facial_features":"optional","session_id":"uuid"}
```

## Outputs

```json
{"emotion":"confused","confidence":0.87,"signals":["short replies","question marks"]}
```

## Tools

Sentiment model, prosody analyzer, optional vision API

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o-mini | text sentiment model |

## Memory

Redis (session affect timeline)

## Prompt (Summary)

```
Infer dominant emotion from multimodal cues; avoid overconfidence.
```

## Workflows

Each turn → Emotion Detection → Orchestrator adapts tone

## KPIs

- F1 > 0.7 on labeled emotions
- Latency < 800ms

## Failure Handling

Low confidence → default neutral; do not change teaching style drastically

## Observability

Emotion distribution per session

## Security

Facial data requires explicit opt-in; delete after inference

## Test Cases

- Frustrated language detected
- Neutral small talk → neutral

## Implementation Notes

Not implemented.
