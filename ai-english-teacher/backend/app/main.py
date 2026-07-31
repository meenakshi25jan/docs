from fastapi import FastAPI

from app.api import auth, health, users
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": settings.APP_NAME,
        "docs": "/docs",
        "health": "/health",
    }
