# CI/CD pipeline

## Workflows

| Workflow | File | Trigger |
|----------|------|---------|
| CI | `.github/workflows/ci.yml` | Push/PR to paths under `ai-english-teacher/` or `render.yaml` |
| Deploy | `.github/workflows/deploy.yml` | After CI succeeds on `main`, or manual |

## CI stages

1. Validate `render.yaml`
2. Check migration files on disk
3. Backend: install, import app, pytest (Postgres + pgvector service)
4. Frontend: `npm ci`, `lint`, `build`, assert `/grammar-class` in route table
5. Trivy scan (CRITICAL/HIGH, non-blocking exit 0)
6. Aggregate `ci-success` job

## Deploy stages

1. Validate `render.yaml`
2. Optional: POST Render deploy hooks (`RENDER_DEPLOY_HOOK_API`, `RENDER_DEPLOY_HOOK_WEB`)
3. Optional: `migrate.py` with `DATABASE_URL` secret
4. Wait 120s
5. `deploy_verify.py` with retries (up to ~6 min)

## GitHub configuration

### Secrets (Settings → Secrets and variables → Actions)

| Secret | Required | Purpose |
|--------|----------|---------|
| `DATABASE_URL` | For migrations in deploy | Neon connection string |
| `OPENAI_API_KEY` | Set on Render, not CI | AI (Render env) |
| `RENDER_DEPLOY_HOOK_API` | Optional | Trigger API redeploy |
| `RENDER_DEPLOY_HOOK_WEB` | Optional | Trigger web redeploy |

### Variables (optional)

| Variable | Default |
|----------|---------|
| `DEPLOY_WEB_URL` | `https://ai-english-teacher-web.onrender.com` |
| `DEPLOY_API_URL` | `https://ai-english-teacher-api.onrender.com` |

### Environments

- `production` — deploy workflow uses GitHub Environment for approval gates (configure in repo settings)

## Branch protection (recommended)

- Require **AI English Teacher CI** before merge to `main`
- Require up-to-date branches
- Restrict force-push to `main`
