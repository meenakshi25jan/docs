from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.db.session import check_database_connection

router = APIRouter(prefix="/health", tags=["health"])
settings = get_settings()


@router.get("")
async def health() -> dict:
    connected, latency_ms = await check_database_connection()
    status_value = "healthy" if connected else "degraded"
    body: dict = {
        "status": status_value,
        "app": settings.APP_NAME,
        "database": "reachable" if connected else "unreachable",
    }
    if latency_ms is not None:
        body["database_latency_ms"] = latency_ms
    return body


@router.get("/live")
async def health_live() -> dict:
    return {"status": "alive", "app": settings.APP_NAME}


@router.get("/ready")
async def health_ready():
    connected, latency_ms = await check_database_connection()
    body: dict = {
        "status": "ready" if connected else "not_ready",
        "app": settings.APP_NAME,
        "database": "reachable" if connected else "unreachable",
    }
    if latency_ms is not None:
        body["database_latency_ms"] = latency_ms
    if not connected:
        return JSONResponse(status_code=503, content=body)
    return body
