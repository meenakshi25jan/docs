# Shell compatibility (Render / dash vs bash)

## Root cause

Render runs the **Start Command** with `/bin/sh`, which on Debian/Ubuntu is **dash** — not bash. Dash does not support:

- `set -o pipefail`
- `[[ ... ]]`, `(( ))`, `source`, `declare`, arrays, process substitution

If the dashboard Start Command is `./start.sh`, the kernel executes the shebang (`#!/usr/bin/env bash`). If the command is explicitly `sh ./start.sh` or Render ignores the shebang path, dash parses the file and fails with:

```text
./start.sh: 4: set: Illegal option -o pipefail
```

## Fix (repository)

| Layer | Requirement |
|-------|-------------|
| `backend/start.sh` | `#!/usr/bin/env bash`, `set -Eeuo pipefail`, bash guard if `BASH_VERSION` unset |
| `render.yaml` | `startCommand: bash ./start.sh` |
| `backend/Dockerfile` | `RUN chmod +x start.sh`, `CMD ["bash", "./start.sh"]` |
| CI | `validate_shell_scripts.py` + `shellcheck` in `validate-config` job |

## Fix (Render dashboard)

**API → Settings → Start Command:**

```bash
bash ./start.sh
```

Not `./start.sh` or `sh ./start.sh`. Dashboard overrides blueprint — sync blueprint alone is not enough if Start Command was edited manually.

## Audited shell scripts (`ai-english-teacher/`)

| Path | Shebang | Runtime | Bash-only features | Render executes? |
|------|---------|---------|-------------------|------------------|
| `backend/start.sh` | `#!/usr/bin/env bash` | bash | `pipefail` | Yes (API start) |
| `backend/scripts/backup_verify.sh` | `#!/usr/bin/env bash` | bash | pipefail, `[[ ]]`, `BASH_SOURCE` | No (ops manual) |
| `scripts/ci_lint_backend.sh` | `#!/usr/bin/env bash` | bash | pipefail | CI only |
| `scripts/recovery.sh` | `#!/usr/bin/env bash` | bash | pipefail | Manual recovery |
| `scripts/trigger_render_deploy.sh` | `#!/usr/bin/env bash` | bash | pipefail | Manual / hooks |
| `deploy/cheapest/deploy.sh` | `#!/usr/bin/env bash` | bash | pipefail | Local deploy |
| `deploy/oracle-cloud/deploy-now.sh` | `#!/usr/bin/env bash` | bash | pipefail | Oracle VM |
| `deploy/oracle-cloud/setup-vm.sh` | `#!/usr/bin/env bash` | bash | pipefail | Oracle VM |

## Render configuration

| File | API `startCommand` | Status |
|------|-------------------|--------|
| `render.yaml` (root) | `bash ./start.sh` | Canonical blueprint |
| `archive/deployment/render-backend.yaml` | Docker CMD (not startCommand) | Archived; uses `CMD ["bash", "./start.sh"]` in Dockerfile |

## Validation

```bash
sudo apt-get install -y shellcheck   # optional locally; CI installs it
python3 ai-english-teacher/scripts/validate_shell_scripts.py
python3 ai-english-teacher/scripts/validate_render_config.py
python3 ai-english-teacher/scripts/validate_docker.py
```

## Startup flow (production API)

```text
Render: bash ./start.sh
  → bash guard (BASH_VERSION, command -v bash)
  → log commit, shell, PATH, PYTHONPATH, python3 --version
  → require DATABASE_URL, SKIP_MIGRATIONS=false, OPENAI_API_KEY (production)
  → python -m scripts.migrate
  → python -m scripts.verify_migrations_applied
  → exec uvicorn app.main:app
```

## Post-deploy verification

```bash
python3 ai-english-teacher/scripts/post_deploy_verify.py
```

Checks health, metrics, routes, and optional authenticated API smoke tests. Exit non-zero on failure.
