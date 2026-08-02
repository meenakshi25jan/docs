# AI Voice English Teacher — Architecture (v1)

## 1. Product scope (v1)

- User registers/logs in (JWT auth, Postgres via Neon).
- User picks a **mode**: Grammar (leveled, starts at Level 1 and progresses), Conversation
  (free chat with correction), Band Score / Assessment (IELTS-style scoring of a transcript).
- User picks a **teacher voice**: male / female (browser TTS voice, filtered by gender).
- User speaks → browser captures speech → text sent to backend → an **agent** processes it,
  returns a spoken-style correction + reply + (for grammar mode) the next exercise/level →
  browser speaks the reply back.
- Progress (grammar level, scores, attempt history) is persisted per user.

## 2. Why a multi-agent design

Different tasks need different system prompts, different output shapes, and different
guardrails:
- **Grammar Agent** — deterministic leveling logic + LLM-generated exercises/corrections.
- **Conversation Agent** — open-ended chat, correction is a side-channel, not the main reply.
- **Assessment Agent** — analyzes a transcript, must return a strict structured band score.

Putting all of this in one prompt makes behavior inconsistent and hard to guardrail. Instead
we use an **Orchestrator → Worker Agent** pattern with a shared **Guardrail layer** wrapping
every call in and out.

```
Client (browser: mic + speaker)
      │  POST /api/agent/message  {mode, text, session_id}
      ▼
┌─────────────────────────────────────────────┐
│                 FastAPI                       │
│  ┌───────────────┐                            │
│  │  Guardrail:IN  │  topic/abuse filter,       │
│  └──────┬────────┘  length limits, PII scrub   │
│         ▼                                     │
│  ┌───────────────┐                            │
│  │  Orchestrator  │  routes by `mode`          │
│  └──────┬────────┘                            │
│         ├──► Grammar Agent      ┐             │
│         ├──► Conversation Agent │  each calls  │
│         └──► Assessment Agent   ┘  Grok LLM    │
│         ▼                                     │
│  ┌───────────────┐                            │
│  │ Guardrail:OUT  │  schema validation,        │
│  └──────┬────────┘  safe-content check         │
│         ▼                                     │
│      Response  {reply_text, correction, level, score}
└─────────────────────────────────────────────┘
      │
      ▼
Neon Postgres (users, sessions, messages, grammar_progress, attempts)
```

## 3. Orchestration pattern

- **Router-Worker**: `Orchestrator.handle(mode, payload)` picks the worker agent. Each worker
  is a small class with one job: build a system prompt, call the LLM client, parse/validate
  the response into a Pydantic schema.
- Agents never call each other directly — only the orchestrator sequences them (e.g. Grammar
  Agent can hand off to Assessment Agent when a level is completed).
- All LLM calls go through one `llm_client.py` so provider (Grok) swap or fallback is a
  single change point.

## 4. Guardrails (v1, expand later)

Input guardrail:
- Reject empty / oversized input.
- Reject obvious off-topic or abusive content before it reaches the LLM (keyword + LLM-classifier
  hybrid — v1 ships keyword-based, classifier is a next step).

Output guardrail:
- Enforce the agent's response matches its Pydantic schema (e.g. Assessment Agent must return
  `{band_score, strengths, improvements}` — if the LLM returns free text, we retry once, then
  fail safe with a generic message instead of forwarding malformed output).
- Strip anything that looks like leaked system prompt or credentials.

## 5. Data model (Postgres / Neon)

- `users(id, email, password_hash, display_name, voice_pref, created_at)`
- `sessions(id, user_id, mode, started_at)`
- `messages(id, session_id, role, content, correction, created_at)`
- `grammar_progress(user_id, level, streak, updated_at)`
- `attempts(id, user_id, mode, score_json, created_at)`

## 6. Tech stack (v1 → decided)

| Layer | Choice | Why |
|---|---|---|
| Backend | Python 3.11 + FastAPI | async, good for streaming + LLM I/O |
| LLM | Grok (xAI), OpenAI-compatible `chat/completions` | as requested; swappable via `llm_client.py` |
| DB | Postgres on Neon, SQLAlchemy async + asyncpg | serverless Postgres, matches your ask |
| Auth | JWT (python-jose) + bcrypt (passlib) | simple, stateless |
| STT/TTS (v1) | Browser Web Speech API (`SpeechRecognition` / `speechSynthesis`) | free, zero backend infra, ships today, has male/female voice selection |
| STT/TTS (v2, recommended next) | Whisper (STT) + a real TTS engine (e.g. Piper/Coqui self-hosted, or a paid API) | browser STT is Chrome-only and inconsistent across devices; needed once you go mobile or want reliability |
| Frontend (v1) | React + Vite (web) | fastest path to a working demo in the browser |
| Frontend (v2) | React Native | reuse logic, ship mobile |
| Dev environment | VS Code, `.env` for secrets, Uvicorn dev server | matches your ask |

## 7. Known v1 limitations (by design, to keep the scaffold runnable)

- Browser speech APIs are used instead of a dedicated STT/TTS service — this is the fastest
  way to get *voice in, voice out* working end-to-end without extra billing/infra. Reliability
  varies by browser (best in Chrome desktop).
- Off-topic/abuse guardrail is keyword-based, not an LLM classifier — good enough for v1,
  should be upgraded before public launch.
- No streaming responses yet (LLM call is request/response, not token-streamed) — can be added
  once the flow is validated.

## 8. v2 — the "teacher" layer

v1 above still exists (`/api/agent/message` with grammar/conversation/assessment modes) and
is kept as a "Free Practice" tab. On top of it, v2 adds a persona + state-machine layer so the
app behaves like a teacher across a whole class and across days, not a single Q&A turn:

```
GET  /api/lesson/today     → LessonOrchestrator.get_today()
POST /api/lesson/message   → LessonOrchestrator.handle_message()
POST /api/books/upload     → chunk + store an uploaded book/notes file
POST /api/books/topic      → BookAgent: retrieve + explain a topic from a chosen book
```

- **`LessonProgress`** (new table) is the teacher's memory: current day number, which of the
  5 stages the student is on (`warmup → vocabulary → grammar → speaking_test → homework`),
  streak, words learned, and any pending homework. This is what lets the app say "yesterday we
  practiced X" instead of starting cold every session.
- **`LessonOrchestrator`** (`agents/lesson_orchestrator.py`) is the state machine: decides
  whether today is a new day (rotate topic, reset stage, update streak) or a continuation,
  then calls `TeacherAgent` for the current stage and advances the stage once the agent
  reports the student completed it.
- **`TeacherAgent`** (`agents/teacher_agent.py`) is a single stage-aware LLM call — told
  explicitly which of the 5 stages it's in and whether it's opening the stage (teach + ask)
  or reacting to an answer (correct + decide to advance). This is the persona: "Mr. David".
- **`BookAgent`** (`agents/book_agent.py`) + `Book`/`BookChunk` tables implement the "upload a
  book, ask about a topic" flow. Retrieval is naive keyword-overlap scoring over fixed-size
  chunks (no vector DB) — good enough for small uploaded documents, swappable for embeddings
  later without touching the router.

Frontend: `ClassRoom.jsx` replaced the bare mode-button chatbot as the default view. It shows
a `TeacherPanel` (avatar, lesson topic, today's goal checklist, streak/words stats) and a
`DailyPath` (the 5-stage progress strip) instead of a blank transcript, and adds a
`BookPanel` for the upload/ask-about-a-book flow. The old three-mode UI still exists, embedded
under the "Free Practice" tab.

## 9. v3 — profile memory, dashboard, real classroom mode

Three more additions on top of v2:

- **`StudentProfile`** (new table): `level`, `target_band`, `native_language`, `weaknesses`
  (a list, e.g. `["Past tense", "Pronunciation"]`). Set via `GET/PUT /api/profile`. On first
  visit with an empty profile, the frontend shows `ProfileForm.jsx` before starting class.
  `LessonOrchestrator` rotates through `weaknesses` day-by-day (`_pick_focus_weakness`) and
  passes the pick into `TeacherAgent` as `focus_weakness`, which — only in the `warmup` stage
  (mention it) and `grammar` stage (steer the grammar point toward it, if it fits the topic)
  — is woven into the prompt. This is what produces "last week you struggled with past tense,
  let's practice that again" instead of a cold, generic warm-up.
- **Teacher Dashboard**: `LessonTodayResponse` now also returns `level`, `target_band`,
  `latest_band_score` (pulled from the most recent `assessment`-mode `Attempt`), and
  `focus_weakness`. `TeacherPanel.jsx` renders all of it — goal checklist, streak, words
  learned, and a band-score-vs-target readout — so progress is visible, not just spoken.
- **Real Classroom Mode**: `useSpeech.js`'s `speak()` now returns a Promise that resolves on
  the browser's actual `utterance.onend` (previously callers fired-and-forgot). `ClassRoom.jsx`
  uses that to auto-chain `speak → listen → send → speak → …` without a button press each
  turn — toggle via the "Real Classroom Mode" checkbox; the mic is disabled while the teacher
  is talking so recognition doesn't pick up the TTS output. Manual mic-press still works as a
  fallback/override at any point, and is required when auto mode is off.

## 10. Next steps after this scaffold runs

1. Swap keyword guardrail for a lightweight moderation LLM call.
2. Add streaming (SSE or websockets) so the reply starts speaking before generation finishes.
3. Add a real gamified leveling table (XP, badges) — currently `grammar_progress` is a simple
   level counter.
4. Move STT/TTS server-side (Whisper + a TTS engine) for mobile + reliability.
