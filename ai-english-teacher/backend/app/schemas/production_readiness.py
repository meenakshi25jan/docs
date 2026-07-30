"""Production readiness response schemas — deployment verification only."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ReadinessStatus = Literal["ok", "warning", "critical", "unknown"]


class ReadinessWarning(BaseModel):
    code: str
    message: str
    severity: ReadinessStatus = "warning"


class DeploymentCheck(BaseModel):
    name: str
    passed: bool = False
    status: ReadinessStatus = "unknown"
    detail: str = ""


class MigrationCheck(BaseModel):
    filename: str
    applied: bool = False
    status: ReadinessStatus = "unknown"
    detail: str = ""


class EnvironmentCheck(BaseModel):
    name: str
    passed: bool = False
    status: ReadinessStatus = "unknown"
    detail: str = ""


class SecurityCheck(BaseModel):
    name: str
    passed: bool = False
    status: ReadinessStatus = "unknown"
    detail: str = ""


class MigrationVerificationResponse(BaseModel):
    status: ReadinessStatus = "unknown"
    applied: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    unexpected: list[str] = Field(default_factory=list)
    checks: list[MigrationCheck] = Field(default_factory=list)
    warnings: list[ReadinessWarning] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EnvironmentVerificationResponse(BaseModel):
    status: ReadinessStatus = "ok"
    passed: bool = True
    checks: list[EnvironmentCheck] = Field(default_factory=list)
    warnings: list[ReadinessWarning] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SecurityVerificationResponse(BaseModel):
    status: ReadinessStatus = "ok"
    passed: bool = True
    checks: list[SecurityCheck] = Field(default_factory=list)
    warnings: list[ReadinessWarning] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProductionReadinessSummary(BaseModel):
    status: ReadinessStatus = "unknown"
    passed: bool = False
    warnings: list[ReadinessWarning] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    checks: list[DeploymentCheck] = Field(default_factory=list)
    migration_status: ReadinessStatus = "unknown"
    environment_status: ReadinessStatus = "unknown"
    security_status: ReadinessStatus = "unknown"
    health_status: ReadinessStatus = "unknown"
    metadata: dict[str, Any] = Field(default_factory=dict)
