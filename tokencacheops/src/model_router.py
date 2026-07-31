"""Model routing engine for task-aware inference."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .config import INPUT_COST_PER_MILLION, MODEL_PROFILES, OUTPUT_COST_PER_MILLION, TASK_MODEL_ROUTING


@dataclass
class RoutingDecision:
    """Model routing result for a request."""

    task_type: str
    model_tier: str
    latency_ms: float
    input_cost: float
    output_cost: float
    total_cost: float


class ModelRouter:
    """Route tasks to appropriate model tiers."""

    def __init__(self):
        self.routing_map = TASK_MODEL_ROUTING.copy()

    def route(self, task_type: str, prompt_tokens: int, output_tokens: int) -> RoutingDecision:
        model_tier = self.routing_map.get(task_type, "medium")
        profile = MODEL_PROFILES[model_tier]
        input_cost = (prompt_tokens / 1_000_000) * INPUT_COST_PER_MILLION * profile["input_cost_mult"]
        output_cost = (output_tokens / 1_000_000) * OUTPUT_COST_PER_MILLION * profile["output_cost_mult"]
        return RoutingDecision(
            task_type=task_type,
            model_tier=model_tier,
            latency_ms=profile["latency_ms"],
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=input_cost + output_cost,
        )

    def get_latency(self, task_type: str) -> float:
        tier = self.routing_map.get(task_type, "medium")
        return MODEL_PROFILES[tier]["latency_ms"]
