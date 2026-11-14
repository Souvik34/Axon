import hashlib
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import (
    AskRequest,
    AskResponse,
    AskSource,
    DocumentSearchRequest,
    DocumentSearchResponse,
    RetrievedChunk,
)
from app.core.config import settings
from app.core.database import get_db
from app.models import Document
from app.services.document.ingestion import ingest_document
from app.services.document.rag import answer_from_documents
from app.services.document.retriever import retrieve_similar_chunks

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB



@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, TXT and DOCX files are supported."
        )

    storage_dir = Path(settings.DOCUMENT_STORAGE_DIR)
    storage_dir.mkdir(parents=True, exist_ok=True)

    generated_filename = f"{uuid.uuid4()}{extension}"
    file_path = storage_dir / generated_filename

    file_size = 0

    try:
        # 1. Save uploaded file with size validation
        with file_path.open("wb") as destination:
            while True:
                content = await file.read(1024 * 1024)

                if not content:
                    break

                file_size += len(content)

                if file_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File size exceeds the 10 MB limit."
                    )

                destination.write(content)

        if file_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        # 2. Calculate SHA-256 content hash
        content_hash = hashlib.sha256(
            file_path.read_bytes()
        ).hexdigest()

 
        # 3. Check for duplicate documents
        existing_documents = db.scalars(
            select(Document).where(
                Document.content_hash == content_hash
            )
        ).all()

        # Prefer a failed document if one exists
        failed_document = next(
            (
                doc for doc in existing_documents
                if doc.status == "failed"
            ),
            None
        )

        if failed_document:
            existing_file_path = (
                storage_dir / failed_document.storage_key
            )

            shutil.copy2(file_path, existing_file_path)
            file_path.unlink(missing_ok=True)

            failed_document.status = "uploaded"
            db.commit()

            chunk_count = ingest_document(failed_document, db)

            return {
                "document_id": str(failed_document.id),
                "filename": failed_document.filename,
                "status": failed_document.status,
                "chunks_created": chunk_count,
                "retried": True
            }

        if existing_documents:
            existing_document = existing_documents[0]

            raise HTTPException(
                status_code=409,
                detail={
                    "message": "This document has already been uploaded or is being processed.",
                    "existing_document_id": str(existing_document.id),
                    "filename": existing_document.filename,
                    "status": existing_document.status
                }
            )


        # 4. Create document record
        document = Document(
            filename=file.filename,
            file_type=extension.lstrip("."),
            file_size=file_size,
            storage_key=generated_filename,
            content_hash=content_hash,
            status="uploaded"
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        # 5. Extract, chunk and generate embeddings
        chunk_count = ingest_document(document, db)

        return {
            "document_id": str(document.id),
            "filename": document.filename,
            "status": document.status,
            "chunks_created": chunk_count
        }

    except HTTPException:
        file_path.unlink(missing_ok=True)
        raise

    except Exception as exc:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail=f"Document ingestion failed: {str(exc)}"
        ) from exc

    finally:
        await file.close()

@router.post("/search", response_model=DocumentSearchResponse)
def search_documents(
    request: DocumentSearchRequest,
    db: Session = Depends(get_db)
):
    results = retrieve_similar_chunks(
        query=request.query,
        db=db,
        top_k=request.top_k
    )

    return DocumentSearchResponse(
        query=request.query,
        results=[
            RetrievedChunk(**result)
            for result in results
        ],
        total_results=len(results)
    )



@router.post("/ask", response_model=AskResponse)
def ask_documents(
    request: AskRequest,
    db: Session = Depends(get_db)
):
    result = answer_from_documents(
        query=request.query,
        db=db,
        top_k=request.top_k
    )

    return AskResponse(
        answer=result["answer"],
        sources=[
            AskSource(**source)
            for source in result["sources"]
        ]
    )
