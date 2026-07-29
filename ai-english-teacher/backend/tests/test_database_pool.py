from app.core.database import _engine_pool_kwargs
from app.core.db_url import is_neon_database_url


class _Settings:
    DATABASE_POOL_SIZE = 20
    DATABASE_MAX_OVERFLOW = 10


def test_is_neon_database_url():
    assert is_neon_database_url("postgresql://u:p@ep-x.us-east-2.aws.neon.tech/db")
    assert not is_neon_database_url("postgresql://postgres@localhost:5432/db")


def test_neon_pool_capped():
    neon = "postgresql://u:p@ep-x.neon.tech/db"
    kwargs = _engine_pool_kwargs(_Settings(), neon)
    assert kwargs == {"pool_size": 5, "max_overflow": 5}


def test_local_pool_unchanged():
    local = "postgresql://postgres@localhost:5432/ai_english_teacher"
    kwargs = _engine_pool_kwargs(_Settings(), local)
    assert kwargs == {"pool_size": 20, "max_overflow": 10}
