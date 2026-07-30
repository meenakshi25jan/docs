"""API tests for Knowledge Intelligence."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


class TestKnowledgeAPI:
    @pytest.mark.asyncio
    async def test_knowledge_search_api(self, client: AsyncClient):
        with patch(
            "app.services.knowledge_intelligence_service.retrieve_knowledge",
            new_callable=AsyncMock,
            return_value=[],
        ):
            res = await client.get("/api/v1/knowledge/search?q=past+tense")
        assert res.status_code == 200
        data = res.json()
        assert data["query"] == "past tense"
        assert "grounding" in data

    @pytest.mark.asyncio
    async def test_lesson_context_api(self, client: AsyncClient):
        with patch(
            "app.services.knowledge_intelligence_service.retrieve_knowledge",
            new_callable=AsyncMock,
            return_value=[],
        ):
            res = await client.get(
                "/api/v1/knowledge/lesson-context?lesson_id=grammar-9-modal-verbs"
            )
        assert res.status_code == 200
        data = res.json()
        assert data["lesson_id"] == "grammar-9-modal-verbs"
        assert data["grounding"]["compact_text"]

    @pytest.mark.asyncio
    async def test_mistake_context_api(self, client: AsyncClient):
        with patch(
            "app.services.knowledge_intelligence_service.retrieve_knowledge",
            new_callable=AsyncMock,
            return_value=[],
        ):
            res = await client.get(
                "/api/v1/knowledge/mistake-context?error_category=past_tense"
            )
        assert res.status_code == 200
        data = res.json()
        assert data["error_category"] == "past_tense"
        assert data["grounding"]["compact_text"]

    @pytest.mark.asyncio
    async def test_knowledge_requires_auth(self, public_client: AsyncClient):
        res = await public_client.get("/api/v1/knowledge/search?q=test")
        assert res.status_code in (401, 403)
