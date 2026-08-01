# Rollback — AI English Teacher

## Automatic rollback (CD workflow)

The deploy workflow (`deploy.yml`) runs a **rollback job** when any deploy step after the gate fails:

`build-push` → `migrate` → `deploy-backend` → `deploy-frontend` → `wait-live` → `health-check` → `smoke-test`

### How "last known-good" is tracked

1. On **successful** deploy, job `save-deploy-state` writes `deploy-state.json`:
   ```json
   {
     "last_good_commit": "<git-sha>",
     "deployed_at": "2026-08-01T02:00:00Z",
     "api_url": "https://...",
     "web_url": "https://..."
   }
   ```
2. Artifact `deploy-state` is uploaded (90-day retention).
3. GitHub Actions cache key `deploy-state-production-<sha>` stores the file for the rollback job.

### What the rollback job does

1. Restores the previous `deploy-state.json` artifact/cache.
2. Runs `scripts/rollback_deploy.py` which:
   - POSTs `RENDER_ROLLBACK_HOOK` (or `RENDER_DEPLOY_HOOK` as fallback)
   - POSTs `VERCEL_ROLLBACK_HOOK` if configured
   - Attempts `vercel rollback --yes` when `VERCEL_TOKEN` is set
3. **Fails the workflow loudly** (`exit 1`) so the failed deploy is visible in GitHub Actions.

> **Important:** Render deploy hooks redeploy the latest commit on the connected branch — they cannot deploy an arbitrary old SHA by themselves. For true SHA-level rollback:
> - Use **Render Dashboard → Rollback** to the previous deploy, or
> - Configure the API service to pull the GHCR image tag `ghcr.io/<owner>/ai-english-teacher-api:<last-good-sha>`

Document your chosen Render strategy in the Render dashboard (git-native vs container registry).

## Manual rollback

### Render (API)

1. [Render Dashboard](https://dashboard.render.com) → **ai-english-teacher-api**
2. **Events** or **Deploys** tab → select last healthy deploy → **Rollback**

### Vercel (frontend)

1. Vercel Dashboard → Project → **Deployments**
2. Find last green deployment → **⋯** → **Promote to Production**

Or CLI:

```bash
cd ai-english-teacher/frontend
npx vercel rollback --yes --token "$VERCEL_TOKEN"
```

### Database migrations

If a failed deploy included a **bad migration** that already ran:

1. **Do not** run `alembic downgrade` on production unless you have tested the downgrade path in CI (we test `downgrade -1` in CI for this reason).
2. Restore Neon from backup (Neon PITR) if schema/data is corrupted.
3. Ship a forward-fix migration (`003_fix_...`) rather than downgrading in production when possible.

## Verify rollback

```bash
curl -s https://ai-english-teacher-api.onrender.com/build-info | jq .
curl -s https://ai-english-teacher-web.onrender.com/build-info.json | jq .
```

Confirm `commit` matches the last known-good SHA from `deploy-state.json`.

## Smoke test after rollback

```bash
cd ai-english-teacher/backend
SMOKE_BASE_URL=https://ai-english-teacher-api.onrender.com \
SMOKE_EXPECT_COMMIT=<last-good-sha> \
pytest app/tests/test_smoke.py -v
```
