#!/usr/bin/env python3
"""Compare traditional RAG vs OKF-enhanced RAG on the same enterprise question."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from rag_okf_enhanced import OKFEnhancedRAG
from rag_traditional import TraditionalRAG

DEFAULT_QUERY = "How does our payment service authenticate requests?"


def print_result(result) -> None:
    print(f"\n{'=' * 72}")
    print(result.approach)
    print(f"Query: {result.query}")
    print(f"{'=' * 72}")

    for index, chunk in enumerate(result.chunks, start=1):
        title = chunk.metadata.get("title", chunk.id)
        print(f"\n[{index}] {title} (score={chunk.score:.3f})")
        if chunk.metadata:
            meta_preview = {
                k: chunk.metadata[k]
                for k in ("type", "service", "tags")
                if k in chunk.metadata
            }
            if meta_preview:
                print(f"    metadata: {meta_preview}")
        if chunk.related:
            print(f"    related concepts: {', '.join(chunk.related)}")
        preview = chunk.text.replace("\n", " ")
        print(f"    excerpt: {preview[:220]}{'...' if len(preview) > 220 else ''}")

    print("\nNotes:")
    for note in result.notes:
        print(f"  - {note}")


def verdict(traditional, okf) -> str:
    traditional_titles = {c.id for c in traditional.chunks}
    okf_has_auth = any("authentication" in c.id.lower() for c in okf.chunks)
    okf_related_count = sum(len(c.related) for c in okf.chunks)
    traditional_fragmented = any("chunk-" in c.id for c in traditional.chunks)

    lines = [
        "\n" + "=" * 72,
        "VERDICT: OKF does NOT replace RAG — it makes RAG smarter",
        "=" * 72,
        "",
        "Traditional RAG:",
        f"  - Retrieved {len(traditional.chunks)} arbitrary document chunks",
        f"  - Fragmented IDs: {traditional_fragmented}",
        f"  - No concept relationships preserved",
        "",
        "OKF-enhanced RAG:",
        f"  - Retrieved whole concepts including auth: {okf_has_auth}",
        f"  - Graph-linked related concepts: {okf_related_count} links surfaced",
        f"  - Metadata available for filtering (service, tags, type)",
        "",
        "Conclusion:",
        "  RAG = retrieval mechanism (embeddings + similarity search)",
        "  OKF = knowledge organization layer (concepts + metadata + links)",
        "  Best approach: OKF-organized knowledge fed INTO your existing RAG pipeline.",
    ]
    return "\n".join(lines)


def main() -> None:
    query = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_QUERY

    doc_path = ROOT / "documents" / "payment-system-docs.md"
    bundle_path = ROOT / "okf_bundle"

    traditional = TraditionalRAG(chunk_size=180, overlap=30)
    traditional.ingest_markdown(doc_path)
    traditional_result = traditional.retrieve(query, top_k=3)

    okf_rag = OKFEnhancedRAG(bundle_path)
    okf_rag.ingest_bundle()
    okf_result = okf_rag.retrieve(
        query,
        top_k=2,
        graph_depth=1,
        service="payment-service",
        tags={"security", "api", "payments"},
    )

    print_result(traditional_result)
    print_result(okf_result)
    print(verdict(traditional_result, okf_result))

    output = {
        "query": query,
        "traditional_rag": {
            "approach": traditional_result.approach,
            "chunks": [
                {"id": c.id, "score": round(c.score, 4), "source": c.source}
                for c in traditional_result.chunks
            ],
        },
        "okf_enhanced_rag": {
            "approach": okf_result.approach,
            "chunks": [
                {
                    "id": c.id,
                    "score": round(c.score, 4),
                    "metadata": c.metadata,
                    "related": c.related,
                }
                for c in okf_result.chunks
            ],
        },
        "conclusion": "OKF complements RAG; it does not replace vector search or embeddings.",
    }
    print("\nJSON summary:")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
