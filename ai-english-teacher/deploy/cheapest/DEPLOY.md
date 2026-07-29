# Cheapest Cloud Deployment ($0/month)

> **See also:** [RUNBOOK.md](../../RUNBOOK.md) — complete prerequisites, deployment, and error catalog in one document.

Deploy the AI English Teacher platform for **$0/month** using free tiers.

## Recommended Stack (cheapest)

| Component | Provider | Cost | Why |
|-----------|----------|------|-----|
| PostgreSQL + pgvector | [Neon](https://neon.tech) | **$0** | 0.5 GB free forever, pgvector support |
| Backend API | [Render](https://render.com) | **$0** | 750 free instance-hours/month |
| Frontend | [Vercel](https://vercel.com) | **$0** | Unlimited hobby deployments, global CDN |
| Redis | Skipped | **$0** | Not required for MVP (optional later) |

**Total: $0/month** for hobby/low-traffic usage.

> Render free tier services **sleep after 15 minutes** of inactivity (cold start ~30s).
> For always-on backend, upgrade Render to Starter ($7/mo) or use Fly.io (~$3/mo).

---

## Option A: One-Click Render Deploy (easiest)

### 1. Create free database on Neon

1. Sign up at https://neon.tech
2. Create project: `ai-english-teacher`
3. Copy the connection string: `postgresql://user:pass@host/db?sslmode=require`
4. In Neon SQL editor, run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### 2. Deploy on Render

1. Go to https://dashboard.render.com/blueprints
2. Click **New Blueprint Instance**
3. Connect your GitHub repo
4. Render detects `ai-english-teacher/render.yaml` automatically
5. When prompted, set `DATABASE_URL` to your Neon connection string
6. Click **Apply**

Render deploys both backend and frontend. URLs:
- API: `https://ai-english-teacher-api.onrender.com`
- Web: `https://ai-english-teacher-web.onrender.com`
- Docs: `https://ai-english-teacher-api.onrender.com/docs`

### 3. (Optional) Deploy frontend on Vercel for faster loads

```bash
cd ai-english-teacher/frontend
npx vercel --prod
# Set env: NEXT_PUBLIC_API_URL=https://ai-english-teacher-api.onrender.com/api/v1
```

Update `CORS_ORIGINS` in Render backend settings to include your Vercel URL.

---

## Option B: Fly.io Backend (~$0–3/month)

Best if you want a single-command backend deploy with auto-scaling to zero.

```bash
cd ai-english-teacher

# Install Fly CLI: https://fly.io/docs/hands-on/install-flyctl/
fly auth login

# Launch (uses fly.toml)
fly launch --no-deploy --copy-config

# Set secrets
fly secrets set \
  DATABASE_URL="postgresql://..." \
  JWT_SECRET_KEY="$(openssl rand -hex 32)" \
  CORS_ORIGINS='["https://your-app.vercel.app"]'

# Deploy
fly deploy
```

Pair with Neon (free DB) + Vercel (free frontend) for total $0–3/month.

---

## Option C: Automated script

```bash
cd ai-english-teacher
chmod +x deploy/cheapest/deploy.sh
./deploy/cheapest/deploy.sh
```

The script walks you through Neon setup, runs migrations, and prints Render/Fly deploy commands.

---

## Environment Variables

### Backend (required)

| Variable | Example | Notes |
|----------|---------|-------|
| `DATABASE_URL` | `postgresql://...@neon.tech/db` | From Neon dashboard |
| `JWT_SECRET_KEY` | auto-generated | Render generates this |
| `CORS_ORIGINS` | `["https://your-app.vercel.app"]` | JSON array of allowed origins |

### Backend (optional — enables real AI)

| Variable | Notes |
|----------|-------|
| `OPENAI_API_KEY` | OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI key |

Without AI keys, the platform runs in **mock mode** (returns sample scores).

### Frontend

| Variable | Example |
|----------|---------|
| `NEXT_PUBLIC_API_URL` | `https://ai-english-teacher-api.onrender.com/api/v1` |

---

## Cost Comparison

| Provider | Monthly Cost | Notes |
|----------|-------------|-------|
| **Neon + Render + Vercel** | **$0** | Recommended cheapest |
| Fly.io + Neon + Vercel | $0–3 | Backend scales to zero |
| Azure AKS (original design) | ~$8,100 | Production scale |
| AWS EKS | ~$7,500 | Production scale |
| Hetzner VPS (CX22) | ~€4 | DIY docker-compose |
| **Oracle Cloud Free** | **$0** | 4 ARM cores, 24 GB — [OCI guide](../oracle-cloud/OCI_DEPLOY.md) |

---

## Troubleshooting

**Cold start slow on Render?** Free tier sleeps after 15 min. First request takes ~30s. Upgrade to Starter ($7/mo) or use Fly.io with `min_machines_running = 1`.

**Database connection fails?** Ensure Neon connection string includes `?sslmode=require`. Render sets `DATABASE_URL` automatically if linked.

**CORS errors?** Add your frontend URL to `CORS_ORIGINS` in backend env vars.

**Migrations failed?** Run manually:
```bash
cd ai-english-teacher/backend
DATABASE_URL="your-neon-url" MIGRATIONS_DIR=../database/migrations python3 scripts/migrate.py
```
