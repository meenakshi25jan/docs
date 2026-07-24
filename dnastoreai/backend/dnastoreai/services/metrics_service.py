"""Metrics aggregation service."""

from __future__ import annotations

from dnastoreai.core.config import Settings, ensure_directories
from dnastoreai.metrics.collector import AIMetrics, BiologicalMetrics, PlatformMetrics, RecoveryMetricsSummary, StorageMetrics
from dnastoreai.services.archive_service import ArchiveService


class MetricsService:
    """Aggregate platform-wide metrics."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = ensure_directories(settings)
        self.archive_service = ArchiveService(settings)

    def get_platform_metrics(self) -> PlatformMetrics:
        archives = self.archive_service.list_archives()
        if not archives:
            return PlatformMetrics()

        total_logical = sum(a["original_size"] for a in archives)
        total_dna = sum(a["total_dna_length"] for a in archives)

        return PlatformMetrics(
            storage=StorageMetrics(
                compression_ratio=1.0,
                dna_length=total_dna,
                logical_size=total_logical,
                physical_size=total_dna * 2,
                density=total_logical / max(total_dna * 2, 1),
            ),
            biological=BiologicalMetrics(),
            recovery=RecoveryMetricsSummary(),
            ai=AIMetrics(),
        )
