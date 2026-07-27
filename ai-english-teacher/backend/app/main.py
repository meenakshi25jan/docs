import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.v1.auth import router as auth_router
from app.api.v1.assessments import router as assessments_router
from app.api.v1.conversations import router as conversations_router
from app.api.v1.extended import (
    writing_router,
    plans_router,
    dashboard_router,
    reports_router,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
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

try:
    from prometheus_client import make_asgi_app
    app.mount("/metrics", make_asgi_app())
except ImportError:
    pass


@app.get("/health")
async def health():
    db_status = "ok"
    try:
        get_settings().DATABASE_URL.strip()
        if not get_settings().DATABASE_URL.strip():
            db_status = "not_configured"
    except Exception:
        db_status = "error"
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "database": db_status,
    }


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "api": settings.API_V1_PREFIX,
    }
