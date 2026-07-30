"""Reliability and observability response schemas."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ReliabilityLevel = Literal["ok", "warning", "critical", "unknown"]


class ReliabilityWarning(BaseModel):
    code: str
    message: str
    severity: ReliabilityLevel = "warning"


class ReliabilityCheck(BaseModel):
    name: str
    passed: bool = False
    status: ReliabilityLevel = "unknown"
    detail: str = ""


class LoggingStatusResponse(BaseModel):
    status: ReliabilityLevel = "ok"
    passed: bool = True
    logging_enabled: bool = True
    request_id_enabled: bool = True
    json_format_enabled: bool = False
    checks: list[ReliabilityCheck] = Field(default_factory=list)
    warnings: list[ReliabilityWarning] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BackupStatusResponse(BaseModel):
    status: ReliabilityLevel = "unknown"
    passed: bool = False
    backup_verified: bool = False
    database_configured: bool = False
    checks: list[ReliabilityCheck] = Field(default_factory=list)
    warnings: list[ReliabilityWarning] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PerformanceStatusResponse(BaseModel):
    status: ReliabilityLevel = "ok"
    passed: bool = True
    load_smoke_available: bool = False
    checks: list[ReliabilityCheck] = Field(default_factory=list)
    warnings: list[ReliabilityWarning] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ObservabilityStatusResponse(BaseModel):
    status: ReliabilityLevel = "unknown"
    passed: bool = False
    request_id_enabled: bool = True
    logging_enabled: bool = True
    sentry_configured: bool = False
    checks: list[ReliabilityCheck] = Field(default_factory=list)
    warnings: list[ReliabilityWarning] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReliabilityStatusResponse(BaseModel):
    status: ReliabilityLevel = "unknown"
    passed: bool = False
    warnings: list[ReliabilityWarning] = Field(default_factory=list)
    checks: list[ReliabilityCheck] = Field(default_factory=list)
    observability: ObservabilityStatusResponse | None = None
    logging: LoggingStatusResponse | None = None
    backup: BackupStatusResponse | None = None
    performance: PerformanceStatusResponse | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
