"""Tests for optional table query resilience."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import ProgrammingError

from app.repositories.optional_tables import query_optional_table


@pytest.mark.asyncio
async def test_query_optional_table_returns_default_on_missing_table():
    db = AsyncMock()
    db.rollback = AsyncMock()

    async def failing_query():
        raise ProgrammingError("SELECT", {}, Exception("relation voice_analyses does not exist"))

    result = await query_optional_table(db, failing_query, [])
    assert result == []
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_query_optional_table_returns_value_on_success():
    db = MagicMock()

    async def ok_query():
        return {"speaking": 80.0}

    result = await query_optional_table(db, ok_query, {})
    assert result == {"speaking": 80.0}
