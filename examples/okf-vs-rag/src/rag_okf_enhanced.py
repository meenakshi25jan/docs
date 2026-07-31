"""OKF-enhanced RAG: concept-level retrieval with metadata filters and graph expansion."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from common import (
    RetrievedChunk,
    RetrievalResult,
    cosine_similarity,
    extract_links,
    resolve_link,
    split_frontmatter,
    term_frequency,
    tokenize,
)


@dataclass
class OKFConcept:
    path: Path
    concept_id: str
    metadata: Dict[str, object]
    body: str
    links: Set[str] = field(default_factory=set)


class OKFEnhancedRAG:
    """
    OKF does not replace RAG — it improves what gets retrieved.

    Pipeline:
    1. Load OKF concepts (one markdown file = one concept)
    2. Optional metadata pre-filter (service, tags, type)
    3. Semantic similarity over whole concepts (not arbitrary chunks)
    4. Graph expansion via markdown cross-links for related context
    """

    def __init__(self, bundle_root: Path):
        self.bundle_root = bundle_root.resolve()
        self.concepts: Dict[str, OKFConcept] = {}
        self.graph: Dict[str, Set[str]] = {}

    def ingest_bundle(self) -> None:
        for path in sorted(self.bundle_root.glob("**/*.md")):
            if path.name in {"index.md", "log.md"}:
                continue
            raw = path.read_text(encoding="utf-8")
            metadata, body = split_frontmatter(raw)
            concept_id = str(path.relative_to(self.bundle_root))
            links = extract_links(body)
            concept = OKFConcept(
                path=path,
                concept_id=concept_id,
                metadata=metadata,
                body=body.strip(),
                links=links,
            )
            self.concepts[concept_id] = concept

        for concept_id, concept in self.concepts.items():
            neighbors: Set[str] = set()
            for link in concept.links:
                resolved = resolve_link(self.bundle_root, concept.path, link)
                if resolved is None:
                    continue
                try:
                    neighbor_id = str(resolved.relative_to(self.bundle_root))
                except ValueError:
                    continue
                if neighbor_id in self.concepts:
                    neighbors.add(neighbor_id)
            self.graph[concept_id] = neighbors

    def _metadata_filter(
        self,
        service: Optional[str] = None,
        tags: Optional[Set[str]] = None,
    ) -> List[OKFConcept]:
        candidates = list(self.concepts.values())
        if service:
            candidates = [
                c
                for c in candidates
                if c.metadata.get("service") == service
            ]
        if tags:
            candidates = [
                c
                for c in candidates
                if tags.intersection(set(c.metadata.get("tags", [])))
            ]
        return candidates

    def _expand_graph(self, seed_ids: List[str], depth: int = 1) -> List[str]:
        visited: Set[str] = set(seed_ids)
        frontier = list(seed_ids)
        for _ in range(depth):
            next_frontier: List[str] = []
            for concept_id in frontier:
                for neighbor in self.graph.get(concept_id, set()):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        next_frontier.append(neighbor)
            frontier = next_frontier
        return list(visited)

    def retrieve(
        self,
        query: str,
        top_k: int = 2,
        graph_depth: int = 1,
        service: Optional[str] = None,
        tags: Optional[Set[str]] = None,
    ) -> RetrievalResult:
        query_vec = term_frequency(tokenize(query))
        candidates = self._metadata_filter(service=service, tags=tags)

        scored: List[RetrievedChunk] = []
        for concept in candidates:
            concept_text = f"{concept.metadata.get('title', '')} {concept.metadata.get('description', '')} {concept.body}"
            score = cosine_similarity(query_vec, term_frequency(tokenize(concept_text)))
            scored.append(
                RetrievedChunk(
                    id=concept.concept_id,
                    text=concept.body,
                    score=score,
                    source=str(concept.path),
                    metadata=concept.metadata,
                    related=sorted(self.graph.get(concept.concept_id, set())),
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        seed = [item.id for item in scored[:top_k]]
        expanded_ids = self._expand_graph(seed, depth=graph_depth)

        final_chunks: List[RetrievedChunk] = []
        seen: Set[str] = set()

        for item in scored:
            if item.id not in expanded_ids or item.id in seen:
                continue
            seen.add(item.id)
            final_chunks.append(item)

        # Add graph neighbors that semantic search missed (agent-style navigation).
        for concept_id in expanded_ids:
            if concept_id in seen:
                continue
            concept = self.concepts[concept_id]
            final_chunks.append(
                RetrievedChunk(
                    id=concept.concept_id,
                    text=concept.body,
                    score=0.0,
                    source=str(concept.path),
                    metadata=concept.metadata,
                    related=sorted(self.graph.get(concept.concept_id, set())),
                )
            )
            seen.add(concept_id)

        final_chunks.sort(key=lambda item: item.score, reverse=True)

        notes = [
            "Knowledge is organized as OKF concepts (one concept per markdown file).",
            "YAML frontmatter enables metadata pre-filtering before semantic search.",
            "Cross-links expand retrieval to related concepts (knowledge graph navigation).",
            "Vector similarity still runs — OKF improves organization, not replacement.",
        ]

        return RetrievalResult(
            approach="OKF-enhanced RAG (concepts + metadata + graph + vector search)",
            query=query,
            chunks=final_chunks,
            notes=notes,
        )
