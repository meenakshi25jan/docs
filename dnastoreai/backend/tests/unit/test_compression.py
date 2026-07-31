"""Unit tests for compression module."""

import pytest

from dnastoreai.modules.compression.compressor import (
    AICompressor,
    compress,
    compression_ratio,
    decompress,
    get_compressor,
)


class TestCompression:
    def test_gzip_roundtrip(self):
        data = b"Hello, DNA storage world!" * 100
        compressed = compress(data, "gzip")
        assert len(compressed) < len(data)
        assert decompress(compressed, "gzip") == data

    def test_zlib_roundtrip(self):
        data = b"zlib test data" * 50
        assert decompress(compress(data, "zlib"), "zlib") == data

    def test_lzma_roundtrip(self):
        data = b"lzma test data" * 50
        assert decompress(compress(data, "lzma"), "lzma") == data

    def test_compression_ratio(self):
        data = b"x" * 1000
        compressed = compress(data, "gzip")
        ratio = compression_ratio(data, compressed)
        assert ratio > 1.0

    def test_compression_ratio_empty(self):
        assert compression_ratio(b"test", b"") == 0.0

    def test_get_compressor_invalid(self):
        with pytest.raises(ValueError):
            get_compressor("invalid")  # type: ignore[arg-type]

    def test_ai_compressor_not_implemented(self):
        ai = AICompressor()
        with pytest.raises(NotImplementedError):
            ai.compress(b"test")

    def test_ai_compressor_name(self):
        assert "ai:" in AICompressor().name

    def test_compressor_names(self):
        assert get_compressor("gzip").name == "gzip"
        assert get_compressor("zlib").name == "zlib"
        assert get_compressor("lzma").name == "lzma"
