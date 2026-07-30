# Frequently asked questions

## Why does `/grammar-class` return 404 in production but 200 locally?

Production Render web is serving an **old Next.js build**. The route exists in source and in local `npm run build`.

**Fix:** Render Dashboard → `ai-english-teacher-web` → Manual Deploy → **Clear build cache**. Confirm:

- Runtime: **Node** (not Docker)
- Root directory: `ai-english-teacher/frontend`
- Branch: `main`
- Blueprint: root `render.yaml`

Or set GitHub secret `RENDER_DEPLOY_HOOK_WEB` and run the Deploy workflow.

## Why do Student Intelligence / Analytics return 500?

Neon is missing tables from migrations **005–007** (`voice_analyses`, `lesson_completions`, etc.) because migrations were skipped.

**Fix:** Set `SKIP_MIGRATIONS=false` in Render API env (or use `render.yaml` blueprint). Redeploy API — `start.sh` runs migrations before uvicorn. Also run GitHub **Migrate** workflow with `DATABASE_URL` secret.

## Why are `/health/live` and `/health/ready` missing?

Production API is running code older than the current `main` branch. Merge the CI/CD PR and redeploy the API.

## Which `render.yaml` should I use?

Only **`render.yaml` at the repository root**. Do not use archived `render-backend.yaml`.

## Does deploy work without GitHub secrets?

CI runs on every PR. **Deploy** requires `DATABASE_URL` for migrations. Deploy hooks are optional but recommended to force Render rebuilds.

## How do I verify production?

```bash
python3 ai-english-teacher/scripts/diagnose_deployment.py
python3 ai-english-teacher/scripts/post_deploy_verify.py
bash ai-english-teacher/scripts/recovery.sh
```

## How do I roll back?

See [ROLLBACK.md](./ROLLBACK.md). Render: deploy previous successful build. Database: Neon point-in-time restore if migration caused issues.

## Can I use Docker for the frontend on Render?

No. Docker web builds caused stale routes and wrong `server.js` paths. Use **Node** runtime per `render.yaml`.
