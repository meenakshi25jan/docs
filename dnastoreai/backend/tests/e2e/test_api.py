"""End-to-end API tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from dnastoreai.core.config import Settings, get_settings
from dnastoreai.main import create_app


@pytest.fixture
def app(tmp_path):
    settings = Settings(
        data_dir=tmp_path,
        archive_dir=tmp_path / "archive",
        upload_dir=tmp_path / "uploads",
        experiment_dir=tmp_path / "experiments",
        chroma_persist_dir=tmp_path / "chroma",
        vector_db_enabled=False,
    )
    get_settings.cache_clear()
    import dnastoreai.core.dependencies as deps
    deps.get_engine.cache_clear()
    deps.get_session_factory.cache_clear()

    application = create_app()
    return application


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestAPIE2E:
    @pytest.mark.asyncio
    async def test_health(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_store_and_retrieve(self, client):
        files = {"file": ("test.txt", b"E2E test content for DNA storage", "text/plain")}
        response = await client.post(
            "/api/v1/store?compression=gzip&encoding=basic&ecc=reed_solomon&block_size=4096",
            files=files,
        )
        assert response.status_code == 200
        data = response.json()
        archive_id = data["archive_id"]
        assert data["total_dna_length"] > 0

        response = await client.post(
            "/api/v1/retrieve",
            json={"archive_id": archive_id, "config": {"substitution_rate": 0.0}},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_archives(self, client):
        response = await client.get("/api/v1/archive")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_metrics(self, client):
        response = await client.get("/api/v1/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "storage" in data

    @pytest.mark.asyncio
    async def test_simulate(self, client):
        files = {"file": ("sim.txt", b"simulation test", "text/plain")}
        store_resp = await client.post("/api/v1/store", files=files)
        archive_id = store_resp.json()["archive_id"]

        response = await client.post(
            "/api/v1/simulate",
            json={"archive_id": archive_id},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_dna(self, client):
        files = {"file": ("dna.txt", b"DNA sequence test data", "text/plain")}
        store_resp = await client.post("/api/v1/store", files=files)
        archive_id = store_resp.json()["archive_id"]

        response = await client.get(f"/api/v1/dna/{archive_id}")
        assert response.status_code == 200
        assert response.json()["sequence"]

    @pytest.mark.asyncio
    async def test_dna_not_found(self, client):
        response = await client.get("/api/v1/dna/nonexistent")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_experiment(self, client):
        response = await client.post(
            "/api/v1/experiment",
            json={
                "name": "e2e-test",
                "dataset_type": "text",
                "file_count": 2,
                "encoding": "basic",
                "ecc": "reed_solomon",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "experiment_id" in data
