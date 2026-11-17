
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import DocumentChunk
from app.services.llm.embeddings import generate_embedding


def retrieve_similar_chunks(
    query: str,
    db: Session,
    top_k: int = 5
) -> list[dict]:

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be positive.")

    query_embedding = generate_embedding(query)

    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    ).label("distance")

    statement = (
        select(DocumentChunk, distance)
        .where(DocumentChunk.embedding.is_not(None))
        .order_by(distance)
        .limit(top_k)
    )

    results = db.execute(statement).all()

    retrieved_chunks = []

    for chunk, cosine_distance in results:
        retrieved_chunks.append({
            "document_id": str(chunk.document_id),
            "chunk_index": chunk.chunk_index,
            "page_number": (chunk.chunk_metadata or {}).get("page_number"),
            "content": chunk.content,
            "similarity": round(1 - float(cosine_distance), 4)
        })

    return retrieved_chunks


def retrieve_keyword_chunks(
    query: str,
    db: Session,
    top_k: int = 5
) -> list[dict]:

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be positive.")

    search_query = func.plainto_tsquery("english", query)

    rank = func.ts_rank_cd(
        DocumentChunk.search_vector,
        search_query
    ).label("rank")

    statement = (
        select(DocumentChunk, rank)
        .where(
            DocumentChunk.search_vector.op("@@")(search_query)
        )
        .order_by(rank.desc())
        .limit(top_k)
    )

    results = db.execute(statement).all()

    retrieved_chunks = []

    for chunk, relevance in results:
        retrieved_chunks.append({
            "document_id": str(chunk.document_id),
            "chunk_index": chunk.chunk_index,
            "page_number": (chunk.chunk_metadata or {}).get("page_number"),
            "content": chunk.content,
            "keyword_score": round(float(relevance), 4)
        })

    return retrieved_chunks


def retrieve_hybrid_chunks(
    query: str,
    db: Session,
    top_k: int = 5,
    candidate_k: int = 10
) -> list[dict]:

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if top_k <= 0 or candidate_k <= 0:
        raise ValueError("top_k and candidate_k must be positive.")

    vector_results = retrieve_similar_chunks(
        query, db, candidate_k
    )

    keyword_results = retrieve_keyword_chunks(
        query, db, candidate_k
    )

    rrf_scores = {}
    chunks = {}
    retrieval_sources = {}

    rrf_constant = 60

    for source, results in (
        ("vector", vector_results),
        ("keyword", keyword_results)
    ):
        for rank, chunk in enumerate(results, start=1):
            key = (
                chunk["document_id"],
                chunk["chunk_index"]
            )

            rrf_scores[key] = (
                rrf_scores.get(key, 0)
                + 1 / (rrf_constant + rank)
            )

            chunks[key] = chunk

            retrieval_sources.setdefault(key, []).append(source)

    ranked_chunks = sorted(
        rrf_scores,
        key=lambda key: rrf_scores[key],
        reverse=True
    )

    hybrid_results = []

    for key in ranked_chunks[:top_k]:
        chunk = chunks[key]

        hybrid_results.append({
            "document_id": chunk["document_id"],
            "chunk_index": chunk["chunk_index"],
            "page_number": chunk.get("page_number"),
            "content": chunk["content"],
            "similarity": chunk.get("similarity"),
            "hybrid_score": round(rrf_scores[key], 6),
            "retrieved_by": retrieval_sources[key]
        })

    return hybrid_results
