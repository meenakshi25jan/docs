from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response

from app.core.build_info import get_build_info
from app.core.config import get_settings
from app.core.metrics import metrics_response
from app.db.session import check_database_connection

router = APIRouter(tags=["health"])
settings = get_settings()


def _build_metadata() -> dict[str, str]:
    info = get_build_info()
    return {
        "commit": info["commit"],
        "builtAt": info["builtAt"],
        "service": info["service"],
        "environment": settings.APP_ENV,
    }


@router.get("/home")
async def home() -> dict:
    return {
        "message": "Welcome to AI English Teacher Platform",
        "features": [
            "Grammar correction",
            "Conversation practice",
            "Audio conversation",
            "Band score estimation",
        ],
        "build": _build_metadata(),
    }


@router.get("/build-info")
async def build_info() -> dict:
    """Deployment identity — aligned with frontend public/build-info.json shape."""
    return get_build_info()


@router.get("/health")
async def health() -> dict:
    connected, latency_ms = await check_database_connection()
    status_value = "healthy" if connected else "degraded"
    body: dict = {
        "status": status_value,
        "app": settings.APP_NAME,
        "database": "reachable" if connected else "unreachable",
        "build": _build_metadata(),
    }
    if latency_ms is not None:
        body["database_latency_ms"] = latency_ms
    return body


@router.get("/health/live")
async def health_live() -> dict:
    return {
        "status": "alive",
        "app": settings.APP_NAME,
        "build": _build_metadata(),
    }


@router.get("/health/ready")
async def health_ready():
    connected, latency_ms = await check_database_connection()
    body: dict = {
        "status": "ready" if connected else "not_ready",
        "app": settings.APP_NAME,
        "database": "reachable" if connected else "unreachable",
        "build": _build_metadata(),
    }
    if latency_ms is not None:
        body["database_latency_ms"] = latency_ms
    if not connected:
        return JSONResponse(status_code=503, content=body)
    return body


@router.get("/metrics")
async def metrics() -> Response:
    """Prometheus scrape endpoint — no auth; restrict at network edge in production."""
    payload, content_type = metrics_response()
    return Response(content=payload, media_type=content_type)
