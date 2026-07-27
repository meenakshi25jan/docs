# AGENTS.md

## Cursor Cloud specific instructions

This monorepo contains two independent products:

| Product | Path | Default port |
|---------|------|--------------|
| AWS Amplify Framework Documentation | `/workspace` (root) | 3000 |
| AI English Teacher Platform | `/workspace/ai-english-teacher` | 3000 (frontend), 8000 (backend) |

Only one app can bind port 3000 at a time. Run the Amplify docs on a different port when the AI English Teacher frontend is up (e.g. `NODE_OPTIONS=--openssl-legacy-provider yarn dev -p 3001`).

### System prerequisites (one-time per VM)

- **Docker**: start with `sudo service docker start` before `docker compose` commands.
- **Python venv**: `python3.12-venv` must be installed (`sudo apt-get install -y python3.12-venv`).

### AWS Amplify docs (root)

- Install: `yarn install` (from repo root).
- Dev server: `NODE_OPTIONS=--openssl-legacy-provider yarn dev` (required on Node 22+ due to OpenSSL/webpack in Next.js 10).
- Alternate port: append `-p 3001`.
- Tests/lint: `yarn test`, `yarn spellcheck`. CI also runs `yarn build` (heavy; needs `NODE_OPTIONS=--openssl-legacy-provider`).

### AI English Teacher

**Infrastructure (PostgreSQL + Redis):**

```bash
cd ai-english-teacher
sudo docker compose up -d postgres redis
```

SQL migrations run automatically via `docker-entrypoint-initdb.d` on first Postgres start.

**Backend (FastAPI):**

```bash
cd ai-english-teacher/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Copy `backend/.env.example` → `backend/.env` before first run.
- After `pip install -r requirements.txt`, also install `pydantic[email]` and pin `bcrypt==4.2.1` (passlib 1.7.4 breaks with bcrypt 5.x).
- Tests: `PYTHONPATH=. DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_english_teacher JWT_SECRET_KEY=test-secret pytest tests/ -v`
- API docs: http://localhost:8000/docs

**Frontend (Next.js 15):**

`npm run dev` from `ai-english-teacher/frontend` fails in this monorepo (`trace.getSpanContext is not a function`) because Next.js resolves the workspace root to `/workspace` (parent `yarn.lock`) and picks up conflicting OpenTelemetry packages.

**Recommended:** run the production image built in isolation:

```bash
cd ai-english-teacher
mkdir -p frontend/public   # required for Docker build if missing
sudo docker compose build frontend
sudo docker run -d --name ai-frontend -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 \
  ai-english-teacher-frontend
```

Or full stack: `sudo docker compose up --build` (postgres, redis, backend, frontend).

**Frontend lint/build caveats:** `npm run lint` and `npm run build` fail ESLint parsing (`moduleResolution: bundler` vs ESLint expecting `node`/`classic`). Use `npm run build -- --no-lint` inside Docker where the isolated context succeeds.

### Hello-world verification

1. **Amplify docs**: open http://localhost:3001 — landing page with platform icons.
2. **AI English Teacher API**: `POST /api/v1/auth/register` then `POST /api/v1/assessments` with the returned JWT (see `backend/app/api/v1/`).
3. **AI English Teacher UI**: http://localhost:3000 (homepage) and http://localhost:3000/dashboard/student.
