"""
BookAgent — lets the teacher explain a topic *from a book the student
uploaded* instead of generic knowledge.

Retrieval is vector similarity search (pgvector, via `top_chunks_vector`)
when chunks have embeddings. `top_chunks` (keyword overlap) is kept as a
fallback for chunks ingested before the `embedding` column existed, so old
books don't silently return nothing.
"""

import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.embeddings import embed_text
from app.guardrails import GuardrailError
from app.llm_client import llm_client
from app.models import BookChunk

SYSTEM_PROMPT = """You are "Mr. David", a warm AI English teacher. The student, {student_name},
asked you to explain the topic "{topic}" using their own uploaded book/notes titled "{book_title}".

Here are the most relevant excerpts from that book:
---
{context}
---

Teach this like a real tutor sitting with the student:
1. Give a simple, practical explanation of the topic in your own words, grounded in the
   excerpts above (don't just repeat them verbatim).
2. Give ONE concrete real-life example showing the topic in use.
3. Suggest ONE small way the student could practice or apply it themselves ("how to innovate/
   use it") — e.g. a sentence to try, a mini exercise, or a real-world scenario.
4. End with a short question inviting them to try it.

Keep the whole thing spoken-style and encouraging — 4-6 sentences total, not a lecture.

Respond ONLY as JSON with exactly these keys:
{{"reply_text": "<the explanation + question, spoken style>",
  "example": "<the one concrete example, standalone, 1-2 sentences>"}}
"""

_WORD_RE = re.compile(r"[a-zA-Z']+")


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    """Simple fixed-size character chunker with overlap."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
        if start <= 0:
            break
    return [c for c in chunks if c.strip()]


def _score_chunk(chunk_text_: str, topic_words: set[str]) -> int:
    chunk_words = set(w.lower() for w in _WORD_RE.findall(chunk_text_))
    return len(chunk_words & topic_words)


class BookAgent:
    async def top_chunks_vector(
        self, db: AsyncSession, book_id: str, topic: str, k: int = 3
    ) -> list[BookChunk]:
        """Vector similarity search within one book's chunks. Only considers
        chunks that have an embedding; falls back to keyword search if none do
        (e.g. a book uploaded before this column existed).
        """
        query_vector = embed_text(topic)
        stmt = (
            select(BookChunk)
            .where(BookChunk.book_id == book_id, BookChunk.embedding.is_not(None))
            .order_by(BookChunk.embedding.cosine_distance(query_vector))
            .limit(k)
        )
        result = await db.execute(stmt)
        chunks = result.scalars().all()
        if chunks:
            return list(chunks)

        # no embedded chunks for this book yet - fall back to keyword search
        all_stmt = select(BookChunk).where(BookChunk.book_id == book_id)
        all_chunks = (await db.execute(all_stmt)).scalars().all()
        return self.top_chunks(list(all_chunks), topic, k=k)

    def top_chunks(self, chunks: list[BookChunk], topic: str, k: int = 3) -> list[BookChunk]:
        """Keyword-overlap fallback for chunks without embeddings."""
        topic_words = set(w.lower() for w in _WORD_RE.findall(topic))
        if not topic_words or not chunks:
            return chunks[:k]
        scored = sorted(chunks, key=lambda c: _score_chunk(c.content, topic_words), reverse=True)
        if _score_chunk(scored[0].content, topic_words) == 0:
            return chunks[:k]
        return scored[:k]

    async def explain(
        self, *, student_name: str, book_title: str, topic: str, context_chunks: list[str]
    ) -> dict:
        context = "\n---\n".join(context_chunks) if context_chunks else "(no matching excerpt found)"
        prompt = SYSTEM_PROMPT.format(
            student_name=student_name, topic=topic, book_title=book_title, context=context
        )
        try:
            data = await llm_client.chat_json(prompt, topic)
        except Exception as e:
            raise GuardrailError(f"LLM call failed: {e}")

        return {
            "reply_text": data.get("reply_text", "Let's look at that together."),
            "example": data.get("example", ""),
        }


book_agent = BookAgent()
