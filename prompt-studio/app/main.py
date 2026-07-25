from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import generate, health

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready Prompt Studio — generate optimized, safe, structured prompts.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(generate.router)

static_dir: Path = settings.static_dir
if static_dir.is_dir():
    app.mount("/assets", StaticFiles(directory=static_dir), name="assets")


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    index_path = static_dir / "index.html"
    if not index_path.is_file():
        raise RuntimeError(f"Missing UI: {index_path}")
    return FileResponse(index_path)
