"""Archive management service."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from dnastoreai.core.config import Settings, ensure_directories
from dnastoreai.core.exceptions import ArchiveNotFoundError
from dnastoreai.modules.optimization.optimizer import gc_content
from dnastoreai.modules.optimization.optimizer import fitness_score as calc_fitness


class ArchiveService:
    """Manage DNA archives on the filesystem."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = ensure_directories(settings)

    def _archive_path(self, archive_id: str) -> Path:
        return self.settings.archive_dir / archive_id

    def list_archives(self) -> list[dict]:
        """List all archives."""
        archives = []
        if not self.settings.archive_dir.exists():
            return archives

        for path in sorted(self.settings.archive_dir.iterdir()):
            manifest = path / "manifest.json"
            if manifest.exists():
                data = json.loads(manifest.read_text())
                archives.append({
                    "id": data["archive_id"],
                    "filename": data["filename"],
                    "file_type": Path(data["filename"]).suffix.lstrip("."),
                    "original_size": data["original_size"],
                    "total_dna_length": sum(len(b["sequence"]) for b in data.get("blocks", [])),
                    "num_blocks": len(data.get("blocks", [])),
                    "encoding": data.get("config", {}).get("encoding", "gc_balanced"),
                    "created_at": data.get("created_at", datetime.now(UTC).isoformat()),
                })
        return archives

    def get_dna(self, archive_id: str, block_index: int = 0) -> dict:
        """Get DNA sequence for an archive block."""
        archive_path = self._archive_path(archive_id)
        manifest_path = archive_path / "manifest.json"

        if not manifest_path.exists():
            raise ArchiveNotFoundError(archive_id)

        manifest = json.loads(manifest_path.read_text())
        blocks = manifest.get("blocks", [])
        if block_index >= len(blocks):
            raise ArchiveNotFoundError(f"{archive_id}/block/{block_index}")

        block = blocks[block_index]
        sequence = block["sequence"]
        return {
            "id": block["header"]["block_id"],
            "archive_id": archive_id,
            "block_index": block_index,
            "sequence": sequence,
            "fitness_score": calc_fitness(sequence),
            "gc_content": gc_content(sequence),
            "length": len(sequence),
        }

    def get_archive(self, archive_id: str) -> dict:
        """Get full archive metadata."""
        manifest_path = self._archive_path(archive_id) / "manifest.json"
        if not manifest_path.exists():
            raise ArchiveNotFoundError(archive_id)
        return json.loads(manifest_path.read_text())
