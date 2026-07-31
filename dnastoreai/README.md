# DNAStoreAI

**AI-Assisted DNA Data Storage and Retrieval Research Platform**

A research-grade, end-to-end DNA storage simulator for publication-level experimentation and future integration with real DNA synthesis and sequencing hardware.

## Features

- **Full Pipeline**: File → Compression → Segmentation → ECC → DNA Encoding → Optimization → Synthesis → Archive → Degradation → Sequencing → Reconstruction
- **12 Modular Components**: Compression, Segmentation, Metadata, ECC, Encoding, Optimization, Synthesis, Degradation, Sequencing, Reconstruction, AI Reconstruction, Semantic Archive
- **Multiple Algorithms**: 4 encoding schemes, 4 ECC strategies, 3 sequencing platforms, 3 compression methods
- **Research Framework**: Experiment runner with CSV/JSON/HTML reports
- **REST API**: FastAPI with full OpenAPI documentation
- **Dashboard**: React + TypeScript + Material UI with visual analytics
- **Containerized**: Docker Compose with PostgreSQL support
- **90%+ Test Coverage**: Unit, integration, and end-to-end tests

## Quick Start

### Docker (Recommended)

```bash
cd dnastoreai
docker compose up --build
```

- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development

**Backend:**

```bash
cd dnastoreai/backend
pip install -e ".[dev]"
uvicorn dnastoreai.main:app --reload --port 8000
```

**Frontend:**

```bash
cd dnastoreai/frontend
npm install
npm run dev
```

## Architecture

```
┌─────────────┐     ┌──────────────────────────────────────────────────┐
│   React UI  │────▶│              FastAPI REST API                     │
└─────────────┘     └──────────────────────┬───────────────────────────┘
                                             │
                    ┌────────────────────────▼───────────────────────────┐
                    │              Pipeline Service                       │
                    └────────────────────────┬───────────────────────────┘
                                             │
     ┌───────────┬───────────┬───────────┬───┴───┬───────────┬───────────┐
     │           │           │           │       │           │           │
┌────▼───┐ ┌────▼───┐ ┌────▼───┐ ┌────▼───┐ ┌─▼──┐ ┌────▼───┐ ┌────▼───┐
│Compress│ │Segment │ │  ECC   │ │ Encode │ │Opt │ │Synthesis│ │Degrade │
└────────┘ └────────┘ └────────┘ └────────┘ └────┘ └────────┘ └────────┘
                                             │
                    ┌────────────────────────▼───────────────────────────┐
                    │  Sequencing → Reconstruction → File Recovery        │
                    └────────────────────────────────────────────────────┘
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/store` | Encode and store a file |
| POST | `/api/v1/retrieve` | Recover a file from archive |
| POST | `/api/v1/simulate` | Run synthesis/degradation/sequencing simulation |
| POST | `/api/v1/experiment` | Run a research experiment |
| GET | `/api/v1/metrics` | Platform metrics |
| GET | `/api/v1/archive` | List all archives |
| GET | `/api/v1/dna/{id}` | Get DNA sequence |

## Supported File Types

txt, pdf, csv, json, xml, docx, pptx, jpg, png, wav, mp4, zip

## Running Tests

```bash
cd dnastoreai/backend
pytest tests/ -v --cov=dnastoreai --cov-fail-under=90
```

## Running Experiments

```bash
cd dnastoreai/backend
python examples/run_experiment.py
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Research Design](docs/RESEARCH_DESIGN.md)
- [Experimental Methodology](docs/EXPERIMENTAL_METHODOLOGY.md)
- [Future AI Roadmap](docs/AI_ROADMAP.md)

## License

MIT
