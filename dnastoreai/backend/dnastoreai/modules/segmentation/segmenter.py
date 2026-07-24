"""File segmentation layer with configurable block size and metadata."""

from __future__ import annotations

import hashlib
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class BlockMetadata:
    """Metadata for a single data block."""

    block_id: str
    file_id: str
    block_index: int
    total_blocks: int
    checksum: str
    timestamp: str
    version: str = "1.0"
    size: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "block_id": self.block_id,
            "file_id": self.file_id,
            "block_index": self.block_index,
            "total_blocks": self.total_blocks,
            "checksum": self.checksum,
            "timestamp": self.timestamp,
            "version": self.version,
            "size": self.size,
        }


@dataclass
class DataBlock:
    """A segmented block of file data with metadata."""

    data: bytes
    metadata: BlockMetadata


@dataclass
class SegmentationResult:
    """Result of file segmentation."""

    file_id: str
    blocks: list[DataBlock]
    original_size: int
    block_size: int
    metadata: dict[str, Any] = field(default_factory=dict)


def _compute_checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _create_block(
    data: bytes,
    file_id: str,
    block_index: int,
    total_blocks: int,
    version: str,
) -> DataBlock:
    block_id = str(uuid.uuid4())
    return DataBlock(
        data=data,
        metadata=BlockMetadata(
            block_id=block_id,
            file_id=file_id,
            block_index=block_index,
            total_blocks=total_blocks,
            checksum=_compute_checksum(data),
            timestamp=datetime.now(UTC).isoformat(),
            version=version,
            size=len(data),
        ),
    )


def segment(
    data: bytes,
    block_size: int = 4096,
    file_id: str | None = None,
    version: str = "1.0",
    parallel: bool = False,
) -> SegmentationResult:
    """Split file data into blocks with metadata."""
    if block_size <= 0:
        raise ValueError("block_size must be positive")

    fid = file_id or str(uuid.uuid4())
    chunks = [data[i : i + block_size] for i in range(0, max(len(data), 1), block_size)]
    if not chunks:
        chunks = [b""]

    total = len(chunks)

    if parallel and total > 1:
        with ThreadPoolExecutor(max_workers=min(8, total)) as executor:
            blocks = list(
                executor.map(
                    lambda args: _create_block(*args),
                    [(chunk, fid, idx, total, version) for idx, chunk in enumerate(chunks)],
                )
            )
    else:
        blocks = [_create_block(chunk, fid, idx, total, version) for idx, chunk in enumerate(chunks)]

    return SegmentationResult(
        file_id=fid,
        blocks=blocks,
        original_size=len(data),
        block_size=block_size,
        metadata={"parallel": parallel, "version": version},
    )


def reassemble(blocks: list[DataBlock]) -> bytes:
    """Reassemble blocks into original data, sorted by block index."""
    sorted_blocks = sorted(blocks, key=lambda b: b.metadata.block_index)
    return b"".join(b.data for b in sorted_blocks)
