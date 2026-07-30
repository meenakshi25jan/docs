# Archived deployment assets

Obsolete or duplicate deployment configuration moved here during CI/CD standardization (2026-07-30).

**Do not use for production.** Canonical config:

- Blueprint: `/render.yaml` (repository root)
- Docs: `/docs/deployment/`

## Contents

| Path | Reason archived |
|------|-----------------|
| `render-backend.yaml` | API-only Docker blueprint; omitted frontend web service |
| `ai-english-teacher-render.yaml.duplicate` | Duplicate of root `render.yaml` |
| `workflows/ci.yml` | Superseded by root `.github/workflows/ci.yml` |
| `workflows/cd.yml` | Azure AKS deploy; not used for Render |
| `workflows/deploy-cheapest.yml` | Manual Fly/Render notify only |

Oracle Cloud, Fly.io, and Vercel guides remain under `ai-english-teacher/deploy/` for optional alternate targets.
