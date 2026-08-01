# AI English Teacher — Project Status (Single Source of Truth)

**Last audited:** 2026-08-01  
**Auditor:** Repository inspection + local verification (no feature code changes)  
**Branch inspected:** `cursor/knowledge-ingestion-37c0` @ `b69ee72c7`  
**Backend root:** `ai-english-teacher/backend/`  
**Frontend root:** `ai-english-teacher/frontend/`

> **Maintenance rule:** Future work sessions MUST update this file when a phase advances. Do not track phase numbering in separate chat threads, READMEs, or ad-hoc docs — update the table below and the Verification Log.

---

## Phase Summary

| Phase | Name | Status | Evidence | What's Missing (if partial) |
|-------|------|--------|----------|----------------------------|
| **1** | Backend Foundation | **COMPLETE** | FastAPI app (`app/main.py`); routers for health, auth (`/register`, `/login`, `/logout`, `/refresh`), users (`/users/me`), conversation; Alembic `001`–`002`; JWT + Argon2 (`app/core/security.py`, `app/services/auth_service.py`); health endpoints `/health`, `/health/live`, `/health/ready`, `/home`, `/build-info`. Verified: `pytest app/tests/test_auth.py` (3 passed); local ASGI hits return HTTP 200 for all health routes. | — |
| **2** | Core Domain Schema | **COMPLETE** | ORM models + migrations `003`–`015`: `user_profile`, `conversation_session`, `conversation_message`, `grammar_feedback` (extended), `band_score`, `learning_plan`, `user_progress`, `user_mistake_memory`, `lesson_knowledge`, `knowledge_embedding` (pgvector HNSW, 384-dim), `voice_settings`. `pgvector` extension via `013_enable_vector`. Seed script `scripts/seed_db.py`; ER diagram `docs/database/er-diagram.md`. Verified: `alembic heads` → `019_kb_embed_chunk_type`; Alembic round-trip `015→019` on local Postgres; `pytest app/tests/test_integration_db.py` (2 passed). | Gamification tables (`achievement`, `user_achievement`) intentionally deferred (documented in `app/db/models/__init__.py`). |
| **3** | Knowledge Ingestion Schema + Pipeline | **PARTIAL** | Models + migrations `016`–`018`: `knowledge_source`, `knowledge_document`, `knowledge_chunk`. Ingestors: PDF/DOCX/txt/manual (`pdf_ingestor.py`), website + robots.txt (`website_ingestor.py`), image/OCR (`image_ingestor.py`). Chunker (`chunker.py`); orchestrator (`ingestion_orchestrator.py`) with delete-and-recreate re-ingestion, license guardrail (`license_type` required before `completed`), failure → `failed` + `error_message`. Verified: `pytest` ingestion suite (11 tests across chunker, pdf, website, image, orchestrator — all passed). | **No video ingestor** (`SourceType` has no `video`; no `video_ingestor.py`). **No HTTP/API route** to trigger ingestion — orchestrator is library-only (README example). **Not registered in FastAPI** (`app/main.py` has no ingestion router). Embeddings only when caller passes `embed_fn` (Phase 4 dependency). |
| **4** | Embedding Pipeline | **PARTIAL** | Orchestrator accepts pluggable `embed_fn` and persists to `knowledge_embedding` when provided (`_persist_embeddings` with batch flush every 25 chunks). Config `EMBEDDING_DIMENSION=384`. Verified: orchestrator tests use stub embed fn and assert rows written. | **No production embedding service** — no `embedding_pipeline.py`, no `sentence-transformers` (or other model) in `requirements.txt`. **Not wired into app startup or ingestion by default.** **Per-chunk failure handling not implemented** — any embed exception fails the entire ingestion job (see `test_orchestrator_failure_sets_failed_status`). No batch job/CLI for backfill. |
| **5** | Cognitive Retriever | **NOT STARTED** | Design docs only (`docs/14-COGNITIVE_ORCHESTRATION_LAYER.md`, `RUNBOOK.md` references `app/cognitive/`). | **`app/retrieval/` does not exist.** No code combining `knowledge_embedding` vector search with `user_mistake_memory`, `grammar_feedback`, or `user_progress`. No structured context builder. |
| **6** | CI/CD Pipeline | **PARTIAL** | `.github/workflows/ci.yml`: lint (flake8/black/isort), mypy, unit tests, integration tests (Postgres+pgvector), migration round-trip, pip-audit + gitleaks, Docker build, `ci-success` gate. `.github/workflows/deploy.yml`: gated on green CI on `main` via `workflow_run`; GHCR push; Neon `alembic upgrade head`; Render + Vercel deploy; commit-SHA poll (`wait_for_deploy_commit.py`); health checks; smoke tests; rollback (`rollback_deploy.py`). `Dockerfile` with `HEALTHCHECK` on `/health/live` and `BUILD_COMMIT_SHA` arg. Verified locally: flake8 0 errors; mypy success; full `pytest` 24 passed / 2 skipped; Alembic round-trip OK; frontend `npm run build` OK. | **CI unit-tests job only runs `test_auth.py` + `test_conversation.py`** — ingestion tests (11) not in CI gate. **Live production not verified in this audit:** `curl https://ai-english-teacher-api.onrender.com/health/live` → HTTP 503 (cold start, down, or misconfigured). Deploy workflow requires secrets (`DATABASE_URL`, `RENDER_DEPLOY_HOOK`, etc.) not available here. Smoke tests skip without `SMOKE_BASE_URL`. |
| **7** | Multi-Agent Orchestration + Grok | **PARTIAL** | `GrokService` makes real HTTP calls to xAI (`app/services/grok_service.py`). `OrchestratorAgent` dispatches `grammar` → `GrammarAgent`, `conversation` → `ConversationAgent` (`app/agents/`). Wired into `/conversation`, `/grammar-check`, `/audio-conversation`. Verified: `pytest app/tests/test_conversation.py` (5 passed) with **mocked** orchestrator (Grok not called in CI). | **No guardrail agent.** **No prompt construction from cognitive retriever** (Phase 5 missing). Orchestrator is a simple mode switch, not multi-agent coordination. Grok integration **not verified end-to-end** without `XAI_API_KEY` (not set in audit env). |
| **8** | Specialized Agents | **PARTIAL** | `GrammarAgent` (JSON-structured correction via Grok). `ConversationAgent` (conversational Grok prompt). `FeedbackService` persists grammar results to DB. `/band-score` returns heuristic CEFR/IELTS mapping from grammar score. | **Missing agents:** Pronunciation, dedicated Feedback, Assessment (only enum value `pronunciation` exists; no agent class). No agent registry, no LangGraph/cognitive layer despite RUNBOOK claims. |
| **9** | Voice System | **PARTIAL** | `STTService` — OpenAI Whisper API (`app/services/stt_service.py`). `TTSService` — Edge TTS with male/female via `user.teacher_voice` / config (`TTS_VOICE_MALE`, `TTS_VOICE_FEMALE`). `/audio-conversation` chains STT → orchestrator → TTS. `voice_settings` table exists. Verified: conversation tests mock STT/TTS; TTS not exercised against live Edge API in tests. | **No Pronunciation Agent.** STT requires `OPENAI_API_KEY` (not verified). **No video→transcript pipeline** (video ingestor absent). Frontend voice APIs (`/voice/personas`, `/voice/turn`) **not implemented on backend**. |
| **10** | Gamification | **NOT STARTED** | `user_progress.streak_days` column only (Phase 2 schema). | No `achievement` / `user_achievement` tables. No XP, levels, or badges logic. Explicitly deferred in `app/db/models/__init__.py`. |
| **11** | Frontend | **PARTIAL** | Next.js 15 app (`ai-english-teacher/frontend/`): pages for login, register, dashboard (student/teacher/admin), conversation, grammar-class, assessment. Standalone build succeeds. Verified: `npm run build` + `postbuild` route verification passed. | **Major API contract mismatch with backend:** frontend calls `/api/v1/*` (auth, curriculum, knowledge, voice, dashboards, etc.) but backend exposes unversioned routes (`/register`, `/login`, `/conversation`). `next.config.js` proxies `/api/v1` → Render `/api/v1/*` which **does not exist** on current backend. Login expects `res.tokens.access_token`; backend returns top-level `access_token`. Register sends `first_name`/`last_name`; backend expects `name`. **Frontend is not wired to current backend without an API gateway or refactor.** |
| **12** | Observability | **PARTIAL** | Structured JSON logging (`app/core/logging.py`). Prometheus `/metrics` (`app/core/metrics.py` + middleware). Optional Sentry (`SENTRY_DSN` in lifespan). `/build-info` + commit SHA in health responses (`app/core/build_info.py`). K8s scrape annotations in `k8s/base/deployment.yaml`. Verified: local `/metrics` returns Prometheus text; `/build-info` returns JSON. | **No Grafana, Loki, or Prometheus server configs** in repo (only client library + k8s annotations). Sentry not verified (no DSN in audit env). No distributed tracing. |

---

## Inconsistencies Found

1. **Frontend ↔ backend API drift (critical):** `frontend/src/lib/api.ts` defines 50+ `/api/v1/*` endpoints; backend has ~10 unversioned routes. Auth path, payload shapes, and response shapes differ (e.g. `tokens.access_token` vs `access_token`).

2. **Documentation overstates implementation:** `RUNBOOK.md`, `docs/14-COGNITIVE_ORCHESTRATION_LAYER.md`, and `docs/agents/*` describe `app/cognitive/`, guardrails, Knowledge Intelligence, LangGraph routing, and 40+ agents — **none of this exists in `app/`**.

3. **CI coverage gap:** `ci.yml` `unit-tests` job runs only `test_auth.py` and `test_conversation.py`. Eleven ingestion tests pass locally but are **not** in the CI gate (integration job only runs `test_integration_db.py`).

4. **Revision ID naming drift:** Migration file `019_knowledge_embedding_knowledge_chunk.py` has `revision = "019_kb_embed_chunk_type"` (short ID) — functional but inconsistent with `016_knowledge_source` style.

5. **Dual deployment targets:** Render/Vercel workflows in `.github/workflows/deploy.yml` vs Azure AKS manifests in `k8s/base/deployment.yaml` with different image registries and API URLs — unclear which is production source of truth.

6. **Embedding table created before ingestion tables:** `knowledge_embedding` (migration `014`, Phase 2) predates `knowledge_chunk` (migration `018`, Phase 3). `019` adds only a column comment — no FK between embedding rows and chunk rows at DB level (polymorphic `knowledge_id` only).

7. **`band_score` endpoint is not a real assessment agent:** `/band-score` applies a static score→CEFR lookup on grammar output; no persistence to `band_score` table from this route.

8. **Render free-tier note vs full requirements:** `RUNBOOK.md` mentions slim `requirements-render.txt` without prometheus; production `requirements.txt` includes `prometheus-client`.

---

## Recommended Next Phase

### **Phase 4 — Embedding Pipeline**

**Reasoning (dependency order):**

1. Phase 3 ingestion persists `knowledge_chunk` rows but leaves `knowledge_embedding` empty unless a caller supplies `embed_fn` — there is no production embedder.
2. Phase 5 (Cognitive Retriever) requires searchable vectors in `knowledge_embedding` plus student memory tables — it cannot be built or tested without real embeddings.
3. Phase 7+ prompt construction from retrieved context depends on Phase 5, which depends on Phase 4.

**Minimum scope for Phase 4:**

- Add a real embedding provider (e.g. `sentence-transformers/all-MiniLM-L6-v2` matching 384-dim schema).
- Implement `app/embedding/` (or similar) with batch encoding and per-chunk error handling (skip/retry failed chunks without failing entire source).
- Wire `embed_fn` into `IngestionOrchestrator` by default (config-driven).
- Add CLI or admin API to backfill embeddings for existing chunks.
- Extend CI unit-tests job to include ingestion + embedding tests.

**Do not start Phase 5 or expand frontend API surface until Phase 4 is verified with integration tests against Postgres + pgvector.**

---

## Verification Log

Commands run during this audit (2026-08-01, UTC). Outputs are verbatim unless truncated.

### Git context

```text
$ git branch --show-current
cursor/project-status-audit-37c0  # branched from cursor/knowledge-ingestion-37c0 @ b69ee72c7

$ git log -1 --oneline
b69ee72c7 fix(deps): upgrade ingestion packages for pip-audit CI gate
```

### Full test suite

```text
$ cd ai-english-teacher/backend
$ export JWT_SECRET=audit-test-secret DATABASE_URL="sqlite+aiosqlite:///:memory:"
$ pytest app/tests -v --tb=no -q

======================== 24 passed, 2 skipped in 1.27s =========================
# Skipped: app/tests/test_smoke.py (SMOKE_BASE_URL not set)
```

### Lint and type check

```text
$ flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics
0

$ mypy app
Success: no issues found in 56 source files
```

### Alembic

```text
$ alembic heads
019_kb_embed_chunk_type (head)

$ # Round-trip on local Postgres (pgvector extension present)
$ export JWT_SECRET=audit-migration-secret
$ export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/migration_db
$ bash ai-english-teacher/scripts/ci_migration_roundtrip.sh

==> alembic upgrade head
INFO  [alembic.runtime.migration] Running upgrade 015_voice_settings -> 016_knowledge_source, knowledge_source table
INFO  [alembic.runtime.migration] Running upgrade 016_knowledge_source -> 017_knowledge_document, knowledge_document table
INFO  [alembic.runtime.migration] Running upgrade 017_knowledge_document -> 018_knowledge_chunk, knowledge_chunk table
INFO  [alembic.runtime.migration] Running upgrade 018_knowledge_chunk -> 019_kb_embed_chunk_type, document knowledge_chunk as valid knowledge_embedding.knowledge_type
==> alembic downgrade -1
INFO  [alembic.runtime.migration] Running downgrade 019_kb_embed_chunk_type -> 018_knowledge_chunk, ...
==> alembic upgrade head (again)
OK: migration round-trip succeeded
```

### Local health / metrics (ASGI, in-memory SQLite)

```text
$ python -c "..."  # httpx AsyncClient against app.main:app

/ -> HTTP 200
/health/live -> HTTP 200 | {"status":"alive","app":"AI English Teacher",...}
/health -> HTTP 200 | {"status":"healthy","database":"reachable",...}
/health/ready -> HTTP 200 | {"status":"ready","database":"reachable",...}
/build-info -> HTTP 200 | {"commit":"unknown","builtAt":"...","service":"ai-english-teacher-api"}
/metrics -> HTTP 200 | # HELP python_gc_objects_collected_total ...
```

### Frontend build

```text
$ cd ai-english-teacher/frontend && npm ci && npm run build

Route (app): /, /login, /register, /conversation, /grammar-class, /assessment,
  /dashboard/student, /dashboard/teacher, /dashboard/admin
postbuild OK — 9 routes verified in standalone output
```

### Live production probe (not verified healthy)

```text
$ curl -s -o /dev/null -w "HTTP %{http_code}\n" --max-time 15 \
    https://ai-english-teacher-api.onrender.com/health/live
HTTP 503
```

**Note:** Production deploy health cannot be marked COMPLETE from this environment. Re-verify after Render redeploy or when `SMOKE_BASE_URL` smoke tests pass in deploy workflow.

### Repository negatives confirmed

```text
$ ls ai-english-teacher/backend/app/retrieval/
# directory does not exist

$ ls ai-english-teacher/backend/app/cognitive/
# directory does not exist

$ rg -l 'embedding_pipeline|sentence.transformers' ai-english-teacher/backend/
# no matches

$ rg -l 'video_ingestor|SourceType.VIDEO' ai-english-teacher/backend/
# no video ingestor
```

---

## File Index (quick reference)

| Area | Key paths |
|------|-----------|
| FastAPI entry | `backend/app/main.py` |
| Auth | `backend/app/api/auth.py`, `backend/app/services/auth_service.py` |
| Agents | `backend/app/agents/{orchestrator,grammar_agent,conversation_agent}.py` |
| Grok | `backend/app/services/grok_service.py` |
| Voice | `backend/app/services/{stt_service,tts_service}.py` |
| Ingestion | `backend/app/ingestion/` |
| Models | `backend/app/db/models/` |
| Migrations | `backend/alembic/versions/001`–`019` |
| Tests | `backend/app/tests/` (13 files, 26 tests) |
| CI/CD | `.github/workflows/{ci,deploy,migrate}.yml` |
| Frontend | `frontend/src/app/`, `frontend/src/lib/api.ts` |
| Design docs (aspirational) | `docs/agents/`, `RUNBOOK.md` |
