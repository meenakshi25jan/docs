"""DNA sequencing simulator for Illumina, Nanopore, and PacBio."""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal

SequencingPlatform = Literal["illumina", "nanopore", "pacbio"]
BASES = "ACGT"


@dataclass
class QualityScore:
    """Per-base quality score."""

    position: int
    base: str
    score: float  # Phred-scale quality


@dataclass
class Read:
    """A single sequencing read."""

    read_id: str
    sequence: str
    quality_scores: list[QualityScore]
    platform: str
    start_position: int = 0

    @property
    def mean_quality(self) -> float:
        if not self.quality_scores:
            return 0.0
        return sum(q.score for q in self.quality_scores) / len(self.quality_scores)


@dataclass
class ErrorDistribution:
    """Error distribution across a sequencing run."""

    substitutions: int = 0
    insertions: int = 0
    deletions: int = 0
    total_bases: int = 0

    @property
    def error_rate(self) -> float:
        total_errors = self.substitutions + self.insertions + self.deletions
        return total_errors / max(self.total_bases, 1)

    def to_dict(self) -> dict[str, Any]:
        return {
            "substitutions": self.substitutions,
            "insertions": self.insertions,
            "deletions": self.deletions,
            "total_bases": self.total_bases,
            "error_rate": self.error_rate,
        }


@dataclass
class Coverage:
    """Coverage statistics for sequencing."""

    mean_depth: float
    min_depth: int
    max_depth: int
    covered_fraction: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "mean_depth": self.mean_depth,
            "min_depth": self.min_depth,
            "max_depth": self.max_depth,
            "covered_fraction": self.covered_fraction,
        }


@dataclass
class SequencingResult:
    """Complete sequencing simulation result."""

    reads: list[Read]
    coverage: Coverage
    error_distribution: ErrorDistribution
    platform: str
    reference_length: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "num_reads": len(self.reads),
            "coverage": self.coverage.to_dict(),
            "error_distribution": self.error_distribution.to_dict(),
            "platform": self.platform,
            "reference_length": self.reference_length,
        }


class SequencingSimulator(ABC):
    """Abstract sequencing simulator."""

    @abstractmethod
    def sequence(self, dna: str, coverage_depth: int = 30) -> SequencingResult:
        ...

    @property
    @abstractmethod
    def platform(self) -> str:
        ...


class IlluminaSimulator(SequencingSimulator):
    """Simulate Illumina short-read sequencing."""

    def __init__(self, read_length: int = 150, error_rate: float = 0.001, seed: int | None = None) -> None:
        self.read_length = read_length
        self.error_rate = error_rate
        if seed is not None:
            random.seed(seed)

    def sequence(self, dna: str, coverage_depth: int = 30) -> SequencingResult:
        dna = dna.upper()
        reads: list[Read] = []
        errors = ErrorDistribution()
        depth_map = [0] * len(dna)

        num_reads = max(1, (len(dna) * coverage_depth) // self.read_length)
        for i in range(num_reads):
            start = random.randint(0, max(0, len(dna) - self.read_length))
            raw = dna[start : start + self.read_length]
            qualities: list[QualityScore] = []
            seq_chars: list[str] = []

            for j, base in enumerate(raw):
                depth_map[start + j] += 1
                q_score = random.gauss(35, 5)
                if random.random() < self.error_rate:
                    new_base = random.choice([b for b in BASES if b != base])
                    seq_chars.append(new_base)
                    errors.substitutions += 1
                    q_score = random.gauss(15, 3)
                else:
                    seq_chars.append(base)
                qualities.append(QualityScore(position=j, base=seq_chars[-1], score=max(0, q_score)))
                errors.total_bases += 1

            reads.append(
                Read(
                    read_id=f"ILLUMINA_{i:06d}",
                    sequence="".join(seq_chars),
                    quality_scores=qualities,
                    platform="illumina",
                    start_position=start,
                )
            )

        return self._build_result(reads, errors, depth_map, dna)

    def _build_result(
        self, reads: list[Read], errors: ErrorDistribution, depth_map: list[int], dna: str
    ) -> SequencingResult:
        depths = [d for d in depth_map if d > 0] or [0]
        return SequencingResult(
            reads=reads,
            coverage=Coverage(
                mean_depth=sum(depth_map) / max(len(dna), 1),
                min_depth=min(depths),
                max_depth=max(depths),
                covered_fraction=sum(1 for d in depth_map if d > 0) / max(len(dna), 1),
            ),
            error_distribution=errors,
            platform="illumina",
            reference_length=len(dna),
        )

    @property
    def platform(self) -> str:
        return "illumina"


class NanoporeSimulator(SequencingSimulator):
    """Simulate Oxford Nanopore long-read sequencing."""

    def __init__(self, mean_read_length: int = 10000, error_rate: float = 0.05, seed: int | None = None) -> None:
        self.mean_read_length = mean_read_length
        self.error_rate = error_rate
        if seed is not None:
            random.seed(seed)

    def sequence(self, dna: str, coverage_depth: int = 30) -> SequencingResult:
        dna = dna.upper()
        reads: list[Read] = []
        errors = ErrorDistribution()
        depth_map = [0] * len(dna)

        num_reads = max(1, (len(dna) * coverage_depth) // self.mean_read_length)
        for i in range(num_reads):
            read_len = max(100, int(random.gauss(self.mean_read_length, self.mean_read_length * 0.3)))
            start = random.randint(0, max(0, len(dna) - min(read_len, len(dna))))
            raw = dna[start : start + min(read_len, len(dna) - start)]
            qualities: list[QualityScore] = []
            seq_chars: list[str] = []

            for j, base in enumerate(raw):
                if start + j < len(depth_map):
                    depth_map[start + j] += 1
                q_score = random.gauss(12, 3)
                roll = random.random()
                if roll < self.error_rate * 0.6:
                    seq_chars.append(random.choice([b for b in BASES if b != base]))
                    errors.substitutions += 1
                elif roll < self.error_rate * 0.8:
                    seq_chars.append(random.choice(BASES))
                    errors.insertions += 1
                elif roll < self.error_rate:
                    errors.deletions += 1
                    continue
                else:
                    seq_chars.append(base)
                qualities.append(QualityScore(position=j, base=seq_chars[-1], score=max(0, q_score)))
                errors.total_bases += 1

            reads.append(
                Read(
                    read_id=f"NANOPORE_{i:06d}",
                    sequence="".join(seq_chars),
                    quality_scores=qualities,
                    platform="nanopore",
                    start_position=start,
                )
            )

        depths = [d for d in depth_map if d > 0] or [0]
        return SequencingResult(
            reads=reads,
            coverage=Coverage(
                mean_depth=sum(depth_map) / max(len(dna), 1),
                min_depth=min(depths),
                max_depth=max(depths),
                covered_fraction=sum(1 for d in depth_map if d > 0) / max(len(dna), 1),
            ),
            error_distribution=errors,
            platform="nanopore",
            reference_length=len(dna),
        )

    @property
    def platform(self) -> str:
        return "nanopore"


class PacBioSimulator(SequencingSimulator):
    """Simulate PacBio HiFi long-read sequencing."""

    def __init__(self, mean_read_length: int = 15000, error_rate: float = 0.001, seed: int | None = None) -> None:
        self.mean_read_length = mean_read_length
        self.error_rate = error_rate
        if seed is not None:
            random.seed(seed)

    def sequence(self, dna: str, coverage_depth: int = 30) -> SequencingResult:
        dna = dna.upper()
        reads: list[Read] = []
        errors = ErrorDistribution()
        depth_map = [0] * len(dna)

        num_reads = max(1, (len(dna) * coverage_depth) // self.mean_read_length)
        for i in range(num_reads):
            read_len = max(500, int(random.gauss(self.mean_read_length, self.mean_read_length * 0.2)))
            start = random.randint(0, max(0, len(dna) - min(read_len, len(dna))))
            raw = dna[start : start + min(read_len, len(dna) - start)]
            qualities: list[QualityScore] = []
            seq_chars: list[str] = []

            for j, base in enumerate(raw):
                if start + j < len(depth_map):
                    depth_map[start + j] += 1
                q_score = random.gauss(30, 2)
                if random.random() < self.error_rate:
                    seq_chars.append(random.choice([b for b in BASES if b != base]))
                    errors.substitutions += 1
                else:
                    seq_chars.append(base)
                qualities.append(QualityScore(position=j, base=seq_chars[-1], score=max(0, q_score)))
                errors.total_bases += 1

            reads.append(
                Read(
                    read_id=f"PACBIO_{i:06d}",
                    sequence="".join(seq_chars),
                    quality_scores=qualities,
                    platform="pacbio",
                    start_position=start,
                )
            )

        depths = [d for d in depth_map if d > 0] or [0]
        return SequencingResult(
            reads=reads,
            coverage=Coverage(
                mean_depth=sum(depth_map) / max(len(dna), 1),
                min_depth=min(depths),
                max_depth=max(depths),
                covered_fraction=sum(1 for d in depth_map if d > 0) / max(len(dna), 1),
            ),
            error_distribution=errors,
            platform="pacbio",
            reference_length=len(dna),
        )

    @property
    def platform(self) -> str:
        return "pacbio"


_SIMULATORS: dict[str, type[SequencingSimulator]] = {
    "illumina": IlluminaSimulator,
    "nanopore": NanoporeSimulator,
    "pacbio": PacBioSimulator,
}


def get_sequencing_simulator(platform: SequencingPlatform, **kwargs: Any) -> SequencingSimulator:
    if platform not in _SIMULATORS:
        raise ValueError(f"Unknown sequencing platform: {platform}")
    return _SIMULATORS[platform](**kwargs)
