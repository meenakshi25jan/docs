from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import IngestionStatus, KnowledgeType, SourceType
from app.db.models.knowledge_chunk import KnowledgeChunk
from app.db.models.knowledge_document import KnowledgeDocument
from app.db.models.knowledge_embedding import KnowledgeEmbedding
from app.db.models.knowledge_source import KnowledgeSource
from app.ingestion.base import BaseIngestor, IngestionInput, IngestResult
from app.ingestion.image_ingestor import ImageIngestor
from app.ingestion.pdf_ingestor import PdfIngestor
from app.ingestion.website_ingestor import WebsiteIngestor

logger = logging.getLogger(__name__)

EmbedFn = Callable[[str], list[float]]


class IngestionOrchestrator:
    """
    Dispatch ingestion by source_type, persist rows, and generate embeddings.

    Re-ingestion strategy: delete-and-recreate for the source_id. This keeps
    chunk indices and embeddings consistent when chunking rules change and
    avoids orphaned rows after partial failures.

    embed_fn is intentionally pluggable — this layer does not import
    sentence-transformers or any specific embedding provider.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._ingestors: dict[str, BaseIngestor] = {
            SourceType.PDF.value: PdfIngestor(),
            SourceType.BOOK.value: PdfIngestor(),
            SourceType.DOCX.value: PdfIngestor(),
            SourceType.MANUAL.value: PdfIngestor(),
            SourceType.WEBSITE.value: WebsiteIngestor(),
            SourceType.IMAGE.value: ImageIngestor(),
        }

    async def ingest_source(
        self,
        *,
        source_id: uuid.UUID,
        embed_fn: EmbedFn | None = None,
        embedding_model: str = "pluggable",
    ) -> KnowledgeSource:
        source = await self.session.get(KnowledgeSource, source_id)
        if source is None:
            raise ValueError(f"knowledge_source not found: {source_id}")

        source.ingestion_status = IngestionStatus.PROCESSING.value
        source.error_message = None
        await self.session.commit()

        try:
            await self._clear_existing_artifacts(source.id)
            ingestor = self._resolve_ingestor(source.source_type)
            payload = self._build_input(source)
            result = await ingestor.ingest(payload)
            document = await self._persist_document(source, result)
            chunks = await self._persist_chunks(document, result)

            if embed_fn is not None:
                await self._persist_embeddings(chunks, embed_fn, embedding_model)

            if not source.license_type:
                raise ValueError(
                    "license_type is required before ingestion can be marked completed"
                )

            source.ingestion_status = IngestionStatus.COMPLETED.value
            source.error_message = None
            await self.session.commit()
            await self.session.refresh(source)
            return source
        except Exception as exc:
            logger.exception("Ingestion failed for source %s", source_id)
            await self.session.rollback()
            failed = await self.session.get(KnowledgeSource, source_id)
            if failed is not None:
                failed.ingestion_status = IngestionStatus.FAILED.value
                failed.error_message = str(exc)[:4000]
                await self.session.commit()
                await self.session.refresh(failed)
                return failed
            raise

    def _resolve_ingestor(self, source_type: str) -> BaseIngestor:
        ingestor = self._ingestors.get(source_type)
        if ingestor is None:
            raise ValueError(f"No ingestor registered for source_type={source_type}")
        return ingestor

    def _build_input(self, source: KnowledgeSource) -> IngestionInput:
        file_path = Path(source.file_path) if source.file_path else None
        return IngestionInput(
            source_type=source.source_type,
            title=source.title,
            file_path=file_path,
            source_url=source.source_url,
        )

    async def _clear_existing_artifacts(self, source_id: uuid.UUID) -> None:
        chunk_ids = await self.session.scalars(
            select(KnowledgeChunk.id)
            .join(KnowledgeDocument, KnowledgeDocument.id == KnowledgeChunk.document_id)
            .where(KnowledgeDocument.source_id == source_id)
        )
        ids = list(chunk_ids)
        if ids:
            await self.session.execute(
                delete(KnowledgeEmbedding).where(
                    KnowledgeEmbedding.knowledge_type == KnowledgeType.KNOWLEDGE_CHUNK.value,
                    KnowledgeEmbedding.knowledge_id.in_(ids),
                )
            )
        await self.session.execute(
            delete(KnowledgeDocument).where(KnowledgeDocument.source_id == source_id)
        )
        await self.session.commit()

    async def _persist_document(
        self, source: KnowledgeSource, result: IngestResult
    ) -> KnowledgeDocument:
        document = KnowledgeDocument(
            source_id=source.id,
            title=result.title,
            raw_text=result.raw_text,
            language=result.language,
            page_count=result.page_count,
        )
        self.session.add(document)
        await self.session.flush()
        return document

    async def _persist_chunks(
        self, document: KnowledgeDocument, result: IngestResult
    ) -> list[KnowledgeChunk]:
        rows: list[KnowledgeChunk] = []
        for chunk in result.chunks:
            row = KnowledgeChunk(
                document_id=document.id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                skill=chunk.skill,
                level=chunk.level,
                page_number=chunk.page_number,
                section_title=chunk.section_title,
                token_count=chunk.token_count,
            )
            self.session.add(row)
            rows.append(row)
        await self.session.flush()
        return rows

    async def _persist_embeddings(
        self,
        chunks: list[KnowledgeChunk],
        embed_fn: EmbedFn,
        embedding_model: str,
    ) -> None:
        for index, chunk in enumerate(chunks):
            vector = embed_fn(chunk.content)
            row = KnowledgeEmbedding(
                knowledge_type=KnowledgeType.KNOWLEDGE_CHUNK.value,
                knowledge_id=chunk.id,
                chunk_index=chunk.chunk_index,
                embedding_model=embedding_model,
                embedding=vector,
            )
            self.session.add(row)
            if index > 0 and index % 25 == 0:
                await self.session.flush()
        await self.session.flush()
