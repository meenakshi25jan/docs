"""Experiment management service."""

from __future__ import annotations

from dnastoreai.core.config import Settings, ensure_directories
from dnastoreai.experiments.runner import Experiment
from dnastoreai.models.schemas import ExperimentRequest


class ExperimentService:
    """Run and manage research experiments."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = ensure_directories(settings)

    def run_experiment(self, request: ExperimentRequest) -> dict:
        experiment = Experiment.from_dataset(
            dataset_type=request.dataset_type,
            count=request.file_count,
            encoding=request.encoding,
            ecc=request.ecc,
            sequencing=request.sequencing,
            compression=request.compression,
            name=request.name,
            output_dir=self.settings.experiment_dir,
        )
        result = experiment.run()
        return result.to_dict()
