# AI English Teacher — Complete Runbook

**One document for prerequisites, setup, deployment, testing, and every known error fix.**

| Live URLs (production) | |
|------------------------|---|
| Frontend | https://ai-english-teacher-web.onrender.com |
| API | https://ai-english-teacher-api.onrender.com |
| API docs | https://ai-english-teacher-api.onrender.com/docs |
| Health | https://ai-english-teacher-api.onrender.com/health |

**Deploy branch:** `main` (recommended) · voice-first: `cursor/voice-first-redesign-f37f` · infra baseline: `cursor/cheapest-cloud-deploy-d164`  
**Repo:** `meenakshi25jan/docs` → folder `ai-english-teacher/`  
**Platform mode:** Voice-first conversational teacher (PRD v2) — unified voice turns, teaching personas, lesson reports

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Requirements & Versions](#2-requirements--versions)
3. [Environment Variables](#3-environment-variables)
4. [Local Development](#4-local-development)
5. [Cloud Deployment ($0/month)](#5-cloud-deployment-0month)
   - [Oracle Cloud (recommended for Ollama)](#oracle-cloud-always-free)
   - [Render + Neon](#render--neon)
6. [Database Migrations](#6-database-migrations)
7. [Smoke Tests & Verification](#7-smoke-tests--verification)
8. [Complete Error Catalog](#8-complete-error-catalog)
9. [Bugs Fixed (Changelog)](#9-bugs-fixed-changelog)
10. [Production Checklist](#10-production-checklist)
11. [Cost Tiers](#11-cost-tiers)
12. [App Routes & API Reference](#12-app-routes--api-reference)
13. [Microsoft Copilot / Azure OpenAI](#13-microsoft-copilot--azure-openai-recommended-for-cloud)
14. [Ollama LLM Setup](#14-ollama-llm-setup-local-only)
15. [Voice-First Practice (PRD v2)](#15-voice-first-practice-prd-v2)
16. [Mobile App (Google Play)](#16-mobile-app-google-play)

---

## 1. Prerequisites

### Accounts (cloud — pick one stack)

| Service | Purpose | Sign up | Cost |
|---------|---------|---------|------|
| **GitHub** | Source code | https://github.com | Free |
| **Neon** | PostgreSQL + pgvector | https://neon.tech | Free (0.5 GB) |
| **Render** | API + frontend hosting | https://render.com | Free tier |
| **Oracle Cloud** | Always-on VM + Ollama | https://cloud.oracle.com/compute/instances/create?region=ap-mumbai-1 | **$0** (2 OCPU, 12 GB ARM) |
| **Vercel** *(optional)* | Faster frontend CDN | https://vercel.com | Free hobby |

### Tools (local development)

| Tool | Minimum version | Check command |
|------|-----------------|---------------|
| Git | 2.x | `git --version` |
| Docker | 24+ | `docker --version` |
| Docker Compose | 2.x | `docker compose version` |
| Node.js | 20+ | `node --version` |
| npm | 10+ | `npm --version` |
| Python | 3.12+ | `python3 --version` |
| pip | latest | `pip3 --version` |

### Optional (real AI features)

| Service | Purpose |
|---------|---------|
| OpenAI API key | GPT-based scoring & conversation |
| Azure OpenAI | Production AI (GPT-5.5 deployment) |
| Azure Speech | Speaking assessment |

> Without AI keys the platform runs in **mock mode** (sample scores and responses).

---

## 2. Requirements & Versions

### Backend (`backend/requirements.txt`)

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.115.6 | REST API framework |
| uvicorn | 0.34.0 | ASGI server |
| sqlalchemy + asyncpg | 2.0.36 / 0.30.0 | Async PostgreSQL ORM |
| bcrypt | 4.2.1 | Password hashing |
| python-jose | 3.3.0 | JWT tokens |
| pydantic-settings | 2.7.0 | Config from env vars |
| openai | 1.58.1 | AI integration + Whisper STT |
| langgraph | latest | Conversation orchestration pipeline |
| langchain-core | latest | Agent framework |

**Render free tier** uses slim `requirements-render.txt` (same core, no Redis/prometheus).

### Frontend (`frontend/package.json`)

| Package | Version | Purpose |
|---------|---------|---------|
| next | 15.x | React framework |
| react | 19.x | UI |
| tailwindcss | 3.4.x | Styling |
| recharts | 2.15.x | Dashboard charts |

### Database

| Requirement | Details |
|-------------|---------|
| PostgreSQL | 16+ (Neon 18 works) |
| Extension | `pgvector` — run `CREATE EXTENSION IF NOT EXISTS vector;` |
| Migrations | 5 SQL files in `database/migrations/` |

---

## 3. Environment Variables

### Backend — required

| Variable | Example | Notes |
|----------|---------|-------|
| `DATABASE_URL` | `postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require` | **Must** include `?sslmode=require` for Neon |
| `JWT_SECRET_KEY` | `openssl rand -hex 32` | Auto-generated on Render |
| `CORS_ORIGINS` | `["https://ai-english-teacher-web.onrender.com","http://localhost:3000"]` | JSON array |

### Backend — optional

| Variable | Default | Notes |
|----------|---------|-------|
| `SKIP_MIGRATIONS` | `true` on Render | Set `false` to auto-run migrations on start |
| `DEBUG` | `false` | Enable API debug mode |
| `AI_PROVIDER` | `auto` | `copilot`, `openai`, `groq`, `ollama`, or `mock` |
| `COGNITIVE_ORCHESTRATION_ENABLED` | `true` | Set `false` to route turns through LangGraph only (cognitive layer disabled) |
| `OPENAI_API_KEY` | empty | Enables real AI scoring & conversation |
| `OPENAI_BASE_URL` | empty | Groq: `https://api.groq.com/openai/v1` |
| `WHISPER_MODEL` | auto | Server STT: `whisper-large-v3-turbo` (Groq) or `whisper-1` |
| `AZURE_OPENAI_ENDPOINT` | empty | Azure OpenAI / Copilot endpoint |
| `AZURE_OPENAI_API_KEY` | empty | Azure OpenAI key |
| `AZURE_OPENAI_DEPLOYMENT` | `gpt-4o-mini` | Chat deployment name |
| `AZURE_SPEECH_KEY` | empty | Future phoneme pronunciation (not wired yet) |
| `AZURE_SPEECH_REGION` | `eastus` | Azure Speech region |
| `REDIS_URL` | `redis://localhost:6379/0` | Optional session memory; in-memory fallback if empty |

### Frontend — required

| Variable | Local | Production (Render) |
|----------|-------|---------------------|
| `NEXT_PUBLIC_API_URL` | `/api/v1` | `/api/v1` |
| `API_PROXY_URL` | `http://localhost:8000` | `https://ai-english-teacher-api.onrender.com` |

The frontend uses a **same-origin proxy** (`/api/v1` → backend) so the browser never calls `localhost` or cross-origin URLs directly. This fixes "Cannot reach the API" when `NEXT_PUBLIC_API_URL` was missing at build time.

Copy examples:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

---

## 4. Local Development

### Option A — Docker Compose (easiest)

```bash
cd ai-english-teacher
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

Migrations run automatically via `database/migrations/` mounted into Postgres init.

### Option B — Manual (backend + frontend separately)

**Step 1 — Start database**
```bash
cd ai-english-teacher
docker compose up -d postgres redis
```

**Step 2 — Backend**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/ai_english_teacher" \
  python3 scripts/migrate.py
uvicorn app.main:app --reload --port 8000
```

**Step 3 — Frontend** (new terminal)
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

**Step 4 — Open**
- http://localhost:3000 — app
- http://localhost:8000/docs — Swagger API

### Run tests

```bash
cd backend
python3 -m pytest tests/ -q
```

Expected: `105 passed` (unit + API integration tests; no production DB or real AI keys required)

---

## 5. Cloud Deployment ($0/month)

### Oracle Cloud (Always Free)

**Best for:** always-on server, local **Ollama** LLM, no cold starts.

| Component | Provider |
|-----------|----------|
| VM (API + frontend + Redis + Ollama) | Oracle Cloud Ampere A1 (free) |
| PostgreSQL | Neon (free) |

**Full guide:** [deploy/oracle-cloud/FULL_STACK_DEPLOY.md](deploy/oracle-cloud/FULL_STACK_DEPLOY.md) (web + mobile + API on one VM)

**Quick start on a new Ubuntu ARM VM:**

```bash
ssh ubuntu@YOUR_VM_IP
curl -fsSL https://raw.githubusercontent.com/meenakshi25jan/docs/main/ai-english-teacher/deploy/oracle-cloud/setup-vm.sh | bash
# Edit .env → set DATABASE_URL from Neon
# Open http://YOUR_VM_IP
```

Don't forget OCI Console → VCN → Security List → open ports **80** and **443**.

---

### Render + Neon

### Architecture

```
Browser → Render Web (Next.js) → Render API (FastAPI) → Neon PostgreSQL
```

### Step 1 — Neon database

1. Go to https://console.neon.tech → **New Project**
2. Name: `ai-english-teacher`, region: **US East (Ohio)**
3. Copy connection string: `postgresql://...@ep-xxx.neon.tech/neondb?sslmode=require`
4. **SQL Editor** → run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### Step 2 — Run migrations (one time)

```bash
cd ai-english-teacher/backend
pip install asyncpg
DATABASE_URL="postgresql://YOUR_NEON_URL?sslmode=require" \
  MIGRATIONS_DIR=../database/migrations \
  python3 scripts/migrate.py
```

Expected output:
```
  apply 001_initial_schema.sql
  apply 002_pgvector.sql
  apply 003_auth_rls.sql
  apply 004_fix_rls_policies.sql
  apply 005_knowledge_and_voice.sql
Migrations complete
```

### Step 3 — Deploy API on Render

**Option A — Blueprint (recommended)**

1. https://dashboard.render.com/blueprints → **New Blueprint Instance**
2. Connect repo `meenakshi25jan/docs`
3. Blueprint file: `ai-english-teacher/render-backend.yaml` (Docker) or `render.yaml`
4. Set `DATABASE_URL` when prompted
5. Branch: `main` (stable) or `cursor/voice-first-redesign-f37f` (voice-first PRD v2 + Phase 0 stabilization)

> **Deploy branch alignment:** `render.yaml` and `render-backend.yaml` default to branch `main`. Feature work (voice-first, cognitive orchestration, Phase 0 fixes) lives on `cursor/voice-first-redesign-f37f`. To test those changes on Render before merging to `main`, set **Branch** to `cursor/voice-first-redesign-f37f` on both API and Web services (Dashboard → Service → Settings → Branch), then Manual Deploy. After merge to `main`, switch services back to `main` for production.

**Option B — Manual Web Service**

| Setting | Value |
|---------|-------|
| Name | `ai-english-teacher-api` |
| Root Directory | `ai-english-teacher` |
| Runtime | **Docker** |
| Dockerfile | `backend/Dockerfile` |
| Branch | `main` (or `cursor/voice-first-redesign-f37f` for voice-first preview) |
| Health Check Path | `/health` |

**API environment variables:**

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Full Neon URL with `?sslmode=require` |
| `JWT_SECRET_KEY` | Generate random string |
| `CORS_ORIGINS` | `["https://ai-english-teacher-web.onrender.com","http://localhost:3000"]` |
| `SKIP_MIGRATIONS` | `true` |

### Step 4 — Deploy frontend on Render

| Setting | Value |
|---------|-------|
| Name | `ai-english-teacher-web` |
| Root Directory | `ai-english-teacher/frontend` |
| Runtime | **Node** (not Docker) |
| Build Command | `npm install && npm run build` |
| Start Command | `npm start` |
| Branch | `main` (or `cursor/voice-first-redesign-f37f` for voice-first preview) |

**Frontend environment:**

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `/api/v1` |
| `API_PROXY_URL` | `https://ai-english-teacher-api.onrender.com` |
| `NODE_VERSION` | `20` |

> **Important:** Use `/api/v1` (same-origin proxy), not the full API URL. The Next.js rewrite in `next.config.js` proxies `/api/v1/*` → `API_PROXY_URL/api/v1/*`. This avoids CORS and "Cannot reach the API" errors.

### Step 5 — Manual deploy (after every code push)

1. Render → **ai-english-teacher-api** → **Manual Deploy** → Deploy latest commit
2. Render → **ai-english-teacher-web** → **Manual Deploy** → Deploy latest commit
3. Wait 3–5 minutes per service

### Alternative — Vercel frontend

| Setting | Value |
|---------|-------|
| Root Directory | `ai-english-teacher/frontend` |
| `NEXT_PUBLIC_API_URL` | `/api/v1` |
| `API_PROXY_URL` | `https://ai-english-teacher-api.onrender.com` |

Update `CORS_ORIGINS` on API to include your Vercel URL.

---

## 6. Database Migrations

| File | Purpose |
|------|---------|
| `001_initial_schema.sql` | 16 tables, indexes, RLS policies |
| `002_pgvector.sql` | Vector extension tables |
| `003_auth_rls.sql` | Login email lookup policy |
| `004_fix_rls_policies.sql` | Fix RLS uuid cast errors on register |
| `005_knowledge_and_voice.sql` | RAG knowledge chunks + `voice_analyses` table |
| `006_curriculum_intelligence.sql` | `lesson_completions` + `revision_schedule` (Curriculum Intelligence v1) |

**Canonical migration path:** `database/migrations/` (used by Docker Compose init and `scripts/migrate.py`).

> **Duplicate migration folder:** A copy also exists at `backend/migrations/`. Do **not** run both. Always use `database/migrations/` or `MIGRATIONS_DIR=../database/migrations` with `scripts/migrate.py`. The `backend/migrations/` copy is legacy and may drift — treat `database/migrations/` as source of truth.

**Run all migrations:**
```bash
cd ai-english-teacher/backend
DATABASE_URL="your-neon-url" python3 scripts/migrate.py
```

**Run single migration manually (Neon SQL Editor):**
```sql
-- Only if 003 was not applied (needed for login)
CREATE POLICY auth_email_lookup ON users
    FOR SELECT
    USING (current_setting('app.auth_lookup', true) = 'on');
```

---

## 7. Smoke Tests & Verification

Run these in order after every deploy.

### API health

```bash
curl https://ai-english-teacher-api.onrender.com/health
```
Expected: `{"status":"healthy","version":"1.0.0","database":"reachable","database_latency_ms":12}` (or `"database":"not_configured"` locally without Postgres)

If the database is down: `{"status":"degraded","version":"1.0.0","database":"unreachable"}`

### Password hashing (confirms bcrypt fix is live)

```bash
curl https://ai-english-teacher-api.onrender.com/health/auth
```
Expected: `{"password_hashing":"ok"}`

### CORS preflight

```bash
curl -X OPTIONS https://ai-english-teacher-api.onrender.com/api/v1/auth/register \
  -H "Origin: https://ai-english-teacher-web.onrender.com" \
  -H "Access-Control-Request-Method: POST" -D -
```
Expected header: `access-control-allow-origin: https://ai-english-teacher-web.onrender.com`

### Register test

```bash
curl -X POST https://ai-english-teacher-api.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass12","first_name":"Test","last_name":"User"}'
```
Expected: `HTTP 201` with `access_token` in response (or `409` if email exists)

### Frontend pages

| URL | Expected |
|-----|----------|
| `/` | Landing page |
| `/register` | Registration form |
| `/login` | Login form |
| `/conversation` | Voice-first lesson (persona + scenario picker) |
| `/grammar-class` | Grade 5–12 grammar voice practice |
| `/assessment` | Assessment page |
| `/dashboard/student` | Student dashboard |

### Voice API smoke tests (auth required)

After login, test with a Bearer token:

```bash
# List teacher personas and scenarios
curl https://ai-english-teacher-api.onrender.com/api/v1/voice/personas

# Unified voice turn (transcript-only smoke test)
curl -X POST https://ai-english-teacher-api.onrender.com/api/v1/voice/turn \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"transcript":"I went to the market yesterday.","scenario":"everyday","persona_id":"conversation_partner"}'
```

Expected: JSON with `response`, `voice_scores`, `teaching_mode`, and `estimates`.

### End-to-end user flow

1. Open `/register` → create account
2. Redirected to `/dashboard/student`
3. Open `/conversation` → pick **teacher persona** and **scenario** → **Start Voice Lesson**
4. Tap **Mic** → speak → teacher responds with voice (auto-play) + optional corrections
5. Click **End lesson & report** → CEFR/IELTS estimates, recurring mistakes, recommendations
6. Open `/assessment` → start placement test (text-based)
7. Open `/grammar-class` → grade-level grammar with voice practice

---

## 8. Complete Error Catalog

### Render / Infrastructure

| Error | Cause | Fix |
|-------|-------|-----|
| **"Welcome to Render" ASCII art** | API not starting | See [API won't start](#api-wont-start-on-render) |
| **Cold start / slow first request** | Free tier sleeps after 15 min | Open `/health` first, wait 30–60s, retry. Or upgrade to Starter ($7/mo) |
| **`Killed` / OOM in logs** | 512 MB RAM limit on free tier | Use `requirements-render.txt`; upgrade to Starter |
| **Build timeout** | Free tier build limit | Use Docker deploy or reduce dependencies |

### API won't start on Render

**Settings → Build & Deploy:**

| Setting | Value |
|---------|-------|
| Root Directory | `ai-english-teacher` (Docker) or `ai-english-teacher/backend` (Python) |
| Build Command | `pip install -r requirements-render.txt` (Python) or use Dockerfile |
| Start Command | `python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Branch | `main` (or `cursor/voice-first-redesign-f37f` for voice-first preview) |

**Environment:** `DATABASE_URL` must be full `postgresql://...?sslmode=require`

**Logs should show:**
```
INFO:     Uvicorn running on http://0.0.0.0:10000
INFO:     Application startup complete.
```

### Database errors

| Error | Cause | Fix |
|-------|-------|-----|
| **`database: not_configured`** | `DATABASE_URL` empty or wrong format | Paste full Neon URL in Render → Environment |
| **Connection refused / SSL error** | Missing SSL param | Keep `?sslmode=require` in Neon URL — app strips it and sets `ssl=True` for asyncpg |
| **`connect() got an unexpected keyword argument 'sslmode'`** | asyncpg rejects sslmode query param | Deploy latest API code (`db_url.py` fix) |
| **`relation "users" does not exist`** | Migrations not run | Run `python3 scripts/migrate.py` against Neon |
| **`connection is closed` on `SET LOCAL app.tenant_id`** | Stale pool after Neon/Render sleep | Deploy latest API (`pool_pre_ping`); use Neon **pooler** URL (`-pooler.neon.tech`) |
| **HTTP 500 on register/login** | RLS or bcrypt issue | Deploy latest code + run migration `003_auth_rls.sql` |

### CORS & Frontend API errors

| Error | Cause | Fix |
|-------|-------|-----|
| **"Cannot reach the API" / "Failed to fetch"** | Frontend called `localhost` (env missing at build) | Redeploy frontend; use `/api/v1` proxy + `API_PROXY_URL` (latest code) |
| **"Cannot reach the API"** | API cold start on free tier | Open `/health` first, wait 30s, retry |
| **CORS error in browser console** | Direct cross-origin API calls | Use `/api/v1` proxy (fixed in latest frontend) |
| **`NEXT_PUBLIC_API_URL` wrong** | Points to localhost in production | Set to `/api/v1` and `API_PROXY_URL` to API URL on Render web |

**CORS_ORIGINS value (copy exactly):**
```
["https://ai-english-teacher-web.onrender.com","http://localhost:3000"]
```

### Frontend 404 errors

| Error | Cause | Fix |
|-------|-------|-----|
| **404 on `/grammar-class`** | Web deploy failed (Docker/ESLint) | Redeploy **ai-english-teacher-web** from `main`; check Events for build errors |
| **Only `/` and `/dashboard/student` work** | Old build before pages were added | Redeploy frontend; build log should list all 9 routes |
| **Voice turn returns 401** | Not logged in or expired token | Login again; token lasts 24h |
| **Voice turn returns 400 "No transcript"** | Empty mic input | Speak clearly; use Chrome/Edge; check mic permissions |
| **Lesson report empty** | No voice turns in conversation | Complete at least one mic turn before **End lesson & report** |

### Auth errors

| Error | Cause | Fix |
|-------|-------|-----|
| **HTTP 500 on register** | bcrypt/passlib crash (old deploy) | Deploy latest API; verify `/health/auth` returns `ok` |
| **HTTP 500 on register** | RLS blocking user insert (old deploy) | Deploy latest API with tenant context fix |
| **HTTP 401 on login** | Wrong password or RLS blocks lookup | Run migration `003_auth_rls.sql` |
| **HTTP 409 on register** | Email already exists | Use different email or login instead |
| **"Invalid credentials"** | Wrong email/password | Reset or register new account |

### Build errors

| Error | Cause | Fix |
|-------|-------|-----|
| **`IndentationError` in config.py** | Fixed in commit `35a16132` | Pull latest branch |
| **`ModuleNotFoundError`** | Wrong requirements file | Use `requirements-render.txt` on free tier |
| **Next.js monorepo warning** | Multiple lockfiles | Fixed via `outputFileTracingRoot` in `next.config.js` |
| **Frontend build: `next: not found`** | Missing `npm install` | Build command must be `npm install && npm run build` |
| **Vercel can't find repo** | Wrong root directory | Set root to `ai-english-teacher/frontend`, branch `main` |

### Docker / Local

| Error | Cause | Fix |
|-------|-------|-----|
| **Port 5432 in use** | Local Postgres running | Stop local Postgres or change port in `docker-compose.yml` |
| **`DATABASE_URL is not set`** | Missing `.env` | Copy `.env.example` to `.env` |
| **Redis connection error** | Redis not running | `docker compose up -d redis` or ignore (optional for MVP) |

---

## 9. Bugs Fixed (Changelog)

Infra fixes on `cursor/cheapest-cloud-deploy-d164`. Voice-first features on `cursor/voice-first-redesign-f37f` (PR #26).

| # | Bug | Symptom | Fix | Commit area |
|---|-----|---------|-----|-------------|
| 1 | CORS only allowed localhost | "Failed to fetch" in browser | Auto-include Render frontend URL in `CORS_ORIGINS` | `config.py` |
| 2 | `passlib` + `bcrypt` incompatible | HTTP 500 on register | Replaced passlib with `bcrypt` directly | `security.py` |
| 3 | RLS blocked user registration | HTTP 500 on register | Set tenant context before user insert | `database.py`, `auth.py` |
| 4 | `SET row_security = off` fails on Neon | HTTP 500 on login | Use `app.auth_lookup` RLS policy instead | `003_auth_rls.sql` |
| 5 | Broken ContextVar in get_db | Wrong tenant on every request | Module-level `tenant_id_ctx` | `database.py` |
| 6 | `SET LOCAL` with bound params | Silent tenant context failure | Use literal UUID in SQL | `database.py` |
| 7 | Lazy DB init missing | API crash on empty `DATABASE_URL` | Lazy engine creation | `database.py` |
| 8 | Missing frontend pages | 404 on `/conversation`, `/login` | Added all app pages | `frontend/src/app/` |
| 9 | Next.js monorepo tracing | Incomplete production build | `outputFileTracingRoot` in config | `next.config.js` |
| 10 | Render wrong build commands | Build failures | Fixed `render.yaml` + docs | `render.yaml` |
| 11 | `IndentationError` in CORS validator | API won't start | Fixed indentation | `config.py` |
| 13 | Frontend API URL baked as localhost | "Cannot reach the API" | Same-origin `/api/v1` proxy via Next.js rewrites | `next.config.js`, `api.ts` |
| 15 | asyncpg rejects `sslmode` URL param | `/health/register` TypeError | Strip sslmode, pass `ssl=True` in connect_args | `db_url.py` |
| 16 | Voice analyze + chat were separate calls | Slow, disconnected UX | Unified `voice-turn` pipeline | `orchestration/voice/voice_turn.py` |
| 17 | No teaching mode selection | Always inline correction | Teaching decision engine (immediate/delayed/Socratic) | `teaching_decision.py` |
| 18 | Render frontend `NEXT_PUBLIC_API_URL` wrong | CORS / cannot reach API | Use `/api/v1` + `API_PROXY_URL` proxy | `next.config.js` |

---

## 10. Production Checklist

### Before go-live

- [ ] Neon database created with `pgvector` extension
- [ ] All migrations applied (`001`–`007`)
- [ ] `DATABASE_URL` set on Render API (with `?sslmode=require`)
- [ ] `JWT_SECRET_KEY` set (random, not default)
- [ ] `CORS_ORIGINS` includes your frontend URL
- [ ] `NEXT_PUBLIC_API_URL` set on frontend service
- [ ] Both Render services deployed from `main` (or voice-first branch until merged)
- [ ] Frontend uses `NEXT_PUBLIC_API_URL=/api/v1` and `API_PROXY_URL` set to API host
- [ ] `AI_PROVIDER` + API keys set for real conversation (not mock mode)
- [ ] Voice lesson flow tested: persona → mic → teacher reply → lesson report
- [ ] `/health` returns healthy
- [ ] `/health/auth` returns `password_hashing: ok`
- [ ] Register + login work end-to-end
- [ ] Neon database password rotated (if ever exposed)

### Security

- [ ] Change default `JWT_SECRET_KEY`
- [ ] Rotate Neon password if shared in chat/logs
- [ ] Do not commit `.env` files
- [ ] Add AI API keys only via Render environment (not code)

### Optional upgrades

- [ ] Render Starter ($7/mo) — no cold starts
- [ ] OpenAI / Azure keys for real AI scoring
- [ ] Custom domain on Render
- [ ] Merge PR to `main` for cleaner deploys

---

## 11. Cost Tiers

| Tier | Stack | Monthly cost | Notes |
|------|-------|-------------|-------|
| **Hobby** | Neon free + Render free × 2 | **$0** | Cold starts, 512 MB RAM |
| **Starter** | Neon free + Render Starter × 2 | **~$14** | Always-on, no cold start |
| **Small prod** | Neon Launch + Render Starter + Vercel Pro | **~$30–42** | Low traffic production |
| **Full Azure** | AKS + Azure OpenAI + PG Flexible | **~$8,100** | Enterprise scale (see `docs/11-COST_ESTIMATION.md`) |

---

## 12. App Routes & API Reference

### Frontend pages

| Route | Description |
|-------|-------------|
| `/` | Landing page |
| `/register` | Create account |
| `/login` | Sign in |
| `/assessment` | Placement / skill assessment |
| `/conversation` | Voice-first AI lesson (personas, scenarios, lesson report) |
| `/grammar-class` | School grammar lessons with voice practice |
| `/dashboard/student` | Student progress dashboard |
| `/dashboard/teacher` | Teacher class view |
| `/dashboard/admin` | Admin system view |

### API endpoints (`/api/v1`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | No | Create account |
| POST | `/auth/login` | No | Sign in |
| GET | `/auth/me` | Yes | Current user |
| POST | `/assessments` | Yes | Start assessment |
| POST | `/assessments/{id}/submit` | Yes | Submit answers |
| GET | `/assessments/{id}/results` | Yes | Get results |
| POST | `/conversations` | Yes | Start lesson (`persona_id` optional) |
| POST | `/conversations/{id}/messages` | Yes | Send text message |
| POST | `/conversations/{id}/voice-turn` | Yes | **Unified voice turn** (STT → coaches → teacher) |
| GET | `/conversations/{id}/lesson-report` | Yes | Lesson completion report |
| GET | `/voice/personas` | No* | Teacher personas + scenarios list |
| POST | `/voice/analyze` | Yes | Analyze speech only (no teacher reply) |
| POST | `/voice/turn` | Yes | Standalone unified voice turn |
| GET | `/grammar/grades` | Yes | Grammar class grade list |
| GET | `/grammar/lessons` | Yes | Lessons for a grade |
| POST | `/grammar/practice` | Yes | Grammar voice practice turn |
| POST | `/writing/submit` | Yes | Submit writing |
| GET | `/dashboard/student` | Yes | Student dashboard data |
| GET | `/dashboard/teacher` | Yes | Teacher dashboard data |
| GET | `/dashboard/admin` | Yes | Admin dashboard data |
| GET | `/curriculum/topics` | No* | Curriculum topic list |
| GET | `/curriculum/skills` | Yes | Curriculum skills |
| GET | `/curriculum/lessons` | Yes | Curriculum lessons |
| GET | `/curriculum/recommended` | Yes | Primary + alternate lesson recommendations |
| GET | `/curriculum/learning-path` | Yes | Daily / weekly / exam / repair / confidence path |
| POST | `/curriculum/lesson-complete` | Yes | Record lesson completion + schedule revision |
| GET | `/curriculum/revision-schedule` | Yes | Learner revision schedule |
| GET | `/knowledge/search` | Yes | Knowledge search + grounding |
| GET | `/knowledge/lesson-context` | Yes | Lesson teaching knowledge |
| GET | `/knowledge/mistake-context` | Yes | Mistake remediation knowledge |

Full interactive docs: https://ai-english-teacher-api.onrender.com/docs

### Voice-first architecture (stack alignment)

```
Browser mic (Web Speech API) → POST /conversations/{id}/voice-turn
  → Server Whisper STT (optional, if audio_base64 sent)
  → Coach agents (fluency, pronunciation, grammar, vocabulary)
  → Teaching Decision Engine (immediate | delayed | Socratic)
  → LangGraph Teacher Orchestrator (memory + RAG + persona)
  → Teacher response → Browser TTS (speechSynthesis)
```

See `docs/13-VOICE_FIRST_PRD_V2.md` for full product spec.

---

## Quick Reference Commands

```bash
# Local full stack
cd ai-english-teacher && docker compose up --build

# Run migrations against Neon
cd ai-english-teacher/backend
DATABASE_URL="postgresql://..." python3 scripts/migrate.py

# Backend tests
cd ai-english-teacher/backend && python3 -m pytest tests/ -q

# Frontend build (verify routes)
cd ai-english-teacher/frontend && npm install && npm run build

# Wake production API
curl https://ai-english-teacher-api.onrender.com/health

# Test registration
curl -X POST https://ai-english-teacher-api.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"yourpass12","first_name":"You","last_name":"Name"}'
```

---

## 13. Microsoft Copilot / Azure OpenAI (recommended for cloud)

Replace Ollama with **Microsoft Copilot** (Azure OpenAI) for real AI on Render.

> Full setup guide: **[deploy/cheapest/COPILOT_AZURE.md](deploy/cheapest/COPILOT_AZURE.md)**

### Quick setup on Render API

| Key | Value |
|-----|-------|
| `AI_PROVIDER` | `copilot` |
| `AZURE_OPENAI_ENDPOINT` | `https://your-name.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | From Azure portal → Keys |
| `AZURE_OPENAI_DEPLOYMENT` | `gpt-4o-mini` |
| `AZURE_OPENAI_API_VERSION` | `2024-12-01-preview` |

Verify: `curl https://ai-english-teacher-api.onrender.com/health/ai` → `"provider":"copilot"`

---

## 14. Ollama LLM Setup (local only)

The repetitive **"Interesting! Tell me more."** replies happen when no LLM is configured (mock mode). Use **Ollama** for free, local AI.

### Install Ollama

1. Download: https://ollama.com
2. Pull a model:
   ```bash
   ollama pull llama3.2
   ```
3. Verify: `curl http://localhost:11434/api/tags`

### Backend configuration

Add to `backend/.env` (local) or Render API environment:

| Variable | Value |
|----------|-------|
| `AI_PROVIDER` | `ollama` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` |
| `OLLAMA_MODEL` | `llama3.2` |

**Docker Compose:** use `OLLAMA_BASE_URL=http://host.docker.internal:11434`

**Render cloud API:** Ollama cannot run on Render free tier. Options:
- Run Ollama on your PC and expose via tunnel (dev only)
- Use a VPS with Ollama (Hetzner ~€4/mo)
- Set `OPENAI_API_KEY` on Render instead

### Verify AI is working

```bash
curl https://ai-english-teacher-api.onrender.com/health/ai
```

Expected: `{"provider":"ollama","model":"llama3.2","configured":true}`

### Recommended Ollama models for English teaching

| Model | Size | Notes |
|-------|------|-------|
| `llama3.2` | 3B | Fast, good for conversation |
| `llama3.1:8b` | 8B | Better grammar corrections |
| `mistral` | 7B | Strong instruction following |
| `qwen2.5:7b` | 7B | Good multilingual support |

---

## 15. Voice-First Practice (PRD v2)

The platform centers on **continuous spoken conversation**, not text chat. The `/conversation` page is the primary voice lesson experience.

### Stack alignment (this app on Render + Neon)

| Layer | Technology | Where |
|-------|------------|-------|
| Client STT | Web Speech API | `frontend/src/hooks/useVoice.ts` |
| Client TTS | `speechSynthesis` | Same hook |
| API proxy | Next.js rewrites | `frontend/next.config.js` → Render API |
| Server STT | OpenAI-compatible Whisper | Groq `whisper-large-v3-turbo` or OpenAI `whisper-1` |
| Orchestration | LangGraph pipeline | `backend/app/orchestration/graph.py` |
| Voice coaches | Fluency, pronunciation, grammar, vocab | `backend/app/orchestration/voice/` |
| Teaching modes | Immediate, delayed, Socratic | `teaching_decision.py` |
| Personas | 7 teacher styles | `personas.py` — IELTS, PTE, TOEFL, Business, etc. |
| Memory | PostgreSQL + pgvector | Neon — `error_tracking`, `voice_analyses` |
| AI LLM | Azure Copilot / OpenAI / Groq / Ollama | `AI_PROVIDER` env var |

### Features (implemented)

| Feature | How |
|---------|-----|
| **Teacher persona picker** | `/conversation` — Friendly Beginner, IELTS Examiner, PTE Coach, etc. |
| **15+ scenarios** | Job interview, visa interview, restaurant, debate, negotiation, … |
| **Unified voice turn** | Mic → `POST /conversations/{id}/voice-turn` (analyze + teach in one call) |
| **Voice-first mode** | Toggle on conversation page (default on) |
| **Teaching modes** | Immediate, delayed batch, or Socratic self-correction |
| **Per-turn scores** | Fluency, pronunciation, grammar, vocabulary on each utterance |
| **Lesson report** | **End lesson & report** → CEFR/IELTS estimates, mistakes, next steps |
| **Grammar class voice** | `/grammar-class` — grades 5–12 with `POST /grammar/practice` |
| **Server Whisper STT** | Send `audio_base64` from mobile or future web recorder |
| **Text-to-speech** | Auto-plays AI replies (toggle "Auto-play voice") |
| **Replay** | Play again on each teacher message |

### Browser support

| Browser | Voice input | Voice output |
|---------|-------------|--------------|
| Chrome / Edge | ✅ | ✅ |
| Safari | ✅ (limited) | ✅ |
| Firefox | ❌ STT | ✅ TTS |

Use **Chrome or Edge** for full voice practice.

### Optional env for server-side STT (Groq free tier)

| Key | Value |
|-----|-------|
| `AI_PROVIDER` | `openai` |
| `OPENAI_API_KEY` | Groq API key |
| `OPENAI_BASE_URL` | `https://api.groq.com/openai/v1` |
| `WHISPER_MODEL` | `whisper-large-v3-turbo` |

Mobile app sends `audio_base64` to `/voice/analyze` and `/grammar/practice` — same backend pipeline.

### Future improvements (not yet built)

| Feature | Tool | Priority |
|---------|------|----------|
| WebSocket streaming + VAD | Real-time continuous listening | P1 |
| Azure Speech phoneme scoring | `AZURE_SPEECH_KEY` (in deps, not wired) | P2 |
| Server-side TTS | Azure / Polly for consistent teacher voice | P2 |
| Dedicated `/speaking` page | Full speaking assessment UI | P3 |
| Audio blob storage | `speaking_sessions` table + S3/Blob | P3 |

---

## 16. Mobile App (Google Play)

Android app in `mobile/` — built with **Expo React Native**.

| Feature | Screen |
|---------|--------|
| Login / Register | Secure token storage (Keychain) |
| Dashboard | CEFR, IELTS, PTE, skill scores |
| AI Practice | Role-play + voice turn API |
| Grammar | Voice grammar practice |
| Assessment | Placement test |

### Development

```bash
cd ai-english-teacher/mobile
npm install
cp .env.example .env   # set EXPO_PUBLIC_API_URL
npm start              # scan QR with Expo Go on Android
```

### Publish to Google Play

Full guide: **[mobile/GOOGLE_PLAY.md](mobile/GOOGLE_PLAY.md)**

```bash
npm install -g eas-cli
eas login
cd ai-english-teacher/mobile
eas build --platform android --profile production
```

Upload the `.aab` to [Google Play Console](https://play.google.com/console) ($25 one-time developer fee).

---

## 17. Student Intelligence v1

Student Intelligence provides a learner-state foundation for personalized teaching (Phase 1).

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/student-intelligence/profile` | Learner profile + CEFR/IELTS/PTE estimates |
| PATCH | `/api/v1/student-intelligence/profile` | Update learning goal, target exam, preferences |
| GET | `/api/v1/student-intelligence/skills` | Eight core skills with score, level, trend |
| GET | `/api/v1/student-intelligence/mistakes` | Recurring mistakes from `error_tracking` |
| GET | `/api/v1/student-intelligence/preferences` | Learning preferences |
| PATCH | `/api/v1/student-intelligence/preferences` | Update preferences |
| GET | `/api/v1/student-intelligence/summary` | Dashboard summary + recommended next focus |

All endpoints require JWT authentication.

### Data sources

| Data | Source tables |
|------|----------------|
| Profile / CEFR / exam targets | `learner_profiles`, `users` |
| Skill scores | `progress_snapshots`, `voice_analyses`, `assessment_results` |
| Mistakes | `error_tracking` |
| Preferences | `learner_profiles.preferences` (JSONB) |
| Progress history | `progress_snapshots` |

No new database tables — reuses existing schema.

### Dashboard integration

The student dashboard (`/dashboard/student`) loads `GET /student-intelligence/summary` via the shared `api.ts` client.

### Smoke tests

```bash
# After login, use access token:
curl -H "Authorization: Bearer $TOKEN" https://ai-english-teacher-api.onrender.com/api/v1/student-intelligence/summary
curl -H "Authorization: Bearer $TOKEN" https://ai-english-teacher-api.onrender.com/api/v1/student-intelligence/skills
curl -H "Authorization: Bearer $TOKEN" https://ai-english-teacher-api.onrender.com/api/v1/student-intelligence/mistakes
```

Expected for new learners: `recommended_next_focus: "placement assessment"`, `has_data: false`.

---

## 18. Teacher Brain v1

Teacher Brain is a planning layer that makes each teacher response more personalized before the existing `TeacherAgent` generates spoken text.

### Integration points

| Path | Location |
|------|----------|
| Cognitive (default) | `cognitive/tool_executor.py` → `execute_teacher_brain()` → `TeacherBrainService` |
| LangGraph fallback | `orchestration/graph.py` → `enrich_context_for_langgraph()` |
| Voice turn API | Optional `teacher_brain` metadata on `/voice/turn` and `/conversations/{id}/voice-turn` |

### Optional API metadata

```json
{
  "teacher_brain": {
    "intent": "practice_continuation",
    "teaching_strategy": "scaffold",
    "skill_focus": "grammar",
    "correction_mode": "immediate",
    "next_prompt": "Can you try one more sentence using past tense?"
  }
}
```

Core fields (`response`, `teaching_mode`, `corrections`, `voice_scores`) are unchanged. `teaching_decision.py` remains the correction-timing authority.

### Mock mode

Teacher Brain uses deterministic heuristics for planning. Response generation uses existing mock `TeacherAgent` / `ConversationAgent` behavior when `AI_PROVIDER=mock`.

### Smoke test

```bash
curl -X POST https://ai-english-teacher-api.onrender.com/api/v1/voice/turn \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"transcript":"I am go to market yesterday.","scenario":"everyday","persona_id":"conversation_partner"}'
```

Expect: `response`, `teaching_mode`, `corrections`, `voice_scores`, and optional `teacher_brain` with `intent` and `skill_focus`.

---

## 19. Memory Intelligence v1

Memory Intelligence is a unified read/write layer that lets the AI Teacher remember recurring mistakes, lesson reflections, Teacher Brain decisions, and learner preferences across sessions.

### Memory types

| Type | Storage |
|------|---------|
| Recurring mistakes | `error_tracking` |
| Lesson reflections | `learner_memories` (`memory_type=lesson_reflection`) |
| Teacher Brain decisions | `learner_memories` (`memory_type=teacher_brain_decision`) |
| Learning events | `learner_memories` (`memory_type=learning_event`) |
| Lesson reports | `reports` (`report_type=lesson_completion`) |
| Preferences | `learner_profiles.preferences` + `learner_memories` |
| Recent turns | `conversation_messages` (read at request time) |

### Read policy (deterministic, no AI required)

- Recent turns: max 12 messages
- Recurring mistakes: max 8, by `occurrence_count` and `last_seen_at`
- Lesson reflections: max 3
- Teacher Brain decisions: max 5
- `memory_summary`: max 1500 characters for TeacherAgent context

### Write points

- After voice turn / cognitive turn: Teacher Brain decision + grammar corrections via `MemoryIntelligenceService.write_after_teacher_turn()`
- After lesson report: full report to `reports`, reflection to `learner_memories`, learning event
- Voice pipeline: grammar errors to `error_tracking` (existing)

### Optional API endpoints

- `GET /api/v1/memory/summary` — compact memory summary for current learner
- `GET /api/v1/memory/reflections` — recent lesson reflections

### Optional voice-turn metadata

```json
{
  "memory": {
    "recurring_mistakes_count": 3,
    "reflections_available": true,
    "memory_summary_available": true
  }
}
```

Core voice-turn fields are unchanged.

### Mock mode

Memory retrieval does not require embeddings or LLM calls. `build_bundle()` returns a safe empty bundle on failure.

### Smoke tests

```bash
# Memory summary (authenticated)
curl https://ai-english-teacher-api.onrender.com/api/v1/memory/summary \
  -H "Authorization: Bearer $TOKEN"

# Lesson report (persists reflection)
curl https://ai-english-teacher-api.onrender.com/api/v1/conversations/$CONV_ID/lesson-report \
  -H "Authorization: Bearer $TOKEN"

# Voice turn with memory metadata
curl -X POST https://ai-english-teacher-api.onrender.com/api/v1/voice/turn \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"transcript":"I am go to market yesterday.","scenario":"everyday"}'
```

### Known limitations

- Text message path does not yet attach full memory metadata (voice-first scope)
- `vocabulary_entries` table not integrated
- Memory decay/archival deferred to v2
- LangGraph path uses same `MemoryIntelligenceService` but with lighter session context when no conversation DB rows exist

---

## 20. Curriculum Intelligence v1

Curriculum Intelligence is the deterministic decision layer that determines what to learn next, what to revise, which learning path to follow, and which lesson Teacher Brain should recommend. It consumes Student Intelligence summaries, Memory Intelligence bundles, learner profiles, assessment results, progress snapshots, and lesson completions — without modifying Teacher Brain core planning logic.

### Architecture

```
Student Intelligence summary + Memory Intelligence bundle + learner profile
  → CurriculumIntelligenceService.build_recommendations()
  → Deterministic recommendation engine (10 rules, priority order)
  → primary recommendation + up to 2 alternates
  → optional curriculum_recommendation metadata on voice-turn response
```

**Key modules:**

| Module | Path | Role |
|--------|------|------|
| Registry | `backend/app/services/curriculum_registry.py` | Topics, skills, lessons, prerequisites, path templates |
| Service | `backend/app/services/curriculum_intelligence_service.py` | Recommendations, paths, revision scheduling |
| Repository | `backend/app/repositories/curriculum_repository.py` | `lesson_completions`, `revision_schedule` persistence |
| API | `backend/app/api/v1/curriculum.py` | REST endpoints |
| Schemas | `backend/app/schemas/curriculum_intelligence.py` | Request/response contracts |

### Curriculum registry

Single source of truth for curriculum content. No AI required.

**Topics:** grammar, vocabulary, speaking, pronunciation, fluency, listening, writing, exam_preparation

**Sources:** `grammar_curriculum.py`, `personas.py`, conversation scenarios, exam personas

**Registry functions:** `get_topics()`, `get_skills()`, `get_lessons()`, `get_lesson()`, `get_paths()`, `get_path()`

### Recommendation engine (deterministic rules)

Priority order — first match wins:

| Rule | Condition | Recommendation |
|------|-----------|----------------|
| 1 | No completed assessment | Placement assessment |
| 2 | Due revision item in schedule | Revision lesson |
| 3 | Recurring mistake `occurrence_count >= 3` | Targeted grammar lesson |
| 4 | `weakest_skill == grammar` | Grammar lesson |
| 5 | `weakest_skill == pronunciation` | Pronunciation lesson |
| 6 | `weakest_skill == fluency` or `speaking` | Conversation scenario |
| 7 | `target_exam == IELTS` | IELTS speaking practice |
| 8 | `target_exam == PTE` | PTE practice |
| 9 | `confidence_score < 0.5` | Beginner confidence lesson |
| 10 | Else | Next lesson from CEFR path |

Each recommendation includes: `lesson_id`, `title`, `reason`, `route`, `skill_focus`, `priority`.

### Learning paths

| Path type | Contents |
|-----------|----------|
| **daily** | One revision + one weak-skill lesson + one speaking practice |
| **weekly** | Three lesson recommendations + two speaking scenarios + revision + assessment checkpoint |
| **exam** | Exam-tagged lessons, speaking-first progression |
| **repair** | Weakest-skill focus |
| **confidence** | Friendly beginner persona, conversational scenarios, low-pressure learning |

Query: `GET /api/v1/curriculum/learning-path?type=daily|weekly|exam|repair|confidence`

### Revision scheduling

Revision items are generated from `error_tracking`, lesson completions, and memory reflections.

| Trigger | Due interval |
|---------|--------------|
| `occurrence_count` 2–4 | Review in 3 days |
| `occurrence_count` 5+ | Review in 1 day |
| Lesson score 70–89 | Review in 7 days |
| Lesson score 90+ | Review in 30 days |

Stored in `revision_schedule` table (migration `006_curriculum_intelligence.sql`).

### New APIs

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/curriculum/topics` | No | List curriculum topics |
| GET | `/curriculum/skills` | Yes | List skills |
| GET | `/curriculum/lessons` | Yes | List lessons (optional `topic`, `skill` filters) |
| GET | `/curriculum/recommended` | Yes | Primary + alternate recommendations |
| GET | `/curriculum/learning-path` | Yes | Path bundle (`type` query param) |
| POST | `/curriculum/lesson-complete` | Yes | Record completion + trigger revision |
| GET | `/curriculum/revision-schedule` | Yes | Learner revision schedule |

### Teacher Brain integration (additive only)

Voice-turn responses may include optional metadata — core Teacher Brain planning is unchanged:

```json
{
  "curriculum_recommendation": {
    "lesson_id": "grammar-9-modal-verbs",
    "title": "Modal Verbs",
    "reason": "Your weakest skill is grammar.",
    "route": "/grammar-class",
    "skill_focus": "grammar"
  }
}
```

### Dashboard integration

Student dashboard (`/dashboard/student`) shows a **Recommended Next Lesson** card using `GET /curriculum/recommended` — title, reason, skill focus, and lesson CTA.

### Mock mode

Curriculum Intelligence does not require embeddings or LLM calls. Registry is static; recommendation engine is fully deterministic. `build_recommendations()` returns a safe empty bundle on failure.

### Smoke tests

```bash
# 1. Login and capture token
TOKEN=$(curl -s -X POST https://ai-english-teacher-api.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass12"}' | jq -r .access_token)

# 2. Recommended next lesson
curl https://ai-english-teacher-api.onrender.com/api/v1/curriculum/recommended \
  -H "Authorization: Bearer $TOKEN"

# 3. Daily learning path
curl "https://ai-english-teacher-api.onrender.com/api/v1/curriculum/learning-path?type=daily" \
  -H "Authorization: Bearer $TOKEN"

# 4. Complete a lesson
curl -X POST https://ai-english-teacher-api.onrender.com/api/v1/curriculum/lesson-complete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"lesson_id":"grammar-9-modal-verbs","score":85,"skill_focus":"grammar"}'

# 5. Revision schedule
curl https://ai-english-teacher-api.onrender.com/api/v1/curriculum/revision-schedule \
  -H "Authorization: Bearer $TOKEN"

# 6. Voice turn — confirm curriculum_recommendation metadata
curl -X POST https://ai-english-teacher-api.onrender.com/api/v1/conversations/$CONV_ID/voice-turn \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"transcript":"Hello teacher, I want to practice speaking.","scenario":"everyday"}'
```

### Known limitations

- Registry content is v1 static — dynamic curriculum authoring deferred to Knowledge Intelligence (Phase 5)
- Revision scheduler does not yet send push/reminder notifications
- Learning paths do not auto-advance on calendar boundaries (request-time generation only)
- Text message path does not attach curriculum metadata (voice-first scope)

---

## 21. Knowledge Intelligence v1

Knowledge Intelligence is the unified retrieval and grounding layer that decides **what teaching knowledge** to use when explaining, demonstrating, correcting, and practicing lessons. Curriculum Intelligence decides what to study; Knowledge Intelligence supplies the content.

### Architecture

```
Curriculum lesson + SI profile + Memory mistakes + user message
  → KnowledgeIntelligenceService.build_grounding_context()
  → lesson/mistake maps + pgvector/keyword + grammar rules
  → GroundingContext (≤800 chars, voice-safe)
  → teaching_instruction injection → Teacher Brain → TeacherAgent
```

| Module | Path | Role |
|--------|------|------|
| Registry | `backend/app/services/knowledge_registry.py` | In-code lesson/mistake/concept maps |
| Service | `backend/app/services/knowledge_intelligence_service.py` | Retrieval, ranking, validation, grounding |
| Store | `backend/app/services/knowledge_store.py` | pgvector + keyword fallback (preserved) |
| API | `backend/app/api/v1/knowledge.py` | Search, lesson-context, mistake-context |

### Registry (in-code v1)

- **Concepts:** articles, past_tense, present_perfect, prepositions, conditionals, modal_verbs, restaurant_roleplay, job_interview, ielts_speaking, pte_speaking, etc.
- **lesson_knowledge_map:** curriculum lesson IDs → concepts + query terms
- **mistake_knowledge_map:** error categories → explanations, examples, corrections, lesson IDs

No migration 007 required for v1.

### Retrieval pipeline

1. Lesson mapping → grammar rule from `grammar_curriculum.py`
2. Mistake mapping → remediation text
3. Skill / CEFR / exam query expansion
4. `knowledge_store.retrieve_knowledge()` (pgvector)
5. Keyword fallback (`curriculum_data.py`)
6. Validation + truncation → `GroundingContext`

### Ranking factors

lesson match, concept match, skill match, mistake match, CEFR match, retrieval score, source quality (grammar_curriculum > knowledge_chunks > registry > keyword), brevity.

### Validation

- Max grounding ~800 characters
- Max 2 examples, 1 practice prompt
- Relevance threshold for vector scores
- Safe empty fallback — voice-turn never breaks

### APIs

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/knowledge/search` | Yes | `q` + optional skill/lesson/CEFR/exam |
| GET | `/knowledge/lesson-context` | Yes | `lesson_id` required |
| GET | `/knowledge/mistake-context` | Yes | `error_category` required |

### Teacher Brain integration (additive)

Grounding injected into `teaching_instruction`:

```
Teaching knowledge:
Use past simple for completed past actions. Example: I went to the market yesterday.
```

Planning logic (`intent_analyzer`, `error_detector`, `strategy_selector`, `response_planner`) is unchanged.

### Voice-turn metadata (optional)

```json
{
  "knowledge_grounding": {
    "lesson_id": "grammar-6-past-simple",
    "skill_focus": "grammar",
    "chunk_count": 2,
    "sources": ["grammar_curriculum"],
    "fallback_used": false
  }
}
```

### Seed script

```bash
cd ai-english-teacher/backend
DATABASE_URL="postgresql://..." python3 scripts/seed_knowledge_chunks.py
# Optional embeddings when AI configured:
DATABASE_URL="..." python3 scripts/seed_knowledge_embeddings.py
```

Safe re-run — inserts only new topic+source pairs.

### Mock mode

When `OPENAI_API_KEY` is unset, embeddings are skipped; keyword + grammar rules still produce grounding.

### Smoke tests

```bash
# Search
curl "https://ai-english-teacher-api.onrender.com/api/v1/knowledge/search?q=past+tense" \
  -H "Authorization: Bearer $TOKEN"

# Lesson context
curl "https://ai-english-teacher-api.onrender.com/api/v1/knowledge/lesson-context?lesson_id=grammar-9-modal-verbs" \
  -H "Authorization: Bearer $TOKEN"

# Mistake context
curl "https://ai-english-teacher-api.onrender.com/api/v1/knowledge/mistake-context?error_category=past_tense" \
  -H "Authorization: Bearer $TOKEN"

# Voice turn — verify knowledge_grounding in response
curl -X POST https://ai-english-teacher-api.onrender.com/api/v1/conversations/$CONV_ID/voice-turn \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"transcript":"I am go to market yesterday.","scenario":"everyday"}'
```

### Known limitations

- No concept graph DB (in-code maps only)
- No admin ingest API (script-based seeding)
- No retrieval log table
- `vocabulary_entries` not integrated
- TeacherAgent reads grounding via `teaching_instruction` (not separate prompt field)

---

## 22. AI Governance v1

AI Governance is a deterministic evaluation and audit layer that scores Teacher responses, curriculum recommendations, knowledge grounding, and memory usage after each turn — without changing planning or blocking voice responses.

### Architecture

```
Voice turn / cognitive orchestrator completes response
  → GovernanceService.evaluate_turn_safe() / evaluate_turn()
  → TeacherResponseEvaluation, CurriculumEvaluation, GroundingEvaluation, MemoryEvaluation
  → GovernanceMetadata (scores + warnings)
  → optional in-memory store + learning_event audit
  → voice-turn response metadata.governance
```

| Module | Path | Role |
|--------|------|------|
| Schemas | `backend/app/schemas/governance.py` | Evaluation + API response models |
| Service | `backend/app/services/governance_service.py` | Deterministic scoring, warnings, audit |
| API | `backend/app/api/v1/governance.py` | Read-only summary, quality, grounding, audit |

Governance runs **after** response generation. Teacher Brain planning modules are not modified.

### Evaluation model

| Dimension | Signals (0–1) |
|-----------|----------------|
| Teacher response | correction quality, explanation quality, encouragement, practice prompt, length compliance |
| Curriculum | weakest-skill match, lesson relevance, revision relevance, path consistency |
| Grounding | grounding present, source count, fallback usage, lesson match, knowledge quality |
| Memory | recurring mistakes used, lesson reflections used, memory summary available |
| Student outcome | progress trend, confidence trend, lesson completion activity, assessment improvement |

Overall score is a weighted blend of turn scores; student outcome is blended into summary averages when SI data is available.

### Governance metadata (voice-turn, optional)

```json
{
  "governance": {
    "teacher_response_score": 0.91,
    "grounding_score": 0.88,
    "curriculum_score": 0.94,
    "memory_score": 0.82,
    "overall_score": 0.89,
    "warnings": [],
    "status": "good"
  }
}
```

Additive and backward compatible — clients that ignore `governance` continue to work.

### Safety warnings (non-blocking)

| Warning | Trigger |
|---------|---------|
| `ungrounded_teaching` | Teaching intent but no knowledge grounding when expected |
| `excessive_response_length` | Response exceeds voice-safe length threshold |
| `missing_practice_prompt` | Teaching turn without practice prompt |
| `curriculum_mismatch` | Recommendation skill ≠ weakest skill |
| `weak_recommendation_confidence` | Low curriculum confidence |
| `missing_memory_context` | Memory expected but not used |
| `grounding_fallback_used` | Knowledge retrieval used fallback path |

Warnings are logged and returned in metadata; they never fail the HTTP request.

### Audit events

Stored in-process per learner (deque, capped) and optionally written as `governance_*` learning events via Memory Intelligence when DB is available.

Event kinds: `teacher_response_generated`, `curriculum_recommendation_generated`, `knowledge_grounding_generated`, `lesson_completed`, `assessment_completed`, `governance_warning`.

No new migration — reuses reports / learner_memories / metadata where possible.

### APIs (JWT required, read-only)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/governance/summary` | Aggregated scores + recent warnings |
| GET | `/governance/evaluations` | Recent turn evaluations (`limit`) |
| GET | `/governance/quality` | Average scores across stored evaluations |
| GET | `/governance/grounding` | Grounding evaluation history |
| GET | `/governance/audit-log` | Governance audit events |

### Integration points

- `cognitive/orchestrator.py` — post-turn `evaluate_turn_safe`
- `orchestration/runner.py` — passes `governance` in metadata
- `orchestration/voice/voice_turn.py` — final eval with curriculum/memory/grounding context
- `api/v1/conversations.py` — `governance` on voice-turn response

### Mock mode

When AI keys are unset, governance still runs on deterministic heuristics over response text and metadata. No OpenAI calls in governance layer.

### Smoke tests

```bash
# Voice lesson — verify governance block in response
curl -X POST https://ai-english-teacher-api.onrender.com/api/v1/conversations/$CONV_ID/voice-turn \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"transcript":"I went to the market yesterday.","scenario":"everyday"}'
# Expect: governance.teacher_response_score, grounding_score, curriculum_score, memory_score

# Governance summary
curl "https://ai-english-teacher-api.onrender.com/api/v1/governance/summary" \
  -H "Authorization: Bearer $TOKEN"

# Quality averages
curl "https://ai-english-teacher-api.onrender.com/api/v1/governance/quality" \
  -H "Authorization: Bearer $TOKEN"

# Grounding history
curl "https://ai-english-teacher-api.onrender.com/api/v1/governance/grounding" \
  -H "Authorization: Bearer $TOKEN"
```

Verify after a voice lesson:

1. Teacher response generated
2. `governance` metadata present on voice-turn
3. Curriculum recommendation metadata present (if curriculum path active)
4. `knowledge_grounding` metadata present (if grounding active)
5. Memory metadata present (if memory bundle used)
6. Scores: `teacher_response_score`, `grounding_score`, `curriculum_score`, `memory_score`

### Known limitations

- In-process evaluation store (not persisted across process restarts on Render)
- No admin mutation APIs (read-only v1)
- Text-message path may omit full governance metadata (voice-first scope)
- Student outcome scoring depends on SI summary availability

---

## 23. Analytics & Insights v1

Analytics & Insights v1 aggregates existing learner data into progress trends, governance quality, curriculum activity, knowledge grounding metrics, and deterministic learner insights — **no new database tables**.

### Purpose

Transform platform events, progress snapshots, governance scores, curriculum completions, and message metadata into read-only analytics for the student dashboard and API consumers.

### Data sources (existing tables only)

| Source | Analytics use |
|--------|----------------|
| `progress_snapshots` | Skill + CEFR + confidence time series |
| `voice_analyses` | Speaking, pronunciation, fluency trends |
| `assessment_results` | Assessment history (future cross-assessment) |
| `lesson_completions` | Completion velocity, skill distribution |
| `revision_schedule` | Pending / completed / overdue revisions |
| `conversation_messages.metadata` | `governance`, `knowledge_grounding`, `curriculum_recommendation` |
| `learner_memories` | Governance learning events (supplement) |
| Student Intelligence `get_summary` | Insights wrapper (contracts unchanged) |

### Architecture

```
Existing DB + message metadata
  → analytics_repository (read-only SQL)
  → AnalyticsService (deterministic aggregation)
  → GET /api/v1/analytics/*
  → Student dashboard (line chart + insights panel)
```

### Analytics APIs (JWT, read-only)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/analytics/overview` | Scorecard + key metrics (30d) |
| GET | `/analytics/progress` | Skill / CEFR / confidence trends |
| GET | `/analytics/governance` | Governance score averages + warnings |
| GET | `/analytics/curriculum` | Completions, revisions, velocity |
| GET | `/analytics/knowledge` | Grounding rate, fallback, sources |
| GET | `/analytics/insights` | Deterministic learner insight cards |

### Dashboard widgets

Student dashboard (`/dashboard/student`) adds:

- Grammar progress line chart (`api.analytics.progress`)
- Learning insights panel (`api.analytics.insights`)
- Optional governance quality card (`api.analytics.governance`)
- Optional curriculum activity summary (`api.analytics.curriculum`)

Existing SI summary, radar chart, and curriculum recommendation cards are preserved.

### Insight generation (deterministic v1)

No AI — rules based on:

- Weakest skill (Student Intelligence)
- Confidence improving (progress snapshots)
- Recurring mistakes (`error_tracking`)
- Governance warnings (e.g. `grounding_fallback_used`)
- Pending revisions (curriculum analytics)

### Empty-state behavior

All endpoints return safe empty responses (`has_data: false`) when no learner profile or no historical data. Dashboard shows friendly empty messages; requests never fail due to missing analytics.

### Mock mode

Analytics uses SQL + metadata only — no OpenAI calls in the analytics layer.

### Smoke tests

```bash
# After login + voice lesson activity
curl "https://ai-english-teacher-api.onrender.com/api/v1/analytics/overview" \
  -H "Authorization: Bearer $TOKEN"

curl "https://ai-english-teacher-api.onrender.com/api/v1/analytics/progress" \
  -H "Authorization: Bearer $TOKEN"

curl "https://ai-english-teacher-api.onrender.com/api/v1/analytics/insights" \
  -H "Authorization: Bearer $TOKEN"

# Open student dashboard — verify trend chart and insights panel
```

### Known limitations

- No cohort / tenant analytics (v2)
- No `analytics_snapshots` materialized table
- Fluency/pronunciation trends use `voice_analyses` (not `progress_snapshots`)
- Governance history depends on message metadata (post–Phase 6 turns)
- Teacher/admin dashboards remain stubs

---

## 24. Enterprise Operations v1

Enterprise Operations v1 adds tenant-scoped teacher and admin workflows, operational health, tenant settings/feature flags (JSONB), and report summaries — **no new database tables**.

### Purpose

Turn the multi-tenant skeleton into an operable SaaS foundation: real teacher roster, learner summaries, admin tenant metrics, composite health, and RBAC-protected `/operations/*` APIs.

### Architecture

```
tenants, users, learner_profiles, lesson_completions, reports,
conversation_messages.metadata (governance, knowledge_grounding)
  → operations_repository (tenant-scoped reads + settings PATCH)
  → OperationsService
  → GET/PATCH /api/v1/operations/*
  → Teacher / Admin dashboards
```

Reuses `AnalyticsService` and `get_summary` (read-only) without changing intelligence contracts.

### Operations APIs

| Method | Path | RBAC |
|--------|------|------|
| GET | `/operations/overview` | admin, super_admin |
| GET | `/operations/health` | admin, super_admin |
| GET | `/operations/tenant` | admin, super_admin |
| PATCH | `/operations/tenant/settings` | admin, super_admin |
| GET | `/operations/feature-flags` | teacher, admin, super_admin |
| GET | `/operations/users` | admin, super_admin |
| GET | `/operations/teacher/roster` | teacher, admin, super_admin |
| GET | `/operations/teacher/learners/{id}/summary` | teacher, admin, super_admin |
| GET | `/operations/admin/summary` | admin, super_admin |
| GET | `/operations/reports/learner/{id}` | teacher, admin, super_admin |

### RBAC matrix

| Role | Roster | Admin summary | Tenant PATCH | Feature flags |
|------|--------|---------------|--------------|---------------|
| student | 403 | 403 | 403 | 403 |
| teacher | ✅ | 403 | 403 | ✅ |
| admin | ✅ | ✅ | ✅ | ✅ |
| super_admin | ✅ | ✅ | ✅ | ✅ |

### Teacher dashboard

`/dashboard/teacher` calls `GET /operations/teacher/roster`:

- Class size, active learners (7d), needs attention count
- Roster table: CEFR, weakest skill, lessons (30d), governance score, status

### Admin dashboard

`/dashboard/admin` calls `GET /operations/admin/summary` + `GET /operations/health`:

- Tenant-scoped user/learner counts (not global)
- Lessons completed (30d), governance avg, warnings, grounding fallback rate
- Operational health checks (DB, AI, auth)

### Tenant settings & feature flags

Stored in `tenants.settings` JSONB:

```json
{
  "features": {
    "voice_enabled": true,
    "governance_metadata": true,
    "curriculum_recommendations": true,
    "knowledge_grounding": true,
    "analytics_dashboard": true
  },
  "limits": { "max_learners": 100 }
}
```

Limits return warnings only in v1 (not enforced).

### Login redirect

| Role | Dashboard |
|------|-----------|
| student | `/dashboard/student` |
| teacher | `/dashboard/teacher` |
| admin / super_admin | `/dashboard/admin` |

### Smoke tests

```bash
# Teacher roster
curl "https://ai-english-teacher-api.onrender.com/api/v1/operations/teacher/roster" \
  -H "Authorization: Bearer $TEACHER_TOKEN"

# Admin summary
curl "https://ai-english-teacher-api.onrender.com/api/v1/operations/admin/summary" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Health
curl "https://ai-english-teacher-api.onrender.com/api/v1/operations/health" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Feature flags
curl "https://ai-english-teacher-api.onrender.com/api/v1/operations/feature-flags" \
  -H "Authorization: Bearer $TOKEN"

# Student should get 403 on teacher roster
```

### Known limitations

- No class/cohort model (teacher sees all tenant learners)
- No cross-tenant super_admin console
- No usage metering persistence
- No PDF report export
- RLS gaps unchanged (separate security hardening phase)
- Role assignment still manual DB (no promote API in v1)

---

## 25. Security Hardening & RLS v1

**Branch:** `cursor/security-hardening-v1-f37f`  
**Migration:** `007_security_rls_hardening.sql`

### Purpose

Harden multi-tenant production security: close IDOR gaps, enforce JWT validation against the database, extend RLS coverage, and expose admin security diagnostics.

### Threats addressed

| Threat | Mitigation |
|--------|------------|
| Cross-learner IDOR (conversations, assessments) | Ownership checks via `security_service` |
| Stale JWT role / tenant | DB-backed `get_current_user` |
| Inactive users | Blocked at login and on each authenticated request |
| Child-table RLS gaps | Migration 007 policies via parent tenant |
| Unprotected voice/memory tables | RLS on `voice_analyses`, `learner_memories` |

### IDOR fixes

- `POST /conversations/{id}/messages`, `voice-turn`, `lesson-report` verify tenant + learner ownership
- `POST /assessments/{id}/start|submit`, `GET /results` verify tenant + ownership
- Students: own learner resources only (404 on violation to limit enumeration)
- Teachers/admins: tenant-scoped learner access in v1 (no class assignments)

### JWT hardening

- `get_current_user` loads `users` row, checks `is_active`, `tenant_id`, and `role` against token
- Login rejects inactive accounts
- Refresh already checked `is_active` (unchanged)
- Token shape unchanged (backward compatible)

### RLS migration 007

Enables or upgrades policies for:

- `conversation_messages` (via `conversations.tenant_id`)
- `assessment_results` (via `assessments.tenant_id`)
- `voice_analyses`, `learner_memories` (direct `tenant_id`)
- Legacy upgrades: `conversations`, `assessments`, `reports`, `progress_snapshots`, `error_tracking` (NULLIF + WITH CHECK)

Apply on Neon:

```bash
psql "$DATABASE_URL" -f database/migrations/007_security_rls_hardening.sql
```

### Security diagnostics APIs (admin only)

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/security/summary` | Overall security posture |
| `GET /api/v1/security/rls` | Per-table RLS coverage |
| `GET /api/v1/security/auth` | Auth hardening flags |
| `GET /api/v1/security/authorization` | RBAC / ownership snapshot |

RBAC: `admin` and `super_admin` only.

### Authorization model (v1)

| Role | Learner data |
|------|----------------|
| student | Own profile and resources only |
| teacher | All learners in tenant |
| admin | Tenant operations + security diagnostics |
| super_admin | Bypass on role-gated routes |

### Tenant isolation model

1. JWT `tenant_id` validated against DB user
2. `SET LOCAL app.tenant_id` per request (`get_db`)
3. RLS policies on tenant and child tables
4. API-layer ownership checks on high-risk ID routes

### RBAC matrix (security routes)

| Route | student | teacher | admin |
|-------|---------|---------|-------|
| `/security/*` | 403 | 403 | 200 |

### Smoke tests

```bash
# Student IDOR — expect 404
curl -X POST "$API/conversations/$OTHER_CONV_ID/messages" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d '{"content":"hi"}'

# Admin security summary
curl "$API/security/summary" -H "Authorization: Bearer $ADMIN_TOKEN"
curl "$API/security/rls" -H "Authorization: Bearer $ADMIN_TOKEN"
curl "$API/security/auth" -H "Authorization: Bearer $ADMIN_TOKEN"
curl "$API/security/authorization" -H "Authorization: Bearer $ADMIN_TOKEN"

# Apply migration 007 on Neon before production RLS validation
psql "$DATABASE_URL" -f database/migrations/007_security_rls_hardening.sql
```

### Known limitations

- Teacher assignment / class cohort model deferred
- MFA, password reset, SSO deferred
- No persisted auth audit log or security event warehouse
- `knowledge_chunks` RLS deferred (nullable global corpus)
- Frontend route middleware deferred (API-enforced auth)
- Some legacy rows may predate metadata policies

---

## 26. Production Readiness v1

**Branch:** `cursor/production-readiness-v1-f37f`  
**Scope:** Deployment verification tooling only — no new product features.

### Purpose

Operational gate for staging/production: automated smoke tests, migration verification, environment checks, readiness APIs, backup/restore guidance, and rollback procedures.

### Production APIs (admin only, read-only)

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/production/readiness` | Aggregate deployment readiness |
| `GET /api/v1/production/migrations` | `schema_migrations` vs expected 001–007 |
| `GET /api/v1/production/security` | Security posture snapshot |
| `GET /api/v1/production/environment` | Env config status (no secrets exposed) |

### Automated smoke script

```bash
cd ai-english-teacher/backend
export API_BASE_URL=https://ai-english-teacher-api.onrender.com
export ADMIN_TOKEN=your_admin_jwt
# optional: STUDENT_TOKEN for RBAC negative checks
python3 scripts/production_smoke_test.py
```

Checks: `/health`, `/health/auth`, `/health/ai`, `/operations/health`, `/security/summary`, `/production/readiness`, `/analytics/overview`, `/governance/summary`.

### Deployment checklist

#### Pre-deploy

- [ ] Migrations 001–007 applied on Neon (`python3 scripts/migrate.py`)
- [ ] `JWT_SECRET_KEY` set (not default)
- [ ] `DATABASE_URL` with `?sslmode=require`
- [ ] `CORS_ORIGINS` includes frontend URL
- [ ] AI keys or `AI_PROVIDER=mock` for staging
- [ ] Run `python3 scripts/production_smoke_test.py` after staging deploy

#### Deploy

- [ ] Merge phase stack to target branch (`main` or staging branch)
- [ ] Render API + Web services deployed
- [ ] Understand `SKIP_MIGRATIONS=true` (manual migrate required)

#### Post-deploy

- [ ] `/health` healthy
- [ ] `/api/v1/production/readiness` → `passed: true` (admin token)
- [ ] `/api/v1/production/migrations` → no `missing`
- [ ] Teacher + admin dashboards load
- [ ] Security IDOR smoke (student → other learner → 404)

#### Rollback

1. Render Dashboard → Service → rollback to previous deploy
2. Database migrations are forward-only — no automatic SQL rollback
3. Bad migration: restore Neon branch/backup then redeploy previous API build

### Migration verification

```bash
DATABASE_URL="..." python3 scripts/migrate.py
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  $API/api/v1/production/migrations
```

### Backup & restore (Neon)

**Backup:** Neon branch snapshot before major migration; optional `pg_dump`; paid tier PITR.

**Restore:** Neon branch restore or PITR → update `DATABASE_URL`; or `psql < backup.sql` on a test branch first.

### Incident response (short)

1. Check `/health` and `/operations/health`
2. Render logs + Neon connectivity
3. Deploy issue → rollback Render
4. Data issue → Neon branch restore
5. Document and post-mortem

### Staging approval flow

1. Apply migrations on staging Neon
2. Deploy staging Render
3. `production_smoke_test.py` → all PASS
4. `/production/readiness` → `passed: true`
5. Manual product smoke
6. Approve production promote

### Known limitations

- No load testing in v1
- No external alerting
- Smoke script needs admin JWT
- `knowledge_chunks` RLS deferred

---

## 27. Reliability & Observability v1

**Branch:** `cursor/reliability-observability-v1-f37f`  
**Scope:** Monitoring, diagnostics, structured logging, request traceability, backup verification, and operational visibility — no new product features.

### Purpose

Operate the platform safely after deployment: correlate requests, inspect logging/backup/performance posture, and run lightweight operational smoke tooling.

### Request IDs (`X-Request-ID`)

- Middleware generates a UUID when the header is absent.
- Incoming `X-Request-ID` is respected and echoed on the response.
- Request ID is bound to logging context (`request_id` in log lines / JSON logs).
- Safe for Render — no external tracing dependency.

Verify:

```bash
curl -sI https://ai-english-teacher-api.onrender.com/health | grep -i x-request-id
curl -sI -H "X-Request-ID: my-trace-001" \
  https://ai-english-teacher-api.onrender.com/health | grep -i x-request-id
```

### Logging strategy

Centralized `setup_logging()` on app startup:

| Variable | Default | Purpose |
|----------|---------|---------|
| `LOG_LEVEL` | `INFO` | Root log level |
| `LOG_JSON_FORMAT` | `false` | `true` for JSON lines (Render log drains) |

Text format: `timestamp level [request_id] logger: message`  
JSON includes: `timestamp`, `level`, `request_id`, `logger`, `message`.

### Reliability APIs (admin / super_admin, read-only)

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/reliability/status` | Aggregate reliability + observability snapshot |
| `GET /api/v1/reliability/logging` | Logging configuration status |
| `GET /api/v1/reliability/backup` | Backup readiness + DB probe |
| `GET /api/v1/reliability/performance` | Load smoke tooling availability |

```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  $API/api/v1/reliability/status
```

### Backup verification

Non-destructive script — verifies `DATABASE_URL`, `schema_migrations`, tenant count, and `SELECT 1`:

```bash
cd ai-english-teacher/backend
export DATABASE_URL='postgresql://...?sslmode=require'   # Neon connection string
./scripts/backup_verify.sh
```

**Neon:** use the primary branch connection string from Neon dashboard; run before major migrations or before promoting staging to production. Pair with Neon branch snapshots / PITR (see §26).

Exit codes: `0` success, `1` failure.

### Load smoke test

Lightweight sequential + small concurrency checks (not stress testing):

```bash
cd ai-english-teacher/backend
export API_BASE_URL=https://ai-english-teacher-api.onrender.com
export ADMIN_TOKEN=your_admin_jwt
# optional: CONCURRENCY=2 ROUNDS=1
python3 scripts/load_smoke.py
```

Targets: `/health`, `/api/v1/production/readiness`, `/api/v1/operations/health`.

### Sentry (optional)

| Variable | Purpose |
|----------|---------|
| `SENTRY_DSN` | Optional error reporting — detection only in v1 (no hard SDK dependency) |

Reliability `/status` reports `sentry_configured` when set.

### Extended production smoke

`scripts/production_smoke_test.py` now also checks:

- Reliability APIs (`/reliability/*`)
- `X-Request-ID` generation and propagation
- Security APIs (`/security/summary`, `/rls`, `/auth`, `/authorization`)
- Operations APIs (`/operations/health`, `/operations/overview`)
- Student RBAC negatives (403) on protected routes

```bash
python3 scripts/production_smoke_test.py
```

### Operational troubleshooting

1. **Missing request ID in logs** — confirm middleware active; check response headers on `/health`.
2. **Reliability backup warnings** — run `backup_verify.sh`; confirm migrations applied.
3. **Performance warnings** — run `load_smoke.py`; inspect latency summary JSON.
4. **Sentry warning** — optional; set `SENTRY_DSN` or ignore for pilot.
5. **Degraded `/health`** — Neon connectivity, `DATABASE_URL`, Render logs (see §26 incident list).

### Reliability smoke checklist (staging / post-deploy)

1. Call all `/api/v1/reliability/*` endpoints (admin token) → 200
2. Verify `X-Request-ID` on `/health`
3. `python3 scripts/production_smoke_test.py` → all PASS
4. `./scripts/backup_verify.sh` → exit 0
5. `python3 scripts/load_smoke.py` → `failures: 0`
6. Confirm no regressions on existing APIs (`/health`, `/production/readiness`, `/security/summary`)

### Automated staging validation

After setting `API_BASE_URL`, `ADMIN_TOKEN`, and optionally `DATABASE_URL`, `STUDENT_TOKEN`, `TEACHER_TOKEN`:

```bash
cd ai-english-teacher/backend
python3 scripts/staging_validation.py
```

Runs health, readiness, reliability, migration/RLS API checks, `production_smoke_test.py`, `backup_verify.sh`, and `load_smoke.py`; prints JSON + recommendation (`GO TO PILOT` / `CONDITIONAL GO` / `NO-GO`).

### Known limitations (v1)

- No OpenTelemetry / distributed tracing
- No PagerDuty / Datadog / New Relic integration
- No full Sentry SDK rollout
- Load smoke is lightweight only — not capacity testing
- Governance audit remains in-process memory

---

## Related docs

| Doc | Path |
|-----|------|
| Cheapest deploy guide | `deploy/cheapest/DEPLOY.md` |
| Render troubleshooting | `deploy/cheapest/RENDER_FIX.md` |
| Neon + Vercel setup | `deploy/cheapest/NEON_VERCEL.md` |
| Voice-first PRD v2 | `docs/13-VOICE_FIRST_PRD_V2.md` |
| Cognitive Orchestration Layer | `docs/14-COGNITIVE_ORCHESTRATION_LAYER.md` |
| System architecture | `docs/02-SYSTEM_ARCHITECTURE.md` |
| API design | `docs/04-API_DESIGN.md` |
| Production readiness | `docs/12-PRODUCTION_READINESS.md` |
| Copilot / Azure OpenAI | `deploy/cheapest/COPILOT_AZURE.md` |
| Mobile app + Google Play | `mobile/GOOGLE_PLAY.md` |
| Oracle Cloud VM | `deploy/oracle-cloud/VM_SETUP.md` |

---

*Last updated: Reliability & Observability v1 · branch `cursor/reliability-observability-v1-f37f` · stack: Render + Neon + Next.js proxy*
