
import json
from pathlib import Path

from app.core.database import SessionLocal
from app.services.document.retriever import retrieve_hybrid_chunks


TOP_K = 5

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "datasets" / "retrieval_dataset.json"


def calculate_metrics(retrieved, relevant):
    retrieved_set = set(retrieved)
    relevant_set = set(relevant)

    relevant_retrieved = retrieved_set.intersection(relevant_set)

    recall = (
        len(relevant_retrieved) / len(relevant_set)
        if relevant_set else 0
    )

    precision = (
    len(relevant_retrieved) / min(TOP_K, len(retrieved))
    if retrieved else 0
    )
    reciprocal_rank = 0

    for rank, chunk_id in enumerate(retrieved, start=1):
        if chunk_id in relevant_set:
            reciprocal_rank = 1 / rank
            break

    return {
        "recall": recall,
        "precision": precision,
        "mrr": reciprocal_rank
    }


def evaluate():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    db = SessionLocal()

    total_recall = 0
    total_precision = 0
    total_mrr = 0

    try:
        for test_case in dataset:
            query = test_case["query"]

            relevant = set(zip(
                test_case["relevant_document_ids"],
                test_case["relevant_chunk_indices"]
            ))

            results = retrieve_hybrid_chunks(
                query=query,
                db=db,
                top_k=TOP_K
            )

            retrieved = [
                (result["document_id"], result["chunk_index"])
                for result in results
            ]

            metrics = calculate_metrics(retrieved, relevant)

            total_recall += metrics["recall"]
            total_precision += metrics["precision"]
            total_mrr += metrics["mrr"]

            print(f"\nQuery: {query}")
            print(f"Recall@{TOP_K}: {metrics['recall']:.4f}")
            print(f"Precision@{TOP_K}: {metrics['precision']:.4f}")
            print(f"MRR: {metrics['mrr']:.4f}")

        count = len(dataset)

        if count:
            print("\n========== FINAL EVALUATION ==========")
            print(f"Queries evaluated: {count}")
            print(f"Average Recall@{TOP_K}: {total_recall / count:.4f}")
            print(f"Average Precision@{TOP_K}: {total_precision / count:.4f}")
            print(f"Average MRR: {total_mrr / count:.4f}")

    finally:
        db.close()


if __name__ == "__main__":
    evaluate()
