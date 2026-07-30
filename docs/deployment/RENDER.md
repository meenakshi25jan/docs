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
| Build | `npm ci && npm run build` |
| Start | `npm start` |

**Do not** use `backend/Dockerfile` on the web service.

## Deploy hooks

Render → Service → Settings → Deploy Hook → copy URL → GitHub secret:

- `RENDER_DEPLOY_HOOK_API`
- `RENDER_DEPLOY_HOOK_WEB`

## Build verification

Web build log must include:

```text
○ /grammar-class
```

## autoDeploy

Both services set `autoDeploy: true` in `render.yaml` — pushes to `main` trigger builds when Blueprint is synced.
