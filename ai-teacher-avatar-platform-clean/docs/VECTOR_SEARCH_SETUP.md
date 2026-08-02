# Vector search upgrade — setup

This upgrades `BookAgent` retrieval from keyword-overlap scoring to real
vector similarity search via `pgvector` on your existing Neon database, per
the "v2 — swap for embeddings-based similarity search" note in
`ARCHITECTURE.md` section 8.

## 1. Install new dependencies

Already added to `requirements.txt`: `pgvector`, `sentence-transformers`.

```powershell
pip install -r requirements.txt
```

First run will download the `all-MiniLM-L6-v2` model (~90MB) — one-time,
cached locally after that.

## 2. Enable pgvector on Neon

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Run this once via `psql` or the Neon SQL Editor. Verify:

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

## 3. Table changes

`BookChunk` now has a nullable `embedding` column (384 dims, matching
`all-MiniLM-L6-v2`). Since your app calls `init_db()` with
`Base.metadata.create_all` on startup, this new column will be added
automatically to a fresh install — but `create_all` does NOT alter existing
tables. If `book_chunks` already exists in your Neon DB, run this once:

```sql
ALTER TABLE book_chunks ADD COLUMN IF NOT EXISTS embedding vector(384);

CREATE INDEX IF NOT EXISTS book_chunks_embedding_idx
ON book_chunks USING hnsw (embedding vector_cosine_ops);
```

The index is optional for small per-user book collections but keeps
retrieval fast as chunk counts grow.

## 4. Backfilling existing books

Books uploaded before this change have `embedding = NULL` on their chunks.
`book_agent.top_chunks_vector()` automatically falls back to the old
keyword search for those — nothing breaks. To upgrade them to vector search
too, re-upload the book, or run a one-off backfill script:

```python
# backfill_embeddings.py — run once from backend/
import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import BookChunk
from app.embeddings import embed_batch

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(BookChunk).where(BookChunk.embedding.is_(None)))
        chunks = result.scalars().all()
        if not chunks:
            print("Nothing to backfill.")
            return
        vectors = embed_batch([c.content for c in chunks])
        for chunk, vector in zip(chunks, vectors):
            chunk.embedding = vector
        await db.commit()
        print(f"Backfilled {len(chunks)} chunks.")

asyncio.run(main())
```

```powershell
python backfill_embeddings.py
```

## 5. What changed, file by file

- `app/embeddings.py` — new. Local embedding model (no extra API key/cost).
- `app/models.py` — `BookChunk.embedding` column added.
- `app/agents/book_agent.py` — added `top_chunks_vector()` (pgvector cosine
  search), kept `top_chunks()` (keyword) as the automatic fallback.
- `app/routers/books.py` — embeds chunks on upload; `/api/books/topic` now
  calls `top_chunks_vector()` instead of loading every chunk into Python
  and scoring keyword overlap there.

Nothing else changes — `BookAgent.explain()`, the prompt, the response
schema, and the frontend are untouched.
