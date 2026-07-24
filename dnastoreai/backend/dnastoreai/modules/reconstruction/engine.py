"""File reconstruction engine with ECC decoding and metrics."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from dnastoreai.modules.ecc.strategies import ECCStrategy, get_ecc_strategy
from dnastoreai.modules.encoding.encoder import DNAEncoder, get_encoder
from dnastoreai.modules.metadata.header import DNAHeader
from dnastoreai.modules.segmentation.segmenter import BlockMetadata, DataBlock, reassemble


@dataclass
class RecoveryMetrics:
    """Metrics for file reconstruction quality."""

    recovery_accuracy: float
    bit_error_rate: float
    sequence_recovery_rate: float
    missing_block_rate: float
    blocks_recovered: int
    blocks_total: int
    checksum_valid: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "recovery_accuracy": self.recovery_accuracy,
            "bit_error_rate": self.bit_error_rate,
            "sequence_recovery_rate": self.sequence_recovery_rate,
            "missing_block_rate": self.missing_block_rate,
            "blocks_recovered": self.blocks_recovered,
            "blocks_total": self.blocks_total,
            "checksum_valid": self.checksum_valid,
        }


@dataclass
class ReconstructionResult:
    """Result of file reconstruction."""

    data: bytes
    metrics: RecoveryMetrics
    missing_blocks: list[int] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class EncodedBlock:
    """An encoded block ready for storage/retrieval."""

    header: DNAHeader
    dna_sequence: str
    ecc_encoded_data: bytes


class ReconstructionEngine:
    """Recover original files from DNA-encoded blocks."""

    def __init__(
        self,
        encoding_method: str = "gc_balanced",
        ecc_type: str = "reed_solomon",
    ) -> None:
        self.encoder: DNAEncoder = get_encoder(encoding_method)  # type: ignore[arg-type]
        self.ecc: ECCStrategy = get_ecc_strategy(ecc_type)

    def encode_block(self, block: DataBlock, header: DNAHeader) -> EncodedBlock:
        """Encode a data block through ECC and DNA encoding."""
        ecc_data = self.ecc.encode(block.data)
        dna_sequence = self.encoder.encode(ecc_data)
        return EncodedBlock(header=header, dna_sequence=dna_sequence, ecc_encoded_data=ecc_data)

    def decode_block(self, encoded: EncodedBlock) -> DataBlock:
        """Decode a single DNA-encoded block."""
        binary_data = self.encoder.decode(encoded.dna_sequence)
        decoded_data = self.ecc.decode(binary_data)
        h = encoded.header
        metadata = BlockMetadata(
            block_id=h.block_id,
            file_id=h.file_id,
            block_index=h.block_index,
            total_blocks=h.total_blocks,
            checksum=h.checksum,
            timestamp=datetime.now(UTC).isoformat(),
            version=h.encoding_version,
            size=len(decoded_data),
        )
        return DataBlock(data=decoded_data, metadata=metadata)

    def reconstruct(
        self,
        encoded_blocks: list[EncodedBlock],
        original_checksum: str | None = None,
    ) -> ReconstructionResult:
        """Reconstruct file from encoded blocks."""
        errors: list[str] = []
        decoded_blocks: list[DataBlock] = []
        missing: list[int] = []

        total_blocks = max((b.header.total_blocks for b in encoded_blocks), default=0)
        present_indices = {b.header.block_index for b in encoded_blocks}

        for i in range(total_blocks):
            if i not in present_indices:
                missing.append(i)

        for encoded in sorted(encoded_blocks, key=lambda b: b.header.block_index):
            try:
                decoded_blocks.append(self.decode_block(encoded))
            except Exception as e:
                errors.append(f"Block {encoded.header.block_index}: {e}")

        recovered_data = reassemble(decoded_blocks) if decoded_blocks else b""
        checksum_valid = True
        if original_checksum:
            actual = hashlib.sha256(recovered_data).hexdigest()
            checksum_valid = actual == original_checksum

        metrics = RecoveryMetrics(
            recovery_accuracy=len(decoded_blocks) / max(total_blocks, 1),
            bit_error_rate=0.0 if checksum_valid else 1.0 - len(decoded_blocks) / max(total_blocks, 1),
            sequence_recovery_rate=len(decoded_blocks) / max(total_blocks, 1),
            missing_block_rate=len(missing) / max(total_blocks, 1),
            blocks_recovered=len(decoded_blocks),
            blocks_total=total_blocks,
            checksum_valid=checksum_valid,
        )

        return ReconstructionResult(
            data=recovered_data,
            metrics=metrics,
            missing_blocks=missing,
            errors=errors,
        )
