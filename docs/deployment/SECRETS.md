# GitHub Secrets & Variables — AI English Teacher

Never commit secret values. `.env` and `.env.*` (except `.env.example`) are gitignored.

## Consolidation note: `DATABASE_URL` vs `NEON_DB_URL`

Use **`DATABASE_URL` only**. Neon connection strings are stored in `DATABASE_URL` — there is no separate `NEON_DB_URL` in this pipeline. Format:

```text
postgresql+asyncpg://USER:PASSWORD@HOST/DBNAME?sslmode=require
```

## Repository secrets (Settings → Secrets and variables → Actions)

| Secret | Required | Purpose | Where to get it |
|--------|----------|---------|-----------------|
| `DATABASE_URL` | **Yes** (CD migrate) | Production Neon PostgreSQL URL for Alembic | [Neon Console](https://console.neon.tech) → Connection string → use `postgresql+asyncpg://` prefix |
| `JWT_SECRET` | **Yes** | Signs JWT access/refresh tokens | Generate: `openssl rand -hex 32` |
| `XAI_API_KEY` | **Yes** (runtime) | Grok LLM grammar/conversation | [xAI Console](https://console.x.ai) |
| `OPENAI_API_KEY` | For audio | Whisper speech-to-text | [OpenAI API keys](https://platform.openai.com/api-keys) |
| `RENDER_DEPLOY_HOOK` | Recommended | Triggers Render API redeploy after migrate | Render Dashboard → API service → Settings → Deploy Hook |
| `RENDER_ROLLBACK_HOOK` | Optional | Dedicated hook for rollback job (can point to previous deploy) | Render Dashboard (manual setup) |
| `VERCEL_TOKEN` | For Vercel CLI deploy | Vercel authentication | Vercel → Settings → Tokens |
| `VERCEL_ORG_ID` | For Vercel CLI | Team/org scope | `vercel whoami` / project settings |
| `VERCEL_PROJECT_ID` | For Vercel CLI | Target project | Vercel project → Settings → General |
| `VERCEL_DEPLOY_HOOK` | Alternative to CLI | HTTP hook deploy | Vercel project → Git → Deploy Hooks |
| `VERCEL_ROLLBACK_HOOK` | Optional | Hook to promote previous deployment | Vercel deploy hooks (manual) |
| `SENTRY_DSN` | Optional | Error tracking (app no-ops if unset) | Sentry project → Client Keys |

### Aliases

- `JWT_SECRET_KEY` is accepted by the app as an alias for `JWT_SECRET` (legacy Render configs). Prefer `JWT_SECRET`.

### GHCR credentials

**Not required.** CD uses the built-in `GITHUB_TOKEN` with `packages: write` permission to push `ghcr.io/<owner>/ai-english-teacher-api:<sha>`.

## Repository variables (non-secret)

| Variable | Default | Purpose |
|----------|---------|---------|
| `DEPLOY_API_URL` | `https://ai-english-teacher-api.onrender.com` | Health/smoke test target |
| `DEPLOY_WEB_URL` | `https://ai-english-teacher-web.onrender.com` | Frontend build-info polling |

## Render service environment (dashboard)

Set on the **Render API service** (not only GitHub):

| Key | Notes |
|-----|-------|
| `DATABASE_URL` | Same Neon URL as GitHub secret |
| `JWT_SECRET` | Same as GitHub |
| `XAI_API_KEY` | Grok |
| `OPENAI_API_KEY` | Whisper |
| `BUILD_COMMIT_SHA` | Set automatically by Render from git, or from Docker image tag |
| `SENTRY_DSN` | Optional |

## Vercel project environment

| Key | Notes |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | Production API base URL |
| `GITHUB_SHA` / build env | Used by `write-build-info.js` for commit SHA |

## Local development

Copy `ai-english-teacher/backend/.env.example` → `.env`. Never commit `.env`.
