
from unittest.mock import patch

from app.services.llm.provider import generate_response

with patch(
    "app.services.llm.provider.groq_generate",
    side_effect=RuntimeError("Simulated Groq quota exhaustion")
):
    response = generate_response([
        {
            "role": "user",
            "content": "Reply with exactly: AXON FALLBACK SUCCESS"
        }
    ])

    print("Final response:", response)
