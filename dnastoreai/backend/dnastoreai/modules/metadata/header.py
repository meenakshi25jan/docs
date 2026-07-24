"""DNA-safe metadata headers with serialization."""

from __future__ import annotations

import json
import struct
from dataclasses import dataclass, field
from typing import Any, ClassVar


@dataclass
class DNAHeader:
    """DNA-safe header for block metadata packaging."""

    file_id: str
    block_id: str
    total_blocks: int
    checksum: str
    encoding_version: str = "1.0"
    ecc_type: str = "reed_solomon"
    block_index: int = 0
    extra: dict[str, Any] = field(default_factory=dict)

    MAGIC: ClassVar[bytes] = b"DNAH"
    VERSION: ClassVar[int] = 1
    HEADER_SIZE: ClassVar[int] = 512

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_id": self.file_id,
            "block_id": self.block_id,
            "block_index": self.block_index,
            "total_blocks": self.total_blocks,
            "checksum": self.checksum,
            "encoding_version": self.encoding_version,
            "ecc_type": self.ecc_type,
            "extra": self.extra,
        }

    def to_bytes(self) -> bytes:
        """Serialize header to fixed-size DNA-safe byte array."""
        payload = json.dumps(self.to_dict(), separators=(",", ":")).encode("utf-8")
        if len(payload) > self.HEADER_SIZE - 8:
            raise ValueError(f"Header payload exceeds {self.HEADER_SIZE - 8} bytes")

        padded = payload.ljust(self.HEADER_SIZE - 8, b"\x00")
        return self.MAGIC + struct.pack(">I", self.VERSION) + padded

    @classmethod
    def from_bytes(cls, data: bytes) -> DNAHeader:
        """Deserialize header from bytes."""
        if len(data) < 8:
            raise ValueError("Header data too short")

        magic = data[:4]
        if magic != cls.MAGIC:
            raise ValueError(f"Invalid header magic: {magic!r}")

        version = struct.unpack(">I", data[4:8])[0]
        if version != cls.VERSION:
            raise ValueError(f"Unsupported header version: {version}")

        payload = data[8 : cls.HEADER_SIZE].rstrip(b"\x00")
        parsed = json.loads(payload.decode("utf-8"))

        return cls(
            file_id=parsed["file_id"],
            block_id=parsed["block_id"],
            block_index=parsed.get("block_index", 0),
            total_blocks=parsed["total_blocks"],
            checksum=parsed["checksum"],
            encoding_version=parsed.get("encoding_version", "1.0"),
            ecc_type=parsed.get("ecc_type", "reed_solomon"),
            extra=parsed.get("extra", {}),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> DNAHeader:
        parsed = json.loads(json_str)
        return cls(**{k: v for k, v in parsed.items() if k in cls.__dataclass_fields__})
