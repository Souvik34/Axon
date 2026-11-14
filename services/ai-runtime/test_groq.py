
from app.services.llm.groq import generate_response

messages = [
    {
        "role": "user",
        "content": "Explain what Retrieval Augmented Generation is in two sentences."
    }
]

try:
    response = generate_response(messages)
    print("Groq response:")
    print(response)

except RuntimeError as exc:
    print("Groq test failed:")
    print(exc)
