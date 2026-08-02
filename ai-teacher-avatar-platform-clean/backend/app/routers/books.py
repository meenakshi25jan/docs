import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.book_agent import book_agent, chunk_text
from app.database import get_db
from app.embeddings import embed_batch
from app.guardrails import GuardrailError, check_input
from app.models import Book, BookChunk, ChatSession, Message, User
from app.schemas import BookInfo, BookTopicRequest, BookTopicResponse, BookUploadResponse
from app.security import get_current_user

router = APIRouter(prefix="/api/books", tags=["books"])

MAX_FILE_BYTES = 8 * 1024 * 1024  # 8MB — plenty for text-based notes/books


def _extract_text(filename: str, raw: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        try:
            from pypdf import PdfReader
        except ImportError as e:
            raise GuardrailError(
                "PDF support isn't installed on the server (pip install pypdf)."
            ) from e
        import io

        reader = PdfReader(io.BytesIO(raw))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    # .txt / .md / anything else — best-effort decode
    return raw.decode("utf-8", errors="ignore")


@router.post("/upload", response_model=BookUploadResponse)
async def upload_book(
    file: UploadFile,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    raw = await file.read()
    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "File too large (max 8MB).")

    try:
        text = _extract_text(file.filename or "upload.txt", raw)
    except GuardrailError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, e.message)

    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Couldn't read any text from that file.")

    book = Book(id=str(uuid.uuid4()), user_id=user.id, title=file.filename or "Untitled book")
    db.add(book)
    await db.flush()

    for i, c in enumerate(chunks):
        db.add(BookChunk(id=str(uuid.uuid4()), book_id=book.id, chunk_index=i, content=c))
    await db.flush()

    # embed after insert so a slow/failed embedding step never blocks the
    # chunks themselves from being saved - book_agent falls back to keyword
    # search for any chunk left with embedding=None
    try:
        vectors = embed_batch(chunks)
        result = await db.execute(select(BookChunk).where(BookChunk.book_id == book.id).order_by(BookChunk.chunk_index))
        stored_chunks = result.scalars().all()
        for stored, vector in zip(stored_chunks, vectors):
            stored.embedding = vector
    except Exception:
        pass  # keyword-search fallback still works without embeddings

    await db.commit()

    return BookUploadResponse(
        book=BookInfo(id=book.id, title=book.title, created_at=book.created_at),
        chunk_count=len(chunks),
    )


@router.get("/", response_model=list[BookInfo])
async def list_books(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.user_id == user.id).order_by(Book.created_at.desc()))
    books = result.scalars().all()
    return [BookInfo(id=b.id, title=b.title, created_at=b.created_at) for b in books]


@router.post("/topic", response_model=BookTopicResponse)
async def explain_topic(
    req: BookTopicRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    topic = check_input(req.topic)

    result = await db.execute(select(Book).where(Book.id == req.book_id, Book.user_id == user.id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found.")

    best = await book_agent.top_chunks_vector(db, book.id, topic, k=3)
    try:
        data = await book_agent.explain(
            student_name=user.display_name or "there",
            book_title=book.title,
            topic=topic,
            context_chunks=[c.content for c in best],
        )
    except GuardrailError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, e.message)

    session_id = req.session_id
    if not session_id:
        session = ChatSession(id=str(uuid.uuid4()), user_id=user.id, mode="book")
        db.add(session)
        await db.flush()
        session_id = session.id

    db.add(Message(session_id=session_id, role="user", content=f"[book topic] {topic}"))
    db.add(Message(session_id=session_id, role="assistant", content=data["reply_text"]))
    await db.commit()

    return BookTopicResponse(
        session_id=session_id,
        reply_text=data["reply_text"],
        example=data["example"],
        source_book=book.title,
    )
