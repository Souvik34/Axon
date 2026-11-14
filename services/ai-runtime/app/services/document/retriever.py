
from sqlalchemy import select
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

    # 1. Convert the user's query into an embedding
    query_embedding = generate_embedding(query)

    # 2. Calculate cosine distance against stored embeddings
    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    ).label("distance")

    # 3. Retrieve the closest matching chunks
    statement = (
        select(DocumentChunk, distance)
        .where(DocumentChunk.embedding.is_not(None))
        .order_by(distance)
        .limit(top_k)
    )

    results = db.execute(statement).all()

    # 4. Prepare the retrieval results
    retrieved_chunks = []

    for chunk, cosine_distance in results:
        retrieved_chunks.append({
            "document_id": str(chunk.document_id),
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "similarity": round(1 - float(cosine_distance), 4)
        })

    return retrieved_chunks
