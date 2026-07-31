"""Unit tests for DNA optimization."""

from dnastoreai.modules.optimization.optimizer import (
    analyze_fitness,
    detect_homopolymers,
    fitness_score,
    gc_content,
    hairpin_risk,
    optimize_sequence,
)


class TestOptimization:
    def test_gc_content(self):
        assert gc_content("ACGT") == 0.5
        assert gc_content("AAAA") == 0.0
        assert gc_content("") == 0.0

    def test_homopolymer_detection(self):
        seq = "AAACCCGGGTTTAAAAA"
        hps = detect_homopolymers(seq)
        assert len(hps) >= 1

    def test_hairpin_risk(self):
        risk = hairpin_risk("ACGTACGTACGT")
        assert 0.0 <= risk <= 1.0

    def test_hairpin_short_sequence(self):
        assert hairpin_risk("AC") == 0.0

    def test_fitness_score(self):
        score = fitness_score("ACGTACGTACGTACGT")
        assert 0.0 <= score <= 1.0

    def test_analyze_fitness(self):
        report = analyze_fitness("AAAAACCCCCGGGGGTTTTT")
        assert report.homopolymer_count > 0
        assert len(report.issues) > 0

    def test_optimize_sequence(self):
        seq = "AAAAACCCCCGGGGGTTTTTACGTACGT"
        result = optimize_sequence(seq)
        assert result.fitness_after >= result.fitness_before or result.homopolymers_removed > 0

    def test_optimize_balanced_sequence(self):
        seq = "ACGTACGTACGTACGT"
        result = optimize_sequence(seq)
        assert result.optimized_sequence
