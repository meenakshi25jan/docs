"""Unit tests for experiment runner."""

from pathlib import Path

from dnastoreai.experiments.runner import Experiment
from dnastoreai.modules.datasets.generators import TextDatasetGenerator


class TestExperiment:
    def test_run_experiment(self, tmp_path):
        files = TextDatasetGenerator().generate(2, min_size=50, max_size=200)
        exp = Experiment(
            files=files,
            encoding="basic",
            ecc="reed_solomon",
            output_dir=tmp_path,
        )
        result = exp.run()
        assert result.experiment_id
        assert result.summary["total_files"] == 2
        assert (tmp_path / result.experiment_id / "report.json").exists()
        assert (tmp_path / result.experiment_id / "report.csv").exists()
        assert (tmp_path / result.experiment_id / "report.html").exists()

    def test_from_dataset(self, tmp_path):
        exp = Experiment.from_dataset("text", count=2, output_dir=tmp_path)
        result = exp.run()
        assert len(result.file_results) == 2

    def test_result_to_dict(self, tmp_path):
        files = TextDatasetGenerator().generate(1, min_size=20, max_size=50)
        exp = Experiment(files=files, output_dir=tmp_path)
        result = exp.run()
        d = result.to_dict()
        assert "experiment_id" in d
        assert "summary" in d

    def test_empty_summary(self, tmp_path):
        exp = Experiment(files=[], output_dir=tmp_path)
        result = exp.run()
        assert result.summary == {}
