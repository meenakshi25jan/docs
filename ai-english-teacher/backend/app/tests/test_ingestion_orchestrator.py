import uuid
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.models.enums import IngestionStatus, KnowledgeType, SourceType
from app.db.models.knowledge_chunk import KnowledgeChunk
from app.db.models.knowledge_document import KnowledgeDocument
from app.db.models.knowledge_embedding import KnowledgeEmbedding
from app.db.models.knowledge_source import KnowledgeSource
from app.ingestion.ingestion_orchestrator import IngestionOrchestrator


@pytest.fixture
async def ingestion_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


def _stub_embed(text: str) -> list[float]:
    return [0.1, 0.2, 0.3]


def _failing_embed_factory(fail_at: int):
    calls = {"count": 0}

    def embed(text: str) -> list[float]:
        calls["count"] += 1
        if calls["count"] >= fail_at:
            raise RuntimeError("embedding provider unavailable")
        return [0.1, 0.2, 0.3]

    return embed


@pytest.mark.asyncio
async def test_orchestrator_ingests_txt_source(ingestion_session, sample_lesson_pdf_path: Path):
    source = KnowledgeSource(
        source_type=SourceType.MANUAL.value,
        title="Lesson Fixture",
        file_path=str(sample_lesson_pdf_path),
        license_type="CC-BY-4.0",
        ingestion_status=IngestionStatus.PENDING.value,
    )
    ingestion_session.add(source)
    await ingestion_session.commit()
    await ingestion_session.refresh(source)

    orchestrator = IngestionOrchestrator(ingestion_session)
    result = await orchestrator.ingest_source(
        source_id=source.id,
        embed_fn=_stub_embed,
        embedding_model="test-stub",
    )

    assert result.ingestion_status == IngestionStatus.COMPLETED.value
    assert result.error_message is None

    documents = (
        await ingestion_session.scalars(
            select(KnowledgeDocument).where(KnowledgeDocument.source_id == source.id)
        )
    ).all()
    assert len(documents) == 1

    chunks = (
        await ingestion_session.scalars(
            select(KnowledgeChunk).where(KnowledgeChunk.document_id == documents[0].id)
        )
    ).all()
    assert len(chunks) >= 1

    embeddings = (
        await ingestion_session.scalars(
            select(KnowledgeEmbedding).where(
                KnowledgeEmbedding.knowledge_type == KnowledgeType.KNOWLEDGE_CHUNK.value
            )
        )
    ).all()
    assert len(embeddings) == len(chunks)


@pytest.mark.asyncio
async def test_orchestrator_failure_sets_failed_status(
    ingestion_session, sample_lesson_pdf_path: Path
):
    source = KnowledgeSource(
        source_type=SourceType.MANUAL.value,
        title="Failing Lesson",
        file_path=str(sample_lesson_pdf_path),
        license_type="CC-BY-4.0",
        ingestion_status=IngestionStatus.PENDING.value,
    )
    ingestion_session.add(source)
    await ingestion_session.commit()
    await ingestion_session.refresh(source)

    orchestrator = IngestionOrchestrator(ingestion_session)
    result = await orchestrator.ingest_source(
        source_id=source.id,
        embed_fn=_failing_embed_factory(fail_at=1),
        embedding_model="test-stub",
    )

    assert result.ingestion_status == IngestionStatus.FAILED.value
    assert result.error_message
    assert "embedding provider unavailable" in result.error_message

    doc_count = await ingestion_session.scalar(
        select(func.count())
        .select_from(KnowledgeDocument)
        .where(KnowledgeDocument.source_id == source.id)
    )
    assert doc_count == 0


@pytest.mark.asyncio
async def test_orchestrator_reingest_does_not_duplicate_rows(
    ingestion_session, sample_lesson_pdf_path: Path
):
    source = KnowledgeSource(
        source_type=SourceType.MANUAL.value,
        title="Re-ingest Lesson",
        file_path=str(sample_lesson_pdf_path),
        license_type="CC-BY-4.0",
        ingestion_status=IngestionStatus.PENDING.value,
    )
    ingestion_session.add(source)
    await ingestion_session.commit()
    await ingestion_session.refresh(source)

    orchestrator = IngestionOrchestrator(ingestion_session)
    await orchestrator.ingest_source(
        source_id=source.id, embed_fn=_stub_embed, embedding_model="test-stub"
    )
    await orchestrator.ingest_source(
        source_id=source.id, embed_fn=_stub_embed, embedding_model="test-stub"
    )

    doc_count = await ingestion_session.scalar(
        select(func.count())
        .select_from(KnowledgeDocument)
        .where(KnowledgeDocument.source_id == source.id)
    )
    chunk_count = await ingestion_session.scalar(
        select(func.count())
        .select_from(KnowledgeChunk)
        .join(KnowledgeDocument, KnowledgeDocument.id == KnowledgeChunk.document_id)
        .where(KnowledgeDocument.source_id == source.id)
    )
    embedding_count = await ingestion_session.scalar(
        select(func.count())
        .select_from(KnowledgeEmbedding)
        .where(KnowledgeEmbedding.knowledge_type == KnowledgeType.KNOWLEDGE_CHUNK.value)
    )

    assert doc_count == 1
    assert chunk_count is not None and chunk_count >= 1
    assert embedding_count == chunk_count


@pytest.mark.asyncio
async def test_orchestrator_requires_license_before_completed(
    ingestion_session, sample_lesson_pdf_path: Path
):
    source = KnowledgeSource(
        source_type=SourceType.MANUAL.value,
        title="No License",
        file_path=str(sample_lesson_pdf_path),
        license_type=None,
        ingestion_status=IngestionStatus.PENDING.value,
    )
    ingestion_session.add(source)
    await ingestion_session.commit()
    await ingestion_session.refresh(source)

    orchestrator = IngestionOrchestrator(ingestion_session)
    result = await orchestrator.ingest_source(source_id=source.id, embed_fn=_stub_embed)

    assert result.ingestion_status == IngestionStatus.FAILED.value
    assert "license_type is required" in (result.error_message or "")
