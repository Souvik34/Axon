
from openai import OpenAI

from app.core.config import settings


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY,
)


def generate_response(messages: list[dict[str, str]]) -> str:
    try:
        response = client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=2048,
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError("OpenRouter returned an empty response.")

        return content

    except Exception as exc:
        raise RuntimeError(f"OpenRouter API error: {exc}") from exc
