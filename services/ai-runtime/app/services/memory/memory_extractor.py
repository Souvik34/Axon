
import json
import logging
import re

from app.services.llm.provider import generate_response
from app.services.memory.memory_service import save_memory

logger = logging.getLogger(__name__)


def extract_memories(
    user_message: str,
    assistant_response: str,
    db
) -> list[dict]:

    prompt = f"""
You are Cortex's memory extraction component.

Extract useful, long-term information explicitly stated by the user.

Store:
- Explicit user preferences
- Important user facts
- Long-term goals
- Ongoing project decisions
- Instructions for future conversations

Do not store:
- Temporary questions
- Generic knowledge
- Assistant-generated assumptions
- Sensitive personal information

Return ONLY JSON:
{{
    "memories": [
        {{
            "content": "A concise fact",
            "memory_type": "preference"
        }}
    ]
}}

Allowed types: preference, fact, goal, project_fact, instruction.

If nothing is worth remembering, return:
{{"memories": []}}

USER MESSAGE:
{user_message}

ASSISTANT RESPONSE:
{assistant_response}
"""

    response = generate_response([
        {"role": "user", "content": prompt}
    ])

    try:
        cleaned = response.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

        data = json.loads(cleaned)

        if not isinstance(data, dict):
            return []

        items = data.get("memories", [])

        if not isinstance(items, list):
            return []

    except (json.JSONDecodeError, TypeError, AttributeError):
        logger.exception("Memory extraction returned invalid JSON.")
        logger.error("Raw extraction response: %s", response)
        return []

    extracted = []

    for item in items:
        if not isinstance(item, dict):
            continue

        content = item.get("content")
        memory_type = item.get("memory_type")

        if not isinstance(content, str) or not content.strip():
            continue

        if memory_type not in {
            "preference", "fact", "goal",
            "project_fact", "instruction"
        }:
            continue

        try:
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

        except Exception:
            logger.exception("Failed to save extracted memory.")
            db.rollback()

    return extracted
