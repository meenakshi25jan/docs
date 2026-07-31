"""Bootstrap sys.path so `app` resolves when scripts run as files or modules."""

from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent


def ensure_backend_on_sys_path() -> Path:
    """Insert backend root on sys.path so `import app` works."""
    root = str(BACKEND_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    return BACKEND_ROOT


def resolve_migrations_dir() -> Path | None:
    """Locate SQL migrations (build copy or source tree)."""
    env_dir = os.environ.get("MIGRATIONS_DIR", "").strip()
    if env_dir:
        candidate = Path(env_dir)
        if candidate.is_dir():
            return candidate

    candidates = [
        BACKEND_ROOT / "migrations",
        REPO_ROOT / "database" / "migrations",
    ]
    for path in candidates:
        if path.is_dir():
            return path
    return None


def list_migration_files() -> list[Path]:
    """Sorted SQL migration files from the resolved migrations directory."""
    migrations_dir = resolve_migrations_dir()
    if migrations_dir is None:
        return []
    return sorted(migrations_dir.glob("*.sql"))


def print_runtime_diagnostics(label: str = "migration-bootstrap") -> None:
    """Log cwd, PYTHONPATH, Python runtime, and path resolution for Render troubleshooting."""
    migrations = resolve_migrations_dir()
    migration_files = list_migration_files()
    print(f"==> [{label}] Working directory: {os.getcwd()}", flush=True)
    print(f"==> [{label}] Python executable: {sys.executable}", flush=True)
    print(
        f"==> [{label}] Python version: {sys.version.split()[0]}",
        flush=True,
    )
    print(f"==> [{label}] PYTHONPATH: {os.environ.get('PYTHONPATH', '(not set)')}", flush=True)
    print(f"==> [{label}] Backend root: {BACKEND_ROOT}", flush=True)
    print(f"==> [{label}] Repository root: {REPO_ROOT}", flush=True)
    print(
        f"==> [{label}] Migrations directory: {migrations or 'NOT FOUND'}",
        flush=True,
    )
    print(f"==> [{label}] Found {len(migration_files)} migration file(s)", flush=True)
    print(f"==> [{label}] sys.path: {sys.path[:8]}", flush=True)
