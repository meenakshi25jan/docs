# Operations runbook — AI English Teacher

## Service map

| Service | URL | Render name |
|---------|-----|-------------|
| Web | https://ai-english-teacher-web.onrender.com | `ai-english-teacher-web` |
| API | https://ai-english-teacher-api.onrender.com | `ai-english-teacher-api` |
| Database | Neon PostgreSQL + pgvector | `DATABASE_URL` secret |

## Health checks

```bash
curl -sS https://ai-english-teacher-api.onrender.com/health/live
curl -sS https://ai-english-teacher-api.onrender.com/health/ready
curl -sS https://ai-english-teacher-api.onrender.com/health
curl -sS https://ai-english-teacher-web.onrender.com/grammar-class -o /dev/null -w "%{http_code}\n"
```

Expected: API health 200; `/grammar-class` 200 after correct web deploy.

## Deploy (standard)

1. Merge to `main` → Render `autoDeploy` builds API + web from root `render.yaml`
2. GitHub **Deploy** workflow runs after CI (migrations + verification)
3. Confirm `deploy_verify.py` passes locally if needed:

```bash
python3 ai-english-teacher/scripts/deploy_verify.py
```

## Deploy (manual / recovery)

1. Render Dashboard → service → **Manual Deploy** → **Clear build cache**
2. Web service must be **Node** runtime, root `ai-english-teacher/frontend`, **not** Docker
3. Trigger deploy hooks if configured in GitHub secrets
4. Run migrations:

```bash
cd ai-english-teacher/backend
export DATABASE_URL='postgresql://...'
python3 scripts/migrate.py
```

## Rollback

See [ROLLBACK.md](ROLLBACK.md). Summary:

1. Revert git commit on `main` and redeploy, or
2. Render → deploy previous successful build
3. Database: migrations are forward-only; restore Neon backup if schema rollback required

## Incident response

| Symptom | Likely cause | Action |
|---------|--------------|--------|
| `/grammar-class` 404 | Stale web build or wrong runtime | Manual deploy web, Node runtime, clear cache |
| API 500 on student routes | Missing migrations 005–007 | Run `migrate.py` on Neon |
| `/health/ready` 503 | DB unreachable | Check `DATABASE_URL`, Neon status, pool settings |
| CORS errors | Wrong `CORS_ORIGINS` | Update Render API env |
| AI mock responses | Missing `OPENAI_API_KEY` | Set Groq/OpenAI key on API service |

## Monitoring

- Render service logs
- `/metrics` on API (Prometheus)
- GitHub Actions deploy workflow notifications
- Admin: `/api/v1/production/readiness` (JWT admin)

## Contacts and docs

- [RENDER.md](RENDER.md) — Blueprint setup
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — common errors
- [DISASTER_RECOVERY.md](DISASTER_RECOVERY.md) — backup and restore
