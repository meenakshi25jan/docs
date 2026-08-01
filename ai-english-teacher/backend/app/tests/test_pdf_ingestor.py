from pathlib import Path

import pytest

from app.ingestion.base import IngestionInput
from app.ingestion.pdf_ingestor import PdfIngestor


@pytest.mark.asyncio
async def test_pdf_ingestor_reads_txt_fixture(sample_txt_path):
    ingestor = PdfIngestor()
    result = await ingestor.ingest(
        IngestionInput(
            source_type="manual",
            title="Present Simple",
            file_path=sample_txt_path,
        )
    )

    assert "present simple" in result.raw_text.lower()
    assert len(result.chunks) >= 1
    assert result.chunks[0].chunk_index == 0


@pytest.mark.asyncio
async def test_pdf_ingestor_reads_pdf_fixture():
    ingestor = PdfIngestor()
    pdf_path = Path(__file__).resolve().parent / "fixtures" / "ingestion" / "sample.pdf"
    result = await ingestor.ingest(
        IngestionInput(
            source_type="pdf",
            title="PDF Fixture",
            file_path=pdf_path,
        )
    )

    assert "present simple" in result.raw_text.lower()
    assert result.page_count == 1
    assert len(result.chunks) >= 1


@pytest.mark.asyncio
async def test_pdf_ingestor_missing_file_raises(tmp_path):
    ingestor = PdfIngestor()
    with pytest.raises(FileNotFoundError):
        await ingestor.ingest(
            IngestionInput(
                source_type="pdf",
                title="Missing",
                file_path=tmp_path / "missing.pdf",
            )
        )
