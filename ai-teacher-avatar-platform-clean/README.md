# AI Voice English Teacher — v1 scaffold

See `docs/ARCHITECTURE.md` for the full design (multi-agent orchestration, guardrails,
data model, and what's deliberately simplified for v1 vs. what to build next).

## Quick start (Windows)

Run `.\setup-and-run.ps1` from the repo root — it creates `backend/.env` (prompting for
your Neon `DATABASE_URL` and LLM API key), installs backend + frontend dependencies, and
starts both servers. Or follow the manual steps below.

## Run locally (VS Code)

### 1. Backend (Python 3.11+, FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # fill in your Neon DATABASE_URL and GROK_API_KEY
uvicorn app.main:app --reload --port 8000
```

Tables are auto-created on startup for dev (see `app/database.py: init_db`). Swap in
Alembic migrations before production.

### 2. Frontend (Node.js, Vite + React)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Use Chrome desktop for the best Web Speech API support.

## What each piece is for

| Path | Purpose |
|---|---|
| `backend/app/main.py` | FastAPI app, CORS, router registration |
| `backend/app/config.py` | Env-based settings (Neon URL, Grok key, JWT secret) |
| `backend/app/models.py` | SQLAlchemy models: users, sessions, messages, grammar_progress, attempts |
| `backend/app/security.py` | JWT auth (register/login/current-user dependency) |
| `backend/app/guardrails.py` | Input/output guardrail checks, used by the orchestrator |
| `backend/app/llm_client.py` | Single wrapper around the Grok chat-completions API |
| `backend/app/agents/*` | One agent class per task (grammar, conversation, assessment) |
| `backend/app/agents/orchestrator.py` | Routes requests to the right agent, persists messages/progress |
| `backend/app/routers/*` | HTTP endpoints (`/api/auth/*`, `/api/agent/*`) |
| `frontend/src/useSpeech.js` | Browser STT (SpeechRecognition) + TTS (speechSynthesis) hook |
| `frontend/src/components/VoiceTeacher.jsx` | Mode picker, mic button, transcript, voice toggle |

## Notes

- Grok's API is OpenAI-compatible, so `llm_client.py` uses plain `httpx` calls to
  `{GROK_API_BASE}/chat/completions` — check xAI's current docs for the exact model name
  you have access to on the free tier and put it in `GROK_MODEL`.
- `voice_pref` (male/female) is stored per-user and matched to a browser TTS voice by name
  heuristics client-side — see the note in `useSpeech.js` about upgrading this later.
