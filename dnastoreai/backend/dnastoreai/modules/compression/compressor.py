"""Compression layer with gzip, zlib, lzma and future AI interface."""

from __future__ import annotations

import gzip
import lzma
import zlib
from abc import ABC, abstractmethod
from typing import Literal

CompressionMethod = Literal["gzip", "zlib", "lzma"]


class Compressor(ABC):
    """Abstract compressor interface."""

    @abstractmethod
    def compress(self, data: bytes) -> bytes:
        ...

    @abstractmethod
    def decompress(self, data: bytes) -> bytes:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...


class GzipCompressor(Compressor):
    def compress(self, data: bytes) -> bytes:
        return gzip.compress(data, compresslevel=6)

    def decompress(self, data: bytes) -> bytes:
        return gzip.decompress(data)

    @property
    def name(self) -> str:
        return "gzip"


class ZlibCompressor(Compressor):
    def compress(self, data: bytes) -> bytes:
        return zlib.compress(data, level=6)

    def decompress(self, data: bytes) -> bytes:
        return zlib.decompress(data)

    @property
    def name(self) -> str:
        return "zlib"


class LzmaCompressor(Compressor):
    def compress(self, data: bytes) -> bytes:
        return lzma.compress(data, preset=6)

    def decompress(self, data: bytes) -> bytes:
        return lzma.decompress(data)

    @property
    def name(self) -> str:
        return "lzma"


class AICompressor(Compressor):
    """Placeholder for future transformer/latent/learned compression."""

    def __init__(self, model_name: str = "dnastoreai/compressor-v1") -> None:
        self.model_name = model_name

    def compress(self, data: bytes) -> bytes:
        raise NotImplementedError(
            f"AI compression with model '{self.model_name}' is not yet implemented. "
            "Use gzip, zlib, or lzma for production workflows."
        )

    def decompress(self, data: bytes) -> bytes:
        raise NotImplementedError("AI decompression is not yet implemented.")

    @property
    def name(self) -> str:
        return f"ai:{self.model_name}"


_COMPRESSORS: dict[str, Compressor] = {
    "gzip": GzipCompressor(),
    "zlib": ZlibCompressor(),
    "lzma": LzmaCompressor(),
}


def get_compressor(method: CompressionMethod) -> Compressor:
    if method not in _COMPRESSORS:
        raise ValueError(f"Unknown compression method: {method}")
    return _COMPRESSORS[method]


def compress(data: bytes, method: CompressionMethod = "gzip") -> bytes:
    """Compress data using the specified method."""
    return get_compressor(method).compress(data)


def decompress(data: bytes, method: CompressionMethod = "gzip") -> bytes:
    """Decompress data using the specified method."""
    return get_compressor(method).decompress(data)


def compression_ratio(original: bytes, compressed: bytes) -> float:
    """Calculate compression ratio (original / compressed)."""
    if len(compressed) == 0:
        return 0.0
    return len(original) / len(compressed)
