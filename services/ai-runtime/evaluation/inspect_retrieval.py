
from app.core.database import SessionLocal
from app.services.document.retriever import retrieve_hybrid_chunks

queries = [
    "Which language model providers does Cortex use?",
    "What is the primary LLM provider?",
    "Which provider acts as the fallback when Groq is unavailable?"
]

db = SessionLocal()

try:
    for query in queries:
        print(f"\n{'=' * 70}")
        print(f"QUERY: {query}")
        print("=" * 70)

        results = retrieve_hybrid_chunks(query, db, top_k=5)

        for rank, result in enumerate(results, start=1):
            print(f"\nRank: {rank}")
            print(f"Document ID: {result['document_id']}")
            print(f"Chunk Index: {result['chunk_index']}")
            print(f"Similarity: {result['similarity']}")
            print(f"Hybrid Score: {result['hybrid_score']}")
            print(f"Content: {result['content']}")
            print("Retrieved by:", result.get("retrieved_by"))

finally:
    db.close()
