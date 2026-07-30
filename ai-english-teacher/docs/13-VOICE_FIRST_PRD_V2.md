# Voice-First AI English Teacher — PRD v2

## Vision

Build an AI English teacher that conducts natural **voice conversations** like an experienced human teacher: listen continuously, understand context, detect mistakes without unnecessary interruption, correct at appropriate moments, remember recurring mistakes, and personalize future lessons.

The learner should feel like they are talking to a real teacher, not a chatbot.

## Core Learning Loop

```
Student Speaks → Speech Recognition → Conversation Understanding → Teacher Reasoning
→ Mistake Detection → Teaching Decision → Teacher Speaks → Student Replies → (continuous)
```

Unlike chat-based AI, this loop runs continuously during the lesson.

## Primary AI Agents

| Agent | Role |
|-------|------|
| **Voice Conversation Agent** | Turn-taking, pacing, live audio → structured transcript |
| **Teacher Agent (Master Brain)** | Lesson direction, questions, explanations, difficulty |
| **Grammar Correction Agent** | Tense, articles, prepositions, word order |
| **Pronunciation Coach** | Phonemes, stress, intonation, rhythm |
| **Vocabulary Coach** | Range, collocations, idioms |
| **Fluency Coach** | Rate, hesitation, fillers, pauses |
| **Memory Agent** | Long-term learner profile and recurring mistakes |
| **Lesson Planner Agent** | Adaptive lessons from CEFR, goals, history |
| **Assessment Agent** | Continuous CEFR / IELTS / PTE estimates |

## Teaching Modes

- **Immediate correction** — inline fix for blocking errors
- **Delayed correction** — batch feedback after natural pauses or extended speech
- **Socratic correction** — guide learner to self-correct via questions

Implemented in `backend/app/orchestration/voice/teaching_decision.py`.

## Real-Time Pipeline (v2 Implementation)

```
Microphone → STT → Voice Analysis (fluency, pronunciation, grammar, vocabulary)
→ Teaching Decision Engine → Teacher Orchestrator (LangGraph) → Natural Voice Response → TTS
```

Unified entry points:

- `POST /api/v1/voice/turn` — standalone voice turn
- `POST /api/v1/conversations/{id}/voice-turn` — voice turn within a lesson
- `GET /api/v1/conversations/{id}/lesson-report` — post-lesson summary

## Teacher Personas

Personas share the same learner memory but use different prompts and correction strategies:

- Friendly Beginner Teacher
- IELTS Examiner
- PTE Coach
- TOEFL Speaking Trainer
- Business English Trainer
- Interview Coach
- Conversation Partner

Configured in `backend/app/orchestration/personas.py`. Listed via `GET /api/v1/voice/personas`.

## Classroom Scenarios

15+ scenarios including job interview, restaurant, airport immigration, hotel check-in, doctor consultation, visa interview, debate, negotiation, and everyday conversation.

## Lesson Completion Report

After each session:

- Overall speaking, fluency, pronunciation, grammar, vocabulary scores
- Estimated CEFR and IELTS/PTE speaking (labeled as estimates)
- Recurring mistakes from memory
- New vocabulary
- AI-generated recommendations and next-lesson plan

## Performance Targets

| Metric | Target |
|--------|--------|
| Voice latency | < 700 ms |
| Teacher response | < 1.5 s |
| Turn detection | < 300 ms |
| Grammar correction | < 1 s |

## Implementation Status (this release)

### Implemented

- Unified voice turn pipeline (`orchestration/voice/voice_turn.py`)
- Teaching decision engine (immediate / delayed / Socratic)
- Teacher personas and 15 classroom scenarios
- Lesson completion report API
- Voice-first conversation UI with persona selection
- Integration with existing LangGraph orchestration, memory, and scoring

### Next phase (not in this release)

- WebSocket streaming audio and VAD for true continuous listening
- Azure Speech SDK phoneme-level pronunciation
- Server-side TTS for consistent teacher voice
- `speaking_sessions` persistence and audio blob storage
- Full microservice split per architecture docs

## Related Documentation

- `RUNBOOK.md` — **complete deploy, smoke tests, error catalog** (Render + Neon stack)
- `docs/01-PRODUCT_REQUIREMENTS.md` — original PRD
- `docs/02-SYSTEM_ARCHITECTURE.md` — system architecture
- `docs/07-AI_AGENT_DESIGN.md` — agent design
- `RUNBOOK.md` — operations
