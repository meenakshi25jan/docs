"""Observability — trace agent/tool/latency for continuous improvement."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CognitiveTrace:
    trace_id: str
    events: list[dict[str, Any]] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    agent_calls: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    total_latency_ms: int = 0

    def record_step(self, step: str, latency_ms: int, meta: dict[str, Any] | None = None) -> None:
        self.events.append({
            "step": step,
            "latency_ms": latency_ms,
            "meta": meta or {},
        })

    def record_tool(self, tool: str, latency_ms: int, success: bool) -> None:
        self.tool_calls.append({"tool": tool, "latency_ms": latency_ms, "success": success})

    def record_agent(self, agent: str, latency_ms: int, success: bool) -> None:
        self.agent_calls.append({"agent": agent, "latency_ms": latency_ms, "success": success})

    def record_error(self, step: str, error: str) -> None:
        self.errors.append({"step": step, "error": error})

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "total_latency_ms": self.total_latency_ms,
            "events": self.events,
            "tool_calls": self.tool_calls,
            "agent_calls": self.agent_calls,
            "errors": self.errors,
        }


class StepTimer:
    def __init__(self, trace: CognitiveTrace, step: str):
        self.trace = trace
        self.step = step
        self.start = time.perf_counter()

    def __enter__(self) -> "StepTimer":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        ms = int((time.perf_counter() - self.start) * 1000)
        self.trace.record_step(self.step, ms)

    def finish(self, meta: dict[str, Any] | None = None) -> int:
        ms = int((time.perf_counter() - self.start) * 1000)
        self.trace.record_step(self.step, ms, meta)
        return ms
