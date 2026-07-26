# AI English Teacher Platform

A production-ready, cloud-native AI-powered English learning platform supporting IELTS, PTE, TOEFL, and Corporate English training.

## Architecture

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS, ShadCN UI |
| Backend | FastAPI (Python 3.12), async architecture |
| Database | PostgreSQL 16 + pgvector |
| Cache | Redis 7 |
| AI | Azure OpenAI GPT-5.5 (with OpenAI abstraction layer) |
| Speech | Azure Speech Services + Whisper |
| Auth | JWT, OAuth2 (Google, Microsoft) |
| Deployment | Docker, Kubernetes (AKS/EKS), Terraform |
| Monitoring | Application Insights, Prometheus, Grafana |
| CI/CD | GitHub Actions |

## Quick Start

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
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
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
