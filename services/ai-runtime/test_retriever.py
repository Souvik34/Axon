
from app.core.database import SessionLocal
from app.services.document.retriever import retrieve_similar_chunks


db = SessionLocal()

try:
    query = "How does AI use numerical representations to understand text?"

    results = retrieve_similar_chunks(
        query=query,
        db=db,
        top_k=3
    )

    print("\nSearch query:", query)
    print("\nRetrieved chunks:", len(results))

    for index, result in enumerate(results, start=1):
        print(f"\nResult {index}")
        print("Document ID:", result["document_id"])
        print("Similarity:", result["similarity"])
        print("Content:", result["content"])

finally:
    db.close()
