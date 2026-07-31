# Production status report — AI English Teacher API

**Last verified:** 2026-07-31 (Cloud Agent full audit)  
**Git `main`:** `3f99de7a217496e82cba98a15b68ef8415aefc6e`  
**Production web Next build ID:** `WjWnTF_iSLNiPaqsi9n8e` (stale — local build `U7i-UliQJEDrSOV4TeA_s`)

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
| CI `validate-config` | ❌ Failed — `008` missing from `check_migrations.py` (PR #42) |
| Deploy workflow | ⏭ Skipped — CI failure blocks `workflow_run` trigger |

**Conclusion:** Backend is production-ready on Render. Remaining gap is **web** redeploy with clear build cache for `/grammar-class`.

---

## Startup flow

```text
Render bash ./start.sh
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
| Web `/grammar-class` 404 | `render.yaml` now runs `rm -rf .next` before build; still redeploy web + clear cache |
| Stale `build-info.json` on prod | Same web redeploy; `write-build-info.js` now fails build if metadata incomplete |
| CI blocked on migration 008 | PR #42 — merge to restore `validate-config` |

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

---

## Final deployment checklist (2026-07-31)

| Component | Status |
|-----------|--------|
| Latest commit deployed (web) | ❌ `3f99de7a2` not deployed — build `WjWnTF_iSLNiPaqsi9n8e` |
| Latest commit deployed (API) | ✅ APIs healthy; migrations applied |
| Build cache cleared | ❌ Manual Render action; `rm -rf .next` added to blueprint buildCommand |
| `build-info.json` validation | ✅ `write-build-info.js` exits 1 on missing fields (verified) |
| Route manifest verified (local) | ✅ `/grammar-class` in manifest |
| Standalone build verified (local) | ✅ `grammar-class.html` present |
| `build-info.json` verified (local) | ✅ commit, routes, nextBuildId, builtAt |
| `build-info.json` (production) | ❌ 404 |
| `/grammar-class` | ❌ HTTP 404 |
| Backend health | ✅ HTTP 200 |
| Metrics | ✅ HTTP 307 → Prometheus |
| Database migrations | ✅ 001–008 (via API smoke) |
| SQL verification (direct) | ⏭ No `DATABASE_URL` in agent env |
| CI pipeline | ❌ `validate-config` until PR #42 merges |
