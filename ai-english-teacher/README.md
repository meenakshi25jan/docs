# AI English Teacher Platform

A production-ready, cloud-native AI-powered English learning platform supporting IELTS, PTE, TOEFL, and Corporate English training.

## Architecture

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS |
| Mobile | Expo React Native (Android) |
| Backend | FastAPI (Python 3.12), LangGraph orchestration |
| Database | PostgreSQL 16 + pgvector (Neon) |
| Cache | Redis 7 (optional, Oracle VM) |
| AI | Groq / Azure OpenAI / Ollama (provider abstraction) |
| Speech | Groq Whisper + browser Web Speech API |
| Auth | JWT, OAuth2 (Google, Microsoft) |
| Deployment | Render + Neon ($0), Oracle Cloud VM, Fly.io, Azure AKS |

**Full architecture (C4 diagrams, agent flows, deployment plans):** **[docs/ARCHITECTURE_COMPLETE.md](docs/ARCHITECTURE_COMPLETE.md)**

## Quick Start

> **Full guide:** See **[RUNBOOK.md](RUNBOOK.md)** — prerequisites, local setup, cloud deploy, all errors & fixes in one place.

### Prerequisites

- Docker & Docker Compose
- Node.js 20+
- Python 3.12+
- PostgreSQL 16 (or use Docker Compose)

### Local Development

```bash
# Start infrastructure
docker compose up -d postgres redis

# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/ai_english_teacher" \
  python3 scripts/migrate.py
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open http://localhost:3000 (frontend) and http://localhost:8000/docs (API).

### Full Stack with Docker

```bash
docker compose up --build
```

### Cheapest Cloud Deploy ($0/month)

See **[RUNBOOK.md §5](RUNBOOK.md#5-cloud-deployment-0month)** for the complete step-by-step guide.

```bash
# Quick reference
cat RUNBOOK.md
./deploy/cheapest/deploy.sh   # interactive helper
```

**One-click:** Connect this repo to [Render Blueprints](https://dashboard.render.com/blueprints) — it reads `render.yaml` automatically. Set `DATABASE_URL` from a free [Neon](https://neon.tech) project.

| Component | Provider | Cost |
|-----------|----------|------|
| PostgreSQL | Neon | $0 |
| Backend API | Render free tier | $0 |
| Frontend | Vercel or Render | $0 |
| **Total** | | **$0/month** |

## Project Structure

```
ai-english-teacher/
├── docs/                    # Architecture & design documents
├── database/                # SQL migrations & seeds
├── backend/                 # FastAPI microservices
│   └── app/
│       ├── agents/          # AI agent implementations
│       ├── api/             # REST route handlers
│       ├── core/            # Config, security, dependencies
│       ├── models/          # SQLAlchemy ORM models
│       ├── schemas/         # Pydantic request/response schemas
│       ├── services/        # Business logic layer
│       └── scoring/         # AI scoring engine
├── frontend/                # Next.js application
├── infrastructure/          # Terraform IaC
├── k8s/                     # Kubernetes manifests
└── .github/workflows/       # CI/CD pipelines
```

## Documentation

| # | Document | Path |
|---|----------|------|
| **Runbook** | **Prerequisites, deploy, all errors & fixes** | **[RUNBOOK.md](RUNBOOK.md)** |
| 1 | Product Requirements | [docs/01-PRODUCT_REQUIREMENTS.md](docs/01-PRODUCT_REQUIREMENTS.md) |
| 2 | System Architecture | [docs/02-SYSTEM_ARCHITECTURE.md](docs/02-SYSTEM_ARCHITECTURE.md) |
| 3 | Database Design | [docs/03-DATABASE_DESIGN.md](docs/03-DATABASE_DESIGN.md) |
| 4 | API Design | [docs/04-API_DESIGN.md](docs/04-API_DESIGN.md) |
| 7 | AI Agent Design | [docs/07-AI_AGENT_DESIGN.md](docs/07-AI_AGENT_DESIGN.md) |
| 8 | Deployment Architecture | [docs/08-DEPLOYMENT_ARCHITECTURE.md](docs/08-DEPLOYMENT_ARCHITECTURE.md) |
| 10 | Testing Strategy | [docs/10-TESTING_STRATEGY.md](docs/10-TESTING_STRATEGY.md) |
| 11 | Cost Estimation | [docs/11-COST_ESTIMATION.md](docs/11-COST_ESTIMATION.md) |
| 12 | Production Readiness | [docs/12-PRODUCTION_READINESS.md](docs/12-PRODUCTION_READINESS.md) |

## License

MIT
