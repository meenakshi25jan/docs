"""TokenCacheOps: Five-tier intelligent cache architecture."""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

from .baselines import BaseCache, CacheEntry, CacheResult
from .config import RETENTION_WEIGHTS, TIER_CAPACITIES
from .semantic_engine import SemanticEngine


@dataclass
class TierStats:
    """Per-tier cache statistics."""

    name: str
    capacity: int
    entries: Dict[int, CacheEntry] = field(default_factory=dict)
    access_count: int = 0
    hit_count: int = 0


class RetentionScorer:
    """Compute retention scores using multi-factor formula."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or RETENTION_WEIGHTS.copy()
        self._access_graph: Dict[int, set] = defaultdict(set)
        self._global_access_count = 0

    def record_access(self, entry_id: int, related_ids: Optional[List[int]] = None) -> None:
        self._global_access_count += 1
        if related_ids:
            for rid in related_ids:
                self._access_graph[entry_id].add(rid)
                self._access_graph[rid].add(entry_id)

    def compute(
        self,
        entry: CacheEntry,
        current_time: float,
        tier_name: str,
    ) -> float:
        """RetentionScore = w1*Recency + w2*Frequency + w3*SemanticReuse +
        w4*BusinessImportance + w5*InfluenceRank + w6*PenetrationFactor +
        w7*TokenEfficiency + w8*Freshness - w9*SecuritySensitivity
        """
        meta = entry.metadata
        age = current_time - meta.get("created_at", current_time)
        max_age = meta.get("max_age", 3600.0)

        recency = 1.0 - min(1.0, age / max(max_age, 1.0))
        frequency = min(1.0, meta.get("access_count", 0) / 50.0)
        semantic_reuse = min(1.0, meta.get("semantic_hits", 0) / 20.0)
        business_importance = meta.get("business_importance", 0.5)
        influence_rank = min(1.0, len(self._access_graph.get(entry.entry_id, set())) / 30.0)
        penetration = min(1.0, meta.get("cross_tier_promotions", 0) / 3.0 + meta.get("access_count", 0) / 100.0)
        token_efficiency = min(1.0, (entry.prompt_tokens + entry.output_tokens) / 5000.0)
        freshness = 1.0 - min(1.0, meta.get("staleness", 0.0))
        security_sensitivity = meta.get("security_sensitivity", 0.0)

        tier_bonus = {"strategic": 0.15, "evaluation": 0.08, "hot_access": 0.05}.get(tier_name, 0.0)

        score = (
            self.weights["recency"] * recency
            + self.weights["frequency"] * frequency
            + self.weights["semantic_reuse"] * semantic_reuse
            + self.weights["business_importance"] * business_importance
            + self.weights["influence_rank"] * influence_rank
            + self.weights["penetration_factor"] * penetration
            + self.weights["token_efficiency"] * token_efficiency
            + self.weights["freshness"] * freshness
            - self.weights["security_sensitivity"] * security_sensitivity
            + tier_bonus
        )
        return max(0.0, min(1.0, score))


class TokenCacheOps(BaseCache):
    """Proposed: Five-tier intelligent cache with retention scoring."""

    TIER_ORDER = ["strategic", "evaluation", "hot_access", "archive", "disposal"]

    def __init__(
        self,
        capacity: int,
        semantic_engine: SemanticEngine,
        retention_weights: Optional[Dict[str, float]] = None,
    ):
        super().__init__(capacity, "TokenCacheOps")
        self.semantic = semantic_engine
        self.scorer = RetentionScorer(retention_weights)
        self.tiers: Dict[str, TierStats] = {}
        for tier_name, frac in TIER_CAPACITIES.items():
            tier_cap = max(10, int(capacity * frac))
            self.tiers[tier_name] = TierStats(name=tier_name, capacity=tier_cap)
        self._embeddings_by_tier: Dict[str, List[np.ndarray]] = {t: [] for t in self.TIER_ORDER}
        self._entry_ids_by_tier: Dict[str, List[int]] = {t: [] for t in self.TIER_ORDER}
        self._start_time = time.time()
        self.retention_scores: Dict[int, float] = {}

    def _current_time(self) -> float:
        return time.time() - self._start_time

    def _find_match_with_threshold(
        self, query_embedding: np.ndarray, candidate_embeddings: np.ndarray,
        candidate_ids: List[int], threshold: float,
    ) -> Tuple[Optional[int], float]:
        q = query_embedding / (np.linalg.norm(query_embedding) + 1e-9)
        norms = np.linalg.norm(candidate_embeddings, axis=1, keepdims=True) + 1e-9
        sims = (candidate_embeddings / norms) @ q
        best_idx = int(np.argmax(sims))
        best_sim = float(sims[best_idx])
        if best_sim >= threshold:
            return candidate_ids[best_idx], best_sim
        return None, best_sim

    def _find_in_tiers(self, query_hash: str, embedding: Optional[np.ndarray]) -> Tuple[Optional[CacheEntry], str, float]:
        """Search tiers from hottest to coldest."""
        for tier_name in ["hot_access", "strategic", "evaluation", "archive"]:
            tier = self.tiers[tier_name]
            for entry in tier.entries.values():
                if entry.query_hash == query_hash:
                    return entry, tier_name, 1.0

        if embedding is not None:
            for tier_name in ["hot_access", "strategic", "evaluation", "archive"]:
                ids = self._entry_ids_by_tier[tier_name]
                embs = self._embeddings_by_tier[tier_name]
                if len(embs) == 0:
                    continue
                # Tier-aware threshold: hotter tiers use slightly relaxed matching
                tier_threshold = self.semantic.threshold - {"hot_access": 0.025, "strategic": 0.015, "evaluation": 0.008}.get(tier_name, 0.0)
                match_id, sim = self._find_match_with_threshold(
                    embedding, np.array(embs), ids, tier_threshold,
                )
                if match_id is not None:
                    entry = None
                    for t in self.TIER_ORDER:
                        if match_id in self.tiers[t].entries:
                            entry = self.tiers[t].entries[match_id]
                            tier_name = t
                            break
                    if entry is not None:
                        return entry, tier_name, sim
        return None, "", 0.0

    def lookup(self, query_text: str, query_hash: str, embedding: Optional[np.ndarray] = None) -> CacheResult:
        entry, tier_name, sim = self._find_in_tiers(query_hash, embedding)
        if entry is not None:
            entry.metadata["access_count"] = entry.metadata.get("access_count", 0) + 1
            self.scorer.record_access(entry.entry_id)
            self.tiers[tier_name].hit_count += 1
            self.tiers[tier_name].access_count += 1

            if sim >= 0.99:
                self.stats["exact_hits"] += 1
                hit_type = "exact"
                latency = 0.4
            else:
                entry.metadata["semantic_hits"] = entry.metadata.get("semantic_hits", 0) + 1
                self.stats["semantic_hits"] += 1
                hit_type = "semantic"
                latency = 1.8

            self._maybe_promote(entry, tier_name)
            tokens_saved = entry.prompt_tokens + entry.output_tokens
            return CacheResult(
                hit=True, hit_type=hit_type, entry=entry,
                latency_ms=latency, tokens_saved=tokens_saved, similarity=sim,
            )

        self.stats["misses"] += 1
        return CacheResult(hit=False, hit_type="miss", latency_ms=1.2)

    def _maybe_promote(self, entry: CacheEntry, current_tier: str) -> None:
        """Promote high-value entries to hotter tiers."""
        score = self.scorer.compute(entry, self._current_time(), current_tier)
        self.retention_scores[entry.entry_id] = score
        tier_idx = self.TIER_ORDER.index(current_tier)

        if score > 0.75 and tier_idx > 0:
            target = self.TIER_ORDER[tier_idx - 1]
            if len(self.tiers[target].entries) < self.tiers[target].capacity:
                self._move_entry(entry, current_tier, target)
                entry.metadata["cross_tier_promotions"] = entry.metadata.get("cross_tier_promotions", 0) + 1
        elif score < 0.25 and tier_idx < len(self.TIER_ORDER) - 1:
            target = self.TIER_ORDER[tier_idx + 1]
            self._move_entry(entry, current_tier, target)

    def _move_entry(self, entry: CacheEntry, from_tier: str, to_tier: str) -> None:
        if entry.entry_id in self.tiers[from_tier].entries:
            del self.tiers[from_tier].entries[entry.entry_id]
            if entry.entry_id in self._entry_ids_by_tier[from_tier]:
                idx = self._entry_ids_by_tier[from_tier].index(entry.entry_id)
                self._entry_ids_by_tier[from_tier].pop(idx)
                self._embeddings_by_tier[from_tier].pop(idx)
        self.tiers[to_tier].entries[entry.entry_id] = entry
        if entry.embedding is not None:
            self._embeddings_by_tier[to_tier].append(entry.embedding)
            self._entry_ids_by_tier[to_tier].append(entry.entry_id)

    def store(self, entry: CacheEntry) -> None:
        entry.metadata.setdefault("created_at", self._current_time())
        entry.metadata.setdefault("access_count", 0)
        entry.metadata.setdefault("semantic_hits", 0)
        entry.metadata.setdefault("max_age", 3600.0)
        entry.metadata.setdefault("staleness", 0.0)

        target_tier = "hot_access"
        if entry.metadata.get("business_importance", 0) > 0.85:
            target_tier = "strategic"
        elif entry.metadata.get("security_sensitivity", 0) > 0.7:
            target_tier = "archive"

        tier = self.tiers[target_tier]
        if len(tier.entries) >= tier.capacity:
            self._evict_from_tier(target_tier)

        tier.entries[entry.entry_id] = entry
        self.entries[entry.entry_id] = entry
        if entry.embedding is not None:
            self._embeddings_by_tier[target_tier].append(entry.embedding)
            self._entry_ids_by_tier[target_tier].append(entry.entry_id)

        score = self.scorer.compute(entry, self._current_time(), target_tier)
        self.retention_scores[entry.entry_id] = score

    def _evict_from_tier(self, tier_name: str) -> None:
        tier = self.tiers[tier_name]
        if not tier.entries:
            return

        scores = {
            eid: self.scorer.compute(entry, self._current_time(), tier_name)
            for eid, entry in tier.entries.items()
        }
        evict_id = min(scores, key=scores.get)
        entry = tier.entries.pop(evict_id)
        del self.entries[evict_id]
        if evict_id in self._entry_ids_by_tier[tier_name]:
            idx = self._entry_ids_by_tier[tier_name].index(evict_id)
            self._entry_ids_by_tier[tier_name].pop(idx)
            self._embeddings_by_tier[tier_name].pop(idx)

        disposal = self.tiers["disposal"]
        if len(disposal.entries) < disposal.capacity:
            disposal.entries[evict_id] = entry
        else:
            del self.retention_scores[evict_id]

    @property
    def size(self) -> int:
        return sum(len(t.entries) for t in self.tiers.values())

    @property
    def memory_consumption(self) -> float:
        return self.size / max(1, self.capacity)

    def get_tier_distribution(self) -> Dict[str, int]:
        return {name: len(t.entries) for name, t in self.tiers.items()}
