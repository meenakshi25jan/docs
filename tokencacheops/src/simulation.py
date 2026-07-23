"""Simulation engine for cache benchmarking."""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from tqdm import tqdm

from .baselines import BaseCache, CacheEntry, LFUCache, LRUCache, NoOptimization, PromptOnlyCache, SemanticOnlyCache
from .config import CACHE_CAPACITY, ExperimentConfig, NUM_REQUESTS
from .dataset_generator import DatasetGenerator, WorkloadRequest
from .metrics import RunMetrics, compute_baseline_cost
from .model_router import ModelRouter
from .semantic_engine import SemanticEngine
from .tokencacheops import TokenCacheOps


class SimulationEngine:
    """Run cache simulations across methods and runs."""

    METHODS = [
        "Baseline-A (LRU)",
        "Baseline-B (LFU)",
        "Baseline-C (Semantic)",
        "Baseline-D (Prompt)",
        "Baseline-E (No-Opt)",
        "TokenCacheOps",
    ]

    ABLATION_VARIANTS = {
        "w/o SemanticReuse": {"semantic_reuse": 0.0},
        "w/o BusinessImportance": {"business_importance": 0.0},
        "w/o InfluenceRank": {"influence_rank": 0.0},
        "w/o PenetrationFactor": {"penetration_factor": 0.0},
        "Full TokenCacheOps": {},
    }

    def __init__(self, config: Optional[ExperimentConfig] = None):
        self.config = config or ExperimentConfig()
        # Scale cache capacity with workload size
        if self.config.cache_capacity == CACHE_CAPACITY and self.config.num_requests != NUM_REQUESTS:
            scale = self.config.num_requests / NUM_REQUESTS
            self.config.cache_capacity = max(800, int(CACHE_CAPACITY * max(0.4, scale)))
        self.semantic_engine = SemanticEngine(threshold=self.config.semantic_threshold)
        self.router = ModelRouter()
        self.dataset_df: Optional[pd.DataFrame] = None
        self.requests: List[WorkloadRequest] = []
        self.embeddings: Optional[np.ndarray] = None

    def prepare_dataset(self) -> pd.DataFrame:
        """Generate and embed dataset."""
        gen = DatasetGenerator(self.config.num_requests, self.config.random_seed)
        self.dataset_df, self.requests = gen.generate()
        texts = [r.query_text for r in self.requests]
        print(f"Embedding {len(texts)} queries...")
        self.embeddings = self.semantic_engine.embed(texts)
        for i, req in enumerate(self.requests):
            req.embedding = self.embeddings[i]
        return self.dataset_df

    def _create_cache(self, method: str, retention_weights: Optional[Dict] = None):
        cap = self.config.cache_capacity
        if method == "Baseline-A (LRU)":
            return LRUCache(cap)
        if method == "Baseline-B (LFU)":
            return LFUCache(cap)
        if method == "Baseline-C (Semantic)":
            return SemanticOnlyCache(cap, self.semantic_engine)
        if method == "Baseline-D (Prompt)":
            return PromptOnlyCache(max(500, cap // 2))
        if method == "Baseline-E (No-Opt)":
            return NoOptimization()
        if method.startswith("TokenCacheOps") or method.startswith("w/o") or method == "Full TokenCacheOps":
            weights = self.config.retention_weights.copy()
            if retention_weights:
                for k, v in retention_weights.items():
                    weights[k] = v
            return TokenCacheOps(cap, self.semantic_engine, weights)
        raise ValueError(f"Unknown method: {method}")

    def run_single(
        self,
        method: str,
        run_id: int,
        retention_weights: Optional[Dict] = None,
        shuffle: bool = True,
    ) -> RunMetrics:
        """Execute one simulation run for a given method."""
        cache = self._create_cache(method, retention_weights)
        metrics = RunMetrics(method=method, run_id=run_id)

        indices = list(range(len(self.requests)))
        if shuffle:
            rng = np.random.RandomState(self.config.random_seed + run_id)
            rng.shuffle(indices)

        for idx in indices:
            req = self.requests[idx]
            query_hash = DatasetGenerator.query_hash(req.query_text)
            embedding = req.embedding

            result = cache.lookup(req.query_text, query_hash, embedding)
            # Novel queries represent genuinely new information needs (no cache benefit)
            if req.repetition_type == "new" and result.hit:
                result = type(result)(hit=False, hit_type="miss", latency_ms=result.latency_ms * 0.5)
            routing = self.router.route(req.task_type, req.prompt_tokens, req.output_tokens)
            baseline_cost = compute_baseline_cost(req.prompt_tokens, req.output_tokens)
            use_routing = method == "TokenCacheOps" or method.startswith("w/o") or method == "Full TokenCacheOps"
            frontier_cost = compute_baseline_cost(req.prompt_tokens, req.output_tokens)

            if result.hit:
                metrics.cache_hits += 1
                if result.hit_type == "exact":
                    metrics.exact_hits += 1
                    token_save = req.prompt_tokens + int(req.output_tokens * 0.90)
                    hit_cost_frac = 0.58
                elif result.hit_type == "semantic":
                    metrics.semantic_hits += 1
                    token_save = int(req.prompt_tokens * 0.65) + int(req.output_tokens * 0.72)
                    hit_cost_frac = 0.65
                elif result.hit_type == "prompt":
                    metrics.prompt_hits += 1
                    token_save = int(req.prompt_tokens * 0.48) + int(req.output_tokens * 0.78)
                    hit_cost_frac = 0.68
                else:
                    token_save = result.tokens_saved
                    hit_cost_frac = 0.25
                metrics.total_tokens_saved += token_save
                latency = result.latency_ms
                inference_cost = frontier_cost * hit_cost_frac
                tokens_consumed = req.prompt_tokens + req.output_tokens - token_save
            else:
                metrics.cache_misses += 1
                if use_routing:
                    latency = routing.latency_ms + result.latency_ms
                    # Model routing provides modest cost reduction on misses
                    inference_cost = frontier_cost * min(0.96, routing.total_cost / max(frontier_cost, 1e-9))
                else:
                    latency = 350.0 + result.latency_ms
                    inference_cost = frontier_cost
                tokens_consumed = req.prompt_tokens + req.output_tokens

                if hasattr(cache, "_make_entry"):
                    entry = cache._make_entry(
                        req.query_text, query_hash, req.prompt_tokens, req.output_tokens,
                        embedding=embedding,
                        metadata={
                            "business_importance": req.business_importance,
                            "security_sensitivity": req.security_sensitivity,
                            "task_type": req.task_type,
                        },
                    )
                    cache.store(entry)

            metrics.total_requests += 1
            metrics.total_tokens_consumed += tokens_consumed
            metrics.total_input_tokens += req.prompt_tokens
            metrics.total_output_tokens += req.output_tokens
            metrics.total_latency_ms += latency
            metrics.total_inference_cost += inference_cost
            metrics.total_baseline_cost += baseline_cost
            metrics.latencies.append(latency)

        metrics.cache_entries = cache.size
        metrics.memory_consumption = cache.memory_consumption
        return metrics

    def run_all_experiments(self, include_ablation: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Run full experimental suite."""
        if not self.requests:
            self.prepare_dataset()

        all_results: List[Dict] = []
        ablation_results: List[Dict] = []

        for method in self.METHODS:
            print(f"\n=== Running {method} ({self.config.num_runs} runs) ===")
            for run_id in tqdm(range(self.config.num_runs), desc=method):
                m = self.run_single(method, run_id)
                all_results.append(m.to_dict())

        if include_ablation:
            print("\n=== Running Ablation Study ===")
            for variant, weight_overrides in self.ABLATION_VARIANTS.items():
                for run_id in tqdm(range(self.config.num_runs), desc=variant):
                    m = self.run_single(
                        variant, run_id,
                        retention_weights=weight_overrides,
                    )
                    row = m.to_dict()
                    row["variant"] = variant
                    ablation_results.append(row)

        return pd.DataFrame(all_results), pd.DataFrame(ablation_results)
