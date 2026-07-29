# Render Fix — App Stuck on "Welcome to Render"

> **See also:** [RUNBOOK.md](../../RUNBOOK.md) — complete prerequisites, deployment, and error catalog in one document.

Your API is **not starting**. Follow every step below in order.

---

## Step 1: Open your service

https://dashboard.render.com → click **ai-english-teacher-api**

---

## Step 2: Fix Build Command

Go to **Settings** → **Build & Deploy**

**Build Command** — paste exactly:
```
pip install -r requirements-render.txt && mkdir -p migrations && cp -r ../database/migrations/* migrations/ 2>/dev/null || true
```

**Start Command** — paste exactly:
```
python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Root Directory:** `ai-english-teacher/backend`

**Branch:** `main`

Click **Save Changes**.

---

## Step 3: Environment variables

Go to **Environment** tab:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Your Neon URL (must end with `?sslmode=require`) |
| `PYTHON_VERSION` | `3.12.4` |
| `SKIP_MIGRATIONS` | `true` |

Example DATABASE_URL:
```
postgresql://user:pass@ep-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

---

## Step 4: Manual deploy

Click **Manual Deploy** → **Deploy latest commit**

Wait 3–5 minutes. Watch the **Logs** tab.

### ✅ Success looks like:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:10000
INFO:     Application startup complete.
```

### ❌ Failure looks like:
```
ModuleNotFoundError
Out of memory
Error: Invalid value for '--port'
```

Paste errors here if you see them.

---

## Step 5: Test (after logs show "startup complete")

Open: https://ai-english-teacher-api.onrender.com/health

Expected:
```json
{"status":"healthy","version":"1.0.0"}
```

---

## Still stuck? Upgrade to Starter ($7/mo)

Free tier has only **512 MB RAM**. If logs show `Killed` or `OOM`:

**Settings** → **Instance Type** → **Starter ($7/month)**

This also removes the cold-start screen permanently.

---

## Quick checklist

- [ ] Branch = `main`
- [ ] Root Directory = `ai-english-teacher/backend`
- [ ] Build uses `requirements-render.txt`
- [ ] Start command uses `python3 -m uvicorn`
- [ ] `DATABASE_URL` is set with `?sslmode=require`
- [ ] Logs show "Application startup complete"
- [ ] `/health` returns JSON (not Render ASCII art)

---

## Frontend 404 on `/conversation`, `/login`, or `/register`

The homepage and `/dashboard/student` work but newer pages return **404** when the
**ai-english-teacher-web** service is still running an old build.

### Fix

1. Open https://dashboard.render.com → **ai-english-teacher-web**
2. **Settings** → confirm:
   - **Branch:** `main`
   - **Root Directory:** `ai-english-teacher/frontend`
   - **Build Command:** `npm install && npm run build`
   - **Start Command:** `npm start`
3. **Manual Deploy** → **Deploy latest commit**
4. Wait for build logs to list routes including `/conversation`, `/login`, `/register`
5. Test: https://ai-english-teacher-web.onrender.com/conversation

---

## "Failed to fetch" on Register / Login

Usually caused by **CORS** or the API **cold start** on Render free tier.

### Fix

1. Open https://dashboard.render.com → **ai-english-teacher-api**
2. **Environment** → set `CORS_ORIGINS` to:
   ```
   ["https://ai-english-teacher-web.onrender.com","http://localhost:3000"]
   ```
3. **Manual Deploy** → Deploy latest commit on `main`
4. Wait 30–60 seconds after deploy, then retry registration

If it still fails, open https://ai-english-teacher-api.onrender.com/health first to wake the API, then register again.

### Run login migration (one time)

After deploying the latest API, run migration `003_auth_rls.sql` against Neon (SQL Editor):

```sql
CREATE POLICY auth_email_lookup ON users
    FOR SELECT
    USING (current_setting('app.auth_lookup', true) = 'on');
```

Or from Render shell / locally:

```bash
cd ai-english-teacher/backend && DATABASE_URL='your-neon-url' python3 scripts/migrate.py
```

---

## "connection is closed" when starting conversation

Happens when Render or Neon wakes from sleep and the API tries to reuse a dead PostgreSQL connection.

### Fix

1. Deploy the latest API (`pool_pre_ping` + `pool_recycle` fix on `main`).
2. In **ai-english-teacher-api** → **Environment**, use your Neon **pooler** URL (recommended):
   ```
   postgresql://user:pass@ep-xxxx-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
   In Neon dashboard: **Connection details** → enable **Connection pooling** → copy that URL.
3. Optional pool settings (already in `render.yaml` for Blueprint deploys):

| Key | Value |
|-----|-------|
| `DATABASE_POOL_SIZE` | `5` |
| `DATABASE_MAX_OVERFLOW` | `5` |
| `DATABASE_POOL_RECYCLE` | `280` |
| `DATABASE_POOL_PRE_PING` | `true` |

4. **Manual Deploy** the API, open `/health` to wake it, then retry **Start conversation**.
