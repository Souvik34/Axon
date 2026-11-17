
from sentence_transformers import CrossEncoder


_model = None


def get_reranker():
    global _model

    if _model is None:
        _model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2",
            max_length=512
        )

    return _model


def rerank_chunks(
    query: str,
    chunks: list[dict],
    top_k: int = 3
) -> list[dict]:

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be positive.")

    if not chunks:
        return []

    model = get_reranker()

    pairs = [
        (query, chunk["content"])
        for chunk in chunks
    ]

    scores = model.predict(
        pairs,
        batch_size=16,
        show_progress_bar=False
    )

    reranked_chunks = []

    for chunk, score in zip(chunks, scores):
        reranked_chunks.append({
            **chunk,
            "rerank_score": float(score)
        })

    reranked_chunks.sort(
        key=lambda chunk: chunk["rerank_score"],
        reverse=True
    )

    return reranked_chunks[:top_k]
