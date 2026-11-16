
from sqlalchemy.orm import Session
from sqlalchemy import func, select

from app.models import Memory
from app.services.memory.embedding_service import generate_embedding



def save_memory(content: str, memory_type: str, db: Session) -> Memory:
    if not content or not content.strip():
        raise ValueError("Memory content cannot be empty.")

    if not memory_type or not memory_type.strip():
        raise ValueError("Memory type cannot be empty.")

    clean_content = content.strip()
    clean_type = memory_type.strip().lower()

    # Avoid saving an exact duplicate.
    existing = db.scalar(
        select(Memory).where(
            func.lower(func.trim(Memory.content)) == clean_content.lower()
        ).limit(1)
    )

    if existing:
        return existing

    embedding = generate_embedding(clean_content)

    memory = Memory(
        content=clean_content,
        memory_type=clean_type,
        embedding=embedding
    )

    db.add(memory)
    db.commit()
    db.refresh(memory)

    return memory




def get_memories(
    db: Session,
    memory_type: str | None = None,
    limit: int = 20
) -> list[Memory]:
    if limit <= 0:
        raise ValueError("Limit must be positive.")

    statement = select(Memory)

    if memory_type:
        statement = statement.where(
            Memory.memory_type == memory_type.lower()
        )

    statement = (
        statement
        .order_by(Memory.updated_at.desc())
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def delete_memory(
    memory_id,
    db: Session
) -> bool:
    memory = db.get(Memory, memory_id)

    if memory is None:
        return False

    db.delete(memory)
    db.commit()

    return True



# Add this function below the existing functions.

def search_memories(
    query: str,
    db: Session,
    limit: int = 5
) -> list[Memory]:
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if limit <= 0:
        raise ValueError("Limit must be positive.")

    query_embedding = generate_embedding(query)

    statement = (
        select(Memory)
        .where(Memory.embedding.is_not(None))
        .order_by(
            Memory.embedding.cosine_distance(query_embedding)
        )
        .limit(limit)
    )

    return list(db.scalars(statement).all())
