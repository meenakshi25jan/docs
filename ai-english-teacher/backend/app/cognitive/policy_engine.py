"""Policy engine — latency, cost, privacy, tool allowlist."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.cognitive.tool_router import ToolName


@dataclass
class PolicyDecision:
    allowed: bool
    web_search_allowed: bool
    max_tokens: int
    max_latency_ms: int
    model_tier: str
    retry_count: int
    reason: str = ""


DEFAULT_POLICY = PolicyDecision(
    allowed=True,
    web_search_allowed=True,
    max_tokens=1200,
    max_latency_ms=8000,
    model_tier="full",
    retry_count=2,
)


def evaluate_policy(
    *,
    tenant_id: str | None = None,
    tools: list[ToolName],
    token_budget_remaining: int | None = None,
) -> PolicyDecision:
    decision = PolicyDecision(
        allowed=True,
        web_search_allowed=True,
        max_tokens=DEFAULT_POLICY.max_tokens,
        max_latency_ms=DEFAULT_POLICY.max_latency_ms,
        model_tier=DEFAULT_POLICY.model_tier,
        retry_count=DEFAULT_POLICY.retry_count,
    )

    if token_budget_remaining is not None and token_budget_remaining < 200:
        decision.max_tokens = min(decision.max_tokens, token_budget_remaining)
        decision.model_tier = "mini"
        decision.reason = "token_budget_low"

    blocked_tools = set()
    if ToolName.WEB_SEARCH in tools and not decision.web_search_allowed:
        blocked_tools.add(ToolName.WEB_SEARCH)

    if blocked_tools:
        decision.reason = f"blocked_tools={list(blocked_tools)}"

    return decision
