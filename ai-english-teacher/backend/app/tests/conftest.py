import os
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from PIL import Image, ImageDraw
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.dependencies import get_db
from app.db.base import Base
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
INGESTION_FIXTURES_DIR = Path(__file__).parent / "fixtures" / "ingestion"


@pytest.fixture(scope="session", autouse=True)
def configure_test_env() -> None:
    os.environ.setdefault("JWT_SECRET", "test-secret-key-for-pytest-only")
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    get_settings.cache_clear()


@pytest.fixture
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_engine) -> AsyncGenerator[AsyncClient, None]:
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_txt_path() -> Path:
    return INGESTION_FIXTURES_DIR / "sample.txt"


@pytest.fixture
def sample_html_path() -> Path:
    return INGESTION_FIXTURES_DIR / "sample.html"


@pytest.fixture
def sample_lesson_pdf_path(tmp_path: Path, sample_txt_path: Path) -> Path:
    target = tmp_path / "lesson.txt"
    target.write_text(sample_txt_path.read_text(encoding="utf-8"), encoding="utf-8")
    return target


@pytest.fixture
def sample_image_path(tmp_path: Path) -> Path:
    image_path = tmp_path / "sample.png"
    image = Image.new("RGB", (400, 120), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((10, 40), "OCR SAMPLE TEXT", fill="black")
    image.save(image_path)
    return image_path
