#!/usr/bin/env python3
"""
Staging validation runner — execute after deploying cursor/reliability-observability-v1-f37f.

Requires environment variables for full run:

  API_BASE_URL          e.g. https://your-staging-api.onrender.com
  API_PREFIX            default /api/v1
  ADMIN_TOKEN           admin JWT
  TEACHER_TOKEN         teacher JWT (optional, for teacher flow checks)
  STUDENT_TOKEN         student JWT (optional, RBAC + IDOR checks)
  STUDENT_TOKEN_B       second student JWT (optional, cross-learner checks)
  DATABASE_URL          Neon connection string (for backup_verify.sh)

Usage:
  cd ai-english-teacher/backend
  export API_BASE_URL=...
  export ADMIN_TOKEN=...
  python3 scripts/staging_validation.py

Output: JSON summary + human-readable sections; exit 0 if no blocking failures.
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


@dataclass
class CheckResult:
    name: str
    passed: bool
    status_code: int | None = None
    detail: str = ""
    blocking: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "status_code": self.status_code,
            "detail": self.detail[:500],
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


def _recommendation(blocking: list[CheckResult], failed: list[CheckResult]) -> str:
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
    p = os.environ.get("API_PREFIX", "/api/v1")
    return p if p.startswith("/") else f"/{p}"


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
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=_timeout()) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body, dict(resp.headers)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, body, dict(exc.headers)
    except urllib.error.URLError as exc:
        return 0, f"{type(exc).__name__}: {exc.reason}", {}
    except Exception as exc:
        return 0, f"{type(exc).__name__}: {exc}", {}


def _api_path(path: str) -> str:
    return f"{_api_root()}{_prefix()}{path}"


def _root_path(path: str) -> str:
    return f"{_api_root()}{path}"


def run_api_checks(report: ValidationReport) -> None:
    admin = os.environ.get("ADMIN_TOKEN")
    student = os.environ.get("STUDENT_TOKEN")
    teacher = os.environ.get("TEACHER_TOKEN")

    for path in ("/health", "/health/auth", "/health/ai"):
        code, body, hdrs = _http_get(_root_path(path))
        ok = code == 200
        rid = hdrs.get(REQUEST_ID_HEADER) or hdrs.get(REQUEST_ID_HEADER.lower())
        detail = body[:200]
        if path == "/health" and not rid:
            ok = False
            detail = "missing X-Request-ID (deploy Phase 11?)"
        report.add(
            CheckResult(f"GET {path}", ok, code, detail, blocking=path == "/health")
        )

    if not admin:
        report.add(
            CheckResult(
                "ADMIN_TOKEN",
                False,
                None,
                "not set — authenticated checks skipped",
                blocking=True,
            )
        )
        return

    auth_endpoints = [
        ("/operations/health", admin, 200, True),
        ("/security/summary", admin, 200, True),
        ("/production/readiness", admin, 200, True),
        ("/reliability/status", admin, 200, True),
        ("/reliability/logging", admin, 200, False),
        ("/reliability/backup", admin, 200, False),
        ("/reliability/performance", admin, 200, False),
    ]
    for path, token, expect, blocking in auth_endpoints:
        code, body, _ = _http_get(_api_path(path), token=token)
        ok = code == expect
        report.add(CheckResult(f"GET {path}", ok, code, body[:200], blocking=blocking))

    # Production readiness passed flag
    code, body, _ = _http_get(_api_path("/production/readiness"), token=admin)
    if code == 200:
        try:
            data = json.loads(body)
            passed = data.get("passed", False)
            report.add(
                CheckResult(
                    "production.readiness.passed",
                    passed,
                    code,
                    f"status={data.get('status')} warnings={len(data.get('warnings', []))}",
                    blocking=True,
                )
            )
            report.sections["production_readiness"] = {
                "status": data.get("status"),
                "passed": passed,
                "warnings": data.get("warnings", []),
            }
        except json.JSONDecodeError:
            report.add(
                CheckResult("production.readiness.parse", False, code, "invalid json", blocking=True)
            )

    # Reliability flags
    code, body, _ = _http_get(_api_path("/reliability/status"), token=admin)
    if code == 200:
        try:
            data = json.loads(body)
            obs = data.get("observability") or {}
            log = data.get("logging") or {}
            backup = data.get("backup") or {}
            perf = data.get("performance") or {}
            report.sections["reliability"] = {
                "request_id_enabled": obs.get("request_id_enabled"),
                "logging_enabled": log.get("logging_enabled"),
                "backup_verified": backup.get("backup_verified"),
                "load_smoke_available": perf.get("load_smoke_available"),
            }
            for name, val in report.sections["reliability"].items():
                report.add(
                    CheckResult(f"reliability.{name}", bool(val), code, str(val), blocking=False)
                )
        except json.JSONDecodeError:
            pass

    # Migrations via API
    code, body, _ = _http_get(_api_path("/production/migrations"), token=admin)
    if code == 200:
        try:
            data = json.loads(body)
            applied = data.get("applied") or [c.get("filename") for c in data.get("checks", []) if c.get("applied")]
            missing = data.get("missing") or []
            unexpected = data.get("unexpected") or []
            report.sections["migrations"] = {
                "applied": applied,
                "missing": missing,
                "unexpected": unexpected,
            }
            report.add(
                CheckResult(
                    "migrations.complete",
                    len(missing) == 0,
                    code,
                    f"missing={missing} unexpected={unexpected}",
                    blocking=True,
                )
            )
        except json.JSONDecodeError:
            report.add(CheckResult("migrations.parse", False, code, "invalid json", blocking=True))

    # RLS via security API
    code, body, _ = _http_get(_api_path("/security/rls"), token=admin)
    if code == 200:
        try:
            data = json.loads(body)
            report.sections["rls"] = data
            covered = {t.get("table") for t in data.get("tables", [])}
            for table in RLS_TABLES:
                report.add(
                    CheckResult(
                        f"rls.{table}",
                        table in covered,
                        code,
                        "listed in /security/rls",
                        blocking=True,
                    )
                )
        except json.JSONDecodeError:
            pass

    # Student RBAC
    if student:
        for path in (
            "/security/summary",
            "/production/readiness",
            "/reliability/status",
            "/operations/health",
        ):
            code, body, _ = _http_get(_api_path(path), token=student)
            report.add(
                CheckResult(
                    f"student forbidden {path}",
                    code == 403,
                    code,
                    body[:120],
                    blocking=True,
                )
            )

    # Teacher flow
    if teacher:
        code, body, _ = _http_get(_api_path("/operations/teacher/roster"), token=teacher)
        report.add(
            CheckResult("teacher roster", code == 200, code, body[:120], blocking=False)
        )

    # Admin flow extras
    for path in ("/operations/overview", "/operations/feature-flags", "/operations/tenant"):
        code, body, _ = _http_get(_api_path(path), token=admin)
        report.add(CheckResult(f"admin {path}", code == 200, code, body[:120], blocking=False))


def run_subprocess_tools(report: ValidationReport) -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)

    smoke = os.path.join(script_dir, "production_smoke_test.py")
    if os.path.isfile(smoke):
        proc = subprocess.run(
            [sys.executable, smoke],
            cwd=backend_dir,
            capture_output=True,
            text=True,
            timeout=_timeout() * 3,
            env=os.environ.copy(),
        )
        report.sections["production_smoke_test"] = {
            "exit_code": proc.returncode,
            "stdout_tail": proc.stdout[-2000:],
            "stderr_tail": proc.stderr[-500:],
        }
        report.add(
            CheckResult(
                "production_smoke_test.py",
                proc.returncode == 0,
                None,
                proc.stdout.splitlines()[-3:] if proc.stdout else "",
                blocking=True,
            )
        )

    backup_sh = os.path.join(script_dir, "backup_verify.sh")
    if os.environ.get("DATABASE_URL") and os.path.isfile(backup_sh):
        proc = subprocess.run(
            ["bash", backup_sh],
            cwd=backend_dir,
            capture_output=True,
            text=True,
            timeout=_timeout() * 2,
            env=os.environ.copy(),
        )
        report.sections["backup_verify"] = {
            "exit_code": proc.returncode,
            "stdout": proc.stdout[-1500:],
        }
        report.add(
            CheckResult(
                "backup_verify.sh",
                proc.returncode == 0,
                None,
                proc.stdout.splitlines()[-2:] if proc.stdout else proc.stderr[:200],
                blocking=True,
            )
        )
    else:
        report.add(
            CheckResult(
                "backup_verify.sh",
                False,
                None,
                "skipped — DATABASE_URL not set",
                blocking=False,
            )
        )

    load_smoke = os.path.join(script_dir, "load_smoke.py")
    if os.path.isfile(load_smoke) and os.environ.get("ADMIN_TOKEN"):
        proc = subprocess.run(
            [sys.executable, load_smoke],
            cwd=backend_dir,
            capture_output=True,
            text=True,
            timeout=_timeout() * 3,
            env=os.environ.copy(),
        )
        report.sections["load_smoke"] = {
            "exit_code": proc.returncode,
            "stdout_tail": proc.stdout[-2000:],
        }
        report.add(
            CheckResult(
                "load_smoke.py",
                proc.returncode == 0,
                None,
                proc.stdout.splitlines()[-5:] if proc.stdout else "",
                blocking=False,
            )
        )


def main() -> int:
    report = ValidationReport()
    report.sections["expected_migrations"] = EXPECTED_MIGRATIONS
    report.sections["target"] = _api_root()

    run_api_checks(report)
    run_subprocess_tools(report)

    summary = report.summary()
    output = {
        "summary": summary,
        "sections": report.sections,
        "checks": [c.to_dict() for c in report.checks],
    }
    print(json.dumps(output, indent=2))

    rec = summary["recommendation"]
    print(f"\nRecommendation: {rec}")

    return 0 if summary["blocking_failed"] == 0 and summary["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
