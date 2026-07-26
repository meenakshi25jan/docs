"""FastAPI application entry point."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ai.embeddings import EmbeddingService
from app.ai.summarizer import Summarizer
from app.api.routes import router
from app.crawler.crawler import ResearchCrawler
from app.database.database import get_job_by_id, get_session, init_db, update_job_status
from app.reports.report_generator import ReportGenerator
from app.utils.logger import get_logger, setup_logger
from config import get_settings

setup_logger()
logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    await init_db()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI Web Crawler and Research Assistant",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()


async def run_research_cli(query: str, depth: int, pages: int) -> dict:
    """Execute a full research pipeline from CLI."""
    settings = get_settings()
    await init_db()

    crawler = ResearchCrawler(settings)
    try:
        result = await crawler.run(query=query, depth=depth, max_pages=pages)

        embedding_service = EmbeddingService(settings)
        await embedding_service.index_job_pages(result.job_id, result.pages)

        semantic_hits = await embedding_service.semantic_search(
            query, job_id=result.job_id, n_results=10
        )

        summarizer = Summarizer(settings)
        summary = await summarizer.summarize(
            query, result.pages, semantic_context=semantic_hits
        )

        report_gen = ReportGenerator(settings)
        report_paths = report_gen.generate_all(query, summary, result.pages, result.job_id)

        async with get_session() as session:
            job = await get_job_by_id(session, result.job_id)
            if job:
                await update_job_status(
                    session,
                    job,
                    "completed",
                    pages_crawled=result.stats.pages_crawled,
                    summary=summary.executive_summary,
                    confidence_score=summary.confidence_score,
                    report_paths=report_paths,
                )

        output = {
            "status": "completed",
            "job_id": result.job_id,
            "pages": result.stats.pages_crawled,
            "report": report_paths.get("markdown", ""),
            "reports": report_paths,
            "confidence_score": summary.confidence_score,
        }
        print(json.dumps(output, indent=2))
        return output
    finally:
        await crawler.close()


def build_cli_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="AI Web Crawler and Research Assistant",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Run a research crawl")
    search_parser.add_argument("--query", "-q", required=True, help="Search query")
    search_parser.add_argument("--depth", "-d", type=int, default=2, help="Crawl depth")
    search_parser.add_argument("--pages", "-p", type=int, default=100, help="Max pages")

    serve_parser = subparsers.add_parser("serve", help="Start the REST API server")
    serve_parser.add_argument("--host", default=None, help="API host")
    serve_parser.add_argument("--port", type=int, default=None, help="API port")

    return parser


def main() -> None:
    """CLI entry point."""
    parser = build_cli_parser()
    args = parser.parse_args()
    settings = get_settings()

    if args.command == "search":
        asyncio.run(run_research_cli(args.query, args.depth, args.pages))
    elif args.command == "serve":
        host = args.host or settings.api_host
        port = args.port or settings.api_port
        logger.info("Starting API server on {}:{}", host, port)
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=settings.debug,
        )


if __name__ == "__main__":
    main()
