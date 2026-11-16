
import json
import logging
import re
from urllib.parse import urlparse

from app.services.llm.provider import generate_response

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are Axon, an autonomous agentic AI assistant.

Answer the user's request using only the supplied execution evidence.

SOURCE AND ACCURACY RULES:

1. Never invent facts, dates, repository names, commit details, or URLs.
2. Clearly disclose empty results and failed tool executions.
3. Distinguish verified facts from interpretations.
4. Cite factual claims using only supplied source IDs.
5. Use citations in exactly this format: [S1], [S2].
6. Never construct, modify, or guess source URLs.
7. Use the exact URL supplied by the source record.
8. Never assume a historical repository name is still its current name.
9. If an email mentions Cortex but GitHub returns Axon, preserve that
   distinction and cite the actual GitHub URL returned by the tool.
10. Do not infer a commit's purpose from its email subject alone.
11. Explain a commit's purpose using its commit message and actual
    changes. If evidence is insufficient, explicitly say so.

GITHUB COMMIT ANALYSIS:

When GitHub commit evidence is available, inspect:
- Repository owner and name.
- Commit SHA.
- Commit message.
- Changed file names.
- File statuses.
- Additions, deletions, and total changes.
- Available patches or code changes.

Do not claim that files were changed unless the evidence lists them.
Do not invent file names or statistics.
If patches are unavailable, explain that the analysis is limited
to the available commit metadata.

Be concise, structured, and evidence-grounded.
"""

MAX_EVIDENCE_CHARS = 14000


def _is_valid_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.netloc)
        )
    except Exception:
        return False


def _source_type(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()

    if "mail.google.com" in host:
        return "Gmail message"

    if "github.com" in host and "/commit/" in path:
        return "GitHub commit"

    if "github.com" in host:
        return "GitHub source"

    return "External source"


def _collect_sources(value, sources, seen=None):
    if seen is None:
        seen = set()

    if isinstance(value, dict):

        # Uploaded document chunk references.
        document_id = value.get("document_id")
        chunk_index = value.get("chunk_index")

        if document_id is not None and chunk_index is not None:
            key = (
                "document",
                str(document_id),
                str(chunk_index),
            )

            if key not in seen and len(sources) < 30:
                seen.add(key)

                sources.append({
                    "id": f"S{len(sources) + 1}",
                    "type": "Uploaded document",
                    "document_id": str(document_id),
                    "chunk_index": chunk_index,
                    "filename": value.get("filename"),
                })

        # URLs explicitly returned by source tools.
        for key, item in value.items():

            if (
                key.lower() in {
                    "html_url",
                    "url",
                    "web_url",
                    "permalink",
                }
                and isinstance(item, str)
                and _is_valid_url(item)
            ):
                source_key = ("url", item)

                if source_key not in seen and len(sources) < 30:
                    seen.add(source_key)

                    sources.append({
                        "id": f"S{len(sources) + 1}",
                        "type": _source_type(item),
                        "url": item,
                    })

            _collect_sources(item, sources, seen)

    elif isinstance(value, list):
        for item in value:
            _collect_sources(item, sources, seen)



def _compact_value(
    value,
    depth=0,
    max_string_chars=700,
    max_list_items=20,
    max_dict_items=20,
):
    """Compact execution data while preserving primitive values and important nested structures."""

    # Preserve primitive values even when deeply nested.
    if isinstance(value, str):
        if len(value) > max_string_chars:
            return value[:max_string_chars] + "... [truncated]"
        return value

    if isinstance(value, (int, float, bool)) or value is None:
        return value

    if depth >= 10:
        return "[Maximum nesting depth reached]"

    if isinstance(value, dict):
        priority_keys = [
            "tool",
            "name",
            "status",
            "error",
            "subject",
            "message",
            "commit",
            "commit_message",
            "owner",
            "repo",
            "repository",
            "sha",
            "html_url",
            "url",
            "author",
            "date",
            "stats",
            "files",
            "filename",
            "additions",
            "deletions",
            "changes",
            "total",
            "patch",
            "content",
            "body",
            "text",
            "document_id",
            "chunk_index",
            "sources",
            "output",
        ]

        keys = list(value.keys())

        keys.sort(
            key=lambda key: (
                priority_keys.index(key)
                if key in priority_keys
                else len(priority_keys)
            )
        )

        result = {}

        for key in keys[:max_dict_items]:
            result[key] = _compact_value(
                value[key],
                depth + 1,
                max_string_chars,
                max_list_items,
                max_dict_items,
            )

        if len(value) > max_dict_items:
            result["_omitted_fields"] = len(value) - max_dict_items

        return result

    if isinstance(value, list):
        result = [
            _compact_value(
                item,
                depth + 1,
                max_string_chars,
                max_list_items,
                max_dict_items,
            )
            for item in value[:max_list_items]
        ]

        if len(value) > max_list_items:
            result.append(
                f"[{len(value) - max_list_items} additional items omitted]"
            )

        return result

    return str(value)[:max_string_chars]


def _build_compact_evidence(evidence):
    """Fit evidence within the configured context budget."""

    configurations = [
        (700, 20, 20),
        (500, 15, 18),
        (300, 12, 16),
        (150, 10, 12),
    ]

    for string_limit, list_limit, dict_limit in configurations:

        compacted = _compact_value(
            evidence,
            max_string_chars=string_limit,
            max_list_items=list_limit,
            max_dict_items=dict_limit,
        )

        serialized = json.dumps(
            compacted,
            ensure_ascii=False,
            default=str,
        )

        if len(serialized) <= MAX_EVIDENCE_CHARS:
            return serialized

    raise RuntimeError(
        "Execution evidence is too large even after compaction."
    )


def _resolve_citations(answer: str, sources: list) -> str:

    source_map = {
        source["id"]: source["url"]
        for source in sources
        if source.get("url")
    }

    valid_source_ids = {
        source["id"] for source in sources
    }

    def replace(match):
        source_id = match.group(1)

        if source_id in source_map:
            # Use the exact URL returned by the source.
            return f"[{source_id}]({source_map[source_id]})"

        if source_id in valid_source_ids:
            return f"[{source_id}]"

        # Remove unsupported citations.
        return ""

    return re.sub(
        r"\[(S\d+)\]",
        replace,
        answer,
    )


def synthesize_response(
    user_request: str,
    execution: dict,
) -> str:

    if not user_request or not user_request.strip():
        raise ValueError("User request cannot be empty.")

    if not isinstance(execution, dict):
        raise ValueError(
            "Execution result must be a dictionary."
        )

    sources = []

    _collect_sources(
        execution.get("results", []),
        sources,
    )

    evidence = {
        "goal": execution.get("goal"),
        "results": execution.get("results", []),
        "summary": execution.get("summary", {}),
        "available_sources": sources,
    }

    compact_evidence = _build_compact_evidence(evidence)

    logger.info(
        "Synthesizing response with %s evidence characters "
        "and %s sources.",
        len(compact_evidence),
        len(sources),
    )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": (
                f"USER REQUEST:\n{user_request}\n\n"
                f"EXECUTION EVIDENCE:\n{compact_evidence}\n\n"
                "Analyze the actual evidence before answering.\n"
                "For GitHub commits, report the available commit "
                "message, changed files, statuses, and statistics.\n"
                "Explain the purpose only when supported by the "
                "commit message or code changes.\n"
                "Use the exact source IDs and URLs provided."
            ),
        },
    ]

    try:
        response = generate_response(messages)

        if not response or not response.strip():
            raise RuntimeError(
                "LLM returned an empty response."
            )

        return _resolve_citations(
            response.strip(),
            sources,
        )

    except Exception:
        logger.exception("Response synthesis failed.")
        raise
