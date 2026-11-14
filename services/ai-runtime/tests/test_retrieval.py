
import pytest

from app.core.database import SessionLocal
from app.services.document.retriever import (
    retrieve_similar_chunks,
    retrieve_keyword_chunks,
    retrieve_hybrid_chunks,
)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_keyword_retrieval(db):
    results = retrieve_keyword_chunks(
        "Groq Gemini",
        db,
        top_k=5
    )

    assert len(results) > 0
    assert any(
        "Groq" in result["content"]
        and "Gemini" in result["content"]
        for result in results
    )


def test_vector_retrieval(db):
    results = retrieve_similar_chunks(
        "Which AI model providers does Cortex use?",
        db,
        top_k=5
    )

    assert len(results) > 0
    assert all(
        result["similarity"] is not None
        for result in results
    )


def test_hybrid_retrieval(db):
    results = retrieve_hybrid_chunks(
        "Which AI model providers does Cortex use?",
        db,
        top_k=5
    )

    assert len(results) > 0
    assert all(
        "hybrid_score" in result
        for result in results
    )

    scores = [
        result["hybrid_score"]
        for result in results
    ]

    assert scores == sorted(scores, reverse=True)
