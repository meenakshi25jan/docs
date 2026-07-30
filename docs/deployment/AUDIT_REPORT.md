# Repository audit & CI/CD implementation report

**Date:** 2026-07-30  
**Scope:** AI English Teacher deployment standardization

---

## 1. Repository audit

### Deployment-related files found

| Location | Status |
|----------|--------|
| `render.yaml` (root) | **Canonical** — updated |
| `ai-english-teacher/render.yaml` | Archived (duplicate) |
| `ai-english-teacher/render-backend.yaml` | Archived (API Docker only) |
| `ai-english-teacher/.github/workflows/*` | Archived (never ran from subfolder) |
| `ai-english-teacher/frontend/Dockerfile` | Kept (optional local/docker) |
| `ai-english-teacher/backend/Dockerfile` | Kept (optional API docker) |
| `ai-english-teacher/deploy/cheapest/*` | Kept (guides + scripts) |
| `ai-english-teacher/deploy/oracle-cloud/*` | Kept (alternate target) |
| `ai-english-teacher/backend/scripts/*` | Extended |
| Root `.github/workflows/*` (Amplify docs) | Unchanged (other products) |

### Problems found

1. **Multiple Render blueprints** — `render-backend.yaml` deployed API only; wrong branch on Blueprint
2. **Web service misconfiguration** — Docker + `backend/Dockerfile` caused stale frontend builds
3. **CI workflows in subfolder** — `ai-english-teacher/.github/workflows` not executed by GitHub
4. **Azure CD workflow** — AKS deploy irrelevant to Render production
5. **No post-deploy verification** in automation
6. **Migrations manual** — `SKIP_MIGRATIONS=true` without CI/deploy integration

---

## 2. Files archived

Moved to `archive/deployment/`:

- `render-backend.yaml`
- `ai-english-teacher-render.yaml.duplicate`
- `workflows/ci.yml`, `cd.yml`, `deploy-cheapest.yml`

---

## 3. Files created / updated

| File | Action |
|------|--------|
| `.github/workflows/ci.yml` | Created |
| `.github/workflows/deploy.yml` | Created |
| `render.yaml` | Updated (`autoDeploy`, `ENVIRONMENT`) |
| `ai-english-teacher/scripts/validate_render_config.py` | Created |
| `ai-english-teacher/scripts/check_migrations.py` | Created |
| `ai-english-teacher/scripts/deploy_verify.py` | Created |
| `docs/deployment/*` | Created |
| `archive/deployment/README.md` | Created |

---

## 4. CI/CD architecture

GitHub push → CI (test/build/validate) → on `main` success → Deploy (hooks/migrate/verify)

See `docs/deployment/CI_CD.md` and Mermaid in `docs/deployment/README.md`.

---

## 5. Security improvements

- Secrets only in GitHub Secrets / Render env
- Trivy scan in CI
- `validate_render_config.py` prevents web Docker misconfig
- Production environment gate on deploy workflow
- Branch protection recommendations documented

---

## 6. Cost optimizations

- Render free tier (API + web)
- Neon free tier
- `requirements-render.txt` slim API deps
- npm/pip caching in GitHub Actions

---

## 7. Manual deployment steps

1. Apply Blueprint from root `render.yaml`
2. Set `DATABASE_URL`, `OPENAI_API_KEY` on API
3. `python3 ai-english-teacher/backend/scripts/migrate.py`
4. Manual deploy web with clear cache if needed

---

## 8. Automated deployment steps

1. Merge to `main`
2. CI runs automatically
3. Deploy workflow runs on CI success
4. Optional hooks + migrations + `deploy_verify.py`

---

## 9. Production readiness score

| Area | Score | Notes |
|------|-------|-------|
| CI coverage | 8/10 | Backend tests; frontend lint+build |
| CD automation | 7/10 | Depends on Render hooks/autoDeploy |
| Config single source | 9/10 | Root `render.yaml` |
| Documentation | 9/10 | `docs/deployment/` |
| Live `/grammar-class` | 5/10 | Requires fresh Render web deploy |

**Overall:** 7/10 — pipeline ready; production URLs need Render redeploy

---

## 10. Remaining risks

- Render free tier cold starts
- No down-migrations
- Deploy verify fails if Render slow > retry window
- Groq key rotation discipline
- Neon migrations 005–007 must be applied

---

## 11. Future enhancements

- Playwright E2E for `/grammar-class`
- Render API polling instead of fixed sleep
- Staging environment + preview deploys
- Dependabot for npm/pip
- Sentry / structured log export

---

## 12. Validation checklist

- [ ] Blueprint: `render.yaml`, branch `main`
- [ ] Web: Node, root `frontend`
- [ ] GitHub secrets configured
- [ ] CI green on `main`
- [ ] `/grammar-class` HTTP 200
- [ ] `deploy_verify.py` passes
