
import math


def recall_at_k(
    ranked_ids: list[str],
    relevant_ids: set[str],
    k: int = 5
) -> float:

    if k <= 0:
        raise ValueError("k must be positive.")

    if not relevant_ids:
        return 0.0

    retrieved = set(ranked_ids[:k])
    return len(retrieved & relevant_ids) / len(relevant_ids)


def mrr_at_k(
    ranked_ids: list[str],
    relevant_ids: set[str],
    k: int = 5
) -> float:

    if k <= 0:
        raise ValueError("k must be positive.")

    for rank, chunk_id in enumerate(ranked_ids[:k], start=1):
        if chunk_id in relevant_ids:
            return 1.0 / rank

    return 0.0


def ndcg_at_k(
    ranked_ids: list[str],
    relevance: dict[str, int],
    k: int = 5
) -> float:

    if k <= 0:
        raise ValueError("k must be positive.")

    def dcg(scores: list[int]) -> float:
        return sum(
            (2 ** score - 1) / math.log2(rank + 1)
            for rank, score in enumerate(scores, start=1)
        )

    actual_scores = [
        relevance.get(chunk_id, 0)
        for chunk_id in ranked_ids[:k]
    ]

    ideal_scores = sorted(
        relevance.values(),
        reverse=True
    )[:k]

    ideal_dcg = dcg(ideal_scores)

    if ideal_dcg == 0:
        return 0.0

    return dcg(actual_scores) / ideal_dcg


def evaluate_rankings(
    rankings: dict[str, list[str]],
    relevance_judgments: dict[str, dict[str, int]],
    k: int = 5
) -> dict:

    if k <= 0:
        raise ValueError("k must be positive.")

    per_query = {}

    for query_id, relevance in relevance_judgments.items():

        ranked_ids = rankings.get(query_id, [])

        relevant_ids = {
            chunk_id
            for chunk_id, score in relevance.items()
            if score > 0
        }

        per_query[query_id] = {
            "recall": recall_at_k(
                ranked_ids, relevant_ids, k
            ),
            "mrr": mrr_at_k(
                ranked_ids, relevant_ids, k
            ),
            "ndcg": ndcg_at_k(
                ranked_ids, relevance, k
            )
        }

    query_count = len(per_query)

    if query_count == 0:
        return {
            "k": k,
            "query_count": 0,
            "metrics": {},
            "per_query": {}
        }

    average_metrics = {
        metric: round(
            sum(result[metric] for result in per_query.values())
            / query_count,
            4
        )
        for metric in ("recall", "mrr", "ndcg")
    }

    return {
        "k": k,
        "query_count": query_count,
        "metrics": average_metrics,
        "per_query": per_query
    }
