"""Unit tests for reconstruction engine."""

import hashlib

from dnastoreai.modules.metadata.header import DNAHeader
from dnastoreai.modules.reconstruction.engine import ReconstructionEngine
from dnastoreai.modules.segmentation.segmenter import segment


class TestReconstruction:
    def test_encode_decode_block(self):
        engine = ReconstructionEngine("basic", "reed_solomon")
        data = b"reconstruction test data"
        seg = segment(data, block_size=1000)
        block = seg.blocks[0]
        header = DNAHeader(
            file_id=seg.file_id,
            block_id=block.metadata.block_id,
            block_index=0,
            total_blocks=1,
            checksum=block.metadata.checksum,
        )
        encoded = engine.encode_block(block, header)
        decoded = engine.decode_block(encoded)
        assert decoded.data == data

    def test_full_reconstruction(self):
        engine = ReconstructionEngine("gc_balanced", "reed_solomon")
        data = b"full pipeline reconstruction test" * 5
        seg = segment(data, block_size=50)

        encoded_blocks = []
        for block in seg.blocks:
            header = DNAHeader(
                file_id=seg.file_id,
                block_id=block.metadata.block_id,
                block_index=block.metadata.block_index,
                total_blocks=block.metadata.total_blocks,
                checksum=block.metadata.checksum,
            )
            encoded_blocks.append(engine.encode_block(block, header))

        checksum = hashlib.sha256(data).hexdigest()
        result = engine.reconstruct(encoded_blocks, checksum)
        assert result.data == data
        assert result.metrics.checksum_valid

    def test_missing_blocks(self):
        engine = ReconstructionEngine()
        data = b"test"
        seg = segment(data, block_size=2)
        blocks = []
        for block in seg.blocks[:1]:
            header = DNAHeader(
                file_id=seg.file_id, block_id=block.metadata.block_id,
                block_index=block.metadata.block_index,
                total_blocks=block.metadata.total_blocks,
                checksum=block.metadata.checksum,
            )
            blocks.append(engine.encode_block(block, header))

        result = engine.reconstruct(blocks)
        assert result.metrics.missing_block_rate > 0

    def test_recovery_metrics_to_dict(self):
        engine = ReconstructionEngine()
        data = b"metrics test"
        seg = segment(data, block_size=1000)
        block = seg.blocks[0]
        header = DNAHeader(
            file_id=seg.file_id, block_id=block.metadata.block_id,
            block_index=0, total_blocks=1, checksum=block.metadata.checksum,
        )
        encoded = engine.encode_block(block, header)
        result = engine.reconstruct([encoded])
        assert "recovery_accuracy" in result.metrics.to_dict()
