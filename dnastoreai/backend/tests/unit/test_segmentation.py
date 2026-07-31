"""Unit tests for segmentation module."""

import pytest

from dnastoreai.modules.segmentation.segmenter import reassemble, segment


class TestSegmentation:
    def test_basic_segmentation(self):
        data = b"Hello World" * 100
        result = segment(data, block_size=50)
        assert result.original_size == len(data)
        assert len(result.blocks) > 1
        assert result.blocks[0].metadata.block_index == 0

    def test_reassemble(self):
        data = b"test data for reassembly" * 20
        result = segment(data, block_size=30)
        recovered = reassemble(result.blocks)
        assert recovered == data

    def test_empty_data(self):
        result = segment(b"", block_size=100)
        assert len(result.blocks) == 1

    def test_parallel_segmentation(self):
        data = b"x" * 10000
        result = segment(data, block_size=500, parallel=True)
        assert reassemble(result.blocks) == data

    def test_invalid_block_size(self):
        with pytest.raises(ValueError):
            segment(b"test", block_size=0)

    def test_metadata_fields(self):
        result = segment(b"test", block_size=100, file_id="custom-id")
        assert result.file_id == "custom-id"
        meta = result.blocks[0].metadata
        assert meta.total_blocks == 1
        assert meta.checksum
        assert meta.version == "1.0"

    def test_block_metadata_to_dict(self):
        result = segment(b"test", block_size=2)
        d = result.blocks[0].metadata.to_dict()
        assert "block_id" in d
        assert "checksum" in d
