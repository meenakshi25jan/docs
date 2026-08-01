from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ingestion.base import IngestionInput
from app.ingestion.website_ingestor import WebsiteIngestor


@pytest.mark.asyncio
async def test_website_ingestor_extracts_article_text(sample_html_path: Path):
    html = sample_html_path.read_text(encoding="utf-8")
    ingestor = WebsiteIngestor()

    mock_response = MagicMock()
    mock_response.text = html
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch.object(ingestor, "_ensure_robots_allowed", new=AsyncMock()):
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client_cls.return_value.__aenter__.return_value = mock_client
            result = await ingestor.ingest(
                IngestionInput(
                    source_type="website",
                    title="Lesson Page",
                    source_url="https://example.test/grammar/present-simple",
                )
            )

    assert "present simple tense" in result.raw_text.lower()
    assert len(result.chunks) >= 1
    assert result.chunks[0].section_title


@pytest.mark.asyncio
async def test_website_ingestor_blocks_disallowed_robots():
    ingestor = WebsiteIngestor()
    with patch.object(ingestor, "_ensure_robots_allowed", side_effect=PermissionError("blocked")):
        with pytest.raises(PermissionError, match="blocked"):
            await ingestor.ingest(
                IngestionInput(
                    source_type="website",
                    title="Blocked",
                    source_url="https://example.test/private",
                )
            )
