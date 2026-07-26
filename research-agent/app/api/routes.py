"""FastAPI route definitions."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field

from app.ai.embeddings import EmbeddingService
from app.ai.summarizer import Summarizer
from app.crawler.crawler import ResearchCrawler
from app.database.database import get_job_by_id, get_job_pages, get_session, update_job_status
from app.database.models import page_to_dict
from app.reports.report_generator import ReportGenerator
from app.utils.logger import get_logger
from config import get_settings

logger = get_logger()
router = APIRouter()


class SearchRequest(BaseModel):
    """Request body for research search endpoint."""

    query: str = Field(..., min_length=1, max_length=512)
    depth: int = Field(default=2, ge=0, le=5)
    max_pages: int = Field(default=100, ge=1, le=5000)


class SearchResponse(BaseModel):
    """Response for completed research job."""

    status: str
    job_id: int
    pages: int
    report: str
    reports: dict[str, str] = Field(default_factory=dict)
    confidence_score: float | None = None


class SemanticSearchRequest(BaseModel):
    """Request for semantic search over indexed content."""

    query: str = Field(..., min_length=1)
    job_id: int | None = None
    n_results: int = Field(default=10, ge=1, le=50)


class JobStatusResponse(BaseModel):
    """Crawl job status response."""

    job_id: int
    query: str
    status: str
    pages_crawled: int
    confidence_score: float | None = None
    report_paths: dict[str, str] | None = None


async def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Optional API key authentication."""
    settings = get_settings()
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@router.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "version": get_settings().app_version}


@router.post("/search", response_model=SearchResponse, dependencies=[Depends(verify_api_key)])
async def search_and_research(request: SearchRequest) -> SearchResponse:
    """Search the web, crawl pages, summarize, and generate reports."""
    settings = get_settings()
    crawler = ResearchCrawler(settings)

    try:
        result = await crawler.run(
            query=request.query,
            depth=request.depth,
            max_pages=request.max_pages,
        )

        embedding_service = EmbeddingService(settings)
        await embedding_service.index_job_pages(result.job_id, result.pages)

        semantic_hits = await embedding_service.semantic_search(
            request.query, job_id=result.job_id, n_results=10
        )

        summarizer = Summarizer(settings)
        summary = await summarizer.summarize(
            request.query, result.pages, semantic_context=semantic_hits
        )

        report_gen = ReportGenerator(settings)
        report_paths = report_gen.generate_all(
            request.query, summary, result.pages, result.job_id
        )

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

        return SearchResponse(
            status="completed",
            job_id=result.job_id,
            pages=result.stats.pages_crawled,
            report=report_paths.get("markdown", ""),
            reports=report_paths,
            confidence_score=summary.confidence_score,
        )
    except Exception as exc:
        logger.exception("Research job failed: {}", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        await crawler.close()


@router.get("/jobs/{job_id}", response_model=JobStatusResponse, dependencies=[Depends(verify_api_key)])
async def get_job_status(job_id: int) -> JobStatusResponse:
    """Get status of a research job."""
    async with get_session() as session:
        job = await get_job_by_id(session, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return JobStatusResponse(
            job_id=job.id,
            query=job.query,
            status=job.status,
            pages_crawled=job.pages_crawled,
            confidence_score=job.confidence_score,
            report_paths=job.report_paths,
        )


@router.get("/jobs/{job_id}/pages", dependencies=[Depends(verify_api_key)])
async def get_job_pages_endpoint(job_id: int) -> list[dict[str, Any]]:
    """List all crawled pages for a job."""
    async with get_session() as session:
        job = await get_job_by_id(session, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        pages = await get_job_pages(session, job_id)
        return [page_to_dict(p) for p in pages]


@router.post("/semantic-search", dependencies=[Depends(verify_api_key)])
async def semantic_search(request: SemanticSearchRequest) -> list[dict[str, Any]]:
    """Search indexed content semantically."""
    service = EmbeddingService()
    return await service.semantic_search(
        request.query,
        job_id=request.job_id,
        n_results=request.n_results,
    )
