# OKF vs RAG: Side-by-Side Demo

This example answers the question from the article: **Is Google's Open Knowledge Format (OKF) replacing RAG?**

**Short answer: No.** OKF organizes knowledge; RAG retrieves it. Together they work better than either alone.

## What this demo shows

| Layer | Traditional RAG | OKF-enhanced RAG |
|-------|---------------|------------------|
| Knowledge unit | Fixed-size text chunks from one big document | One concept per markdown file |
| Structure | Lost when documents are split | YAML metadata + cross-links |
| Retrieval | Vector similarity only | Metadata filter + vector search + graph expansion |
| Best for | Quick prototypes | Enterprise knowledge + AI agents |

## Project layout

```
examples/okf-vs-rag/
├── compare.py                 # Run the side-by-side comparison
├── documents/
│   └── payment-system-docs.md # Monolithic doc (traditional RAG input)
├── okf_bundle/                # OKF concepts (one file per concept)
│   ├── authentication.md
│   ├── payment-gateway.md
│   └── ...
└── src/
    ├── common.py
    ├── rag_traditional.py     # Chunk + embed + retrieve
    └── rag_okf_enhanced.py    # Concept + metadata + graph + retrieve
```

## Run it

```bash
cd examples/okf-vs-rag
python3 compare.py
```

Custom query:

```bash
python3 compare.py "investigate a production auth outage in payments"
```

## Key takeaway

```
RAG retrieves information.
OKF organizes information.

One does not replace the other.
```

In production you would still use a vector database and embedding model. OKF improves **what gets embedded** — whole concepts with relationships — instead of random paragraph fragments.

## References

- [Google Cloud: Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
- [OKF Specification (GitHub)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
