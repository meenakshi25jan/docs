"""DNA sequence optimization for biological feasibility."""

from __future__ import annotations

import re
from dataclasses import dataclass

HOMOPOLYMER_PATTERN = re.compile(r"(A{5,}|C{5,}|G{5,}|T{5,})")
BASES = "ACGT"
COMPLEMENT = {"A": "T", "T": "A", "C": "G", "G": "C"}


@dataclass
class OptimizationResult:
    """Result of DNA sequence optimization."""

    original_sequence: str
    optimized_sequence: str
    fitness_before: float
    fitness_after: float
    homopolymers_removed: int
    gc_adjustments: int
    hairpins_removed: int


@dataclass
class FitnessReport:
    """Detailed fitness analysis of a DNA sequence."""

    fitness_score: float
    gc_content: float
    homopolymer_count: int
    max_homopolymer_length: int
    hairpin_risk: float
    issues: list[str]


def gc_content(sequence: str) -> float:
    """Calculate GC content as fraction [0, 1]."""
    if not sequence:
        return 0.0
    seq = sequence.upper()
    gc = sum(1 for b in seq if b in "GC")
    return gc / len(seq)


def detect_homopolymers(sequence: str, min_length: int = 5) -> list[tuple[str, int, int]]:
    """Detect homopolymer runs of minimum length."""
    results = []
    for match in HOMOPOLYMER_PATTERN.finditer(sequence.upper()):
        results.append((match.group(), match.start(), match.end()))
    return [r for r in results if len(r[0]) >= min_length]


def hairpin_risk(sequence: str, window: int = 10) -> float:
    """Estimate hairpin formation risk using simple thermodynamic proxy."""
    seq = sequence.upper()
    if len(seq) < window * 2:
        return 0.0

    max_complementarity = 0
    for i in range(len(seq) - window):
        left = seq[i : i + window]
        for j in range(i + window, len(seq) - window + 1):
            right = seq[j : j + window]
            complement_score = sum(
                1 for a, b in zip(left, reversed(right), strict=False) if COMPLEMENT.get(a) == b
            )
            max_complementarity = max(max_complementarity, complement_score)

    return max_complementarity / window


def fitness_score(sequence: str) -> float:
    """Compute overall sequence fitness score [0, 1]."""
    report = analyze_fitness(sequence)
    return report.fitness_score


def analyze_fitness(sequence: str) -> FitnessReport:
    """Detailed fitness analysis."""
    seq = sequence.upper()
    issues: list[str] = []

    gc = gc_content(seq)
    gc_penalty = 0.0
    if gc < 0.4 or gc > 0.6:
        gc_penalty = abs(gc - 0.5) * 2
        issues.append(f"GC content {gc:.2%} outside 40-60% range")

    homopolymers = detect_homopolymers(seq)
    homopolymer_penalty = min(1.0, len(homopolymers) * 0.15)
    max_hp = max((len(h[0]) for h in homopolymers), default=0)
    if homopolymers:
        issues.append(f"Found {len(homopolymers)} homopolymer runs (max length {max_hp})")

    hp_risk = hairpin_risk(seq)
    hairpin_penalty = hp_risk * 0.3
    if hp_risk > 0.7:
        issues.append(f"High hairpin risk: {hp_risk:.2f}")

    score = max(0.0, 1.0 - gc_penalty - homopolymer_penalty - hairpin_penalty)

    return FitnessReport(
        fitness_score=score,
        gc_content=gc,
        homopolymer_count=len(homopolymers),
        max_homopolymer_length=max_hp,
        hairpin_risk=hp_risk,
        issues=issues,
    )


def _break_homopolymer(sequence: list[str], start: int, end: int) -> bool:
    """Break a homopolymer by substituting a middle base."""
    if end - start < 5:
        return False
    mid = (start + end) // 2
    base = sequence[mid]
    alternatives = [b for b in BASES if b != base]
    sequence[mid] = alternatives[hash("".join(sequence)) % len(alternatives)]
    return True


def _adjust_gc(sequence: list[str], target: float = 0.5) -> int:
    """Adjust GC content toward target."""
    adjustments = 0
    current_gc = gc_content("".join(sequence))
    if 0.4 <= current_gc <= 0.6:
        return 0

    for i in range(len(sequence)):
        if current_gc < 0.4 and sequence[i] in "AT":
            sequence[i] = "G" if i % 2 == 0 else "C"
            adjustments += 1
        elif current_gc > 0.6 and sequence[i] in "GC":
            sequence[i] = "A" if i % 2 == 0 else "T"
            adjustments += 1
        current_gc = gc_content("".join(sequence))
        if 0.4 <= current_gc <= 0.6:
            break

    return adjustments


def optimize_sequence(sequence: str, max_iterations: int = 10) -> OptimizationResult:
    """Optimize DNA sequence for biological feasibility."""
    original = sequence.upper()
    chars = list(original)
    fitness_before = fitness_score(original)

    homopolymers_removed = 0
    gc_adjustments = 0
    hairpins_removed = 0

    for _ in range(max_iterations):
        hps = detect_homopolymers("".join(chars))
        if not hps:
            break
        for _, start, end in hps:
            if _break_homopolymer(chars, start, end):
                homopolymers_removed += 1

    gc_adjustments = _adjust_gc(chars)

    optimized = "".join(chars)
    fitness_after = fitness_score(optimized)

    return OptimizationResult(
        original_sequence=original,
        optimized_sequence=optimized,
        fitness_before=fitness_before,
        fitness_after=fitness_after,
        homopolymers_removed=homopolymers_removed,
        gc_adjustments=gc_adjustments,
        hairpins_removed=hairpins_removed,
    )
