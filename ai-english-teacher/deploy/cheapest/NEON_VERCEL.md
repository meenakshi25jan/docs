# Deploy: Neon + Vercel + Render ($0/month)

Your accounts:
- **Neon:** https://console.neon.tech/app/org-plain-unit-29140140/projects
- **Vercel:** https://vercel.com/meenakshi25jans-projects

---

## Step 1 — Create Neon database (your screenshot)

On the **Create project** screen, use:

| Field | Value |
|-------|-------|
| Project name | `ai-english-teacher` |
| Postgres version | `18` (keep default) |
| Region | `AWS US East 2 (Ohio)` ✓ (matches Vercel US East) |
| Enable Neon Auth | **Off** (we use our own JWT auth) |

Click **Create**.

Then:
1. Click **Connect** on the project dashboard
2. Copy the connection string (`postgresql://...?sslmode=require`)
3. Open **SQL Editor** and run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

---

## Step 2 — Deploy frontend on Vercel

1. Go to https://vercel.com/meenakshi25jans-projects
2. Click **Add New… → Project**
3. Import your GitHub repo `meenakshi25jan/docs`
4. Configure:

| Setting | Value |
|---------|-------|
| Root Directory | `ai-english-teacher/frontend` |
| Framework Preset | Next.js (auto-detected) |
| Build Command | `npm run build` |
| Output Directory | *(leave default — do not set `.next`)* |

5. **Environment Variables** (add before deploy):

| Name | Value |
|------|-------|
| `NEXT_PUBLIC_API_URL` | `https://ai-english-teacher-api.onrender.com/api/v1` *(update after Step 3)* |

6. Click **Deploy**

Your frontend URL will be something like:
`https://ai-english-teacher-xxxx.vercel.app`

---

## Step 3 — Deploy backend on Render (free API)

1. Go to https://dashboard.render.com/blueprints
2. **New Blueprint Instance** → connect `meenakshi25jan/docs`
3. When asked which blueprint file, use **`render.yaml`** at **repo root** (API + web)
   - Or create a **Web Service** manually:
     - Root: `ai-english-teacher/backend`
     - Build: `pip install -r requirements-render.txt && mkdir -p migrations && cp -r ../database/migrations/* migrations/ && chmod +x start.sh`
     - Start: `bash ./start.sh`
4. Set environment variables:

| Name | Value |
|------|-------|
| `DATABASE_URL` | Your Neon connection string from Step 1 |
| `CORS_ORIGINS` | `["https://YOUR-APP.vercel.app","http://localhost:3000"]` |
| `JWT_SECRET_KEY` | Any long random string |

5. Deploy → API URL: `https://ai-english-teacher-api.onrender.com`

---

## Step 4 — Connect frontend to API

Back in **Vercel → Project → Settings → Environment Variables**:

```
NEXT_PUBLIC_API_URL = https://ai-english-teacher-api.onrender.com/api/v1
```

Click **Redeploy** for the change to take effect.

---

## Step 5 — Run migrations (if not auto-applied)

From your machine or paste `DATABASE_URL` here for the agent to run:

```bash
cd ai-english-teacher/backend
pip install asyncpg
DATABASE_URL="postgresql://..." MIGRATIONS_DIR=../database/migrations python3 scripts/migrate.py
```

---

## Verify

| Check | URL |
|-------|-----|
| API health | `https://ai-english-teacher-api.onrender.com/health` |
| API docs | `https://ai-english-teacher-api.onrender.com/docs` |
| Frontend | `https://your-app.vercel.app` |
| Register user | Frontend → Get Started |

---

## Cost

| Service | Cost |
|---------|------|
| Neon (0.5 GB, scales to zero) | $0 |
| Vercel (hobby) | $0 |
| Render (free tier, sleeps when idle) | $0 |
| **Total** | **$0/month** |

---

## Troubleshooting

**CORS error in browser?**  
Update `CORS_ORIGINS` on Render to include your exact Vercel URL (with `https://`).

**API cold start slow?**  
Render free tier sleeps after 15 min. First request takes ~30s.

**Build fails on Vercel?**  
Ensure Root Directory is `ai-english-teacher/frontend`, not repo root.
