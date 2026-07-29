#!/usr/bin/env python3
"""Generate embeddings for knowledge_chunks rows missing vectors."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app.core.database import get_session_factory
from app.services.embeddings import embed_text, embedding_to_pgvector


async def main() -> None:
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(
            text("SELECT id, topic, content FROM knowledge_chunks WHERE embedding IS NULL")
        )
        rows = result.fetchall()
        if not rows:
            print("All knowledge chunks already have embeddings.")
            return
        print(f"Embedding {len(rows)} knowledge chunks...")
        for row in rows:
            vec = await embed_text(f"{row.topic}: {row.content}")
            if not vec:
                print("AI not configured — skipping embedding generation.")
                return
            await session.execute(
                text("UPDATE knowledge_chunks SET embedding = CAST(:vec AS vector) WHERE id = :id"),
                {"vec": embedding_to_pgvector(vec), "id": row.id},
            )
        await session.commit()
        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
