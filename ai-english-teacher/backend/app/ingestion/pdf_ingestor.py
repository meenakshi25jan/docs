from __future__ import annotations

from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader

from app.ingestion.base import BaseIngestor, IngestionInput, IngestResult
from app.ingestion.chunker import split_text_into_chunks


class PdfIngestor(BaseIngestor):
    """Extract text from PDF, DOCX, and plain-text files, then chunk."""

    async def ingest(self, source: IngestionInput) -> IngestResult:
        if source.file_path is None:
            raise ValueError("file_path is required for PDF/DOCX ingestion")

        path = Path(source.file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        suffix = path.suffix.lower()
        page_count: int | None
        if suffix == ".pdf":
            raw_text, page_count = _extract_pdf(path)
        elif suffix == ".docx":
            raw_text, page_count = _extract_docx(path)
        elif suffix in {".txt", ".md"}:
            raw_text = path.read_text(encoding="utf-8")
            page_count = None
        else:
            raise ValueError(f"Unsupported file type for PdfIngestor: {suffix}")

        chunks = split_text_into_chunks(raw_text)
        return IngestResult(
            title=source.title,
            raw_text=raw_text,
            language=source.language,
            page_count=page_count,
            chunks=chunks,
        )


def _extract_pdf(path: Path) -> tuple[str, int]:
    reader = PdfReader(str(path))
    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    raw_text = "\n\n".join(page for page in pages if page)
    return raw_text, len(reader.pages)


def _extract_docx(path: Path) -> tuple[str, int | None]:
    document = DocxDocument(str(path))
    paragraphs = [
        paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()
    ]
    return "\n\n".join(paragraphs), None
