"""Research experiment framework with report generation."""

from __future__ import annotations

import csv
import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dnastoreai.modules.compression.compressor import compress, compression_ratio
from dnastoreai.modules.datasets.generators import GeneratedFile, get_dataset_generator
from dnastoreai.modules.optimization.optimizer import fitness_score, optimize_sequence
from dnastoreai.services.pipeline_service import PipelineConfig, PipelineService


@dataclass
class ExperimentConfig:
    """Configuration for a research experiment."""

    encoding: str = "gc_balanced"
    ecc: str = "reed_solomon"
    compression: str = "gzip"
    sequencing: str = "illumina"
    block_size: int = 4096
    substitution_rate: float = 0.001
    degradation_years: float = 1.0
    coverage_depth: int = 30
    name: str = "experiment"


@dataclass
class ExperimentResult:
    """Result of a single experiment run."""

    experiment_id: str
    config: ExperimentConfig
    file_results: list[dict[str, Any]]
    summary: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "config": self.config.__dict__,
            "file_results": self.file_results,
            "summary": self.summary,
            "timestamp": self.timestamp,
        }


class Experiment:
    """Research experiment runner."""

    def __init__(
        self,
        files: list[GeneratedFile] | None = None,
        encoding: str = "gc_balanced",
        ecc: str = "reed_solomon",
        sequencing: str = "illumina",
        compression: str = "gzip",
        name: str = "experiment",
        output_dir: Path | None = None,
    ) -> None:
        self.files = files or []
        self.config = ExperimentConfig(
            encoding=encoding,
            ecc=ecc,
            sequencing=sequencing,
            compression=compression,
            name=name,
        )
        self.output_dir = output_dir or Path("./data/experiments")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pipeline = PipelineService()

    def run(self) -> ExperimentResult:
        """Execute the experiment on all files."""
        experiment_id = str(uuid.uuid4())
        file_results: list[dict[str, Any]] = []

        for gf in self.files:
            config = PipelineConfig(
                compression=self.config.compression,
                encoding=self.config.encoding,
                ecc=self.config.ecc,
                sequencing=self.config.sequencing,
                block_size=self.config.block_size,
                substitution_rate=self.config.substitution_rate,
                degradation_time_years=self.config.degradation_years,
                coverage_depth=self.config.coverage_depth,
            )
            store_result = self.pipeline.store(gf.data, gf.filename, config)
            retrieve_result = self.pipeline.retrieve(store_result.archive_id, config)

            file_results.append({
                "filename": gf.filename,
                "file_type": gf.file_type,
                "original_size": len(gf.data),
                "archive_id": store_result.archive_id,
                "dna_length": store_result.total_dna_length,
                "compression_ratio": store_result.compression_ratio,
                "recovery_accuracy": retrieve_result.metrics.recovery.recovery_accuracy,
                "checksum_valid": retrieve_result.checksum_valid,
                "fitness_score": fitness_score(store_result.sequences[0] if store_result.sequences else ""),
            })

        summary = self._compute_summary(file_results)
        result = ExperimentResult(
            experiment_id=experiment_id,
            config=self.config,
            file_results=file_results,
            summary=summary,
        )

        self._generate_reports(result)
        return result

    def _compute_summary(self, file_results: list[dict[str, Any]]) -> dict[str, Any]:
        if not file_results:
            return {}
        n = len(file_results)
        return {
            "total_files": n,
            "avg_compression_ratio": sum(r["compression_ratio"] for r in file_results) / n,
            "avg_recovery_accuracy": sum(r["recovery_accuracy"] for r in file_results) / n,
            "avg_fitness_score": sum(r["fitness_score"] for r in file_results) / n,
            "success_rate": sum(1 for r in file_results if r["checksum_valid"]) / n,
        }

    def _generate_reports(self, result: ExperimentResult) -> None:
        exp_dir = self.output_dir / result.experiment_id
        exp_dir.mkdir(parents=True, exist_ok=True)

        # JSON report
        (exp_dir / "report.json").write_text(json.dumps(result.to_dict(), indent=2))

        # CSV report
        if result.file_results:
            with open(exp_dir / "report.csv", "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=result.file_results[0].keys())
                writer.writeheader()
                writer.writerows(result.file_results)

        # HTML report
        html = self._generate_html_report(result)
        (exp_dir / "report.html").write_text(html)

    def _generate_html_report(self, result: ExperimentResult) -> str:
        rows = "".join(
            f"<tr><td>{r['filename']}</td><td>{r['original_size']}</td>"
            f"<td>{r['compression_ratio']:.2f}</td><td>{r['recovery_accuracy']:.2%}</td>"
            f"<td>{'✓' if r['checksum_valid'] else '✗'}</td></tr>"
            for r in result.file_results
        )
        return f"""<!DOCTYPE html>
<html><head><title>Experiment {result.experiment_id}</title>
<style>body{{font-family:sans-serif;margin:2em}}table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #ddd;padding:8px;text-align:left}}th{{background:#1a237e;color:white}}</style>
</head><body>
<h1>DNAStoreAI Experiment Report</h1>
<p>ID: {result.experiment_id} | Encoding: {result.config.encoding} | ECC: {result.config.ecc}</p>
<h2>Summary</h2>
<pre>{json.dumps(result.summary, indent=2)}</pre>
<h2>File Results</h2>
<table><tr><th>File</th><th>Size</th><th>Compression</th><th>Recovery</th><th>Valid</th></tr>
{rows}</table></body></html>"""

    @classmethod
    def from_dataset(
        cls,
        dataset_type: str = "mixed",
        count: int = 5,
        **kwargs: Any,
    ) -> Experiment:
        generator = get_dataset_generator(dataset_type)
        files = generator.generate(count)
        return cls(files=files, **kwargs)
