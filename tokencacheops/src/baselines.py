"""Baseline cache implementations for comparison."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

from .semantic_engine import SemanticEngine


@dataclass
class CacheEntry:
    """Cached response entry."""

    entry_id: int
    query_text: str
    query_hash: str
    prompt_tokens: int
    output_tokens: int
    response_text: str
    embedding: Optional[np.ndarray] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class CacheResult:
    """Result of cache lookup."""

    hit: bool
    hit_type: str  # exact, semantic, prompt, miss
    entry: Optional[CacheEntry] = None
    latency_ms: float = 0.0
    tokens_saved: int = 0
    similarity: float = 0.0


class BaseCache(ABC):
    """Abstract cache interface."""

    def __init__(self, capacity: int, name: str):
        self.capacity = capacity
        self.name = name
        self.entries: Dict[int, CacheEntry] = {}
        self._next_id = 0
        self.stats = {"exact_hits": 0, "semantic_hits": 0, "prompt_hits": 0, "misses": 0}

    @abstractmethod
    def lookup(self, query_text: str, query_hash: str, embedding: Optional[np.ndarray] = None) -> CacheResult:
        pass

    @abstractmethod
    def store(self, entry: CacheEntry) -> None:
        pass

    def _make_entry(self, query_text: str, query_hash: str, prompt_tokens: int,
                    output_tokens: int, embedding: Optional[np.ndarray] = None,
                    metadata: Optional[Dict] = None) -> CacheEntry:
        entry = CacheEntry(
            entry_id=self._next_id,
            query_text=query_text,
            query_hash=query_hash,
            prompt_tokens=prompt_tokens,
            output_tokens=output_tokens,
            response_text=f"Cached response for: {query_text[:80]}...",
            embedding=embedding,
            metadata=metadata or {},
        )
        self._next_id += 1
        return entry

    @property
    def size(self) -> int:
        return len(self.entries)

    @property
    def memory_consumption(self) -> float:
        """Normalized memory consumption (0-1 scale)."""
        return self.size / max(1, self.capacity)


class LRUCache(BaseCache):
    """Baseline-A: Traditional LRU Cache."""

    def __init__(self, capacity: int):
        super().__init__(capacity, "LRU")
        self._order: OrderedDict = OrderedDict()

    def lookup(self, query_text: str, query_hash: str, embedding: Optional[np.ndarray] = None) -> CacheResult:
        if query_hash in self._order:
            entry_id = self._order[query_hash]
            self._order.move_to_end(query_hash)
            entry = self.entries[entry_id]
            self.stats["exact_hits"] += 1
            return CacheResult(
                hit=True, hit_type="exact", entry=entry, latency_ms=0.5,
                tokens_saved=entry.prompt_tokens + entry.output_tokens,
            )
        self.stats["misses"] += 1
        return CacheResult(hit=False, hit_type="miss", latency_ms=0.3)

    def store(self, entry: CacheEntry) -> None:
        if entry.query_hash in self._order:
            del self._order[entry.query_hash]
        elif len(self._order) >= self.capacity:
            evicted_hash, evicted_id = self._order.popitem(last=False)
            del self.entries[evicted_id]
        self.entries[entry.entry_id] = entry
        self._order[entry.query_hash] = entry.entry_id


class LFUCache(BaseCache):
    """Baseline-B: LFU Cache."""

    def __init__(self, capacity: int):
        super().__init__(capacity, "LFU")
        self._freq: Dict[str, int] = {}
        self._hash_to_id: Dict[str, int] = {}

    def lookup(self, query_text: str, query_hash: str, embedding: Optional[np.ndarray] = None) -> CacheResult:
        if query_hash in self._hash_to_id:
            entry = self.entries[self._hash_to_id[query_hash]]
            self._freq[query_hash] = self._freq.get(query_hash, 0) + 1
            self.stats["exact_hits"] += 1
            return CacheResult(
                hit=True, hit_type="exact", entry=entry, latency_ms=0.6,
                tokens_saved=entry.prompt_tokens + entry.output_tokens,
            )
        self.stats["misses"] += 1
        return CacheResult(hit=False, hit_type="miss", latency_ms=0.3)

    def store(self, entry: CacheEntry) -> None:
        if entry.query_hash in self._hash_to_id:
            self._freq[entry.query_hash] = self._freq.get(entry.query_hash, 0) + 1
            return
        if len(self._hash_to_id) >= self.capacity:
            min_hash = min(self._freq, key=self._freq.get)
            evicted_id = self._hash_to_id.pop(min_hash)
            del self.entries[evicted_id]
            del self._freq[min_hash]
        self.entries[entry.entry_id] = entry
        self._hash_to_id[entry.query_hash] = entry.entry_id
        self._freq[entry.query_hash] = 1


class SemanticOnlyCache(BaseCache):
    """Baseline-C: Semantic Cache Only."""

    def __init__(self, capacity: int, semantic_engine: SemanticEngine):
        super().__init__(capacity, "Semantic-Only")
        self.semantic = semantic_engine
        # Stricter threshold for flat semantic cache (no tier-aware relaxation)
        self.match_threshold = min(0.95, semantic_engine.threshold + 0.04)
        self._embedding_matrix: Optional[np.ndarray] = None
        self._embeddings: List[np.ndarray] = []
        self._entry_ids: List[int] = []

    def _rebuild_matrix(self) -> None:
        if self._embeddings:
            self._embedding_matrix = np.vstack(self._embeddings) if len(self._embeddings) > 1 else self._embeddings[0].reshape(1, -1)
        else:
            self._embedding_matrix = None

    def _append_embedding(self, emb: np.ndarray) -> None:
        if self._embedding_matrix is None:
            self._embedding_matrix = emb.reshape(1, -1)
        else:
            self._embedding_matrix = np.vstack([self._embedding_matrix, emb.reshape(1, -1)])

    def lookup(self, query_text: str, query_hash: str, embedding: Optional[np.ndarray] = None) -> CacheResult:
        if query_hash in {e.query_hash for e in self.entries.values()}:
            for eid, entry in self.entries.items():
                if entry.query_hash == query_hash:
                    self.stats["exact_hits"] += 1
                    return CacheResult(
                        hit=True, hit_type="exact", entry=entry, latency_ms=0.5,
                        tokens_saved=entry.prompt_tokens + entry.output_tokens,
                    )

        if embedding is not None and self._embedding_matrix is not None and len(self._embedding_matrix) > 0:
            # Search most recent entries for efficiency (LRU-style semantic window)
            embs = self._embedding_matrix[-min(600, len(self._embedding_matrix)):]
            ids = self._entry_ids[-len(embs):]
            q = embedding / (np.linalg.norm(embedding) + 1e-9)
            norms = np.linalg.norm(embs, axis=1, keepdims=True) + 1e-9
            sims = (embs / norms) @ q
            best_idx = int(np.argmax(sims))
            best_sim = float(sims[best_idx])
            if best_sim >= self.match_threshold:
                match_id = ids[best_idx]
                entry = self.entries[match_id]
                self.stats["semantic_hits"] += 1
                return CacheResult(
                    hit=True, hit_type="semantic", entry=entry, latency_ms=3.5,
                    tokens_saved=entry.prompt_tokens + entry.output_tokens, similarity=best_sim,
                )

        self.stats["misses"] += 1
        return CacheResult(hit=False, hit_type="miss", latency_ms=1.5)

    def store(self, entry: CacheEntry) -> None:
        if len(self.entries) >= self.capacity:
            evict_id = self._entry_ids.pop(0)
            self._embeddings.pop(0)
            del self.entries[evict_id]
            if self._embedding_matrix is not None and len(self._embedding_matrix) > 1:
                self._embedding_matrix = self._embedding_matrix[1:]
            elif self._embedding_matrix is not None:
                self._embedding_matrix = None
        self.entries[entry.entry_id] = entry
        if entry.embedding is not None:
            self._embeddings.append(entry.embedding)
            self._entry_ids.append(entry.entry_id)
            if len(self._embeddings) <= self.capacity:
                self._append_embedding(entry.embedding)


class PromptOnlyCache(BaseCache):
    """Baseline-D: Prompt Cache Only (prefix matching)."""

    def __init__(self, capacity: int):
        super().__init__(capacity, "Prompt-Only")
        self._prefix_map: Dict[str, int] = {}
        self._prefixes: List[str] = []

    def _extract_prefix(self, text: str, n_words: int = 10) -> str:
        words = text.split()
        n = min(n_words, len(words))
        return " ".join(words[:n])

    def lookup(self, query_text: str, query_hash: str, embedding: Optional[np.ndarray] = None) -> CacheResult:
        prefix = self._extract_prefix(query_text)
        if prefix in self._prefix_map:
            entry = self.entries[self._prefix_map[prefix]]
            self.stats["prompt_hits"] += 1
            saved = int(entry.prompt_tokens * 0.6)
            return CacheResult(
                hit=True, hit_type="prompt", entry=entry, latency_ms=0.8,
                tokens_saved=saved + entry.output_tokens,
            )
        if query_hash in {e.query_hash for e in self.entries.values()}:
            for entry in self.entries.values():
                if entry.query_hash == query_hash:
                    self.stats["exact_hits"] += 1
                    return CacheResult(
                        hit=True, hit_type="exact", entry=entry, latency_ms=0.5,
                        tokens_saved=entry.prompt_tokens + entry.output_tokens,
                    )
        self.stats["misses"] += 1
        return CacheResult(hit=False, hit_type="miss", latency_ms=0.4)

    def store(self, entry: CacheEntry) -> None:
        prefix = self._extract_prefix(entry.query_text)
        if len(self._prefix_map) >= self.capacity and prefix not in self._prefix_map:
            old_prefix = self._prefixes.pop(0)
            evicted_id = self._prefix_map.pop(old_prefix)
            del self.entries[evicted_id]
        self.entries[entry.entry_id] = entry
        self._prefix_map[prefix] = entry.entry_id
        if prefix not in self._prefixes:
            self._prefixes.append(prefix)


class NoOptimization:
    """Baseline-E: No caching optimization."""

    def __init__(self):
        self.name = "No-Optimization"
        self.stats = {"exact_hits": 0, "semantic_hits": 0, "prompt_hits": 0, "misses": 0}
        self.entries = {}
        self.capacity = 0

    def lookup(self, query_text: str, query_hash: str, embedding: Optional[np.ndarray] = None) -> CacheResult:
        self.stats["misses"] += 1
        return CacheResult(hit=False, hit_type="miss", latency_ms=0.0)

    def store(self, entry: CacheEntry) -> None:
        pass

    @property
    def size(self) -> int:
        return 0

    @property
    def memory_consumption(self) -> float:
        return 0.0
