"""Security diagnostics response schemas — read-only admin probes."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

SecurityDiagnosticStatus = Literal["ok", "warning", "critical", "unknown"]


class SecurityCheck(BaseModel):
    name: str
    status: SecurityDiagnosticStatus = "ok"
    detail: str = ""


class SecurityWarning(BaseModel):
    code: str
    message: str
    severity: SecurityDiagnosticStatus = "warning"


class RLSTableStatus(BaseModel):
    table_name: str
    rls_enabled: bool = False
    has_select_policy: bool = False
    has_insert_policy: bool = False
    has_update_policy: bool = False
    has_delete_policy: bool = False
    has_with_check: bool = False
    status: SecurityDiagnosticStatus = "unknown"
    warnings: list[str] = Field(default_factory=list)


class RLSCoverageResponse(BaseModel):
    status: SecurityDiagnosticStatus = "ok"
    tables: list[RLSTableStatus] = Field(default_factory=list)
    warnings: list[SecurityWarning] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuthSecurityResponse(BaseModel):
    db_backed_user_validation: bool = False
    active_user_enforced: bool = False
    tenant_validation: bool = False
    role_validation: bool = False
    jwt_secret_safe: bool = False
    login_blocks_inactive: bool = False
    refresh_checks_active: bool = False
    status: SecurityDiagnosticStatus = "unknown"
    warnings: list[SecurityWarning] = Field(default_factory=list)


class AuthorizationSecurityResponse(BaseModel):
    role_checks_available: bool = True
    ownership_checks_enabled: bool = False
    protected_routes_count: int = 0
    role_gated_routes_count: int = 0
    known_gaps: list[str] = Field(default_factory=list)
    status: SecurityDiagnosticStatus = "ok"
    warnings: list[SecurityWarning] = Field(default_factory=list)


class SecuritySummaryResponse(BaseModel):
    status: SecurityDiagnosticStatus = "ok"
    tenant_id: UUID | None = None
    rls_status: SecurityDiagnosticStatus = "unknown"
    auth_status: SecurityDiagnosticStatus = "unknown"
    authorization_status: SecurityDiagnosticStatus = "unknown"
    warnings: list[SecurityWarning] = Field(default_factory=list)
    checks: list[SecurityCheck] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
