from app.core.database import SessionLocal
from app.services.memory.memory_service import (
    save_memory,
    get_memories,
    delete_memory
)


db = SessionLocal()

try:
    # 1. Save a test memory
    memory = save_memory(
        content="Cortex uses Groq as its primary LLM provider.",
        memory_type="project_fact",
        db=db
    )

    print("Saved:", memory.id, memory.content)

    # 2. Retrieve memories
    memories = get_memories(db=db)

    print("\nRetrieved memories:")

    for item in memories:
        print(item.memory_type, "-", item.content)

    # 3. Delete the test memory
    deleted = delete_memory(
        memory_id=memory.id,
        db=db
    )

    print("\nDeleted:", deleted)

finally:
    db.close()