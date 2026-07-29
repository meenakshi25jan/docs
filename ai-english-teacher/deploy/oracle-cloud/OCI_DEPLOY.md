# Oracle Cloud (OCI) Deployment Guide

Deploy the AI English Teacher platform on **Oracle Cloud Infrastructure Always Free** — $0/month.

| Component | Where it runs |
|-----------|---------------|
| Frontend (Next.js) | OCI VM (Docker) |
| Backend (FastAPI + LangGraph) | OCI VM (Docker) |
| Redis (sessions) | OCI VM (Docker) |
| AI (Groq or Ollama) | Groq cloud (recommended) or OCI VM (optional) |
| PostgreSQL | [Neon](https://neon.tech) free tier |

**Create VM (Mumbai / India West):**  
https://cloud.oracle.com/compute/instances/create?region=ap-mumbai-1

**Click-by-click wizard:** [VM_SETUP.md](VM_SETUP.md)

---

## Why Oracle Cloud?

- **2 OCPU + 12 GB RAM** free (Ampere A1, 2026 Always Free limit)
- No 15-minute sleep like Render free tier
- Web + mobile + API on one VM
- Debit card accepted for signup verification

---

## Quick Start

### Step 1 — Create VM

Open: https://cloud.oracle.com/compute/instances/create?region=ap-mumbai-1

| Setting | Recommended (~50 users) | With local Ollama |
|---------|-------------------------|-------------------|
| Image | Ubuntu 24.04 **Minimal aarch64** | Same |
| Shape | A1.Flex **1 OCPU / 6 GB** | A1.Flex **2 OCPU / 12 GB** |
| Network | Create new VCN + **public subnet** | Same |
| Public IPv4 | **ON** | Same |
| Boot volume | 50 GB | Same |

> ⚠️ Do **not** use `VM.Standard.E2.1.Micro` (1 GB RAM).

Open **Security List** ingress: TCP **80**, **443**, **22**.

Full wizard: [VM_SETUP.md](VM_SETUP.md)

### Step 2 — Neon database

1. https://neon.tech → project `ai-english-teacher`
2. SQL: `CREATE EXTENSION IF NOT EXISTS vector;`
3. Copy `DATABASE_URL` with `?sslmode=require`

### Step 3 — Groq API key (recommended)

1. https://console.groq.com → Create API key (`gsk_...`)

### Step 4 — Deploy on VM

```bash
ssh -i ~/.ssh/oci_key ubuntu@YOUR_VM_PUBLIC_IP

curl -fsSL https://raw.githubusercontent.com/meenakshi25jan/docs/main/ai-english-teacher/deploy/oracle-cloud/setup-vm.sh | bash
```

Edit `.env` when prompted:

```bash
nano ~/docs/ai-english-teacher/deploy/oracle-cloud/.env
```

Minimum (Groq — recommended):

```env
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require
PUBLIC_URL=http://YOUR_VM_PUBLIC_IP
AI_PROVIDER=openai
OPENAI_API_KEY=gsk_your_groq_key
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.1-8b-instant
```

Re-run setup or start manually:

```bash
cd ~/docs/ai-english-teacher/deploy/oracle-cloud
docker compose -f docker-compose.oracle.yml --env-file .env up -d --build
```

**Browser:** `http://YOUR_VM_PUBLIC_IP/register`

---

## Manual deploy

```bash
git clone --branch main https://github.com/meenakshi25jan/docs.git
cd docs/ai-english-teacher/deploy/oracle-cloud
cp .env.example .env
nano .env
docker compose -f docker-compose.oracle.yml --env-file .env up -d --build
```

### Ollama (optional, 2 OCPU / 12 GB only)

```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2
```

```bash
docker compose -f docker-compose.oracle.yml --env-file .env --profile ollama up -d --build
docker compose -f docker-compose.oracle.yml exec ollama ollama pull llama3.2
```

---

## Architecture

```
Internet → port 80
┌─────────────────────────────────────┐
│  OCI VM (Ampere A1, Mumbai)         │
│  nginx → frontend :3000             │
│       → backend  :8000              │
│  redis :6379                        │
│  ollama :11434 (optional)           │
└─────────────────────────────────────┘
       ↓
  Neon PostgreSQL (free)
  Groq API (free, recommended)
```

---

## Environment variables

| Variable | Required | Example |
|----------|----------|---------|
| `DATABASE_URL` | Yes | Neon URL + `?sslmode=require` |
| `JWT_SECRET_KEY` | Yes | `openssl rand -hex 32` |
| `PUBLIC_URL` | Yes | `http://123.45.67.89` |
| `AI_PROVIDER` | No | `openai` (Groq), `ollama`, `copilot`, `mock` |
| `OPENAI_API_KEY` | If Groq | `gsk_...` |
| `OPENAI_BASE_URL` | If Groq | `https://api.groq.com/openai/v1` |

---

## Useful commands

```bash
cd ~/docs/ai-english-teacher/deploy/oracle-cloud

docker compose -f docker-compose.oracle.yml logs -f
docker compose -f docker-compose.oracle.yml --env-file .env up -d --build
docker compose -f docker-compose.oracle.yml down
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| VCN dropdown empty | **Create new virtual cloud network** |
| Public IPv4 won't enable | Use **public subnet** |
| Out of capacity | Another availability domain; retry later |
| Browser can't connect | Open ports 80/443 in Security List |
| Mock AI replies | Set Groq key; `AI_PROVIDER=openai` |
| CORS error | `PUBLIC_URL` must match browser URL |

---

## Resource recommendations (Always Free 2026)

| Workload | OCPU | RAM | AI |
|----------|------|-----|-----|
| ~50 users (recommended) | 1 | 6 GB | Groq |
| App + Ollama | 2 | 12 GB | Ollama local |
| Max free tier | 2 | 12 GB | Groq or Ollama |

---

## Related docs

- [VM_SETUP.md](VM_SETUP.md) — full Mumbai wizard (all 4 steps)
- [FULL_STACK_DEPLOY.md](FULL_STACK_DEPLOY.md) — web + mobile
- [RUNBOOK.md](../../RUNBOOK.md) — errors and API reference
