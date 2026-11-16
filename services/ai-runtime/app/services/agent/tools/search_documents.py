
from app.core.database import SessionLocal
from app.services.document.rag import answer_from_documents


def search_documents(query: str) -> dict:
    """
    Search uploaded documents using Axon's hybrid RAG pipeline.
    """

    db = SessionLocal()

    try:
        return answer_from_documents(
            query=query,
            db=db
        )
    finally:
        db.close()
