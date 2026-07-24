"""End-to-end DNA storage pipeline service."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dnastoreai.core.config import Settings, ensure_directories
from dnastoreai.metrics.collector import (
    PlatformMetrics,
    RecoveryMetricsSummary,
    compute_biological_metrics,
    compute_storage_metrics,
)
from dnastoreai.modules.compression.compressor import compress, compression_ratio, decompress
from dnastoreai.modules.degradation.simulator import DegradationParameters, DegradationSimulator
from dnastoreai.modules.metadata.header import DNAHeader
from dnastoreai.modules.optimization.optimizer import fitness_score, optimize_sequence
from dnastoreai.modules.reconstruction.engine import EncodedBlock, ReconstructionEngine
from dnastoreai.modules.segmentation.segmenter import segment
from dnastoreai.modules.sequencing.simulator import get_sequencing_simulator
from dnastoreai.modules.synthesis.simulator import SynthesisSimulator


@dataclass
class PipelineConfig:
    compression: str = "gzip"
    encoding: str = "gc_balanced"
    ecc: str = "reed_solomon"
    block_size: int = 4096
    optimize: bool = True
    substitution_rate: float = 0.001
    insertion_rate: float = 0.0001
    deletion_rate: float = 0.0001
    degradation_temperature: float = 25.0
    degradation_humidity: float = 50.0
    degradation_time_years: float = 1.0
    sequencing: str = "illumina"
    coverage_depth: int = 30


@dataclass
class StoreResult:
    archive_id: str
    filename: str
    original_size: int
    compressed_size: int
    total_dna_length: int
    num_blocks: int
    compression_ratio: float
    sequences: list[str]
    metrics: PlatformMetrics
    checksum: str


@dataclass
class RetrieveResult:
    archive_id: str
    filename: str
    data: bytes
    checksum_valid: bool
    metrics: PlatformMetrics
    missing_blocks: list[int] = field(default_factory=list)


@dataclass
class SimulateResult:
    archive_id: str
    synthesis_stats: dict[str, Any] | None = None
    degradation_stats: dict[str, Any] | None = None
    sequencing_stats: dict[str, Any] | None = None


class PipelineService:
    """Orchestrates the full DNA storage pipeline."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = ensure_directories(settings)

    def _archive_path(self, archive_id: str) -> Path:
        return self.settings.archive_dir / archive_id

    def store(self, data: bytes, filename: str, config: PipelineConfig | None = None) -> StoreResult:
        """Encode and store a file in the DNA archive."""
        cfg = config or PipelineConfig()
        archive_id = str(uuid.uuid4())
        archive_path = self._archive_path(archive_id)
        archive_path.mkdir(parents=True, exist_ok=True)

        # Compression
        compressed = compress(data, cfg.compression)  # type: ignore[arg-type]
        comp_ratio = compression_ratio(data, compressed)

        # Segmentation
        seg_result = segment(compressed, block_size=cfg.block_size, file_id=archive_id)

        # Encoding
        engine = ReconstructionEngine(encoding_method=cfg.encoding, ecc_type=cfg.ecc)
        encoded_blocks: list[EncodedBlock] = []
        sequences: list[str] = []

        for block in seg_result.blocks:
            header = DNAHeader(
                file_id=archive_id,
                block_id=block.metadata.block_id,
                block_index=block.metadata.block_index,
                total_blocks=block.metadata.total_blocks,
                checksum=block.metadata.checksum,
                encoding_version="1.0",
                ecc_type=cfg.ecc,
            )
            encoded = engine.encode_block(block, header)
            seq = encoded.dna_sequence

            if cfg.optimize:
                opt = optimize_sequence(seq)
                seq = opt.optimized_sequence
                encoded = EncodedBlock(header=header, dna_sequence=seq, ecc_encoded_data=encoded.ecc_encoded_data)

            encoded_blocks.append(encoded)
            sequences.append(seq)

        checksum = hashlib.sha256(data).hexdigest()
        total_dna_length = sum(len(s) for s in sequences)

        # Persist archive
        archive_data = {
            "archive_id": archive_id,
            "filename": filename,
            "original_size": len(data),
            "compressed_size": len(compressed),
            "checksum": checksum,
            "config": cfg.__dict__,
            "blocks": [
                {
                    "header": b.header.to_dict(),
                    "sequence": b.dna_sequence,
                }
                for b in encoded_blocks
            ],
            "created_at": datetime.now(UTC).isoformat(),
        }
        (archive_path / "manifest.json").write_text(json.dumps(archive_data, indent=2))

        for i, block in enumerate(encoded_blocks):
            (archive_path / f"block_{i:04d}.fasta").write_text(
                f">{block.header.block_id}\n{block.dna_sequence}\n"
            )

        metrics = PlatformMetrics(
            storage=compute_storage_metrics(len(data), len(compressed), total_dna_length),
            biological=compute_biological_metrics(sequences[0] if sequences else ""),
        )

        return StoreResult(
            archive_id=archive_id,
            filename=filename,
            original_size=len(data),
            compressed_size=len(compressed),
            total_dna_length=total_dna_length,
            num_blocks=len(encoded_blocks),
            compression_ratio=comp_ratio,
            sequences=sequences,
            metrics=metrics,
            checksum=checksum,
        )

    def retrieve(self, archive_id: str, config: PipelineConfig | None = None) -> RetrieveResult:
        """Retrieve and reconstruct a file from the DNA archive."""
        archive_path = self._archive_path(archive_id)
        manifest_path = archive_path / "manifest.json"

        if not manifest_path.exists():
            from dnastoreai.core.exceptions import ArchiveNotFoundError
            raise ArchiveNotFoundError(archive_id)

        manifest = json.loads(manifest_path.read_text())
        stored_config = manifest.get("config", {})
        cfg = config or PipelineConfig(**{k: v for k, v in stored_config.items() if k in PipelineConfig.__dataclass_fields__})

        engine = ReconstructionEngine(encoding_method=cfg.encoding, ecc_type=cfg.ecc)

        # Simulate degradation and sequencing on stored sequences
        synth = SynthesisSimulator(
            substitution_rate=cfg.substitution_rate,
            insertion_rate=cfg.insertion_rate,
            deletion_rate=cfg.deletion_rate,
        )
        degrad = DegradationSimulator(
            DegradationParameters(
                temperature=cfg.degradation_temperature,
                humidity=cfg.degradation_humidity,
                time_years=cfg.degradation_time_years,
            )
        )
        seq_sim = get_sequencing_simulator(cfg.sequencing)  # type: ignore[arg-type]

        encoded_blocks: list[EncodedBlock] = []
        mutation_rates: list[float] = []

        for block_data in manifest["blocks"]:
            header = DNAHeader(**block_data["header"])
            seq = block_data["sequence"]

            synth_result = synth.synthesize(seq)
            degrad_result = degrad.degrade(synth_result.synthesized_sequence)
            seq_result = seq_sim.sequence(degrad_result.degraded_sequence, cfg.coverage_depth)

            # Use consensus from best read
            recovered_seq = seq_result.reads[0].sequence if seq_result.reads else degrad_result.degraded_sequence
            mutation_rates.append(seq_result.error_distribution.error_rate)

            encoded_blocks.append(
                EncodedBlock(header=header, dna_sequence=recovered_seq, ecc_encoded_data=b"")
            )

        recon = engine.reconstruct(encoded_blocks, manifest.get("checksum"))

        # Decompress
        try:
            final_data = decompress(recon.data, cfg.compression)  # type: ignore[arg-type]
        except Exception:
            final_data = recon.data

        metrics = PlatformMetrics(
            recovery=RecoveryMetricsSummary(
                recovery_accuracy=recon.metrics.recovery_accuracy,
                bit_error_rate=recon.metrics.bit_error_rate,
                sequence_recovery_rate=recon.metrics.sequence_recovery_rate,
                missing_block_rate=recon.metrics.missing_block_rate,
            ),
            biological=compute_biological_metrics(
                encoded_blocks[0].dna_sequence if encoded_blocks else "",
                mutation_rate=sum(mutation_rates) / max(len(mutation_rates), 1),
            ),
        )

        return RetrieveResult(
            archive_id=archive_id,
            filename=manifest["filename"],
            data=final_data,
            checksum_valid=recon.metrics.checksum_valid,
            metrics=metrics,
            missing_blocks=recon.missing_blocks,
        )

    def simulate(self, archive_id: str, config: PipelineConfig | None = None) -> SimulateResult:
        """Run simulation stages on an archive without full retrieval."""
        archive_path = self._archive_path(archive_id)
        manifest_path = archive_path / "manifest.json"

        if not manifest_path.exists():
            from dnastoreai.core.exceptions import ArchiveNotFoundError
            raise ArchiveNotFoundError(archive_id)

        manifest = json.loads(manifest_path.read_text())
        stored_config = manifest.get("config", {})
        cfg = config or PipelineConfig(**{k: v for k, v in stored_config.items() if k in PipelineConfig.__dataclass_fields__})

        synth_stats = degrad_stats = seq_stats = None

        if manifest["blocks"]:
            seq = manifest["blocks"][0]["sequence"]

            synth = SynthesisSimulator(cfg.substitution_rate, cfg.insertion_rate, cfg.deletion_rate)
            synth_result = synth.synthesize(seq)
            synth_stats = synth_result.statistics.to_dict()

            degrad = DegradationSimulator(
                DegradationParameters(cfg.degradation_temperature, cfg.degradation_humidity, cfg.degradation_time_years)
            )
            degrad_result = degrad.degrade(synth_result.synthesized_sequence)
            degrad_stats = degrad_result.statistics.to_dict()

            seq_sim = get_sequencing_simulator(cfg.sequencing)  # type: ignore[arg-type]
            seq_result = seq_sim.sequence(degrad_result.degraded_sequence, cfg.coverage_depth)
            seq_stats = seq_result.to_dict()

        return SimulateResult(
            archive_id=archive_id,
            synthesis_stats=synth_stats,
            degradation_stats=degrad_stats,
            sequencing_stats=seq_stats,
        )
