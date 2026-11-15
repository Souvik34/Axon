import json

from app.services.llm.provider import generate_response
from app.services.memory.memory_service import save_memory


def extract_memories(
    user_message: str,
    assistant_response: str,
    db
) -> list[dict]:

    prompt = f"""
You are Cortex's memory extraction component.

Extract useful, long-term information from this conversation.

Store only:
- Explicit user preferences
- Important user facts
- Long-term goals
- Ongoing project decisions
- Instructions that should influence future conversations

Do not store:
- Temporary questions
- Generic knowledge
- Assistant-generated assumptions
- Sensitive personal information

Return ONLY valid JSON in this format:
{{
    "memories": [
        {{
            "content": "A concise fact",
            "memory_type": "preference"
        }}
    ]
}}

If nothing is worth remembering, return:
{{"memories": []}}

USER MESSAGE:
{user_message}

ASSISTANT RESPONSE:
{assistant_response}
"""

    response = generate_response([
        {
            "role": "user",
            "content": prompt
        }
    ])

    try:
        data = json.loads(response)
    except (json.JSONDecodeError, TypeError):
        return []

    extracted = []

    for item in data.get("memories", []):
        content = item.get("content")
        memory_type = item.get("memory_type")

        if not isinstance(content, str) or not content.strip():
            continue

        if memory_type not in {
            "preference",
            "fact",
            "goal",
            "project_fact",
            "instruction"
        }:
            continue

        memory = save_memory(
            content=content,
            memory_type=memory_type,
            db=db
        )

        extracted.append({
            "id": str(memory.id),
            "content": memory.content,
            "memory_type": memory.memory_type
        })

    return extracted