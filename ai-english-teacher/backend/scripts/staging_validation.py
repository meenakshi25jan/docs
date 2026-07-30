#!/usr/bin/env python3
"""
Staging validation runner — read-only checks for pilot promotion readiness.

Environment variables:
  API_BASE_URL          default https://ai-english-teacher-api.onrender.com
  API_PREFIX            default /api/v1
  ADMIN_TOKEN           admin JWT (required for authenticated checks)
  TEACHER_TOKEN         optional teacher JWT
  STUDENT_TOKEN         optional student JWT
  STUDENT_TOKEN_B       optional second student JWT (reserved for cross-tenant checks)
  DATABASE_URL          optional Neon URL (used by backup_verify.sh)
  TIMEOUT_SECONDS       default 60

Usage:
  cd ai-english-teacher/backend
  export ADMIN_TOKEN=...
  python3 scripts/staging_validation.py

Prints JSON to stdout. Exit 0 if all checks pass; exit 1 if any check fails.
Does not make AI calls.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

REQUEST_ID_HEADER = "X-Request-ID"

EXPECTED_MIGRATIONS = [
    "001_initial_schema.sql",
    "002_pgvector.sql",
    "003_auth_rls.sql",
    "004_fix_rls_policies.sql",
    "005_knowledge_and_voice.sql",
    "006_curriculum_intelligence.sql",
    "007_security_rls_hardening.sql",
]

RLS_TABLES = [
    "conversation_messages",
    "assessment_results",
    "voice_analyses",
    "learner_memories",
]

STUDENT_FORBIDDEN_PATHS = [
    "/security/summary",
    "/production/readiness",
    "/reliability/status",
    "/operations/health",
]


@dataclass
class CheckResult:
    name: str
    passed: bool
    status_code: int | None = None
    detail: str = ""
    blocking: bool = False

    def to_dict(self) -> dict[str, Any]:
        detail = self.detail
        if not isinstance(detail, str):
            detail = str(detail)
        return {
            "name": self.name,
            "passed": self.passed,
            "status_code": self.status_code,
            "detail": detail[:500],
            "blocking": self.blocking,
        }


@dataclass
class ValidationReport:
    checks: list[CheckResult] = field(default_factory=list)
    sections: dict[str, Any] = field(default_factory=dict)

    def add(self, result: CheckResult) -> None:
        self.checks.append(result)

    def blocking_failures(self) -> list[CheckResult]:
        return [c for c in self.checks if not c.passed and c.blocking]

    def summary(self) -> dict[str, Any]:
        failed = [c for c in self.checks if not c.passed]
        blocking = self.blocking_failures()
        return {
            "total": len(self.checks),
            "passed": len(self.checks) - len(failed),
            "failed": len(failed),
            "blocking_failed": len(blocking),
            "recommendation": _recommendation(blocking, failed),
        }


def _recommendation(
    blocking: list[CheckResult],
    failed: list[CheckResult],
) -> str:
    if blocking:
        return "NO-GO"
    if failed:
        return "CONDITIONAL GO"
    return "GO TO PILOT"


def _api_root() -> str:
    return os.environ.get(
        "API_BASE_URL",
        "https://ai-english-teacher-api.onrender.com",
    ).rstrip("/")


def _prefix() -> str:
    path = os.environ.get("API_PREFIX", "/api/v1")
    return path if path.startswith("/") else f"/{path}"


def _timeout() -> int:
    return int(os.environ.get("TIMEOUT_SECONDS", "60"))


def _http_get(
    url: str,
    token: str | None = None,
    extra_headers: dict[str, str] | None = None,
) -> tuple[int, str, dict[str, str]]:
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if extra_headers:
        headers.update(extra_headers)

    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=_timeout()) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status, body, dict(response.headers)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, body, dict(exc.headers)
    except urllib.error.URLError as exc:
        return 0, f"{type(exc).__name__}: {exc.reason}", {}
    except OSError as exc:
        return 0, f"{type(exc).__name__}: {exc}", {}


def _api_path(path: str) -> str:
    return f"{_api_root()}{_prefix()}{path}"


def _root_path(path: str) -> str:
    return f"{_api_root()}{path}"


def _request_id(headers: dict[str, str]) -> str | None:
    return headers.get(REQUEST_ID_HEADER) or headers.get(REQUEST_ID_HEADER.lower())


def _parse_json(body: str) -> dict[str, Any] | None:
    try:
        data = json.loads(body)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        return None
    return None


def _tail(text: str, limit: int = 2000) -> str:
    if not text:
        return ""
    return text[-limit:]


def run_health_checks(report: ValidationReport) -> None:
    code, body, headers = _http_get(_root_path("/health"))
    request_id = _request_id(headers)
    ok = code == 200 and bool(request_id)
    detail = body[:200]
    if code == 200 and not request_id:
        detail = "missing X-Request-ID header"
    report.add(
        CheckResult(
            name="GET /health",
            passed=ok,
            status_code=code,
            detail=detail,
            blocking=True,
        )
    )
    report.sections["health"] = {
        "status_code": code,
        "request_id": request_id,
    }

    for path in ("/health/auth", "/health/ai"):
        sub_code, sub_body, _ = _http_get(_root_path(path))
        report.add(
            CheckResult(
                name=f"GET {path}",
                passed=sub_code == 200,
                status_code=sub_code,
                detail=sub_body[:200],
                blocking=False,
            )
        )


def run_authenticated_checks(report: ValidationReport) -> None:
    admin = os.environ.get("ADMIN_TOKEN")
    if not admin:
        report.add(
            CheckResult(
                name="ADMIN_TOKEN",
                passed=False,
                status_code=None,
                detail="ADMIN_TOKEN not set",
                blocking=True,
            )
        )
        return

    # Operations
    code, body, _ = _http_get(_api_path("/operations/health"), token=admin)
    report.add(
        CheckResult(
            name="GET /operations/health",
            passed=code == 200,
            status_code=code,
            detail=body[:200],
            blocking=True,
        )
    )

    # Security
    code, body, _ = _http_get(_api_path("/security/summary"), token=admin)
    report.add(
        CheckResult(
            name="GET /security/summary",
            passed=code == 200,
            status_code=code,
            detail=body[:200],
            blocking=True,
        )
    )

    code, body, _ = _http_get(_api_path("/security/rls"), token=admin)
    rls_ok = code == 200
    report.add(
        CheckResult(
            name="GET /security/rls",
            passed=rls_ok,
            status_code=code,
            detail=body[:200],
            blocking=True,
        )
    )

    if rls_ok:
        data = _parse_json(body)
        if data is not None:
            report.sections["rls"] = data
            covered = {
                row.get("table")
                for row in data.get("tables", [])
                if isinstance(row, dict)
            }
            for table in RLS_TABLES:
                report.add(
                    CheckResult(
                        name=f"rls.table.{table}",
                        passed=table in covered,
                        status_code=code,
                        detail="listed in /security/rls",
                        blocking=True,
                    )
                )
        else:
            report.add(
                CheckResult(
                    name="security.rls.parse",
                    passed=False,
                    status_code=code,
                    detail="invalid json",
                    blocking=True,
                )
            )

    # Production readiness
    code, body, _ = _http_get(_api_path("/production/readiness"), token=admin)
    readiness_ok = code == 200
    report.add(
        CheckResult(
            name="GET /production/readiness",
            passed=readiness_ok,
            status_code=code,
            detail=body[:200],
            blocking=True,
        )
    )

    if readiness_ok:
        data = _parse_json(body)
        if data is not None:
            passed = bool(data.get("passed"))
            report.sections["production_readiness"] = {
                "status": data.get("status"),
                "passed": passed,
                "warnings": data.get("warnings", []),
            }
            report.add(
                CheckResult(
                    name="production.readiness.passed",
                    passed=passed,
                    status_code=code,
                    detail=f"passed={passed}",
                    blocking=True,
                )
            )
        else:
            report.add(
                CheckResult(
                    name="production.readiness.parse",
                    passed=False,
                    status_code=code,
                    detail="invalid json",
                    blocking=True,
                )
            )

    # Production migrations
    code, body, _ = _http_get(_api_path("/production/migrations"), token=admin)
    migrations_ok = code == 200
    report.add(
        CheckResult(
            name="GET /production/migrations",
            passed=migrations_ok,
            status_code=code,
            detail=body[:200],
            blocking=True,
        )
    )

    if migrations_ok:
        data = _parse_json(body)
        if data is not None:
            applied = data.get("applied") or []
            missing = data.get("missing") or []
            unexpected = data.get("unexpected") or []
            report.sections["migrations"] = {
                "applied": applied,
                "missing": missing,
                "unexpected": unexpected,
            }
            report.add(
                CheckResult(
                    name="migrations.missing_empty",
                    passed=len(missing) == 0,
                    status_code=code,
                    detail=f"missing={missing}",
                    blocking=True,
                )
            )
        else:
            report.add(
                CheckResult(
                    name="production.migrations.parse",
                    passed=False,
                    status_code=code,
                    detail="invalid json",
                    blocking=True,
                )
            )

    # Reliability
    reliability_flags: dict[str, Any] = {}
    reliability_paths = (
        "/reliability/status",
        "/reliability/logging",
        "/reliability/backup",
        "/reliability/performance",
    )
    reliability_responses: dict[str, tuple[int, str]] = {}
    for path in reliability_paths:
        rel_code, rel_body, _ = _http_get(_api_path(path), token=admin)
        reliability_responses[path] = (rel_code, rel_body)
        report.add(
            CheckResult(
                name=f"GET {path}",
                passed=rel_code == 200,
                status_code=rel_code,
                detail=rel_body[:200],
                blocking=True,
            )
        )

    status_code, status_body = reliability_responses["/reliability/status"]
    if status_code == 200:
        status_data = _parse_json(status_body)
        if status_data is not None:
            observability = status_data.get("observability") or {}
            logging_nested = status_data.get("logging") or {}
            backup_nested = status_data.get("backup") or {}
            performance_nested = status_data.get("performance") or {}
            reliability_flags["request_id_enabled"] = observability.get("request_id_enabled")
            reliability_flags["logging_enabled"] = (
                logging_nested.get("logging_enabled")
                or observability.get("logging_enabled")
            )
            reliability_flags["backup_verified"] = backup_nested.get("backup_verified")
            reliability_flags["load_smoke_available"] = performance_nested.get(
                "load_smoke_available"
            )

    log_code, log_body = reliability_responses["/reliability/logging"]
    if log_code == 200 and reliability_flags.get("logging_enabled") is None:
        log_data = _parse_json(log_body)
        if log_data is not None:
            reliability_flags["logging_enabled"] = log_data.get("logging_enabled")

    backup_code, backup_body = reliability_responses["/reliability/backup"]
    if backup_code == 200 and reliability_flags.get("backup_verified") is None:
        backup_data = _parse_json(backup_body)
        if backup_data is not None:
            reliability_flags["backup_verified"] = backup_data.get("backup_verified")

    perf_code, perf_body = reliability_responses["/reliability/performance"]
    if perf_code == 200 and reliability_flags.get("load_smoke_available") is None:
        perf_data = _parse_json(perf_body)
        if perf_data is not None:
            reliability_flags["load_smoke_available"] = perf_data.get("load_smoke_available")

    report.sections["reliability"] = reliability_flags
    for flag_name, flag_value in reliability_flags.items():
        report.add(
            CheckResult(
                name=f"reliability.{flag_name}",
                passed=bool(flag_value),
                status_code=status_code,
                detail=str(flag_value),
                blocking=False,
            )
        )


def run_rbac_checks(report: ValidationReport) -> None:
    student = os.environ.get("STUDENT_TOKEN")
    if student:
        for path in STUDENT_FORBIDDEN_PATHS:
            code, body, _ = _http_get(_api_path(path), token=student)
            report.add(
                CheckResult(
                    name=f"student forbidden {path}",
                    passed=code == 403,
                    status_code=code,
                    detail=body[:120],
                    blocking=True,
                )
            )

    teacher = os.environ.get("TEACHER_TOKEN")
    if teacher:
        code, body, _ = _http_get(_api_path("/operations/teacher/roster"), token=teacher)
        report.add(
            CheckResult(
                name="GET /operations/teacher/roster",
                passed=code == 200,
                status_code=code,
                detail=body[:200],
                blocking=False,
            )
        )


def run_subprocess_tools(report: ValidationReport) -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)
    env = os.environ.copy()

    smoke_path = os.path.join(script_dir, "production_smoke_test.py")
    if os.path.isfile(smoke_path):
        proc = subprocess.run(
            [sys.executable, smoke_path],
            cwd=backend_dir,
            capture_output=True,
            text=True,
            timeout=_timeout() * 3,
            env=env,
        )
        report.sections["production_smoke_test"] = {
            "exit_code": proc.returncode,
            "stdout_tail": _tail(proc.stdout),
            "stderr_tail": _tail(proc.stderr),
        }
        report.add(
            CheckResult(
                name="production_smoke_test.py",
                passed=proc.returncode == 0,
                status_code=None,
                detail=_tail(proc.stdout or proc.stderr, 500),
                blocking=False,
            )
        )

    backup_path = os.path.join(script_dir, "backup_verify.sh")
    if os.path.isfile(backup_path):
        proc = subprocess.run(
            ["bash", backup_path],
            cwd=backend_dir,
            capture_output=True,
            text=True,
            timeout=_timeout() * 2,
            env=env,
        )
        report.sections["backup_verify"] = {
            "exit_code": proc.returncode,
            "stdout_tail": _tail(proc.stdout),
            "stderr_tail": _tail(proc.stderr),
        }
        report.add(
            CheckResult(
                name="backup_verify.sh",
                passed=proc.returncode == 0,
                status_code=None,
                detail=_tail(proc.stdout or proc.stderr, 500),
                blocking=False,
            )
        )

    load_path = os.path.join(script_dir, "load_smoke.py")
    if os.path.isfile(load_path):
        proc = subprocess.run(
            [sys.executable, load_path],
            cwd=backend_dir,
            capture_output=True,
            text=True,
            timeout=_timeout() * 3,
            env=env,
        )
        report.sections["load_smoke"] = {
            "exit_code": proc.returncode,
            "stdout_tail": _tail(proc.stdout),
            "stderr_tail": _tail(proc.stderr),
        }
        report.add(
            CheckResult(
                name="load_smoke.py",
                passed=proc.returncode == 0,
                status_code=None,
                detail=_tail(proc.stdout or proc.stderr, 500),
                blocking=False,
            )
        )


def main() -> int:
    report = ValidationReport()
    report.sections["target"] = _api_root()
    report.sections["api_prefix"] = _prefix()
    report.sections["expected_migrations"] = EXPECTED_MIGRATIONS

    run_health_checks(report)
    run_authenticated_checks(report)
    run_rbac_checks(report)
    run_subprocess_tools(report)

    output = {
        "summary": report.summary(),
        "sections": report.sections,
        "checks": [check.to_dict() for check in report.checks],
    }
    print(json.dumps(output, indent=2))

    summary = output["summary"]
    if summary["failed"] == 0:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
