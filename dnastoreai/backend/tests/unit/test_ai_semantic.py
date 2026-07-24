"""Unit tests for AI reconstruction and semantic archive."""

from dnastoreai.modules.ai_reconstruction.reconstructor import (
    DNAGraphReconstructor,
    DNATransformerReconstructor,
    predict_missing_bases,
    predict_missing_blocks,
)
from dnastoreai.modules.semantic_archive.archive import SemanticDNAArchive


class TestAIReconstruction:
    def test_transformer_reconstruct(self):
        recon = DNATransformerReconstructor()
        seq, metrics = recon.reconstruct("ACGTACGT")
        assert seq == "ACGTACGT"
        assert metrics.confidence_score > 0

    def test_graph_reconstruct(self):
        recon = DNAGraphReconstructor()
        seq, metrics = recon.reconstruct("ACGTACGT")
        assert metrics.reconstruction_success

    def test_predict_missing_blocks(self):
        result = predict_missing_blocks([0, 2], 5)
        assert isinstance(result, list)

    def test_predict_missing_bases(self):
        result = predict_missing_bases("ACGTACGT", [2])
        assert len(result) == 8
        assert result[2] in "ACGT"

    def test_ai_metrics_to_dict(self):
        recon = DNATransformerReconstructor()
        _, metrics = recon.reconstruct("ACGT")
        assert "prediction_accuracy" in metrics.to_dict()


class TestSemanticArchive:
    def test_store_and_search(self):
        archive = SemanticDNAArchive()
        archive.store_document("doc1", "DNA storage research paper", "ACGTACGT")
        results = archive.semantic_search("DNA storage")
        assert len(results) > 0

    def test_similar_documents(self):
        archive = SemanticDNAArchive()
        archive.store_document("doc1", "DNA encoding methods", "ACGT")
        archive.store_document("doc2", "DNA encoding techniques", "GCTA")
        results = archive.similar_documents("doc1")
        assert isinstance(results, list)

    def test_search_empty(self):
        archive = SemanticDNAArchive()
        assert archive.similar_documents("nonexistent") == []
