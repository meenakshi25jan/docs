"""Knowledge ingestion pipeline — extract, chunk, and persist source material."""

from app.ingestion.ingestion_orchestrator import IngestionOrchestrator

__all__ = ["IngestionOrchestrator"]
