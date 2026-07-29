#!/usr/bin/env bash
# Bootstrap Oracle Cloud Always Free VM for AI English Teacher
# Tested on: Ubuntu 22.04/24.04 ARM (Ampere A1)
#
# Usage (on the VM as ubuntu user):
#   curl -fsSL https://raw.githubusercontent.com/meenakshi25jan/docs/cursor/oracle-cloud-deploy-d164/ai-english-teacher/deploy/oracle-cloud/setup-vm.sh | bash
#
# Full guide: deploy/oracle-cloud/VM_SETUP.md

set -euo pipefail

echo "==> AI English Teacher — Oracle Cloud VM setup"
echo "==> Guide: https://github.com/meenakshi25jan/docs/blob/cursor/oracle-cloud-deploy-d164/ai-english-teacher/deploy/oracle-cloud/VM_SETUP.md"
echo ""

# ── 1. System packages ───────────────────────────────────────────────────────
sudo apt-get update -qq
sudo apt-get install -y -qq git curl ca-certificates gnupg lsb-release ufw openssl

# ── 2. Docker ─────────────────────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
  echo "==> Installing Docker..."
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker "$USER"
  echo "==> Docker installed."
fi

# Docker Compose plugin
if ! docker compose version &>/dev/null 2>&1; then
  sudo apt-get install -y -qq docker-compose-plugin
fi

# Use docker without re-login if possible
if groups | grep -q docker; then
  DOCKER="docker"
else
  DOCKER="sudo docker"
  echo "==> Using sudo for docker (log out/in to avoid sudo)"
fi

# ── 3. Firewall (UFW) ───────────────────────────────────────────────────────
echo "==> Configuring firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# ── 4. Clone or update repo ───────────────────────────────────────────────────
INSTALL_DIR="${INSTALL_DIR:-$HOME/docs}"
REPO_URL="${REPO_URL:-https://github.com/meenakshi25jan/docs.git}"
BRANCH="${BRANCH:-cursor/oracle-cloud-deploy-d164}"

if [ -d "$INSTALL_DIR/.git" ]; then
  echo "==> Updating existing repo at $INSTALL_DIR"
  cd "$INSTALL_DIR"
  git fetch origin
  git checkout "$BRANCH" 2>/dev/null || git checkout main
  git pull origin "$(git branch --show-current)" 2>/dev/null || true
else
  echo "==> Cloning repo to $INSTALL_DIR"
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR" 2>/dev/null || {
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR" && git checkout "$BRANCH" 2>/dev/null || true
  }
fi

DEPLOY_DIR="$INSTALL_DIR/ai-english-teacher/deploy/oracle-cloud"
cd "$DEPLOY_DIR"

# ── 5. Environment file ───────────────────────────────────────────────────────
if [ ! -f .env ]; then
  cp .env.example .env
  PUBLIC_IP=$(curl -s --max-time 5 ifconfig.me || curl -s --max-time 5 icanhazip.com || echo "YOUR_VM_IP")
  sed -i "s|PUBLIC_URL=http://YOUR_VM_PUBLIC_IP|PUBLIC_URL=http://${PUBLIC_IP}|" .env
  JWT=$(openssl rand -hex 32)
  sed -i "s|JWT_SECRET_KEY=change-me-use-openssl-rand-hex-32|JWT_SECRET_KEY=${JWT}|" .env
fi

# Check DATABASE_URL is set
if grep -q 'DATABASE_URL=postgresql://user:password@' .env 2>/dev/null || \
   grep -q 'DATABASE_URL=$' .env 2>/dev/null; then
  echo ""
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  STOP: Set DATABASE_URL in .env before deploying            ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""
  echo "  1. Get free DB: https://neon.tech"
  echo "  2. Run in Neon SQL: CREATE EXTENSION IF NOT EXISTS vector;"
  echo "  3. Edit: nano $DEPLOY_DIR/.env"
  echo "  4. Set DATABASE_URL=postgresql://...@ep-xxx.neon.tech/neondb?sslmode=require"
  echo "  5. Re-run: bash $DEPLOY_DIR/setup-vm.sh"
  echo ""
  exit 1
fi

# ── 6. Deploy ─────────────────────────────────────────────────────────────────
echo "==> Building and starting containers (5–10 minutes on first run)..."
$DOCKER compose -f docker-compose.oracle.yml --env-file .env --profile ollama up -d --build

# ── 7. Pull Ollama model (if using ollama) ───────────────────────────────────
if grep -q '^AI_PROVIDER=ollama' .env 2>/dev/null; then
  MODEL=$(grep '^OLLAMA_MODEL=' .env | cut -d= -f2- | tr -d '"' || echo "llama3.2")
  echo "==> Pulling Ollama model: $MODEL (5–15 min)..."
  sleep 15
  $DOCKER compose -f docker-compose.oracle.yml exec -T ollama ollama pull "$MODEL" || \
    echo "==> Run manually: docker compose exec ollama ollama pull $MODEL"
fi

PUBLIC_IP=$(curl -s --max-time 5 ifconfig.me 2>/dev/null || grep '^PUBLIC_URL=' .env | cut -d= -f2 | sed 's|http://||')
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    Deployment complete!                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "  App:     http://${PUBLIC_IP}"
echo "  Register: http://${PUBLIC_IP}/register"
echo "  Chat:    http://${PUBLIC_IP}/conversation"
echo "  Docs:    http://${PUBLIC_IP}/docs"
echo "  Health:  http://${PUBLIC_IP}/health"
echo ""
echo "  Logs:    cd $DEPLOY_DIR && docker compose -f docker-compose.oracle.yml logs -f"
echo ""
