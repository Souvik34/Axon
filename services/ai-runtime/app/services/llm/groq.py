
from groq import Groq

from app.core.config import settings


client = Groq(
    api_key=settings.GROQ_API_KEY
)


def generate_response(messages: list[dict[str, str]]) -> str:
    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=0.3,
            max_completion_tokens=2048
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError("Groq returned an empty response.")

        return content

    except Exception as exc:
        raise RuntimeError(f"Groq API error: {exc}") from exc
