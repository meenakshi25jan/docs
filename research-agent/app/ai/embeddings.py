"""Embedding generation and ChromaDB vector storage."""

from __future__ import annotations

import asyncio
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from app.utils.helpers import chunk_text
from app.utils.logger import get_logger
from config import Settings, get_settings

logger = get_logger()


class EmbeddingService:
    """Generate embeddings and store them in ChromaDB."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._model: SentenceTransformer | None = None
        self._client: chromadb.ClientAPI | None = None
        self._collection = None

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info("Loading embedding model: {}", self.settings.embedding_model)
            self._model = SentenceTransformer(self.settings.embedding_model)
        return self._model

    def _get_collection(self):
        if self._collection is None:
            self.settings.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=str(self.settings.chroma_persist_dir),
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self._collection = self._client.get_or_create_collection(
                name=self.settings.chroma_collection,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        if not texts:
            return []

        def _encode() -> list[list[float]]:
            model = self._get_model()
            vectors = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
            return vectors.tolist()

        return await asyncio.to_thread(_encode)

    async def index_page(
        self,
        job_id: int,
        page_id: int,
        url: str,
        title: str | None,
        text: str,
    ) -> int:
        """Index page content chunks into ChromaDB."""
        if not text or len(text.strip()) < 50:
            return 0

        chunks = chunk_text(text, chunk_size=400, overlap=50)
        if not chunks:
            return 0

        embeddings = await self.embed_texts(chunks)
        collection = self._get_collection()

        ids = [f"job{job_id}_page{page_id}_chunk{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "job_id": job_id,
                "page_id": page_id,
                "url": url,
                "title": title or "",
                "chunk_index": i,
            }
            for i in range(len(chunks))
        ]

        def _upsert() -> None:
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
            )

        await asyncio.to_thread(_upsert)
        logger.debug("Indexed {} chunks for page {}", len(chunks), page_id)
        return len(chunks)

    async def semantic_search(
        self,
        query: str,
        job_id: int | None = None,
        n_results: int = 10,
    ) -> list[dict[str, Any]]:
        """Perform semantic search over indexed content."""
        query_embedding = (await self.embed_texts([query]))[0]
        collection = self._get_collection()

        where_filter = {"job_id": job_id} if job_id is not None else None

        def _query() -> dict[str, Any]:
            return collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter,
                include=["documents", "metadatas", "distances"],
            )

        results = await asyncio.to_thread(_query)
        output: list[dict[str, Any]] = []

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc, meta, distance in zip(documents, metadatas, distances, strict=False):
            similarity = max(0.0, 1.0 - float(distance))
            output.append(
                {
                    "text": doc,
                    "url": meta.get("url", ""),
                    "title": meta.get("title", ""),
                    "page_id": meta.get("page_id"),
                    "job_id": meta.get("job_id"),
                    "similarity": round(similarity, 4),
                }
            )
        return output

    async def index_job_pages(self, job_id: int, pages: list[Any]) -> int:
        """Index all pages from a crawl job."""
        total_chunks = 0
        for page in pages:
            text = page.visible_text or ""
            chunks = await self.index_page(
                job_id=job_id,
                page_id=page.id,
                url=page.url,
                title=page.title,
                text=text,
            )
            total_chunks += chunks
        logger.info("Indexed {} chunks for job {}", total_chunks, job_id)
        return total_chunks
