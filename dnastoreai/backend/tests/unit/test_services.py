"""Unit tests for services."""

from dnastoreai.core.config import Settings
from dnastoreai.models.schemas import ExperimentRequest
from dnastoreai.services.experiment_service import ExperimentService
from dnastoreai.services.metrics_service import MetricsService


class TestServices:
    def test_metrics_service_empty(self, tmp_path):
        settings = Settings(data_dir=tmp_path, archive_dir=tmp_path / "archive")
        service = MetricsService(settings)
        metrics = service.get_platform_metrics()
        assert metrics.storage.dna_length == 0

    def test_experiment_service(self, tmp_path):
        settings = Settings(
            data_dir=tmp_path,
            archive_dir=tmp_path / "archive",
            experiment_dir=tmp_path / "experiments",
        )
        service = ExperimentService(settings)
        result = service.run_experiment(
            ExperimentRequest(name="test", dataset_type="text", file_count=1)
        )
        assert "experiment_id" in result
