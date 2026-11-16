
from app.core.database import SessionLocal
from app.models import Memory
from app.services.memory.embedding_service import generate_embedding


def backfill_memories():
    db = SessionLocal()

    try:
        memories = (
            db.query(Memory)
            .filter(Memory.embedding.is_(None))
            .all()
        )

        print(f"Found {len(memories)} memories without embeddings.")

        for memory in memories:
            memory.embedding = generate_embedding(memory.content)
            print(f"Embedded: {memory.id}")

        db.commit()
        print("Memory embedding backfill completed.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    backfill_memories()
