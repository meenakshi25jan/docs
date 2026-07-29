#!/usr/bin/env bash
# One-shot deploy on Oracle Cloud VM (run after SSH login as ubuntu).
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/meenakshi25jan/docs/main/ai-english-teacher/deploy/oracle-cloud/deploy-now.sh | bash
#
# With secrets (no prompts):
#   DATABASE_URL="postgresql://..." GROQ_KEY="gsk_..." bash deploy-now.sh
#
# Prerequisites:
#   - Ubuntu 24.04 ARM VM (Ampere A1, 1 OCPU / 6 GB+)
#   - Ports 80 and 443 open in OCI Security List
#   - Neon: CREATE EXTENSION IF NOT EXISTS vector;
#   - Groq key: https://console.groq.com

set -euo pipefail

INSTALL_DIR="${INSTALL_DIR:-$HOME/docs}"
DEPLOY_DIR="$INSTALL_DIR/ai-english-teacher/deploy/oracle-cloud"
REPO_URL="https://github.com/meenakshi25jan/docs.git"
BRANCH="main"

echo "==> AI English Teacher — one-shot deploy"
echo "==> Create VM: https://cloud.oracle.com/compute/instances/create?region=ap-mumbai-1"
echo ""

# ── Secrets ───────────────────────────────────────────────────────────────────
if [ -z "${DATABASE_URL:-}" ]; then
  read -rp "Paste Neon DATABASE_URL: " DATABASE_URL
fi
if [ -z "${GROQ_KEY:-}" ]; then
  read -rp "Paste Groq API key (gsk_...): " GROQ_KEY
fi

PUBLIC_IP=$(curl -s --max-time 5 ifconfig.me 2>/dev/null || curl -s --max-time 5 icanhazip.com 2>/dev/null || true)
if [ -z "$PUBLIC_IP" ]; then
  read -rp "Enter VM public IP: " PUBLIC_IP
fi

# ── Docker ────────────────────────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
  echo "==> Installing Docker..."
  sudo apt-get update -qq
  sudo apt-get install -y -qq git curl ca-certificates openssl
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker "$USER"
  if ! groups | grep -q docker; then
    echo "==> Log out and SSH back in, then re-run this script."
    exit 1
  fi
fi

if ! docker compose version &>/dev/null 2>&1; then
  sudo apt-get install -y -qq docker-compose-plugin
fi

# ── Firewall ──────────────────────────────────────────────────────────────────
sudo ufw allow OpenSSH 2>/dev/null || true
sudo ufw allow 80/tcp 2>/dev/null || true
sudo ufw allow 443/tcp 2>/dev/null || true
sudo ufw --force enable 2>/dev/null || true

# ── Clone repo ────────────────────────────────────────────────────────────────
if [ -d "$INSTALL_DIR/.git" ]; then
  cd "$INSTALL_DIR"
  git fetch origin
  git checkout "$BRANCH"
  git pull origin "$BRANCH" || true
else
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
fi

cd "$DEPLOY_DIR"

# ── .env ──────────────────────────────────────────────────────────────────────
JWT=$(openssl rand -hex 32)
cat > .env <<EOF
DATABASE_URL=${DATABASE_URL}
JWT_SECRET_KEY=${JWT}
PUBLIC_URL=http://${PUBLIC_IP}

AI_PROVIDER=openai
OPENAI_API_KEY=${GROQ_KEY}
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.1-8b-instant

SKIP_MIGRATIONS=false
DEBUG=false
EOF

# ── Deploy ────────────────────────────────────────────────────────────────────
echo "==> Building and starting (5–15 min on first run)..."
docker compose -f docker-compose.oracle.yml --env-file .env up -d --build

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    Deploy complete!                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "  Register:  http://${PUBLIC_IP}/register"
echo "  Chat:      http://${PUBLIC_IP}/conversation"
echo "  Health:    http://${PUBLIC_IP}/health"
echo "  Mobile:    EXPO_PUBLIC_API_URL=http://${PUBLIC_IP}/api/v1"
echo ""
echo "  Logs: cd $DEPLOY_DIR && docker compose -f docker-compose.oracle.yml logs -f"
echo ""
