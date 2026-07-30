# Release process

## Versioning

- Application version: `APP_VERSION` in backend settings (currently `1.0.0`)
- Frontend: `package.json` version (aligned manually on major releases)
- Database: sequential SQL migrations `001`–`007` (no down migrations)

## Standard release

1. **Branch** — feature branches → PR to `main`
2. **CI** — **AI English Teacher CI** must pass (tests, lint, build, Docker, security)
3. **Review** — code review + dependency review on PR
4. **Merge** — merge to `main`
5. **Deploy** — Render auto-deploy + GitHub Deploy workflow
6. **Verify** — `deploy_verify.py` and `performance_smoke.py` in Deploy workflow
7. **Sign-off** — confirm `/grammar-class`, `/conversation`, API `/health/ready`

## Hotfix release

1. Branch from `main`: `cursor/hotfix-<topic>-f37f`
2. Minimal fix + test
3. Fast-track PR with CI green
4. Merge → deploy
5. Optional: trigger `workflow_dispatch` Deploy with migrations if schema change

## Pre-release checklist

- [ ] `render.yaml` validated locally
- [ ] Migrations applied on staging/production Neon
- [ ] Secrets set on Render (not in git)
- [ ] `DEPLOY_VERIFY_GRAMMAR_CLASS` accurate for current web state
- [ ] Rollback plan documented if migration included

## Communication

- GitHub Deploy workflow posts success notice with web/API URLs
- Document user-facing changes in PR description
