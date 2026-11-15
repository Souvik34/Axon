
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from app.models import Memory


def save_memory(
    content: str,
    memory_type: str,
    db: Session
) -> Memory:
    if not content or not content.strip():
        raise ValueError("Memory content cannot be empty.")

    if not memory_type or not memory_type.strip():
        raise ValueError("Memory type cannot be empty.")

    memory = Memory(
        content=content.strip(),
        memory_type=memory_type.strip().lower()
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

    search_query = func.plainto_tsquery("english", query)

    rank = func.ts_rank_cd(
        func.to_tsvector("english", Memory.content),
        search_query
    )

    statement = (
        select(Memory)
        .where(
            func.to_tsvector(
                "english",
                Memory.content
            ).op("@@")(search_query)
        )
        .order_by(rank.desc())
        .limit(limit)
    )

    return list(db.scalars(statement).all())