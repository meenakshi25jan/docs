"""Unit tests for vector store."""

from dnastoreai.core.config import Settings
from dnastoreai.storage.vector_store import VectorStore


class TestVectorStore:
    def test_fallback_add_and_query(self, tmp_path):
        settings = Settings(chroma_persist_dir=tmp_path / "chroma", vector_db_enabled=False)
        store = VectorStore(settings)
        store.add("doc1", [1.0, 0.0, 0.0], {"content": "DNA storage"})
        store.add("doc2", [0.9, 0.1, 0.0], {"content": "DNA encoding"})
        results = store.query([1.0, 0.0, 0.0], top_k=2)
        assert len(results) == 2
        assert results[0][0] == "doc1"

    def test_empty_query(self, tmp_path):
        settings = Settings(chroma_persist_dir=tmp_path / "chroma", vector_db_enabled=False)
        store = VectorStore(settings)
        results = store.query([1.0, 0.0], top_k=5)
        assert results == []

    def test_mismatched_dimensions(self, tmp_path):
        settings = Settings(vector_db_enabled=False)
        store = VectorStore(settings)
        store.add("doc1", [1.0, 0.0], {})
        results = store.query([1.0, 0.0, 0.0], top_k=1)
        assert results[0][1] == 0.0
