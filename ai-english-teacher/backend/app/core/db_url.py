"""Normalize DATABASE_URL for asyncpg (Neon uses ?sslmode=require)."""

from __future__ import annotations

import ssl
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy.engine import make_url


def _ssl_from_mode(sslmode: str | None) -> Any:
    if not sslmode or sslmode == "disable":
        return False
    if sslmode in ("verify-ca", "verify-full"):
        return ssl.create_default_context()
    # require, prefer, allow — Neon needs TLS
    return True


def prepare_asyncpg_url(database_url: str) -> tuple[str, dict[str, Any]]:
    """
    Strip query params that asyncpg rejects (e.g. sslmode) and return connect_args.
    SQLAlchemy otherwise forwards them as connect() kwargs and raises TypeError.
    """
    url = database_url.strip()
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and "+asyncpg" not in url.split("://", 1)[0]:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    sa_url = make_url(url)
    query = dict(sa_url.query)
    connect_args: dict[str, Any] = {}

    sslmode_raw = query.pop("sslmode", None)
    sslmode = (
        sslmode_raw
        if isinstance(sslmode_raw, str)
        else (sslmode_raw[0] if sslmode_raw else None)
    )
    if "ssl" in query:
        ssl_val = query.pop("ssl")
        connect_args["ssl"] = ssl_val not in ("false", "0", "disable")
    elif sslmode:
        connect_args["ssl"] = _ssl_from_mode(sslmode)

    # asyncpg does not accept these as connect() kwargs
    for key in ("channel_binding", "options"):
        query.pop(key, None)

    clean = sa_url.set(query=query)
    return clean.render_as_string(hide_password=False), connect_args


def is_neon_database_url(database_url: str) -> bool:
    return "neon.tech" in database_url.lower()


def prepare_asyncpg_dsn(database_url: str) -> tuple[str, dict[str, Any]]:
    """Plain postgresql:// DSN for asyncpg.connect() (migrate script)."""
    sqlalchemy_url, connect_args = prepare_asyncpg_url(database_url)
    dsn = sqlalchemy_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return dsn, connect_args
