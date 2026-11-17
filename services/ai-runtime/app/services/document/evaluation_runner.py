
from sqlalchemy.orm import Session

from app.services.document.retriever import retrieve_hybrid_chunks
from app.services.document.reranker import rerank_chunks
from app.services.document.evaluation import evaluate_rankings


def evaluate_retrieval(
    evaluation_queries: list[dict],
    db: Session,
    k: int = 5
) -> dict:

    if not evaluation_queries:
        raise ValueError("Evaluation queries cannot be empty.")

    if k <= 0:
        raise ValueError("k must be positive.")

    baseline_rankings = {}
    reranked_rankings = {}
    relevance_judgments = {}

    for item in evaluation_queries:

        query_id = item["query_id"]
        query = item["query"]
        relevance = item["relevance"]

        candidates = retrieve_hybrid_chunks(
            query=query,
            db=db,
            top_k=max(k * 3, 15),
            candidate_k=max(k * 3, 15)
        )

        baseline_rankings[query_id] = [
            f"{chunk['document_id']}:{chunk['chunk_index']}"
            for chunk in candidates
        ]

        reranked = rerank_chunks(
            query=query,
            chunks=candidates,
            top_k=max(k * 3, 15)
        )

        reranked_rankings[query_id] = [
            f"{chunk['document_id']}:{chunk['chunk_index']}"
            for chunk in reranked
        ]

        relevance_judgments[query_id] = relevance

    baseline = evaluate_rankings(
        rankings=baseline_rankings,
        relevance_judgments=relevance_judgments,
        k=k
    )

    reranked = evaluate_rankings(
        rankings=reranked_rankings,
        relevance_judgments=relevance_judgments,
        k=k
    )

    improvements = {
        metric: round(
            reranked["metrics"][metric]
            - baseline["metrics"][metric],
            4
        )
        for metric in baseline["metrics"]
    }

    return {
        "baseline": baseline,
        "reranked": reranked,
        "improvements": improvements
    }
