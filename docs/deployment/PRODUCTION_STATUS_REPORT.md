# Production status report — AI English Teacher API

**Last verified:** 2026-07-31  
**Stack:** FastAPI on Render, Neon PostgreSQL, SQL migrations via `scripts/migrate.py`

---

## Executive summary

| Area | Status |
|------|--------|
| API deploy & startup | ✅ Live |
| SQL migrations 001–008 | ✅ Applied (fixes merged to `main`) |
| Import bootstrap (`app` package) | ✅ `bootstrap_path.py` + `PYTHONPATH` |
| `/health`, `/health/live`, `/health/ready` | ✅ 200 |
| `/docs`, `/openapi.json` | ✅ 200 |
| `/metrics` | ✅ Prometheus text |
| DB APIs (student-intelligence, analytics) | ✅ 200 with auth |
| Web `/grammar-class` | ❌ 404 — stale frontend build (not API) |

**Conclusion:** Backend is production-ready on Render. Remaining gap is **web** redeploy with clear build cache for `/grammar-class`.

---

## Startup flow

```text
Render ./start.sh
  → cd backend, export PYTHONPATH
  → validate DATABASE_URL, SKIP_MIGRATIONS=false
  → python -m scripts.migrate (transactional SQL 001–008)
  → python -m scripts.verify_migrations_applied
  → uvicorn app.main:app
  → /health, /metrics, /api/v1/*
```

---

## Migration files (order)

| File | Creates / fixes |
|------|-----------------|
| 001_initial_schema.sql | users, learner_profiles, conversations, conversation_messages |
| 002_pgvector.sql | vector extension |
| 003_auth_rls.sql | RLS |
| 004_fix_rls_policies.sql | RLS fixes |
| 005_knowledge_and_voice.sql | voice_analyses, knowledge_chunks (+ seed fix) |
| 006_curriculum_intelligence.sql | lesson_completions, revision_schedule |
| 007_security_rls_hardening.sql | security hardening |
| 008_fix_knowledge_chunks_seed.sql | repair NULL topic seed rows |

**Note:** No `curriculum` or `conversation_history` tables — use `lesson_completions` / `revision_schedule` and `conversations` / `conversation_messages`.

---

## Root causes (resolved)

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: app` | `bootstrap_path.py`, `python -m scripts.migrate`, `PYTHONPATH` |
| `SKIP_MIGRATIONS=true` | `render.yaml` false + remove dashboard override |
| knowledge_chunks NULL topic | Fixed 005 VALUES + migration 008 |
| `/metrics` 404 | `prometheus-client` in `requirements-render.txt` |

---

## API verification (production)

```bash
python3 ai-english-teacher/scripts/post_deploy_verify.py
```

Or manually:

| Endpoint | Expected |
|----------|----------|
| GET /health | 200 |
| GET /health/live | 200 |
| GET /health/ready | 200 |
| GET /metrics | 200, `# HELP` |
| GET /api/v1/grammar/grades | 200 |
| POST /api/v1/auth/register | 201 |
| GET /api/v1/student-intelligence/summary | 200 (Bearer) |
| GET /api/v1/analytics/overview | 200 (Bearer) |

---

## Remaining risks

| Risk | Mitigation |
|------|------------|
| Web `/grammar-class` 404 | Redeploy web + clear build cache |
| Render env overrides | Audit API Environment tab |
| Neon connection limits | Pool settings in `render.yaml` |

---

## Key files

| File | Role |
|------|------|
| `render.yaml` | Blueprint |
| `backend/start.sh` | Migrations + uvicorn |
| `backend/scripts/migrate.py` | SQL runner |
| `backend/scripts/bootstrap_path.py` | Import path |
| `backend/scripts/verify_migrations_applied.py` | Table + migration check |
| `scripts/post_deploy_verify.py` | End-to-end smoke |
