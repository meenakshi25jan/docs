"""Unit tests for metadata header module."""

import pytest

from dnastoreai.modules.metadata.header import DNAHeader


class TestDNAHeader:
    def test_roundtrip(self):
        header = DNAHeader(
            file_id="file-1",
            block_id="block-1",
            total_blocks=5,
            checksum="abc123",
            encoding_version="1.0",
            ecc_type="reed_solomon",
            block_index=2,
        )
        serialized = header.to_bytes()
        restored = DNAHeader.from_bytes(serialized)
        assert restored.file_id == "file-1"
        assert restored.block_id == "block-1"
        assert restored.total_blocks == 5
        assert restored.block_index == 2

    def test_json_roundtrip(self):
        header = DNAHeader(
            file_id="f1", block_id="b1", total_blocks=1, checksum="xyz",
        )
        restored = DNAHeader.from_json(header.to_json())
        assert restored.file_id == "f1"

    def test_invalid_magic(self):
        with pytest.raises(ValueError, match="magic"):
            DNAHeader.from_bytes(b"XXXX" + b"\x00" * 508)

    def test_too_short(self):
        with pytest.raises(ValueError, match="too short"):
            DNAHeader.from_bytes(b"short")

    def test_invalid_version(self):
        data = DNAHeader.MAGIC + b"\x00\x00\x00\x02" + b"\x00" * 504
        with pytest.raises(ValueError, match="version"):
            DNAHeader.from_bytes(data)

    def test_to_dict(self):
        header = DNAHeader(file_id="f", block_id="b", total_blocks=1, checksum="c")
        d = header.to_dict()
        assert d["file_id"] == "f"

    def test_oversized_payload(self):
        header = DNAHeader(
            file_id="x" * 1000, block_id="b", total_blocks=1, checksum="c",
        )
        with pytest.raises(ValueError, match="exceeds"):
            header.to_bytes()
