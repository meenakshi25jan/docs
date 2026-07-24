"""DNA degradation simulator modeling aging and environmental damage."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any

BASES = "ACGT"


@dataclass
class DegradationParameters:
    """Environmental parameters for degradation simulation."""

    temperature: float = 25.0  # Celsius
    humidity: float = 50.0  # Percent
    time_years: float = 1.0
    dropout_rate: float = 0.001


@dataclass
class DegradationStatistics:
    """Statistics from degradation simulation."""

    original_length: int
    damaged_length: int
    bases_lost: int
    mutations: int
    dropout_blocks: int
    degradation_factor: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "original_length": self.original_length,
            "damaged_length": self.damaged_length,
            "bases_lost": self.bases_lost,
            "mutations": self.mutations,
            "dropout_blocks": self.dropout_blocks,
            "degradation_factor": self.degradation_factor,
        }


@dataclass
class DegradationResult:
    """Result of DNA degradation simulation."""

    original_sequence: str
    degraded_sequence: str
    statistics: DegradationStatistics
    damage_events: list[dict[str, Any]] = field(default_factory=list)


class DegradationSimulator:
    """Simulate DNA archive degradation over time."""

    def __init__(self, params: DegradationParameters | None = None, seed: int | None = None) -> None:
        self.params = params or DegradationParameters()
        if seed is not None:
            random.seed(seed)

    def _compute_degradation_rate(self) -> float:
        """Compute degradation rate from environmental parameters."""
        temp_factor = math.exp((self.params.temperature - 25.0) / 50.0)
        humidity_factor = 1.0 + (self.params.humidity - 50.0) / 100.0
        time_factor = self.params.time_years
        return self.params.dropout_rate * temp_factor * humidity_factor * time_factor

    def degrade(self, sequence: str) -> DegradationResult:
        """Apply degradation to a DNA sequence."""
        seq = sequence.upper()
        rate = self._compute_degradation_rate()
        result: list[str] = []
        damage_events: list[dict[str, Any]] = []
        mutations = bases_lost = 0

        for i, base in enumerate(seq):
            if random.random() < rate:
                bases_lost += 1
                damage_events.append({"type": "dropout", "position": i, "base": base})
                continue

            if random.random() < rate * 0.5:
                alternatives = [b for b in BASES if b != base]
                new_base = random.choice(alternatives)
                result.append(new_base)
                mutations += 1
                damage_events.append({"type": "mutation", "position": i, "from": base, "to": new_base})
            else:
                result.append(base)

        degraded = "".join(result)
        stats = DegradationStatistics(
            original_length=len(seq),
            damaged_length=len(degraded),
            bases_lost=bases_lost,
            mutations=mutations,
            dropout_blocks=sum(1 for e in damage_events if e["type"] == "dropout"),
            degradation_factor=1.0 - len(degraded) / max(len(seq), 1),
        )

        return DegradationResult(
            original_sequence=seq,
            degraded_sequence=degraded,
            statistics=stats,
            damage_events=damage_events,
        )
