# Automated production recovery

This guide automates the manual Render + Neon recovery checklist (Blueprint sync, API/web redeploy, migrations, verification).

## What cannot be automated from GitHub

Render Blueprint **Manual sync** and fixing service settings (Node vs Docker, root directory) must still be done in the [Render dashboard](https://dashboard.render.com) when Resources are wrong. After Blueprint sync succeeds, use the workflows below.

## One-click: GitHub Actions

### Workflow: **Production Recovery (One-Click)**

**Actions → Production Recovery (One-Click) → Run workflow** (branch `main`)

| Input | Default | Purpose |
|-------|---------|---------|
| `run_migrations` | true | Apply Neon migrations from `DATABASE_URL` |
| `clear_web_cache` | true | Clear web build cache (fixes stale `/grammar-class` 404) |
| `wait_timeout_minutes` | 10 | Max wait per service for health checks |

**Pipeline:**

1. Validate `render.yaml` and environment templates
2. Run `migrate.py` + `verify_migrations_applied.py` (if `DATABASE_URL` set)
3. Trigger API deploy → wait for `/health/live`
4. Trigger web deploy with cache clear → wait for `/grammar-class`
5. Run `post_deploy_verify.py` (register + student/analytics smoke)

### Workflow: **AI English Teacher Deploy**

Same deploy path after CI on `main`, or manual with `trigger_render`, `run_migrations`, `run_verify`.

## Required GitHub secrets

**Settings → Secrets and variables → Actions → Repository secrets**

| Secret | Source |
|--------|--------|
| `DATABASE_URL` | Neon connection string (`?sslmode=require`) |
| `RENDER_DEPLOY_HOOK_API` | Render → `ai-english-teacher-api` → Settings → Deploy Hook |
| `RENDER_DEPLOY_HOOK_WEB` | Render → `ai-english-teacher-web` → Settings → Deploy Hook |

**Optional** (clear web cache via Render API when hooks do not support it):

| Secret | Source |
|--------|--------|
| `RENDER_API_KEY` | Render → Account Settings → API Keys |
| `RENDER_SERVICE_ID_API` | API service URL or API: `srv-…` |
| `RENDER_SERVICE_ID_WEB` | Web service URL or API: `srv-…` |

## Local one-command recovery

From a machine with secrets exported:

```bash
export DATABASE_URL='postgresql://...?sslmode=require'
export RENDER_DEPLOY_HOOK_API='https://api.render.com/deploy/srv-...'
export RENDER_DEPLOY_HOOK_WEB='https://api.render.com/deploy/srv-...'
export CLEAR_WEB_BUILD_CACHE=true

cd ai-english-teacher
chmod +x scripts/automate_recovery.sh
./scripts/automate_recovery.sh
```

Or trigger deploys only:

```bash
export DEPLOY_TARGET=api
python3 ai-english-teacher/scripts/trigger_render_deploy.py

export DEPLOY_TARGET=web
export CLEAR_WEB_BUILD_CACHE=true
python3 ai-english-teacher/scripts/trigger_render_deploy.py
```

## Manual Render checklist (before/after automation)

| Step | Render UI | Expected |
|------|-----------|----------|
| Blueprint sync | Blueprint `ai-english-teacher` → Manual sync | Success, uses root `render.yaml` |
| Resources | Two services: API + Web | Both listed |
| API settings | Root `ai-english-teacher/backend`, `./start.sh`, `/health` | `SKIP_MIGRATIONS=false` |
| Web settings | Root `ai-english-teacher/frontend`, Node, `npm start` | Not Docker |
| Web deploy | Manual Deploy → Clear build cache | Logs show `Standalone OK` |

## Success criteria

| URL | Expected |
|-----|----------|
| `https://ai-english-teacher-web.onrender.com/grammar-class` | 200 |
| `https://ai-english-teacher-api.onrender.com/health/live` | 200 |
| Student dashboard after register | No 500 on analytics |

Verify locally:

```bash
python3 ai-english-teacher/scripts/post_deploy_verify.py
python3 ai-english-teacher/scripts/diagnose_deployment.py
```

Both should exit 0.

## If Blueprint sync fails

See `ai-english-teacher/deploy/cheapest/RENDER_FRESH_START.md` and `docs/deployment/RECOVERY_EXECUTIVE_REPORT.md`.
