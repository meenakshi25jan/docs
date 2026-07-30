# Disaster recovery

## RPO / RTO targets (guidance)

| Asset | RPO | RTO | Mechanism |
|-------|-----|-----|-----------|
| Neon PostgreSQL | Neon PITR (plan-dependent) | 1–4 hours | Neon restore + migrate verify |
| Render services | Last git commit on `main` | 30–90 min | Blueprint redeploy |
| Secrets | Manual | Immediate | Render + GitHub Secrets |

## Database backup

- **Neon** — enable point-in-time recovery on production branch
- Verify connectivity:

```bash
cd ai-english-teacher/backend
bash scripts/backup_verify.sh
```

## Full platform rebuild

1. Restore or create Neon database; set `DATABASE_URL`
2. Delete and recreate Render Blueprint from root `render.yaml` (branch `main`)
3. Set API env: `DATABASE_URL`, `OPENAI_API_KEY`, `JWT_SECRET_KEY`, `SKIP_MIGRATIONS=true`
4. Run migrations: `python3 scripts/migrate.py`
5. Configure GitHub secrets for Deploy workflow
6. Run verification:

```bash
python3 ai-english-teacher/scripts/deploy_verify.py
python3 ai-english-teacher/scripts/performance_smoke.py
```

See also: `ai-english-teacher/deploy/cheapest/RENDER_FRESH_START.md`

## Data loss scenarios

| Scenario | Recovery |
|----------|----------|
| Bad migration | Restore Neon to pre-migration timestamp; fix migration; re-apply |
| Deleted Render service | Recreate from `render.yaml` |
| Leaked JWT secret | Rotate `JWT_SECRET_KEY` on Render; force user re-login |
| Compromised API keys | Rotate `OPENAI_API_KEY` / Groq keys; audit logs |

## Post-recovery validation

- All checks in `deploy_verify.py` pass
- `migration_report.py` and `check_migrations.py` pass
- Admin `/api/v1/production/readiness` returns passed (with admin token)
