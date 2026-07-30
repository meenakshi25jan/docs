# Troubleshooting

## `/grammar-class` returns 404

| Cause | Fix |
|-------|-----|
| Stale web build | Manual deploy web + clear cache |
| Web uses Docker + `backend/Dockerfile` | Switch to **Node** runtime |
| Wrong blueprint (`render-backend.yaml`) | Use root `render.yaml` |
| Wrong branch on Blueprint | Set branch `main` |

## CI fails on frontend build

- Run locally: `cd ai-english-teacher/frontend && npm ci && npm run build`
- Check TypeScript errors (not ignored in `next.config.js`)

## API 500 after deploy

- Run migrations: `python3 scripts/migrate.py` with `DATABASE_URL`
- Check Render logs for missing tables (`005`, `006` migrations)

## Deploy workflow verification fails

- Render free tier cold start — retries in workflow
- Check `deploy_verify.py` output for which URL failed
- API may need 60–90s after deploy before health passes

## CORS errors

- `CORS_ORIGINS` on API must include exact web URL

## Common errors

| Error | Fix |
|-------|-----|
| `connection is closed` (Neon) | Pool settings in render.yaml |
| ESLint fail on Render | `ignoreDuringBuilds: true` in next.config.js |
| `next start` + standalone warning | Use `npm start` → standalone server.js |
