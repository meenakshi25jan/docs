#!/usr/bin/env bash
# Deploy AI English Teacher to the cheapest $0/month cloud stack:
#   - Neon (free PostgreSQL)  →  https://neon.tech
#   - Render (free web tier)  →  https://render.com
#   - Vercel (free frontend)  →  https://vercel.com  (optional, faster frontend)
#
# Total cost: $0/month for hobby/low-traffic usage.
#
# Prerequisites:
#   1. Create a free Neon project → copy the connection string
#   2. Create a free Render account → connect this GitHub repo
#   3. (Optional) Create a free Vercel account for frontend CDN

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  AI English Teacher — Cheapest Cloud Deploy ($0/month)       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ── Step 1: Neon Database (free) ─────────────────────────────────────────────
echo "STEP 1: Create free PostgreSQL on Neon"
echo "  → Go to https://console.neon.tech"
echo "  → Create project: ai-english-teacher"
echo "  → Copy the connection string (postgresql://...)"
echo "  → Enable pgvector: run in SQL editor:"
echo "      CREATE EXTENSION IF NOT EXISTS vector;"
echo ""

if [ -z "${DATABASE_URL:-}" ]; then
  read -rp "Paste your Neon DATABASE_URL: " DATABASE_URL
fi

# ── Step 2: Render Backend ───────────────────────────────────────────────────
echo ""
echo "STEP 2: Deploy backend on Render (free tier)"
echo "  → Go to https://dashboard.render.com/blueprints"
echo "  → Click 'New Blueprint Instance'"
echo "  → Connect this GitHub repo"
echo "  → Set root directory: ai-english-teacher"
echo "  → Render will read render.yaml automatically"
echo ""
echo "  Required env var in Render dashboard:"
echo "    DATABASE_URL = $DATABASE_URL"
echo ""

# ── Step 3: Vercel Frontend (optional, recommended) ─────────────────────────
echo "STEP 3 (optional): Deploy frontend on Vercel (faster than Render free tier)"
echo "  cd $PROJECT_DIR/frontend"
echo "  npx vercel --prod"
echo "  Set env: NEXT_PUBLIC_API_URL=https://ai-english-teacher-api.onrender.com/api/v1"
echo ""

# ── Step 4: Fly.io alternative ────────────────────────────────────────────────
echo "ALTERNATIVE: Deploy backend on Fly.io (~\$0-3/month)"
echo "  cd $PROJECT_DIR"
echo "  fly auth login"
echo "  fly launch --no-deploy --copy-config"
echo "  fly secrets set DATABASE_URL=\"$DATABASE_URL\""
echo "  fly secrets set JWT_SECRET_KEY=\"\$(openssl rand -hex 32)\""
echo "  fly secrets set CORS_ORIGINS='[\"https://your-frontend.vercel.app\"]'"
echo "  fly deploy"
echo ""

# ── Run migrations locally against Neon ─────────────────────────────────────
echo "Running migrations against your Neon database..."
export DATABASE_URL
export MIGRATIONS_DIR="$PROJECT_DIR/database/migrations"
cd "$PROJECT_DIR/backend"
pip install -q asyncpg 2>/dev/null || pip3 install -q asyncpg
python3 scripts/migrate.py
echo ""
echo "✓ Migrations applied to Neon"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Your $0/month stack:"
echo "    Database:  Neon (free — 0.5 GB)"
echo "    Backend:   Render free tier (sleeps after 15 min idle)"
echo "    Frontend:  Render free tier OR Vercel (always-on CDN)"
echo "    Redis:     Not required (skipped to save cost)"
echo "    Est. cost: \$0/month"
echo "═══════════════════════════════════════════════════════════════"
