"""Unit tests for simulation modules."""

from dnastoreai.modules.degradation.simulator import DegradationParameters, DegradationSimulator
from dnastoreai.modules.sequencing.simulator import (
    IlluminaSimulator,
    NanoporeSimulator,
    PacBioSimulator,
    get_sequencing_simulator,
)
from dnastoreai.modules.synthesis.simulator import SynthesisSimulator


class TestSynthesis:
    def test_synthesize(self):
        sim = SynthesisSimulator(seed=42)
        result = sim.synthesize("ACGTACGTACGTACGT" * 10)
        assert result.statistics.total_bases > 0
        assert result.synthesized_sequence

    def test_synthesis_stats_dict(self):
        sim = SynthesisSimulator(seed=42)
        result = sim.synthesize("ACGT" * 100)
        d = result.statistics.to_dict()
        assert "substitutions" in d


class TestDegradation:
    def test_degrade(self):
        sim = DegradationSimulator(DegradationParameters(time_years=10), seed=42)
        result = sim.degrade("ACGTACGTACGTACGT" * 50)
        assert result.statistics.original_length > 0

    def test_degradation_stats(self):
        sim = DegradationSimulator(seed=42)
        result = sim.degrade("ACGT" * 100)
        assert "degradation_factor" in result.statistics.to_dict()


class TestSequencing:
    def test_illumina(self):
        sim = IlluminaSimulator(seed=42)
        result = sim.sequence("ACGTACGTACGTACGT" * 20, coverage_depth=10)
        assert len(result.reads) > 0
        assert result.coverage.mean_depth > 0

    def test_nanopore(self):
        sim = NanoporeSimulator(seed=42)
        result = sim.sequence("ACGTACGTACGTACGT" * 20)
        assert result.platform == "nanopore"

    def test_pacbio(self):
        sim = PacBioSimulator(seed=42)
        result = sim.sequence("ACGTACGTACGTACGT" * 20)
        assert result.platform == "pacbio"

    def test_get_simulator(self):
        sim = get_sequencing_simulator("illumina")
        assert sim.platform == "illumina"

    def test_read_mean_quality(self):
        sim = IlluminaSimulator(seed=42)
        result = sim.sequence("ACGT" * 50)
        assert result.reads[0].mean_quality >= 0

    def test_error_distribution(self):
        sim = IlluminaSimulator(seed=42)
        result = sim.sequence("ACGT" * 50)
        assert "error_rate" in result.error_distribution.to_dict()

    def test_coverage_dict(self):
        sim = IlluminaSimulator(seed=42)
        result = sim.sequence("ACGT" * 50)
        assert "mean_depth" in result.coverage.to_dict()

    def test_sequencing_to_dict(self):
        sim = IlluminaSimulator(seed=42)
        result = sim.sequence("ACGT" * 50)
        d = result.to_dict()
        assert "num_reads" in d
