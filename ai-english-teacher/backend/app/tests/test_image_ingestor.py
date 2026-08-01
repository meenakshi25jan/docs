from unittest.mock import patch

import pytest

from app.ingestion.base import IngestionInput
from app.ingestion.image_ingestor import ImageIngestor


@pytest.mark.asyncio
async def test_image_ingestor_ocr_fixture(sample_image_path):
    ingestor = ImageIngestor()
    with patch("pytesseract.image_to_string", return_value="OCR SAMPLE TEXT for testing"):
        result = await ingestor.ingest(
            IngestionInput(
                source_type="image",
                title="OCR Sample",
                file_path=sample_image_path,
            )
        )

    assert "OCR SAMPLE TEXT" in result.raw_text
    assert len(result.chunks) >= 1


@pytest.mark.asyncio
async def test_image_ingestor_empty_ocr_raises(sample_image_path):
    ingestor = ImageIngestor()
    with patch("pytesseract.image_to_string", return_value="   "):
        with pytest.raises(ValueError, match="No OCR text"):
            await ingestor.ingest(
                IngestionInput(
                    source_type="image",
                    title="Blank",
                    file_path=sample_image_path,
                )
            )
