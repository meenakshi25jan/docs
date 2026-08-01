# AI English Teacher — Branch Protection (manual GitHub setup)

Branch protection cannot be committed from the repository. Configure these rules in **GitHub → Settings → Branches → Branch protection rules**.

## Branch strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production — deploys via CD after green CI |
| `develop` | Staging / integration |
| `feature/*` | Short-lived feature work (`feature/grammar-agent`, etc.) |

## `main` protection rules

1. Go to **Settings → Branches → Add branch protection rule**
2. Branch name pattern: `main`
3. Enable:
   - **Require a pull request before merging**
     - Required approvals: **1**
     - Dismiss stale pull request approvals when new commits are pushed
   - **Require status checks to pass before merging**
     - Required checks (exact names from CI workflow):
       - `Lint (flake8, black, isort)`
       - `Type check (mypy)`
       - `Unit tests (pytest + coverage)`
       - `Integration tests (Postgres + pgvector)`
       - `Migration check (upgrade / downgrade / upgrade)`
       - `Security scan (pip-audit + gitleaks)`
       - `Docker build`
       - `ci-success`
   - **Require branches to be up to date before merging**
   - **Do not allow bypassing the above settings** (admins included, recommended)
   - **Restrict who can push to matching branches** (optional, recommended for teams)
   - **Block force pushes**
   - **Block deletions**

## `develop` protection rules

Repeat the same steps with branch pattern `develop`:

- Require PR before merging (1 approval)
- Require the same CI status checks as `main`
- Block force pushes
- Block deletions

## Why both branch protection AND `workflow_run` deploy?

| Approach | What it prevents |
|----------|------------------|
| **Branch protection** | Broken code merging to `main` via PR |
| **`workflow_run` deploy gate** | Deploy starting while CI is red, skipped, or from a non-CI path |

We use **both**. Branch protection alone does not stop a direct push (if allowed) or a deploy triggered on `push: main` before CI finishes. The CD workflow only runs after **CI completes successfully** on `main`.

## Feature branches

`feature/*` branches do **not** need protection rules. They run CI on pull requests only.
