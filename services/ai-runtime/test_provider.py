
from unittest.mock import patch

from app.services.llm.provider import generate_response


messages = [
    {
        "role": "user",
        "content": "Explain RAG in one sentence."
    }
]


# Test 1: Groq succeeds
with (
    patch("app.services.llm.provider.groq_generate") as mock_groq,
    patch("app.services.llm.provider.gemini_generate") as mock_gemini
):
    mock_groq.return_value = "Response from Groq"

    result = generate_response(messages)

    print("\nTEST 1: Primary provider succeeds")
    print("Result:", result)
    print("Groq called:", mock_groq.called)
    print("Gemini called:", mock_gemini.called)


# Test 2: Groq fails, Gemini succeeds
with (
    patch("app.services.llm.provider.groq_generate") as mock_groq,
    patch("app.services.llm.provider.gemini_generate") as mock_gemini
):
    mock_groq.side_effect = RuntimeError("Simulated Groq failure")
    mock_gemini.return_value = "Response from Gemini"

    result = generate_response(messages)

    print("\nTEST 2: Primary fails, fallback succeeds")
    print("Result:", result)
    print("Groq called:", mock_groq.called)
    print("Gemini called:", mock_gemini.called)
