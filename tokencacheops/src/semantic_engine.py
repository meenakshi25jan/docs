"""Semantic similarity engine using sentence-transformers."""

from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class SemanticEngine:
    """Embedding-based semantic similarity for cache lookup."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", threshold: float = 0.82):
        self.model_name = model_name
        self.threshold = threshold
        self._model = None
        self._embedding_cache: dict = {}

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed(self, texts: List[str], batch_size: int = 256) -> np.ndarray:
        """Batch embed texts with caching."""
        results = []
        to_embed = []
        to_embed_idx = []
        for i, text in enumerate(texts):
            if text in self._embedding_cache:
                results.append(self._embedding_cache[text])
            else:
                results.append(None)
                to_embed.append(text)
                to_embed_idx.append(i)

        if to_embed:
            embeddings = self.model.encode(to_embed, batch_size=batch_size, show_progress_bar=False)
            for idx, emb, text in zip(to_embed_idx, embeddings, to_embed):
                self._embedding_cache[text] = emb
                results[idx] = emb

        return np.array(results)

    def embed_single(self, text: str) -> np.ndarray:
        return self.embed([text])[0]

    def find_best_match(
        self,
        query_embedding: np.ndarray,
        candidate_embeddings: np.ndarray,
        candidate_ids: List[int],
    ) -> Tuple[Optional[int], float]:
        """Find best semantic match above threshold."""
        if len(candidate_embeddings) == 0:
            return None, 0.0
        # Fast cosine similarity via dot product on normalized vectors
        q = query_embedding / (np.linalg.norm(query_embedding) + 1e-9)
        norms = np.linalg.norm(candidate_embeddings, axis=1, keepdims=True) + 1e-9
        normed = candidate_embeddings / norms
        sims = normed @ q
        best_idx = int(np.argmax(sims))
        best_sim = float(sims[best_idx])
        if best_sim >= self.threshold:
            return candidate_ids[best_idx], best_sim
        return None, best_sim

    def similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        return float(cosine_similarity(emb1.reshape(1, -1), emb2.reshape(1, -1))[0, 0])
