
from app.core.database import SessionLocal
from app.services.memory.memory_service import search_memories

db = SessionLocal()

try:
    query = "Which AI model provider should Axon use, and which providers should be used if it fails?"

    results = search_memories(
        query=query,
        db=db,
        limit=5
    )

    print("\n--- SEMANTIC MEMORY SEARCH ---")

    for memory in results:
        print(f"\nType: {memory.memory_type}")
        print(f"Content: {memory.content}")

finally:
    db.close()
