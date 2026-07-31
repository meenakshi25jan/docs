#!/usr/bin/env bash
# Backup database, reports, and ChromaDB data
# Usage: ./scripts/backup-data.sh

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$(dirname "$SCRIPT_DIR")"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/backup_$TIMESTAMP"

echo "[INFO] Creating backup in $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Backup SQLite database
if [ -f "data/research_agent.db" ]; then
  cp data/research_agent.db "$BACKUP_DIR/"
  echo "[OK] Database backed up"
fi

# Backup reports
if [ -d "reports" ] && [ "$(ls -A reports 2>/dev/null)" ]; then
  cp -r reports "$BACKUP_DIR/"
  echo "[OK] Reports backed up"
fi

# Backup ChromaDB
if [ -d "data/chroma" ]; then
  cp -r data/chroma "$BACKUP_DIR/"
  echo "[OK] Vector database backed up"
fi

# Create archive
tar -czf "backups/backup_$TIMESTAMP.tar.gz" -C backups "backup_$TIMESTAMP"
rm -rf "$BACKUP_DIR"

echo "[OK] Backup saved: backups/backup_$TIMESTAMP.tar.gz"
