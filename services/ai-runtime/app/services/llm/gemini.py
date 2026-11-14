
from google import genai
from google.genai import errors

from app.core.config import settings


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


def generate_response(messages: list[dict[str, str]]) -> str:
    try:
        contents = [
            {
                "role": "model" if message["role"] == "assistant" else "user",
                "parts": [{"text": message["content"]}]
            }
            for message in messages
        ]

        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=contents
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text

    except errors.APIError as exc:
        raise RuntimeError(
            f"Gemini API error ({exc.code}): {exc.message}"
        ) from exc
