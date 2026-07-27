from app.core.db_url import prepare_asyncpg_dsn, prepare_asyncpg_url


def test_neon_url_strips_sslmode():
    raw = "postgresql://user:pass@ep-test.neon.tech/neondb?sslmode=require"
    url, connect_args = prepare_asyncpg_url(raw)
    assert "sslmode" not in url
    assert connect_args["ssl"] is True


def test_local_url_without_ssl():
    raw = "postgresql://postgres:postgres@localhost:5432/ai_english_teacher"
    url, connect_args = prepare_asyncpg_url(raw)
    assert connect_args == {}


def test_asyncpg_dsn_format():
    raw = "postgresql://user:pass@host/db?sslmode=require"
    dsn, connect_args = prepare_asyncpg_dsn(raw)
    assert dsn.startswith("postgresql://")
    assert "+asyncpg" not in dsn
    assert connect_args["ssl"] is True
