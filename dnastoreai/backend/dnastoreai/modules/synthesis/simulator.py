"""DNA synthesis simulator with configurable error rates."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

BASES = "ACGT"


@dataclass
class SynthesisStatistics:
    """Statistics from synthesis simulation."""

    total_bases: int
    substitutions: int
    insertions: int
    deletions: int
    substitution_rate: float
    insertion_rate: float
    deletion_rate: float
    output_length: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_bases": self.total_bases,
            "substitutions": self.substitutions,
            "insertions": self.insertions,
            "deletions": self.deletions,
            "substitution_rate": self.substitution_rate,
            "insertion_rate": self.insertion_rate,
            "deletion_rate": self.deletion_rate,
            "output_length": self.output_length,
        }


@dataclass
class SynthesisResult:
    """Result of DNA synthesis simulation."""

    original_sequence: str
    synthesized_sequence: str
    statistics: SynthesisStatistics
    errors: list[dict[str, Any]] = field(default_factory=list)


class SynthesisSimulator:
    """Simulate DNA oligo synthesis imperfections."""

    def __init__(
        self,
        substitution_rate: float = 0.001,
        insertion_rate: float = 0.0001,
        deletion_rate: float = 0.0001,
        seed: int | None = None,
    ) -> None:
        self.substitution_rate = substitution_rate
        self.insertion_rate = insertion_rate
        self.deletion_rate = deletion_rate
        if seed is not None:
            random.seed(seed)

    def synthesize(self, sequence: str) -> SynthesisResult:
        """Simulate synthesis of a DNA sequence."""
        seq = sequence.upper()
        result: list[str] = []
        errors: list[dict[str, Any]] = []
        substitutions = insertions = deletions = 0

        for i, base in enumerate(seq):
            if random.random() < self.deletion_rate:
                deletions += 1
                errors.append({"type": "deletion", "position": i, "base": base})
                continue

            if random.random() < self.insertion_rate:
                inserted = random.choice(BASES)
                result.append(inserted)
                insertions += 1
                errors.append({"type": "insertion", "position": i, "base": inserted})

            if random.random() < self.substitution_rate:
                alternatives = [b for b in BASES if b != base]
                new_base = random.choice(alternatives)
                result.append(new_base)
                substitutions += 1
                errors.append({"type": "substitution", "position": i, "from": base, "to": new_base})
            else:
                result.append(base)

        synthesized = "".join(result)
        stats = SynthesisStatistics(
            total_bases=len(seq),
            substitutions=substitutions,
            insertions=insertions,
            deletions=deletions,
            substitution_rate=substitutions / max(len(seq), 1),
            insertion_rate=insertions / max(len(seq), 1),
            deletion_rate=deletions / max(len(seq), 1),
            output_length=len(synthesized),
        )

        return SynthesisResult(
            original_sequence=seq,
            synthesized_sequence=synthesized,
            statistics=stats,
            errors=errors,
        )
