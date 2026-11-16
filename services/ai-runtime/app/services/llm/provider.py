
import logging

from app.core.config import settings
from app.services.llm.groq import generate_response as groq_generate
from app.services.llm.gemini import generate_response as gemini_generate
from app.services.llm.openrouter import generate_response as openrouter_generate


logger = logging.getLogger(__name__)


def generate_response(messages: list[dict[str, str]]) -> str:
    providers = {
        "groq": groq_generate,
        "gemini": gemini_generate,
        "openrouter": openrouter_generate,
    }

    primary_name = settings.PRIMARY_LLM_PROVIDER.lower()

    if primary_name not in providers:
        raise ValueError(
            f"Unsupported primary LLM provider: {primary_name}"
        )

    fallback_order = [
        name for name in ("openrouter", "gemini", "groq")
        if name != primary_name
    ]

    errors = []

    for provider_name in [primary_name, *fallback_order]:
        try:
            logger.info("Attempting LLM provider: %s", provider_name)
            return providers[provider_name](messages)

        except Exception as error:
            errors.append(f"{provider_name}: {error}")

            logger.warning(
                "%s failed. Error: %s",
                provider_name,
                error
            )

    raise RuntimeError(
        "All LLM providers failed. " + " | ".join(errors)
    )
