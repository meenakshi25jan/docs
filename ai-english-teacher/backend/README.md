# AI English Teacher — Backend Foundation

Production-quality FastAPI backend skeleton for the AI English Teacher platform. This foundation provides user authentication, database models, health checks, and tests — ready for later phases (lessons, AI agents, voice, etc.).

## Prerequisites

- **Python 3.12+** (with `venv` — on Debian/Ubuntu run `sudo apt install python3.12-venv` if `python -m venv` fails)
- **Optional:** [Docker](https://www.docker.com/) for local PostgreSQL (SQLite works with zero extra setup)

## VS Code setup

### 1. Open the backend folder

Open `ai-english-teacher/backend` as your workspace folder (or open the repo root and work in the `backend` subfolder).

### 2. Select the Python interpreter

1. Install the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) in VS Code.
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS) → **Python: Select Interpreter**.
3. Choose **Enter interpreter path…** → select `.venv/bin/python` after creating the venv (step 3 below).

### 3. Create and activate a virtual environment

```bash
cd ai-english-teacher/backend
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL or SQLite connection string (see below) |
| `JWT_SECRET` | Long random secret for signing JWTs |
| `JWT_ALGORITHM` | `HS256` (default) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime in minutes |

**SQLite (zero-setup, no Docker):**

```env
DATABASE_URL=sqlite+aiosqlite:///./ai_english_teacher.db
```

**PostgreSQL (recommended for production-like local dev):**

```bash
docker run --name ai-english-teacher-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=ai_english_teacher \
  -p 5432:5432 \
  -d postgres:16
```

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_english_teacher
```

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Start the API server

```bash
uvicorn app.main:app --reload
```

API available at [http://127.0.0.1:8000](http://127.0.0.1:8000). Interactive docs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 8. Run tests

```bash
pytest
```

Tests use an in-memory SQLite database — they do not touch your dev database.

### 9. Debug with F5 (VS Code)

Copy or merge `.vscode/launch.json` into your workspace. Press **F5** to start the API under the debugger with hot reload.

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Overall health (includes DB probe) |
| `GET` | `/health/live` | Liveness probe |
| `GET` | `/health/ready` | Readiness probe (503 if DB unreachable) |
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and receive JWT tokens |
| `POST` | `/auth/refresh` | Refresh access token |
| `GET` | `/users/me` | Current user profile (Bearer token required) |

## Project structure

```
backend/
├── alembic/              # Database migrations
├── app/
│   ├── api/              # Routers and Pydantic schemas
│   ├── core/             # Config, security, dependencies
│   ├── db/               # SQLAlchemy models and session
│   ├── services/         # Business logic (auth, users)
│   ├── tests/            # pytest suite
│   └── main.py           # FastAPI application entry point
├── .env.example
├── alembic.ini
├── requirements.txt
└── README.md
```

## Quick smoke test

```bash
curl http://127.0.0.1:8000/health/live
```

## Windows PowerShell

From `ai-english-teacher/backend`:

```powershell
# One-time setup (venv, deps, .env, migrations)
.\setup.ps1

# Setup + start server
.\setup.ps1 -StartServer

# Setup + run tests
.\setup.ps1 -RunTests

# After setup, start server only
.\run.ps1

# After setup, run tests only
.\test.ps1
```

If script execution is blocked:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

```bash
curl http://127.0.0.1:8000/health/live

curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"securepass123"}'

curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"securepass123"}'
```

Use the `access_token` from the login response:

```bash
curl http://127.0.0.1:8000/users/me \
  -H "Authorization: Bearer <access_token>"
```
