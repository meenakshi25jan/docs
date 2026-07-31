"""Platform metrics collection and reporting."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dnastoreai.modules.optimization.optimizer import analyze_fitness, gc_content


@dataclass
class StorageMetrics:
    compression_ratio: float = 0.0
    dna_length: int = 0
    logical_size: int = 0
    physical_size: int = 0
    density: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "compression_ratio": self.compression_ratio,
            "dna_length": self.dna_length,
            "logical_size": self.logical_size,
            "physical_size": self.physical_size,
            "density": self.density,
        }


@dataclass
class BiologicalMetrics:
    gc_content: float = 0.0
    homopolymer_count: int = 0
    hairpin_risk: float = 0.0
    mutation_rate: float = 0.0
    fitness_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "gc_content": self.gc_content,
            "homopolymer_count": self.homopolymer_count,
            "hairpin_risk": self.hairpin_risk,
            "mutation_rate": self.mutation_rate,
            "fitness_score": self.fitness_score,
        }


@dataclass
class RecoveryMetricsSummary:
    recovery_accuracy: float = 0.0
    bit_error_rate: float = 0.0
    sequence_recovery_rate: float = 0.0
    missing_block_rate: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "recovery_accuracy": self.recovery_accuracy,
            "bit_error_rate": self.bit_error_rate,
            "sequence_recovery_rate": self.sequence_recovery_rate,
            "missing_block_rate": self.missing_block_rate,
        }


@dataclass
class AIMetrics:
    prediction_accuracy: float = 0.0
    reconstruction_success: bool = False
    confidence_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "prediction_accuracy": self.prediction_accuracy,
            "reconstruction_success": self.reconstruction_success,
            "confidence_score": self.confidence_score,
        }


@dataclass
class PlatformMetrics:
    storage: StorageMetrics = field(default_factory=StorageMetrics)
    biological: BiologicalMetrics = field(default_factory=BiologicalMetrics)
    recovery: RecoveryMetricsSummary = field(default_factory=RecoveryMetricsSummary)
    ai: AIMetrics = field(default_factory=AIMetrics)

    def to_dict(self) -> dict[str, Any]:
        return {
            "storage": self.storage.to_dict(),
            "biological": self.biological.to_dict(),
            "recovery": self.recovery.to_dict(),
            "ai": self.ai.to_dict(),
        }


def compute_storage_metrics(
    original_size: int,
    compressed_size: int,
    dna_length: int,
) -> StorageMetrics:
    physical = dna_length * 2  # 2 bits per base approx
    return StorageMetrics(
        compression_ratio=original_size / max(compressed_size, 1),
        dna_length=dna_length,
        logical_size=original_size,
        physical_size=physical,
        density=original_size / max(physical, 1),
    )


def compute_biological_metrics(sequence: str, mutation_rate: float = 0.0) -> BiologicalMetrics:
    fitness = analyze_fitness(sequence)
    return BiologicalMetrics(
        gc_content=gc_content(sequence),
        homopolymer_count=fitness.homopolymer_count,
        hairpin_risk=fitness.hairpin_risk,
        mutation_rate=mutation_rate,
        fitness_score=fitness.fitness_score,
    )
