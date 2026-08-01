from __future__ import annotations

from pathlib import Path

import pytesseract
from PIL import Image

from app.ingestion.base import BaseIngestor, IngestionInput, IngestResult
from app.ingestion.chunker import split_text_into_chunks


class ImageIngestor(BaseIngestor):
    """OCR image files into text chunks (MVP: pytesseract wrapper)."""

    async def ingest(self, source: IngestionInput) -> IngestResult:
        if source.file_path is None:
            raise ValueError("file_path is required for image ingestion")

        path = Path(source.file_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")

        with Image.open(path) as image:
            raw_text = pytesseract.image_to_string(image).strip()

        if not raw_text:
            raise ValueError(f"No OCR text extracted from image: {path}")

        chunks = split_text_into_chunks(raw_text)
        return IngestResult(
            title=source.title,
            raw_text=raw_text,
            language=source.language,
            page_count=1,
            chunks=chunks,
        )
