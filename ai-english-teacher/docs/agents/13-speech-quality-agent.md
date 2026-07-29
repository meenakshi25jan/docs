# 13. Speech Quality Agent

| Field | Value |
|-------|-------|
| **Wave** | 2 |
| **Priority** | P2 |
| **Status** | `planned` |
| **LangGraph Node** | Voice Preprocess Node |
| **Primary Model** | Signal processing (no LLM) |
| **Owner** | AI Platform Team |

---

## Purpose

Detect microphone quality, noise, echo, and other audio issues before analysis.

## Responsibilities

- SNR and noise floor measurement
- Clipping and echo detection
- Mic quality grading
- User guidance for better recording

## Inputs

```json
{"audio_url":"s3://...","session_id":"uuid"}
```

## Outputs

```json
{"quality":"fair","snr_db":18,"issues":["background_noise"],"guidance":"Move closer to mic"}
```

## Tools

FFmpeg, librosa, WebRTC VAD

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | DSP rules | N/A |

## Memory

Redis (last quality check per session)

## Prompt (Summary)

```
N/A — rule-based agent
```

## Workflows

Audio upload → Speech Quality → Pronunciation (if pass)

## KPIs

- False reject rate < 10%
- Check latency < 500ms

## Failure Handling

Cannot analyze → allow pipeline with warning flag

## Observability

Quality issue rate by device type

## Security

Process audio in memory; no long-term storage for QC-only passes

## Test Cases

- Noisy cafe flagged
- Clean studio audio passes

## Implementation Notes

Not implemented.
