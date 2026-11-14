
import logging

from app.core.config import settings
from app.services.llm.groq import generate_response as groq_generate
from app.services.llm.gemini import generate_response as gemini_generate


logger = logging.getLogger(__name__)


def generate_response(messages: list[dict[str, str]]) -> str:
    providers = {
        "groq": groq_generate,
        "gemini": gemini_generate
    }

    primary_name = settings.PRIMARY_LLM_PROVIDER.lower()

    if primary_name not in providers:
        raise ValueError(
            f"Unsupported primary LLM provider: {primary_name}"
        )

    fallback_name = "gemini" if primary_name == "groq" else "groq"

    primary = providers[primary_name]
    fallback = providers[fallback_name]

    try:
        return primary(messages)

    except Exception as primary_error:
        logger.warning(
            "%s failed. Trying %s. Error: %s",
            primary_name,
            fallback_name,
            primary_error
        )

        try:
            return fallback(messages)

        except Exception as fallback_error:
            raise RuntimeError(
                f"Both LLM providers failed. "
                f"{primary_name}: {primary_error}. "
                f"{fallback_name}: {fallback_error}."
            ) from fallback_error
