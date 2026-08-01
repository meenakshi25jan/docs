import pytest

from app.ingestion.chunker import split_text_into_chunks


def test_split_text_into_chunks_overlap_and_indices():
    text = "word " * 300
    chunks = split_text_into_chunks(text, chunk_size=100, chunk_overlap=20)

    assert len(chunks) > 1
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1
    assert all(chunk.content for chunk in chunks)
    assert all(chunk.token_count and chunk.token_count > 0 for chunk in chunks)


def test_split_text_empty_returns_empty_list():
    assert split_text_into_chunks("   ") == []


def test_split_text_invalid_overlap_raises():
    with pytest.raises(ValueError, match="chunk_overlap"):
        split_text_into_chunks("hello", chunk_size=50, chunk_overlap=50)
