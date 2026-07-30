from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select, text

from app.core.config import get_settings
from app.services.health_service import probe_database, validate_production_jwt_secret
from app.api.v1.auth import router as auth_router
from app.api.v1.assessments import router as assessments_router
from app.api.v1.conversations import router as conversations_router
from app.api.v1.extended import (
    writing_router,
    plans_router,
    dashboard_router,
    reports_router,
)
from app.api.v1.voice import router as voice_router
from app.api.v1.grammar_lessons import router as grammar_router
from app.api.v1.student_intelligence import router as student_intelligence_router
from app.api.v1.memory import router as memory_router
from app.api.v1.curriculum import router as curriculum_router
from app.api.v1.knowledge import router as knowledge_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_production_jwt_secret()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = settings.API_V1_PREFIX
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(assessments_router, prefix=API_PREFIX)
app.include_router(conversations_router, prefix=API_PREFIX)
app.include_router(writing_router, prefix=API_PREFIX)
app.include_router(plans_router, prefix=API_PREFIX)
app.include_router(dashboard_router, prefix=API_PREFIX)
app.include_router(reports_router, prefix=API_PREFIX)
app.include_router(voice_router, prefix=API_PREFIX)
app.include_router(grammar_router, prefix=API_PREFIX)
app.include_router(student_intelligence_router, prefix=API_PREFIX)
app.include_router(memory_router, prefix=API_PREFIX)
app.include_router(curriculum_router, prefix=API_PREFIX)
app.include_router(knowledge_router, prefix=API_PREFIX)

try:
    from prometheus_client import make_asgi_app
    app.mount("/metrics", make_asgi_app())
except ImportError:
    pass


@app.get("/health")
async def health():
    """Health check with live database connectivity probe."""
    db_probe = await probe_database()
    db_status = db_probe["database"]
    overall = "healthy" if db_status in ("reachable", "not_configured") else "degraded"
    body: dict = {
        "status": overall,
        "version": settings.APP_VERSION,
        "database": db_status,
    }
    if db_probe.get("database_latency_ms") is not None:
        body["database_latency_ms"] = db_probe["database_latency_ms"]
    return body


@app.get("/health/auth")
async def health_auth():
    from app.core.security import hash_password, verify_password

    try:
        hashed = hash_password("health-check")
        return {"password_hashing": "ok" if verify_password("health-check", hashed) else "failed"}
    except Exception as exc:
        return {"password_hashing": "error", "detail": str(exc)}


@app.get("/health/register")
async def health_register():
    """Diagnostic: test tenant context + user table access (read-only)."""
    from app.core.database import get_session_factory, set_tenant_context
    from app.models import Tenant

    try:
        factory = get_session_factory()
        async with factory() as session:
            tenant = await session.scalar(select(Tenant).where(Tenant.slug == "default"))
            if not tenant:
                return {"register": "error", "detail": "default tenant missing — run migrations"}
            await set_tenant_context(session, str(tenant.id))
            setting = await session.scalar(text("SELECT current_setting('app.tenant_id', true)"))
            result = await session.execute(
                text("SELECT COUNT(*) FROM users WHERE tenant_id = :tid"),
                {"tid": tenant.id},
            )
            count = result.scalar()
            return {"register": "ok", "tenant_id": str(tenant.id), "setting": setting, "users": count}
    except Exception as exc:
        return {"register": "error", "detail": str(exc), "type": type(exc).__name__}


@app.get("/health/ai")
async def health_ai():
    from app.ai.openai_client import ai_client

    return {
        "provider": ai_client.provider,
        "model": ai_client.model,
        "configured": ai_client.is_configured,
        "hint": (
            "Set AI_PROVIDER=copilot + AZURE_OPENAI_* keys (Microsoft Copilot via Azure)"
            if ai_client.provider == "mock"
            else "ready"
        ),
    }


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    if settings.DEBUG:
        content = {"detail": str(exc), "type": type(exc).__name__}
    else:
        content = {"detail": "Internal server error"}
    return JSONResponse(status_code=500, content=content)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "api": settings.API_V1_PREFIX,
    }
