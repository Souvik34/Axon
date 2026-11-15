
from app.core.database import SessionLocal
from app.services.document.retriever import retrieve_keyword_chunks


QUERIES = [
    "Which language model providers does Cortex use?",
    "What is the primary LLM provider?",
    "Which provider acts as the fallback when Groq is unavailable?",
    "Which programming language supports dynamic typing?",
    "Which database supports ACID transactions?",
    "What is Reciprocal Rank Fusion used for?"
]


db = SessionLocal()

try:
    for query in QUERIES:
        results = retrieve_keyword_chunks(
            query=query,
            db=db,
            top_k=5
        )

        print("\n" + "=" * 70)
        print("QUERY:", query)
        print("=" * 70)

        print("Retrieved chunks:", len(results))

        for rank, result in enumerate(results, start=1):
            print(f"\nRank: {rank}")
            print("Document ID:", result["document_id"])
            print("Chunk Index:", result["chunk_index"])
            print("Keyword Score:", result["keyword_score"])
            print("Content:", result["content"])

finally:
    db.close()
