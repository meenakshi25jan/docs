# Deployment error diagnosis and fixes

**Date:** 2026-07-30

## Errors found (live production)

| Endpoint | Status | Root cause | Repo fix | External action |
|----------|--------|------------|----------|-----------------|
| `/grammar-class` | 404 | Stale Render web build (`WjWnTF_iSLNiPaqsi9n8e`) — route exists in source and local standalone returns 200 | Build verification in `render.yaml`; `diagnose_deployment.py` | Manual Deploy web + Clear cache, Node runtime, branch `main` |
| `/health/live`, `/health/ready` | 404 | Production API not deployed from CI branch | Added endpoints in `main.py` | Merge PR + API redeploy |
| `/api/v1/student-intelligence/summary` | 500 | Missing tables `voice_analyses` etc. (migrations 005–007 not applied) | `optional_tables.py` graceful fallback; `SKIP_MIGRATIONS=false`; `start.sh` | API redeploy applies migrations |
| `/api/v1/analytics/overview` | 500 | Same as above | Same | Same |

## Repository changes

1. **`render.yaml`** — API uses `bash ./start.sh`, `SKIP_MIGRATIONS=false`, web build verifies standalone server path
2. **`optional_tables.py`** — queries against optional migration tables return empty data instead of 500
3. **`frontend/Dockerfile`** — correct standalone path (`frontend/server.js`)
4. **`diagnose_deployment.py`** — automated local + production diagnosis
5. **Docs** — RUNBOOK, NEON_VERCEL updated (removed `render-backend.yaml` references)

## Validation (local)

- 355 pytest tests passed
- Frontend typecheck passed
- Local standalone: `/grammar-class` → 200
- `validate_render_config.py` → OK

## Production readiness

**Repository-controlled errors:** fixed in this branch.  
**Remaining:** Render must redeploy API + web from merged `main` with root `render.yaml`.

Run diagnosis anytime:

```bash
python3 ai-english-teacher/scripts/diagnose_deployment.py
```
