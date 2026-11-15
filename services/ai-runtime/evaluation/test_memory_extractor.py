from app.core.database import SessionLocal
from app.services.memory.memory_extractor import extract_memories
from app.services.memory.memory_service import delete_memory


db = SessionLocal()

try:
    memories = extract_memories(
        user_message=(
            "For Cortex, use Groq as the primary LLM provider "
            "and Gemini as the fallback if Groq is unavailable."
        ),
        assistant_response=(
            "Understood. Both providers should remain available "
            "behind a provider-independent interface."
        ),
        db=db
    )

    print("Extracted memories:", len(memories))

    for memory in memories:
        print(
            memory["memory_type"],
            "-",
            memory["content"]
        )

    # Clean up test memories
    for memory in memories:
        delete_memory(memory["id"], db)

finally:
    db.close()