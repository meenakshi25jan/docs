"""Unit tests for metrics collector."""

from dnastoreai.metrics.collector import (
    AIMetrics,
    BiologicalMetrics,
    PlatformMetrics,
    RecoveryMetricsSummary,
    StorageMetrics,
    compute_biological_metrics,
    compute_storage_metrics,
)


class TestMetrics:
    def test_storage_metrics(self):
        m = compute_storage_metrics(1000, 500, 2000)
        assert m.compression_ratio == 2.0
        assert m.density > 0

    def test_biological_metrics(self):
        m = compute_biological_metrics("ACGTACGTACGT")
        assert 0 <= m.gc_content <= 1

    def test_platform_metrics_to_dict(self):
        m = PlatformMetrics(
            storage=StorageMetrics(dna_length=100),
            biological=BiologicalMetrics(gc_content=0.5),
            recovery=RecoveryMetricsSummary(recovery_accuracy=0.95),
            ai=AIMetrics(prediction_accuracy=0.8),
        )
        d = m.to_dict()
        assert "storage" in d
        assert "biological" in d

    def test_individual_to_dict(self):
        assert "compression_ratio" in StorageMetrics(compression_ratio=2.0).to_dict()
        assert "gc_content" in BiologicalMetrics().to_dict()
        assert "recovery_accuracy" in RecoveryMetricsSummary().to_dict()
        assert "confidence_score" in AIMetrics().to_dict()
