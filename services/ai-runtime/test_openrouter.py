
from app.services.llm.openrouter import generate_response

response = generate_response([
    {
        "role": "user",
        "content": "Reply with exactly: AXON OPENROUTER TEST SUCCESS"
    }
])

print(response)
