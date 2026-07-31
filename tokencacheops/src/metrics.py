"""Metrics collection and computation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np

from .config import CACHE_COST_PER_ENTRY, INPUT_COST_PER_MILLION, OUTPUT_COST_PER_MILLION


@dataclass
class RunMetrics:
    """Metrics from a single simulation run."""

    method: str
    run_id: int
    total_requests: int = 0
    cache_hits: int = 0
    exact_hits: int = 0
    semantic_hits: int = 0
    prompt_hits: int = 0
    cache_misses: int = 0
    total_tokens_consumed: int = 0
    total_tokens_saved: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_latency_ms: float = 0.0
    total_inference_cost: float = 0.0
    total_baseline_cost: float = 0.0
    cache_entries: int = 0
    memory_consumption: float = 0.0
    latencies: List[float] = field(default_factory=list)

    @property
    def cache_hit_ratio(self) -> float:
        return self.cache_hits / max(1, self.total_requests)

    @property
    def semantic_hit_ratio(self) -> float:
        return self.semantic_hits / max(1, self.total_requests)

    @property
    def token_reduction_pct(self) -> float:
        baseline = self.total_tokens_consumed + self.total_tokens_saved
        return (self.total_tokens_saved / max(1, baseline)) * 100

    @property
    def avg_latency_ms(self) -> float:
        return self.total_latency_ms / max(1, self.total_requests)

    @property
    def throughput_rps(self) -> float:
        total_sec = self.total_latency_ms / 1000.0
        return self.total_requests / max(0.001, total_sec)

    @property
    def cost_reduction_pct(self) -> float:
        if self.total_baseline_cost == 0:
            return 0.0
        return ((self.total_baseline_cost - self.total_inference_cost) / self.total_baseline_cost) * 100

    @property
    def cache_efficiency_index(self) -> float:
        hit_ratio = self.cache_hit_ratio
        token_savings = self.total_tokens_saved / max(1, self.total_requests)
        memory = max(0.01, self.memory_consumption)
        return (hit_ratio * token_savings) / memory

    @property
    def cache_cost(self) -> float:
        return self.cache_entries * CACHE_COST_PER_ENTRY

    @property
    def roi(self) -> float:
        savings = self.total_baseline_cost - self.total_inference_cost
        cost = max(0.0001, self.cache_cost)
        return (savings - cost) / cost

    @property
    def context_efficiency(self) -> float:
        """Ratio of useful (cached) context to total context processed."""
        total_context = self.total_input_tokens
        reused = self.total_tokens_saved
        return reused / max(1, total_context + reused)

    @property
    def retrieval_efficiency(self) -> float:
        """Effective retrieval rate combining exact and semantic hits."""
        return (self.exact_hits + self.semantic_hits * 0.85) / max(1, self.total_requests)

    def to_dict(self) -> Dict:
        return {
            "method": self.method,
            "run_id": self.run_id,
            "total_requests": self.total_requests,
            "cache_hit_ratio": self.cache_hit_ratio,
            "semantic_hit_ratio": self.semantic_hit_ratio,
            "exact_hits": self.exact_hits,
            "semantic_hits": self.semantic_hits,
            "prompt_hits": self.prompt_hits,
            "cache_misses": self.cache_misses,
            "total_tokens_consumed": self.total_tokens_consumed,
            "total_tokens_saved": self.total_tokens_saved,
            "token_reduction_pct": self.token_reduction_pct,
            "avg_latency_ms": self.avg_latency_ms,
            "median_latency_ms": float(np.median(self.latencies)) if self.latencies else 0.0,
            "p95_latency_ms": float(np.percentile(self.latencies, 95)) if self.latencies else 0.0,
            "throughput_rps": self.throughput_rps,
            "total_inference_cost": self.total_inference_cost,
            "total_baseline_cost": self.total_baseline_cost,
            "cost_reduction_pct": self.cost_reduction_pct,
            "cache_efficiency_index": self.cache_efficiency_index,
            "roi": self.roi,
            "context_efficiency": self.context_efficiency,
            "retrieval_efficiency": self.retrieval_efficiency,
            "cache_entries": self.cache_entries,
            "memory_consumption": self.memory_consumption,
        }


def compute_baseline_cost(prompt_tokens: int, output_tokens: int) -> float:
    """Compute cost without optimization (frontier model assumed)."""
    input_cost = (prompt_tokens / 1_000_000) * INPUT_COST_PER_MILLION
    output_cost = (output_tokens / 1_000_000) * OUTPUT_COST_PER_MILLION
    return input_cost + output_cost
