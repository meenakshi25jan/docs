"""API route handlers."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from dnastoreai.core.dependencies import (
    get_archive_service,
    get_experiment_service,
    get_metrics_service,
    get_pipeline_service,
)
from dnastoreai.core.exceptions import ArchiveNotFoundError, DNAStoreAIError
from dnastoreai.models.schemas import (
    ArchiveListItem,
    DNARecordResponse,
    ExperimentRequest,
    ExperimentResponse,
    MetricsResponse,
    PipelineConfigSchema,
    RetrieveRequest,
    RetrieveResponse,
    SimulateRequest,
    SimulateResponse,
    StoreResponse,
)
from dnastoreai.services.archive_service import ArchiveService
from dnastoreai.services.experiment_service import ExperimentService
from dnastoreai.services.metrics_service import MetricsService
from dnastoreai.services.pipeline_service import PipelineConfig, PipelineService

router = APIRouter()


def _to_pipeline_config(schema: PipelineConfigSchema) -> PipelineConfig:
    return PipelineConfig(**schema.model_dump())


@router.post("/store", response_model=StoreResponse)
async def store_file(
    file: UploadFile = File(...),
    config: PipelineConfigSchema = Depends(),
    pipeline: PipelineService = Depends(get_pipeline_service),
) -> StoreResponse:
    """Encode and store a file in the DNA archive."""
    try:
        data = await file.read()
        result = pipeline.store(data, file.filename or "unknown", _to_pipeline_config(config))
        return StoreResponse(
            archive_id=result.archive_id,
            filename=result.filename,
            original_size=result.original_size,
            compressed_size=result.compressed_size,
            total_dna_length=result.total_dna_length,
            num_blocks=result.num_blocks,
            compression_ratio=result.compression_ratio,
            sequences=result.sequences[:3],  # Return first 3 for preview
            metrics=result.metrics.to_dict(),
        )
    except DNAStoreAIError as e:
        raise HTTPException(status_code=400, detail=e.message) from e


@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_file(
    request: RetrieveRequest,
    pipeline: PipelineService = Depends(get_pipeline_service),
) -> RetrieveResponse:
    """Retrieve and reconstruct a file from the DNA archive."""
    try:
        result = pipeline.retrieve(request.archive_id, _to_pipeline_config(request.config))
        return RetrieveResponse(
            archive_id=result.archive_id,
            filename=result.filename,
            recovered_size=len(result.data),
            checksum_valid=result.checksum_valid,
            metrics=result.metrics.to_dict(),
            missing_blocks=result.missing_blocks,
        )
    except ArchiveNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message) from e
    except DNAStoreAIError as e:
        raise HTTPException(status_code=400, detail=e.message) from e


@router.post("/simulate", response_model=SimulateResponse)
async def simulate_storage(
    request: SimulateRequest,
    pipeline: PipelineService = Depends(get_pipeline_service),
) -> SimulateResponse:
    """Simulate synthesis, degradation, and sequencing on an archive."""
    try:
        result = pipeline.simulate(request.archive_id, _to_pipeline_config(request.config))
        return SimulateResponse(
            archive_id=result.archive_id,
            synthesis_stats=result.synthesis_stats,
            degradation_stats=result.degradation_stats,
            sequencing_stats=result.sequencing_stats,
        )
    except ArchiveNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message) from e


@router.post("/experiment", response_model=ExperimentResponse)
async def run_experiment(
    request: ExperimentRequest,
    experiment_service: ExperimentService = Depends(get_experiment_service),
) -> ExperimentResponse:
    """Run a research experiment on a synthetic dataset."""
    result = experiment_service.run_experiment(request)
    return ExperimentResponse(
        experiment_id=result["experiment_id"],
        summary=result["summary"],
        file_results=result["file_results"],
    )


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    metrics_service: MetricsService = Depends(get_metrics_service),
) -> MetricsResponse:
    """Get platform-wide metrics."""
    metrics = metrics_service.get_platform_metrics()
    return MetricsResponse(**metrics.to_dict())


@router.get("/archive", response_model=list[ArchiveListItem])
async def list_archives(
    archive_service: ArchiveService = Depends(get_archive_service),
) -> list[ArchiveListItem]:
    """List all DNA archives."""
    archives = archive_service.list_archives()
    return [ArchiveListItem(**a) for a in archives]


@router.get("/dna/{archive_id}", response_model=DNARecordResponse)
async def get_dna_sequence(
    archive_id: str,
    block_index: int = 0,
    archive_service: ArchiveService = Depends(get_archive_service),
) -> DNARecordResponse:
    """Get DNA sequence for an archive."""
    try:
        record = archive_service.get_dna(archive_id, block_index)
        return DNARecordResponse(**record)
    except ArchiveNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message) from e
