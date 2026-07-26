# Research Agent

A production-ready **AI Web Crawler and Research Assistant** built with Python 3.12+, FastAPI, Playwright, and ChromaDB. Search the web, crawl pages recursively, extract structured content, generate embeddings, summarize findings with AI, and export reports in multiple formats.

## Documentation

| Guide | Audience | Link |
|-------|----------|------|
| **Universal Playbook** | Any project, any OS — start here | [docs/UNIVERSAL_PROJECT_PLAYBOOK.md](docs/UNIVERSAL_PROJECT_PLAYBOOK.md) |
| **Beginner Playbook** | Non-developers, step-by-step | [docs/BEGINNER_PLAYBOOK.md](docs/BEGINNER_PLAYBOOK.md) |
| Quick Start | Developers | This README |

### OS-aware project advisor (run first)

Detects your operating system and tells you exactly what to install:

| OS | Command |
|----|---------|
| **Linux / Mac** | `./scripts/advise.sh` or `make advise` |
| **Windows** | `powershell -File scripts\advise.ps1` |
| **Any project type** | `./scripts/advise.sh web` / `ai` / `mobile` / `api` / `data` |

### One-command setup

| OS | Command |
|----|---------|
| **Linux** | `chmod +x scripts/setup-linux.sh && ./scripts/setup-linux.sh` |
| **Windows** | `powershell -ExecutionPolicy Bypass -File scripts\setup-windows.ps1` |
| **macOS** | `chmod +x scripts/setup-mac.sh && ./scripts/setup-mac.sh` |

## Features

- **Web Search**: DuckDuckGo (default), Google Custom Search, Bing Search API
- **Async Crawling**: Parallel downloads with rate limiting, retries, and timeout handling
- **robots.txt Compliance**: Respects crawl rules and crawl-delay directives
- **Content Extraction**: Title, meta, headings, paragraphs, lists, tables, images, links, PDFs
- **HTML Cleaning**: Removes ads, navigation, scripts, and boilerplate
- **Language Detection**: Automatic language identification
- **Database Storage**: SQLite (default) or PostgreSQL
- **Vector Search**: ChromaDB + sentence-transformers embeddings
- **AI Summarization**: OpenAI, Ollama, or local LLM support
- **Multi-format Reports**: Markdown, HTML, JSON, PDF
- **REST API**: FastAPI with optional API key authentication
- **CLI**: Command-line interface for batch research
- **Docker**: Containerized deployment with health checks

## Project Structure

```
research-agent/
├── app/
│   ├── crawler/          # Crawling, scraping, parsing, robots.txt
│   ├── search/           # DuckDuckGo, Google, Bing integrations
│   ├── ai/               # Embeddings and summarization
│   ├── database/         # SQLAlchemy models and async DB layer
│   ├── utils/            # Logging and helpers
│   ├── api/              # FastAPI routes
│   ├── reports/          # Report generation
│   └── main.py           # CLI and app entry point
├── tests/                # Unit tests
├── config.py             # Configuration management
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Database Schema

### `crawl_jobs`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| query | VARCHAR(512) | Research query |
| depth | INTEGER | Crawl depth |
| max_pages | INTEGER | Page limit |
| status | VARCHAR(32) | pending/running/completed/failed |
| pages_crawled | INTEGER | Pages successfully crawled |
| confidence_score | FLOAT | AI confidence (0-1) |
| summary | TEXT | Executive summary |
| report_paths | JSON | Paths to generated reports |
| created_at | DATETIME | Job creation time |
| completed_at | DATETIME | Job completion time |

### `pages`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| job_id | INTEGER | Foreign key to crawl_jobs |
| url | VARCHAR(2048) | Page URL |
| title, meta_description | TEXT | Page metadata |
| h1, h2, paragraphs, lists, tables | JSON | Structured content |
| images, links, pdfs | JSON | Media and links |
| visible_text | TEXT | Extracted plain text |
| language | VARCHAR(16) | Detected language |
| content_hash | VARCHAR(64) | Deduplication hash |
| depth | INTEGER | Crawl depth level |

### `search_results`
Stores initial search engine results linked to each job.

## Installation

### Prerequisites

- Python 3.12+
- pip

### Local Setup

```bash
cd research-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Create data directories
mkdir -p data reports logs
```

### Docker

```bash
cd research-agent
cp .env.example .env

# Build and run
docker compose up --build

# With PostgreSQL
docker compose --profile postgres up --build
```

## Configuration

Copy `.env.example` to `.env` and configure:

```env
# Search provider: duckduckgo | google | bing
SEARCH_PROVIDER=duckduckgo

# LLM provider: none | openai | ollama | local
LLM_PROVIDER=none

# Database (SQLite default)
DATABASE_URL=sqlite+aiosqlite:///./data/research_agent.db

# PostgreSQL
# DATABASE_URL=postgresql+asyncpg://research:research@localhost:5432/research_agent

# Crawler tuning
MAX_CONCURRENT_REQUESTS=10
RATE_LIMIT_DELAY=0.5
DEFAULT_DEPTH=2
DEFAULT_MAX_PAGES=100

# Optional API authentication
# API_KEY=your-secret-key
```

## Usage

### CLI

```bash
# Run a research crawl
python -m app.main search \
    --query "Artificial Intelligence" \
    --depth 2 \
    --pages 100

# Start API server
python -m app.main serve --host 0.0.0.0 --port 8000
```

### REST API

#### Health Check

```bash
curl http://localhost:8000/health
```

#### Search and Research

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Artificial Intelligence",
    "depth": 2,
    "max_pages": 100
  }'
```

**Response:**

```json
{
  "status": "completed",
  "job_id": 1,
  "pages": 87,
  "report": "reports/artificial-intelligence_1_20260726_010000.md",
  "reports": {
    "markdown": "reports/...",
    "html": "reports/...",
    "json": "reports/...",
    "pdf": "reports/..."
  },
  "confidence_score": 0.72
}
```

#### Job Status

```bash
curl http://localhost:8000/jobs/1
```

#### Semantic Search

```bash
curl -X POST http://localhost:8000/semantic-search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning trends", "job_id": 1, "n_results": 10}'
```

### With API Key

```bash
curl -X POST http://localhost:8000/search \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "Climate Change", "depth": 1, "max_pages": 50}'
```

## Report Format

Generated reports include:

1. **Executive Summary** — High-level overview
2. **Findings** — Key discoveries with citations
3. **Timeline** — Chronological events (when applicable)
4. **Key Facts** — Important factual statements
5. **Statistics** — Numeric data points
6. **References** — Cited sources
7. **Source URLs** — All crawled URLs
8. **Confidence Score** — 0.0–1.0 reliability rating

## Crawler Pipeline

```
User Query → Search Engine → Collect URLs → Validate & Deduplicate
    → robots.txt Check → Download HTML → Parse & Clean
    → Extract Content → Follow Links (recursive) → Store in DB
    → Generate Embeddings → AI Summary → Export Reports
```

## Performance Optimizations

- **Async I/O**: aiohttp for concurrent HTTP requests
- **Semaphore-based concurrency**: Configurable parallel request limits
- **Domain rate limiting**: Per-domain delays with robots.txt crawl-delay support
- **Content deduplication**: SHA-256 hashing prevents reprocessing identical pages
- **Connection pooling**: Reused aiohttp sessions and TCP connectors
- **Chunked embeddings**: Text split into overlapping chunks for efficient vector indexing
- **ChromaDB persistence**: On-disk vector storage for semantic search at scale
- **Playwright fallback**: Only used when static HTML fetch is insufficient
- **Bounded content size**: Configurable max download size prevents memory exhaustion

## Testing

```bash
cd research-agent
pip install -r requirements.txt
pytest -v
```

## Scaling Notes

For crawling thousands of pages:

- Increase `MAX_CONCURRENT_REQUESTS` gradually (monitor target server load)
- Use PostgreSQL instead of SQLite for concurrent writes
- Set `RATE_LIMIT_DELAY` appropriately per target domain
- Run multiple workers behind a job queue for horizontal scaling
- Pre-warm the embedding model to avoid cold-start latency

## License

MIT
