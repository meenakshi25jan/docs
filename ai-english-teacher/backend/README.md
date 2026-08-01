# AI English Teacher — Backend MVP

FastAPI backend for the AI English Teacher platform: JWT auth, Grok-powered grammar/conversation agents, Whisper STT, Edge TTS, and feedback persistence.

## Full conversation flow

```
User speaks / sends sentence
        ↓
POST /conversation  or  POST /audio-conversation
        ↓
Orchestrator Agent
        ↓
Grammar Agent  (or Conversation Agent)
        ↓
Grok LLM (xAI)
        ↓
Teacher-style correction
        ↓
Save feedback (PostgreSQL/SQLite)
        ↓
Edge TTS audio + JSON response
```

## Prerequisites

- **Python 3.12+** (with `venv`)
- **xAI API key** (`XAI_API_KEY`) for Grok grammar/conversation
- **OpenAI API key** (`OPENAI_API_KEY`) for Whisper speech-to-text on `/audio-conversation`
- **Optional:** Docker for local PostgreSQL/Neon-style Postgres

Edge TTS requires no API key.

## Quick start

### macOS / Linux

```bash
cd ai-english-teacher/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set JWT_SECRET, XAI_API_KEY, OPENAI_API_KEY
alembic upgrade head
uvicorn app.main:app --reload
```

### Windows PowerShell

```powershell
cd ai-english-teacher\backend
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\dev.ps1
```

Open http://127.0.0.1:8000/docs

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `JWT_SECRET` | Yes | JWT signing secret |
| `DATABASE_URL` | Yes | Postgres/Neon or SQLite URL |
| `XAI_API_KEY` | Yes* | Grok LLM for grammar/conversation |
| `OPENAI_API_KEY` | For audio | Whisper STT for `/audio-conversation` |
| `GROK_MODEL` | No | Default `grok-2-1212` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Default `60` |

**Neon example:**

```env
DATABASE_URL=postgresql+asyncpg://user:password@your_neon_host/your_db?sslmode=require
```

**SQLite (local, no Docker):**

```env
DATABASE_URL=sqlite+aiosqlite:///./ai_english_teacher.db
```

## API endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/home` | No | Platform welcome + features |
| `GET` | `/health` | No | Health + DB probe |
| `GET` | `/health/live` | No | Liveness |
| `GET` | `/health/ready` | No | Readiness |
| `POST` | `/register` | No | Register user |
| `POST` | `/login` | No | Login, get JWT |
| `POST` | `/logout` | No | Client-side token removal hint |
| `POST` | `/refresh` | No | Refresh access token |
| `GET` | `/users/me` | Yes | Current user profile |
| `POST` | `/conversation` | Yes | Text → Grok → feedback + TTS |
| `POST` | `/audio-conversation` | Yes | Audio → Whisper → Grok → TTS |
| `POST` | `/grammar-check` | Yes | Grammar only (no save/TTS) |
| `POST` | `/band-score` | Yes | MVP CEFR/IELTS estimate |
| `GET` | `/feedback` | Yes | User feedback history |

## Test the full flow

### 1. Register

```bash
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rahul",
    "email": "rahul@example.com",
    "password": "Test@1234",
    "phone_number": "9999999999",
    "teacher_voice": "female"
  }'
```

### 2. Login

```bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"rahul@example.com","password":"Test@1234"}'
```

### 3. Grammar conversation

```bash
curl -X POST http://127.0.0.1:8000/conversation \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"text":"I goes to school yesterday","mode":"grammar"}'
```

### 4. Audio conversation

```bash
curl -X POST http://127.0.0.1:8000/audio-conversation \
  -H "Authorization: Bearer <access_token>" \
  -F "mode=grammar" \
  -F "audio=@sample.wav"
```

Response includes `transcribed_text`, grammar `result`, and `voice_output.audio_base64` (MP3).

## VS Code debug

1. Open `ai-english-teacher/backend` in VS Code
2. Select `.venv` Python interpreter
3. Press **F5** → **AI English Teacher API**

## Run tests

```bash
pytest
```

Tests mock Grok/STT/TTS — no API keys needed for the test suite.

## Project structure

```
backend/
├── alembic/
├── app/
│   ├── agents/           # orchestrator, grammar, conversation
│   ├── api/              # auth, conversation, health, users
│   ├── core/             # config, security, dependencies
│   ├── db/models/        # User, GrammarFeedback
│   ├── services/         # grok, stt, tts, auth, feedback
│   ├── tests/
│   └── main.py
├── dev.ps1               # Windows one-script setup+run
├── requirements.txt
└── .env.example
```
