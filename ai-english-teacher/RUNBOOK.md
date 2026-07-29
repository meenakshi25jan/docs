# AI English Teacher — Complete Runbook

**One document for prerequisites, setup, deployment, testing, and every known error fix.**

| Live URLs (production) | |
|------------------------|---|
| Frontend | https://ai-english-teacher-web.onrender.com |
| API | https://ai-english-teacher-api.onrender.com |
| API docs | https://ai-english-teacher-api.onrender.com/docs |
| Health | https://ai-english-teacher-api.onrender.com/health |

**Deploy branch:** `cursor/cheapest-cloud-deploy-d164`  
**Repo:** `meenakshi25jan/docs` → folder `ai-english-teacher/`

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
13. [Mobile App (Google Play)](#16-mobile-app-google-play)

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
| openai | 1.58.1 | AI integration |

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
| Migrations | 3 SQL files in `database/migrations/` |

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
| `OPENAI_API_KEY` | empty | Enables real AI |
| `AZURE_OPENAI_ENDPOINT` | empty | Azure OpenAI endpoint |
| `AZURE_OPENAI_API_KEY` | empty | Azure OpenAI key |
| `REDIS_URL` | `redis://localhost:6379/0` | Optional; not needed for MVP |

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

Expected: `28 passed`

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
Migrations complete
```

### Step 3 — Deploy API on Render

**Option A — Blueprint (recommended)**

1. https://dashboard.render.com/blueprints → **New Blueprint Instance**
2. Connect repo `meenakshi25jan/docs`
3. Blueprint file: `ai-english-teacher/render-backend.yaml` (Docker) or `render.yaml`
4. Set `DATABASE_URL` when prompted
5. Branch: `cursor/cheapest-cloud-deploy-d164`

**Option B — Manual Web Service**

| Setting | Value |
|---------|-------|
| Name | `ai-english-teacher-api` |
| Root Directory | `ai-english-teacher` |
| Runtime | **Docker** |
| Dockerfile | `backend/Dockerfile` |
| Branch | `cursor/cheapest-cloud-deploy-d164` |
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
| Branch | `cursor/cheapest-cloud-deploy-d164` |

**Frontend environment:**

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://ai-english-teacher-api.onrender.com/api/v1` |
| `NODE_VERSION` | `20` |

### Step 5 — Manual deploy (after every code push)

1. Render → **ai-english-teacher-api** → **Manual Deploy** → Deploy latest commit
2. Render → **ai-english-teacher-web** → **Manual Deploy** → Deploy latest commit
3. Wait 3–5 minutes per service

### Alternative — Vercel frontend

| Setting | Value |
|---------|-------|
| Root Directory | `ai-english-teacher/frontend` |
| `NEXT_PUBLIC_API_URL` | `https://ai-english-teacher-api.onrender.com/api/v1` |

Update `CORS_ORIGINS` on API to include your Vercel URL.

---

## 6. Database Migrations

| File | Purpose |
|------|---------|
| `001_initial_schema.sql` | 16 tables, indexes, RLS policies |
| `002_pgvector.sql` | Vector extension tables |
| `003_auth_rls.sql` | Login email lookup policy |
| `004_fix_rls_policies.sql` | Fix RLS uuid cast errors on register |

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
Expected: `{"status":"healthy","version":"1.0.0","database":"configured"}`

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
| `/conversation` | Scenario picker |
| `/assessment` | Assessment page |
| `/dashboard/student` | Student dashboard |

### End-to-end user flow

1. Open `/register` → create account
2. Redirected to `/dashboard/student`
3. Open `/conversation` → pick scenario → Start
4. Open `/assessment` → start placement test

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
| Branch | `cursor/cheapest-cloud-deploy-d164` |

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
| **404 on `/conversation`, `/login`, `/register`** | Stale frontend build | Manual Deploy on `ai-english-teacher-web` with latest commit |
| **Only `/` and `/dashboard/student` work** | Old build before pages were added | Redeploy frontend; build log should list all 8 routes |

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
| **Vercel can't find repo** | Wrong root directory | Set root to `ai-english-teacher/frontend`, branch `cursor/cheapest-cloud-deploy-d164` |

### Docker / Local

| Error | Cause | Fix |
|-------|-------|-----|
| **Port 5432 in use** | Local Postgres running | Stop local Postgres or change port in `docker-compose.yml` |
| **`DATABASE_URL is not set`** | Missing `.env` | Copy `.env.example` to `.env` |
| **Redis connection error** | Redis not running | `docker compose up -d redis` or ignore (optional for MVP) |

---

## 9. Bugs Fixed (Changelog)

All fixes are on branch `cursor/cheapest-cloud-deploy-d164`.

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

---

## 10. Production Checklist

### Before go-live

- [ ] Neon database created with `pgvector` extension
- [ ] All 3 migrations applied (`001`, `002`, `003`)
- [ ] `DATABASE_URL` set on Render API (with `?sslmode=require`)
- [ ] `JWT_SECRET_KEY` set (random, not default)
- [ ] `CORS_ORIGINS` includes your frontend URL
- [ ] `NEXT_PUBLIC_API_URL` set on frontend service
- [ ] Both Render services deployed from `cursor/cheapest-cloud-deploy-d164`
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
| `/conversation` | AI role-play practice |
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
| POST | `/conversations` | Yes | Start role-play |
| POST | `/conversations/{id}/messages` | Yes | Send message |
| POST | `/writing/submit` | Yes | Submit writing |
| GET | `/dashboard/student` | Yes | Student dashboard data |
| GET | `/dashboard/teacher` | Yes | Teacher dashboard data |
| GET | `/dashboard/admin` | Yes | Admin dashboard data |

Full interactive docs: https://ai-english-teacher-api.onrender.com/docs

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

## 15. Voice Practice

Voice is built into the **Conversation** page using the browser Web Speech API (no extra API keys).

### Features (implemented)

| Feature | How |
|---------|-----|
| **Speech-to-text** | 🎤 mic button on `/conversation` |
| **Text-to-speech** | Auto-plays AI replies (toggle "Auto-play voice") |
| **Replay** | "🔊 Play again" on each AI message |
| **Grammar tips** | Shown below AI messages when LLM returns corrections |

### Browser support

| Browser | Voice input | Voice output |
|---------|-------------|--------------|
| Chrome / Edge | ✅ | ✅ |
| Safari | ✅ (limited) | ✅ |
| Firefox | ❌ STT | ✅ TTS |

Use **Chrome or Edge** for full voice practice.

### Future improvements (not yet built)

| Feature | Tool | Priority |
|---------|------|----------|
| Server-side Whisper STT | `faster-whisper` or Ollama whisper | P2 |
| Pronunciation scoring | Azure Speech SDK | P3 |
| Speaking assessment page | New `/speaking` route | P3 |
| Record & replay audio | `MediaRecorder` + blob storage | P3 |

---

## 16. Mobile App (Google Play)

Android app in `mobile/` — built with **Expo React Native**.

| Feature | Screen |
|---------|--------|
| Login / Register | Secure token storage (Keychain) |
| Dashboard | CEFR, IELTS, PTE, skill scores |
| AI Practice | Role-play chat + text-to-speech |
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

## Related docs

| Doc | Path |
|-----|------|
| Cheapest deploy guide | `deploy/cheapest/DEPLOY.md` |
| Render troubleshooting | `deploy/cheapest/RENDER_FIX.md` |
| Neon + Vercel setup | `deploy/cheapest/NEON_VERCEL.md` |
| System architecture | `docs/02-SYSTEM_ARCHITECTURE.md` |
| **Complete architecture (C4 + agents + deploy)** | **`docs/ARCHITECTURE_COMPLETE.md`** |
| API design | `docs/04-API_DESIGN.md` |
| Production readiness | `docs/12-PRODUCTION_READINESS.md` |
| Mobile app + Google Play | `mobile/GOOGLE_PLAY.md` |
| Oracle Cloud VM | `deploy/oracle-cloud/VM_SETUP.md` |

---

*Last updated: branch `cursor/cheapest-cloud-deploy-d164`*
