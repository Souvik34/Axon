
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Document, DocumentChunk
from app.services.document.extractor import extract_text
from app.services.document.chunker import chunk_text
from app.services.llm.embeddings import generate_embedding


def ingest_document(
    document: Document,
    db: Session
) -> int:
    try:
        # 1. Remove previously generated chunks
        db.execute(
            delete(DocumentChunk).where(
                DocumentChunk.document_id == document.id
            )
        )

        # 2. Extract text from the original file
        file_path = Path(settings.DOCUMENT_STORAGE_DIR) / document.storage_key
        text = extract_text(str(file_path))

        # 3. Split extracted text into chunks
        chunks = chunk_text(text)

        # 4. Generate embeddings and prepare database records
        chunk_records = []

        for index, content in enumerate(chunks):
            embedding = generate_embedding(content)

            chunk_records.append(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=content,
                    embedding=embedding,
                    chunk_metadata={}
                )
            )

        # 5. Save chunks and update document status
        db.add_all(chunk_records)
        document.status = "completed"

        db.commit()

        return len(chunk_records)

    except Exception:
        db.rollback()
        document.status = "failed"
        db.commit()
        raise
