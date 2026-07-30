"""Graceful queries when optional migration tables are not yet applied."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypeVar

from sqlalchemy.exc import DBAPIError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


def _is_missing_table_error(exc: BaseException) -> bool:
    msg = str(exc).lower()
    return (
        "does not exist" in msg
        or "undefinedtable" in msg
        or "undefined_table" in msg
        or "relation" in msg
        and "does not exist" in msg
    )


async def query_optional_table(
    db: AsyncSession,
    query_fn: Callable[[], Awaitable[T]],
    default: T,
) -> T:
    """
    Run a query against tables that may be missing before migrations 005–007.
    Returns default instead of raising when the table is absent.
    """
    try:
        return await query_fn()
    except (ProgrammingError, DBAPIError) as exc:
        if _is_missing_table_error(exc):
            await db.rollback()
            return default
        raise
