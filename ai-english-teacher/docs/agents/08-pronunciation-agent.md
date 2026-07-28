# 8. Pronunciation Agent

| Field | Value |
|-------|-------|
| **Wave** | 2 |
| **Priority** | P1 |
| **Status** | `planned` |
| **LangGraph Node** | Voice Analysis Node |
| **Primary Model** | Whisper + phoneme engine |
| **Owner** | AI Platform Team |

---

## Purpose

Analyze phoneme accuracy, stress, fluency, and intonation from student speech.

## Responsibilities

- Transcribe audio via Whisper
- Phoneme alignment and scoring
- Stress and intonation analysis
- Per-word pronunciation feedback

## Inputs

```json
{"session_id":"uuid","audio_url":"s3://...","target_text":"optional","locale":"en-US"}
```

## Outputs

```json
{"phoneme_score":82,"stress_score":78,"words":[{"word":"hello","score":0.9,"tip":"..."}]}
```

## Tools

Whisper, phoneme engine, audio preprocessor

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | Whisper large-v3 | Whisper base |

## Memory

Redis (session audio state)

## Prompt (Summary)

```
Score pronunciation against reference phonemes; give actionable micro-tips.
```

## Workflows

Audio → Whisper → Phoneme Engine → Scoring → Feedback

## KPIs

- Phoneme scoring correlation > 0.8 vs human raters
- P95 pipeline < 5s

## Failure Handling

Low audio quality → route to Speech Quality Agent; ASR fail → retry once

## Observability

Log audio duration, ASR confidence, score distribution

## Security

Encrypt audio at rest; auto-delete per retention policy

## Test Cases

- Clear speech scores > 80
- Mispronounced 'th' flagged

## Implementation Notes

Not implemented. Browser STT exists; server-side pipeline pending.
