"""Dialect-aware column types for Postgres-first models with SQLite test compatibility."""

from __future__ import annotations

from sqlalchemy import JSON, String, Text, TypeDecorator
from sqlalchemy.dialects.postgresql import ARRAY, JSONB


class StringArray(TypeDecorator[list[str] | None]):
    """PostgreSQL text[] in production; JSON array in SQLite tests."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(ARRAY(String(50)))
        return dialect.type_descriptor(JSON())


class JsonDocument(TypeDecorator[dict | None]):
    """PostgreSQL JSONB in production; JSON in SQLite tests."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB(astext_type=Text()))
        return dialect.type_descriptor(JSON())


class EmbeddingVector(TypeDecorator[list[float]]):
    """pgvector column in PostgreSQL; TEXT placeholder in SQLite tests."""

    impl = Text
    cache_ok = True

    def __init__(self, dimension: int) -> None:
        super().__init__()
        self.dimension = dimension

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from pgvector.sqlalchemy import Vector

            return dialect.type_descriptor(Vector(self.dimension))
        return dialect.type_descriptor(Text())
