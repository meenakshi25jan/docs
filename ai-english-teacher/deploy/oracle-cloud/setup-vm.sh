#!/usr/bin/env bash
# Bootstrap Oracle Cloud Always Free VM for AI English Teacher
# Tested on: Ubuntu 22.04/24.04 ARM (Ampere A1)
#
# Usage (on the VM as ubuntu user):
#   curl -fsSL https://raw.githubusercontent.com/meenakshi25jan/docs/cursor/oracle-cloud-deploy-d164/ai-english-teacher/deploy/oracle-cloud/setup-vm.sh | bash
# Or after cloning:
#   cd ai-english-teacher/deploy/oracle-cloud && chmod +x setup-vm.sh && ./setup-vm.sh

set -euo pipefail

echo "==> AI English Teacher — Oracle Cloud VM setup"

# ── 1. System packages ───────────────────────────────────────────────────────
sudo apt-get update -qq
sudo apt-get install -y -qq git curl ca-certificates gnupg lsb-release ufw

# ── 2. Docker ─────────────────────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
  echo "==> Installing Docker..."
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker "$USER"
  echo "==> Docker installed. You may need to log out and back in for group changes."
fi

# Docker Compose plugin
if ! docker compose version &>/dev/null; then
  sudo apt-get install -y -qq docker-compose-plugin
fi

# ── 3. Firewall (UFW) ───────────────────────────────────────────────────────
echo "==> Configuring firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# ── 4. Clone or update repo ───────────────────────────────────────────────────
INSTALL_DIR="${INSTALL_DIR:-$HOME/ai-english-teacher}"
REPO_URL="${REPO_URL:-https://github.com/meenakshi25jan/docs.git}"
BRANCH="${BRANCH:-cursor/oracle-cloud-deploy-d164}"

if [ -d "$INSTALL_DIR/.git" ]; then
  echo "==> Updating existing repo at $INSTALL_DIR"
  cd "$INSTALL_DIR"
  git fetch origin
  git checkout "$BRANCH" 2>/dev/null || git checkout main
  git pull origin "$(git branch --show-current)" || true
else
  echo "==> Cloning repo to $INSTALL_DIR"
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR" 2>/dev/null || {
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR" && git checkout "$BRANCH" 2>/dev/null || true
  }
  cd "$INSTALL_DIR"
fi

DEPLOY_DIR="$INSTALL_DIR/ai-english-teacher/deploy/oracle-cloud"
cd "$DEPLOY_DIR"

# ── 5. Environment file ───────────────────────────────────────────────────────
if [ ! -f .env ]; then
  cp .env.example .env
  PUBLIC_IP=$(curl -s ifconfig.me || curl -s icanhazip.com || echo "YOUR_VM_IP")
  sed -i "s|PUBLIC_URL=http://YOUR_VM_PUBLIC_IP|PUBLIC_URL=http://${PUBLIC_IP}|" .env
  JWT=$(openssl rand -hex 32)
  sed -i "s|JWT_SECRET_KEY=change-me-use-openssl-rand-hex-32|JWT_SECRET_KEY=${JWT}|" .env
  echo ""
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  IMPORTANT: Edit .env and set DATABASE_URL before starting  ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""
  echo "  nano $DEPLOY_DIR/.env"
  echo ""
  echo "  Get a free Neon database: https://neon.tech"
  echo "  Then run: CREATE EXTENSION IF NOT EXISTS vector;"
  echo ""
fi

# ── 6. Deploy ─────────────────────────────────────────────────────────────────
echo "==> Building and starting containers (this may take 5–10 minutes)..."
docker compose -f docker-compose.oracle.yml --env-file .env --profile ollama up -d --build

# ── 7. Pull Ollama model (if using ollama profile) ───────────────────────────
if grep -q '^AI_PROVIDER=ollama' .env 2>/dev/null; then
  MODEL=$(grep '^OLLAMA_MODEL=' .env | cut -d= -f2 || echo "llama3.2")
  echo "==> Pulling Ollama model: $MODEL (may take several minutes)..."
  sleep 10
  docker compose -f docker-compose.oracle.yml exec -T ollama ollama pull "$MODEL" || \
    echo "==> Ollama pull failed — run manually: docker compose exec ollama ollama pull $MODEL"
fi

PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || grep PUBLIC_URL .env | cut -d= -f2 | sed 's|http://||')
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    Deployment complete!                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "  App:     http://${PUBLIC_IP}"
echo "  API:     http://${PUBLIC_IP}/api/v1"
echo "  Docs:    http://${PUBLIC_IP}/docs"
echo "  Health:  http://${PUBLIC_IP}/health"
echo ""
echo "  Logs:    docker compose -f $DEPLOY_DIR/docker-compose.oracle.yml logs -f"
echo "  Restart: docker compose -f $DEPLOY_DIR/docker-compose.oracle.yml restart"
echo ""
echo "  Don't forget to open ports 80/443 in OCI Console → VCN → Security List!"
echo ""
