"""Integration tests for pipeline service."""

import pytest

from dnastoreai.core.config import Settings
from dnastoreai.core.exceptions import ArchiveNotFoundError
from dnastoreai.services.archive_service import ArchiveService
from dnastoreai.services.pipeline_service import PipelineConfig, PipelineService


@pytest.fixture
def pipeline(tmp_path):
    settings = Settings(data_dir=tmp_path, archive_dir=tmp_path / "archive", upload_dir=tmp_path / "uploads")
    return PipelineService(settings)


@pytest.fixture
def archive_service(tmp_path):
    settings = Settings(data_dir=tmp_path, archive_dir=tmp_path / "archive")
    return ArchiveService(settings)


class TestPipelineIntegration:
    def test_store_and_retrieve(self, pipeline):
        data = b"Integration test data for DNA storage pipeline" * 10
        config = PipelineConfig(
            compression="gzip",
            encoding="basic",
            ecc="reed_solomon",
            block_size=100,
            substitution_rate=0.0,
            insertion_rate=0.0,
            deletion_rate=0.0,
        )
        store_result = pipeline.store(data, "test.txt", config)
        assert store_result.archive_id
        assert store_result.num_blocks > 0
        assert store_result.total_dna_length > 0

        retrieve_result = pipeline.retrieve(store_result.archive_id, config)
        assert retrieve_result.filename == "test.txt"

    def test_simulate(self, pipeline):
        data = b"simulation test"
        store_result = pipeline.store(data, "sim.txt", PipelineConfig(substitution_rate=0.0))
        sim_result = pipeline.simulate(store_result.archive_id)
        assert sim_result.synthesis_stats is not None
        assert sim_result.degradation_stats is not None
        assert sim_result.sequencing_stats is not None

    def test_archive_not_found(self, pipeline):
        with pytest.raises(ArchiveNotFoundError):
            pipeline.retrieve("nonexistent-id")

    def test_archive_service_list(self, pipeline, archive_service):
        pipeline.store(b"test1", "file1.txt")
        pipeline.store(b"test2", "file2.txt")
        archives = archive_service.list_archives()
        assert len(archives) == 2

    def test_archive_get_dna(self, pipeline, archive_service):
        result = pipeline.store(b"dna test data here", "dna.txt")
        dna = archive_service.get_dna(result.archive_id)
        assert dna["sequence"]
        assert dna["length"] > 0

    def test_different_encodings(self, pipeline):
        data = b"encoding comparison test data"
        for encoding in ["basic", "rotating", "gc_balanced"]:
            config = PipelineConfig(encoding=encoding, ecc="reed_solomon", substitution_rate=0.0)
            result = pipeline.store(data, f"{encoding}.txt", config)
            assert result.total_dna_length > 0

    def test_different_ecc(self, pipeline):
        data = b"ecc comparison test"
        for ecc in ["reed_solomon", "bch", "ldpc", "fountain"]:
            config = PipelineConfig(ecc=ecc, substitution_rate=0.0)
            result = pipeline.store(data, f"{ecc}.txt", config)
            assert result.archive_id
