"""
tests/test_chunker.py — text chunking tests
Fast — no DB, no LLM, pure text processing.
"""
from ingestion.chunker import chunk_text


def test_chunks_returns_list():
    result = chunk_text("This is a test document.")
    assert isinstance(result, list)


def test_chunks_nonempty_text():
    text = "Apple Inc. reported strong earnings. " * 50
    chunks = chunk_text(text)
    assert len(chunks) > 0


def test_chunks_are_strings():
    text = "Microsoft revenue grew significantly. " * 50
    chunks = chunk_text(text)
    for chunk in chunks:
        assert isinstance(chunk, str)


def test_chunks_max_size():
    text = "Tesla electric vehicle. " * 200
    chunks = chunk_text(text)
    for chunk in chunks:
        assert len(chunk) <= 1200


def test_empty_text_returns_list():
    result = chunk_text("")
    assert isinstance(result, list)
