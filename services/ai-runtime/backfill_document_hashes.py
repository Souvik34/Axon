
import hashlib
from pathlib import Path

from sqlalchemy import select

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import Document


db = SessionLocal()

try:
    documents = db.scalars(
        select(Document).where(Document.content_hash.is_(None))
    ).all()

    for document in documents:
        file_path = Path(settings.DOCUMENT_STORAGE_DIR) / document.storage_key

        if not file_path.exists():
            raise FileNotFoundError(
                f"Missing file for document {document.id}: {file_path}"
            )

        file_bytes = file_path.read_bytes()

        document.content_hash = hashlib.sha256(
            file_bytes
        ).hexdigest()

        print(
            f"Updated: {document.filename} | "
            f"Hash: {document.content_hash}"
        )

    db.commit()

    print(f"\nSuccessfully updated {len(documents)} documents.")

except Exception:
    db.rollback()
    raise

finally:
    db.close()
