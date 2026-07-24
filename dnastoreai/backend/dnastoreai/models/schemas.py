"""Pydantic API schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PipelineConfigSchema(BaseModel):
    compression: str = "gzip"
    encoding: str = "gc_balanced"
    ecc: str = "reed_solomon"
    block_size: int = 4096
    optimize: bool = True
    substitution_rate: float = 0.001
    insertion_rate: float = 0.0001
    deletion_rate: float = 0.0001
    degradation_temperature: float = 25.0
    degradation_humidity: float = 50.0
    degradation_time_years: float = 1.0
    sequencing: str = "illumina"
    coverage_depth: int = 30


class StoreRequest(BaseModel):
    config: PipelineConfigSchema = Field(default_factory=PipelineConfigSchema)


class StoreResponse(BaseModel):
    archive_id: str
    filename: str
    original_size: int
    compressed_size: int
    total_dna_length: int
    num_blocks: int
    compression_ratio: float
    sequences: list[str]
    metrics: dict[str, Any]


class RetrieveRequest(BaseModel):
    archive_id: str
    config: PipelineConfigSchema = Field(default_factory=PipelineConfigSchema)


class RetrieveResponse(BaseModel):
    archive_id: str
    filename: str
    recovered_size: int
    checksum_valid: bool
    metrics: dict[str, Any]
    missing_blocks: list[int]


class SimulateRequest(BaseModel):
    archive_id: str
    config: PipelineConfigSchema = Field(default_factory=PipelineConfigSchema)
    simulate_synthesis: bool = True
    simulate_degradation: bool = True
    simulate_sequencing: bool = True


class SimulateResponse(BaseModel):
    archive_id: str
    synthesis_stats: dict[str, Any] | None = None
    degradation_stats: dict[str, Any] | None = None
    sequencing_stats: dict[str, Any] | None = None


class ExperimentRequest(BaseModel):
    name: str = "experiment"
    dataset_type: str = "mixed"
    file_count: int = 5
    encoding: str = "gc_balanced"
    ecc: str = "reed_solomon"
    sequencing: str = "illumina"
    compression: str = "gzip"


class ExperimentResponse(BaseModel):
    experiment_id: str
    summary: dict[str, Any]
    file_results: list[dict[str, Any]]


class MetricsResponse(BaseModel):
    storage: dict[str, Any]
    biological: dict[str, Any]
    recovery: dict[str, Any]
    ai: dict[str, Any]


class ArchiveListItem(BaseModel):
    id: str
    filename: str
    file_type: str
    original_size: int
    total_dna_length: int
    num_blocks: int
    encoding: str
    created_at: str


class DNARecordResponse(BaseModel):
    id: str
    archive_id: str
    block_index: int
    sequence: str
    fitness_score: float
    gc_content: float
    length: int
