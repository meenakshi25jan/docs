# Render Blueprint setup

## Create fresh (recommended if misconfigured)

1. Delete old Blueprint and services (see `RENDER_FRESH_START.md`)
2. **Blueprints → New Blueprint Instance**
3. Repo: `meenakshi25jan/docs`
4. Branch: **`main`**
5. Blueprint path: **`render.yaml`** (root — not `render-backend.yaml`)

## Service settings after sync

### API — `ai-english-teacher-api`

| Setting | Value |
|---------|--------|
| Runtime | Python |
| Root | `ai-english-teacher/backend` |
| Health check | `/health` |

### Web — `ai-english-teacher-web`

| Setting | Value |
|---------|--------|
| Runtime | **Node** |
| Root | `ai-english-teacher/frontend` |
| Build | `rm -rf .next && npm ci && npm run build` |
| Start | `npm start` |

**Do not** use `backend/Dockerfile` on the web service.

## Deploy hooks (GitHub Actions automation)

Deploy hooks let the **Deploy** workflow trigger Render builds after CI passes, without waiting only on `autoDeploy` timing.

### 1. Create hooks in Render (human — dashboard)

For each service:

1. Open [Render Dashboard](https://dashboard.render.com/)
2. Select the service (`ai-english-teacher-api` or `ai-english-teacher-web`)
3. **Settings** → scroll to **Deploy Hook**
4. Click **Create Deploy Hook** (or copy the existing URL)
5. Copy the full hook URL (looks like `https://api.render.com/deploy/srv-…?key=…`)

Repeat for **both** API and web services.

### 2. Add secrets in GitHub (human — no values in repo)

1. GitHub → **meenakshi25jan/docs** → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** (or environment `production` secrets if you use GitHub Environments):

| Secret name | Paste value from |
|-------------|------------------|
| `RENDER_DEPLOY_HOOK_API` | API service → Settings → Deploy Hook URL |
| `RENDER_DEPLOY_HOOK_WEB` | Web service → Settings → Deploy Hook URL |

Optional but recommended for deploy workflow migrations:

| Secret name | Purpose |
|-------------|---------|
| `DATABASE_URL` | Neon connection string for GitHub-side `migrate.py` before hook triggers |

**Do not commit hook URLs.** They are credentials.

### 3. What the workflow does when secrets are set

`.github/workflows/deploy.yml` runs after **AI English Teacher CI** succeeds on `main`:

1. Optional: `migrate.py` + `verify_migrations_applied` (if `DATABASE_URL` secret set)
2. `curl -X POST $RENDER_DEPLOY_HOOK_API` → starts API deploy
3. Wait for API `/health/live`
4. `curl -X POST $RENDER_DEPLOY_HOOK_WEB` → starts web deploy
5. Wait for `/` and `/grammar-class`
6. `post_deploy_verify.py` with retries

If a hook secret is **missing**, the step logs a warning and relies on Render `autoDeploy: true` from the git push — hooks are not required for the workflow to run, but **recommended** so deploys are explicit after CI.

### 4. Hooks do not clear Render build cache

Deploy hooks trigger a **new deploy** but do **not** replace **Manual Deploy → Clear build cache & deploy** when production is already serving a stale artifact (e.g. old Next.js build ID without `/grammar-class`). For that one-time recovery, a human must clear cache in the dashboard (see `TROUBLESHOOTING.md`).

## Build verification

Web build log must include:

```text
○ /grammar-class
```

## autoDeploy

Both services set `autoDeploy: true` in `render.yaml` — pushes to `main` trigger builds when Blueprint is synced.
