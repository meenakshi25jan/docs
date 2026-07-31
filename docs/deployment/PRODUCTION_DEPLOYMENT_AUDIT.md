# Production deployment audit — SKIP_MIGRATIONS fix

**Date:** 2026-07-31  
**Stack:** FastAPI + Next.js on Render, Neon PostgreSQL  
**Migrations:** Plain SQL via `scripts/migrate.py` (not Alembic at runtime)

---

## 1. Root cause analysis

| Finding | Detail |
|---------|--------|
| **Symptom** | Deploy exits: `SKIP_MIGRATIONS=true is not allowed in production deployments` |
| **Guard** | `start.sh` intentionally blocks production when `SKIP_MIGRATIONS=true` |
| **Repo `render.yaml`** | Already sets `SKIP_MIGRATIONS: "false"` |
| **Import error** | `migrate.py` did not add backend to `sys.path` → `ModuleNotFoundError: app` → migrations never ran |
| **Dashboard override** | Service-level `SKIP_MIGRATIONS=true` overrides blueprint `false` |
| **Not Alembic** | `alembic` is a dependency only; deploy runs `migrate.py` on ordered `*.sql` files |

**Conclusion:** Fix `sys.path` bootstrap so migrations run, ensure `SKIP_MIGRATIONS=false` (remove Render dashboard override if present), then redeploy.

---

## 2. Files changed (this audit)

| File | Change |
|------|--------|
| `render.yaml` | Comment + `SKIP_MIGRATIONS: "false"` (already false) |
| `archive/deployment/render-backend.yaml` | `true` → `false` |
| `archive/deployment/ai-english-teacher-render.yaml.duplicate` | `true` → `false` |
| `ai-english-teacher/backend/Dockerfile` | `ENV SKIP_MIGRATIONS=false` |
| `ai-english-teacher/backend/start.sh` | Logging, `REQUIRE_MIGRATIONS`, dashboard hint |
| `ai-english-teacher/backend/scripts/bootstrap_path.py` | **NEW** — `sys.path`, diagnostics, migrations dir resolution |
| `ai-english-teacher/backend/scripts/__init__.py` | Package for `python -m scripts.migrate` |
| `ai-english-teacher/backend/app/services/startup_diagnostics.py` | `validate_production_migrations_policy()` |
| `ai-english-teacher/deploy/cheapest/RENDER_FIX.md` | `false` + `bash ./start.sh` |
| `ai-english-teacher/scripts/validate_environment.py` | Reject Dockerfile `true` |
| `ai-english-teacher/RUNBOOK.md` | Deploy checklist fix |

---

## 3. Production deployment flow

```mermaid
flowchart TD
  A[Git push main] --> B[Render Blueprint sync render.yaml]
  B --> C[API build: pip + copy SQL migrations]
  C --> D[start.sh]
  D --> E{SKIP_MIGRATIONS=true?}
  E -->|yes in production| F[EXIT 1 — fix dashboard]
  E -->|no| G[migrate.py apply pending SQL]
  G --> H[verify_migrations_applied.py]
  H --> I[uvicorn FastAPI]
  I --> J[/health passes]
  B --> K[Web build: npm ci + build standalone]
  K --> L[npm start]
```

**Note:** This project does **not** run `alembic upgrade head`. Equivalent step is `python3 scripts/migrate.py`.

---

## 4. Migration sequence (SQL files)

| File | Purpose |
|------|---------|
| `001_initial_schema.sql` | `users`, `learner_profiles`, assessments, conversations, etc. |
| `002_pgvector.sql` | Vector extension |
| `003_auth_rls.sql` | RLS policies |
| `004_fix_rls_policies.sql` | RLS fixes |
| `005_knowledge_and_voice.sql` | `voice_analyses`, `knowledge_chunks`, etc. |
| `006_curriculum_intelligence.sql` | Curriculum tables |
| `007_security_rls_hardening.sql` | Security hardening |

Verified by `verify_migrations_applied.py` — expects tables including `users`, `learner_profiles`, `voice_analyses`, `lesson_completions`, `revision_schedule`, `knowledge_chunks`.

There is no separate `students` table; students are `users` with role `student`. Progress/analytics live in domain tables from 001+005+006.

---

## 5. Verification checklist

### Render dashboard (manual — cannot be done from repo)

- [ ] Blueprint **Manual sync** — uses root `render.yaml`
- [ ] Resources: `ai-english-teacher-api` + `ai-english-teacher-web`
- [ ] API **Environment**: **delete** `SKIP_MIGRATIONS=true` or set `false`
- [ ] API **Start Command**: `bash ./start.sh` (not `./start.sh` — dash lacks `pipefail`)
- [ ] Web **Runtime**: Node (not Docker)
- [ ] **Manual Deploy** API after env fix

### Automated

- [ ] `python3 ai-english-teacher/scripts/validate_render_config.py`
- [ ] `python3 ai-english-teacher/scripts/validate_environment.py`
- [ ] GitHub **Production Recovery** or **Deploy** workflow with secrets

### Production URLs

- [ ] `https://ai-english-teacher-api.onrender.com/health/live` → 200
- [ ] `https://ai-english-teacher-web.onrender.com/grammar-class` → 200
- [ ] `python3 ai-english-teacher/scripts/post_deploy_verify.py` → exit 0

### Deploy logs (success pattern)

```text
Environment: production
SKIP_MIGRATIONS=false
Database connected (migrations dir: ...)
Pending migrations: 0
Migration complete
Migration verification complete
Launching FastAPI (uvicorn) on port ...
```

---

## 6. Remaining risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Dashboard `SKIP_MIGRATIONS=true` override | **High** | Delete in Render Environment tab |
| Stale web build (`/grammar-class` 404) | High | Clear build cache + redeploy web |
| Missing `DATABASE_URL` on API | High | Set Neon URL with `?sslmode=require` |
| Blueprint not synced | Medium | Manual sync on blueprint |
| Free-tier cold start / slow deploy | Low | Wait workflows use 10+ min timeout |

---

## 7. Confirmation

After removing the Render dashboard override and redeploying:

- Production **cannot** start with `SKIP_MIGRATIONS=true` (blocked in `start.sh` + `startup_diagnostics`)
- All pending SQL migrations run **before** uvicorn via `migrate.py` with `REQUIRE_MIGRATIONS=true`
- `verify_migrations_applied.py` fails the deploy if tables 005–007 are missing
- Development may still use `SKIP_MIGRATIONS=true` when `ENVIRONMENT` is not `production`
