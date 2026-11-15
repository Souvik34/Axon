
import json
import logging
import re
from urllib.parse import urlparse

from app.services.llm.provider import generate_response

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are Cortex, an agentic AI assistant.

Answer the user's request using only the supplied execution evidence.

Rules:
1. Never invent facts, dates, repository data, or URLs.
2. Clearly disclose empty results and failed tool executions.
3. Distinguish verified facts from interpretations.
4. Cite factual claims using only the supplied source IDs.
5. Use citations in exactly this format: [S1], [S2].
6. Never generate URLs or Markdown links yourself.
7. Be concise and clear.
"""


def _is_valid_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def _collect_sources(value, sources):
    if isinstance(value, dict):
        for key, item in value.items():
            if (
                key.lower() in {"html_url", "url", "web_url", "permalink"}
                and isinstance(item, str)
                and _is_valid_url(item)
                and item not in [s["url"] for s in sources]
            ):
                sources.append({
                    "id": f"S{len(sources) + 1}",
                    "url": item
                })

            _collect_sources(item, sources)

    elif isinstance(value, list):
        for item in value:
            _collect_sources(item, sources)


def _resolve_citations(answer: str, sources: list) -> str:
    source_map = {source["id"]: source["url"] for source in sources}

    def replace(match):
        source_id = match.group(1)

        if source_id not in source_map:
            return ""

        return f"[{source_id}]({source_map[source_id]})"

    return re.sub(r"\[(S\d+)\]", replace, answer)


def synthesize_response(user_request: str, execution: dict) -> str:
    if not user_request or not user_request.strip():
        raise ValueError("User request cannot be empty.")

    if not isinstance(execution, dict):
        raise ValueError("Execution result must be a dictionary.")

    sources = []
    _collect_sources(execution.get("results", []), sources)

    evidence = {
        "goal": execution.get("goal"),
        "results": execution.get("results", []),
        "summary": execution.get("summary", {}),
        "available_sources": sources,
    }

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"USER REQUEST:\n{user_request}\n\n"
                f"EXECUTION EVIDENCE:\n"
                f"{json.dumps(evidence, ensure_ascii=False, default=str)}\n\n"
                "Answer using the evidence. Cite relevant facts with source IDs."
            ),
        },
    ]

    try:
        response = generate_response(messages)

        if not response or not response.strip():
            raise RuntimeError("LLM returned an empty response.")

        return _resolve_citations(response.strip(), sources)

    except Exception:
        logger.exception("Response synthesis failed.")
        raise
