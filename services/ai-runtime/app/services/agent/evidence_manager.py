
import hashlib
import json
import logging
from typing import Any
from urllib.parse import urlparse


logger = logging.getLogger(__name__)

MAX_EVIDENCE_ITEMS = 500
MAX_CONTEXT_ITEMS = 40
MAX_CONTEXT_CHARS = 24000

SOURCE_ID_KEYS = {
    "id",
    "message_id",
    "document_id",
    "chunk_id",
    "commit_sha",
    "sha",
    "issue_id",
    "pull_request_id",
}

SOURCE_URL_KEYS = {
    "url",
    "web_url",
    "html_url",
    "permalink",
    "source_url",
}

TITLE_KEYS = {
    "title",
    "subject",
    "filename",
    "name",
}

CONTENT_KEYS = {
    "content",
    "text",
    "body",
    "description",
    "summary",
    "answer",
    "snippet",
}

CONTAINER_KEYS = {
    "results",
    "emails",
    "documents",
    "chunks",
    "items",
    "commits",
    "issues",
    "pull_requests",
    "messages",
    "data",
    "sources",
    "records",
}


def _safe_string(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, (int, float, bool)):
        return str(value)

    return ""


def _valid_url(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    value = value.strip()

    try:
        parsed = urlparse(value)

        if parsed.scheme not in {"http", "https"}:
            return None

        if not parsed.netloc:
            return None

        return value

    except Exception:
        return None


def _stable_hash(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def _find_value(
    data: dict,
    candidate_keys: set[str],
) -> Any:
    for key in candidate_keys:
        value = data.get(key)

        if value is not None and value != "":
            return value

    return None


def _extract_content(data: dict) -> str:
    parts = []

    for key in CONTENT_KEYS:
        value = data.get(key)

        if isinstance(value, str) and value.strip():
            parts.append(value.strip())

    if not parts:
        return ""

    # Preserve distinct content fields without duplicating text.
    unique_parts = list(dict.fromkeys(parts))

    return "\n\n".join(unique_parts)


def _extract_source_url(data: dict) -> str | None:
    for key in SOURCE_URL_KEYS:
        url = _valid_url(data.get(key))

        if url:
            return url

    return None


def _extract_source_id(data: dict) -> str | None:
    for key in SOURCE_ID_KEYS:
        value = _safe_string(data.get(key))

        if value:
            return value

    return None


def _infer_source_type(
    data: dict,
    parent_type: str | None = None,
) -> str:
    """
    Infer a source category from generic metadata.

    This intentionally contains no provider-specific routing.
    """

    explicit_type = _safe_string(
        data.get("source_type")
        or data.get("type")
        or data.get("category")
    )

    if explicit_type:
        return explicit_type.lower()

    if parent_type:
        return parent_type

    return "external_source"


def _build_evidence_item(
    data: dict,
    source_type: str | None = None,
    step: int | None = None,
) -> dict | None:

    content = _extract_content(data)
    title = _safe_string(
        _find_value(data, TITLE_KEYS)
    )
    source_id = _extract_source_id(data)
    source_url = _extract_source_url(data)

    if not content and not title:
        return None

    resolved_source_type = _infer_source_type(
        data,
        source_type,
    )

    if not source_id and not source_url:
        identity = f"{resolved_source_type}:{title}:{content}"
        source_id = _stable_hash(identity)[:24]

    identity = (
        f"{resolved_source_type}:"
        f"{source_id or source_url}:"
        f"{title}:"
        f"{content}"
    )

    evidence_id = _stable_hash(identity)

    metadata = {
        key: value
        for key, value in data.items()
        if key not in CONTENT_KEYS
        and key not in TITLE_KEYS
        and key not in SOURCE_ID_KEYS
        and key not in SOURCE_URL_KEYS
        and isinstance(value, (str, int, float, bool, type(None)))
    }

    return {
        "evidence_id": evidence_id,
        "source_type": resolved_source_type,
        "source_id": source_id,
        "source_url": source_url,
        "title": title,
        "content": content,
        "step": step,
        "metadata": metadata,
    }


def _walk_output(
    value: Any,
    evidence: list[dict],
    source_type: str | None = None,
    step: int | None = None,
    depth: int = 0,
) -> None:
    """
    Recursively discover evidence in arbitrary tool output.

    Handles nested dictionaries, arrays, and common result envelopes.
    """

    if depth > 10:
        return

    if isinstance(value, list):
        for item in value:
            _walk_output(
                item,
                evidence,
                source_type=source_type,
                step=step,
                depth=depth + 1,
            )
        return

    if not isinstance(value, dict):
        return

    item = _build_evidence_item(
        value,
        source_type=source_type,
        step=step,
    )

    if item:
        evidence.append(item)

    for key, nested in value.items():
        if isinstance(nested, (dict, list)):
            nested_source_type = source_type

            if key.lower() in CONTAINER_KEYS:
                nested_source_type = source_type

            _walk_output(
                nested,
                evidence,
                source_type=nested_source_type,
                step=step,
                depth=depth + 1,
            )


def normalize_execution_evidence(
    execution: dict,
) -> list[dict]:
    """
    Convert completed execution outputs into normalized evidence.

    Works independently of the provider that produced the output.
    """

    if not isinstance(execution, dict):
        return []

    normalized = []

    for result in execution.get("results", []):
        if not isinstance(result, dict):
            continue

        if result.get("status") != "completed":
            continue

        output = result.get("output")

        if output is None:
            continue

        tool_name = result.get("tool")
        step_number = result.get("step")

        _walk_output(
            output,
            normalized,
            source_type=tool_name or "external_source",
            step=step_number,
        )

    return merge_evidence(normalized)


def merge_evidence(
    existing: list[dict] | None,
    incoming: list[dict] | None = None,
) -> list[dict]:
    """
    Merge evidence without duplicating identical findings.

    Existing evidence is preserved and newer metadata is merged.
    """

    merged = {}
    ordered_ids = []

    for item in (existing or []) + (incoming or []):
        if not isinstance(item, dict):
            continue

        evidence_id = item.get("evidence_id")

        if not evidence_id:
            identity = json.dumps(
                item,
                sort_keys=True,
                default=str,
            )
            evidence_id = _stable_hash(identity)

        if evidence_id not in merged:
            merged[evidence_id] = {
                **item,
                "evidence_id": evidence_id,
            }
            ordered_ids.append(evidence_id)
        else:
            current = merged[evidence_id]

            # Preserve existing values while enriching missing fields.
            for key, value in item.items():
                if value is None or value == "":
                    continue

                if key == "metadata":
                    current.setdefault("metadata", {}).update(
                        value if isinstance(value, dict) else {}
                    )
                elif not current.get(key):
                    current[key] = value

    return [
        merged[evidence_id]
        for evidence_id in ordered_ids
    ][-MAX_EVIDENCE_ITEMS:]


def build_shared_context(
    evidence: list[dict],
    max_items: int = MAX_CONTEXT_ITEMS,
    max_chars: int = MAX_CONTEXT_CHARS,
) -> dict:
    """
    Build a compact context that can be passed to any agent.

    Original evidence remains stored separately.
    """

    selected = []
    used_chars = 0

    for item in reversed(evidence or []):
        if not isinstance(item, dict):
            continue

        compact = {
            "evidence_id": item.get("evidence_id"),
            "source_type": item.get("source_type"),
            "source_id": item.get("source_id"),
            "source_url": item.get("source_url"),
            "title": item.get("title"),
            "content": item.get("content", ""),
            "step": item.get("step"),
        }

        serialized = json.dumps(
            compact,
            ensure_ascii=False,
            default=str,
        )

        if used_chars + len(serialized) > max_chars:
            continue

        selected.append(compact)
        used_chars += len(serialized)

        if len(selected) >= max_items:
            break

    selected.reverse()

    return {
        "evidence": selected,
        "evidence_count": len(evidence or []),
        "included_count": len(selected),
        "truncated": len(selected) < len(evidence or []),
    }


def build_evidence_summary(
    evidence: list[dict],
) -> dict:
    """
    Provide source distribution and coverage metadata.
    """

    source_counts = {}

    for item in evidence or []:
        source_type = item.get(
            "source_type",
            "unknown",
        )

        source_counts[source_type] = (
            source_counts.get(source_type, 0) + 1
        )

    return {
        "total_evidence": len(evidence or []),
        "source_counts": source_counts,
        "unique_sources": len({
            (
                item.get("source_type"),
                item.get("source_id"),
                item.get("source_url"),
            )
            for item in evidence or []
        }),
    }


def add_evidence_to_state(
    state: dict,
    execution: dict,
) -> dict:
    """
    Update shared evidence after an execution.

    Returns a partial LangGraph state update.
    """

    new_evidence = normalize_execution_evidence(
        execution
    )

    all_evidence = merge_evidence(
        state.get("evidence", []),
        new_evidence,
    )

    shared_context = build_shared_context(
        all_evidence
    )

    return {
        "evidence": all_evidence,
        "shared_context": shared_context,
        "execution": execution,
    }
