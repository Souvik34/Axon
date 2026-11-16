
import json

from app.services.llm.provider import generate_response


def expand_query(query: str, max_queries: int = 3) -> list[str]:
    """
    Generate alternative search queries while preserving
    the original query.
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if max_queries <= 0:
        raise ValueError("max_queries must be positive.")

    original_query = query.strip()

    prompt = f"""
You are a query expansion component in an Agentic RAG system.

Generate up to {max_queries} alternative search queries
that improve retrieval of information relevant to the user's question.

Guidelines:
- Preserve the original intent.
- Use different relevant keywords and phrasing.
- Include important entities and technical terms.
- Do not answer the question.
- Avoid unrelated or overly broad queries.
- Return only valid JSON.

Required format:
{{
    "queries": [
        "alternative search query 1",
        "alternative search query 2"
    ]
}}

USER QUESTION:
{original_query}
"""

    try:
        response = generate_response([
            {
                "role": "user",
                "content": prompt
            }
        ])

        data = json.loads(response)

        if not isinstance(data, dict):
            return [original_query]

        expanded_queries = data.get("queries", [])

        if not isinstance(expanded_queries, list):
            return [original_query]

        results = [original_query]
        seen = {original_query.lower()}

        for item in expanded_queries:
            if not isinstance(item, str):
                continue

            item = item.strip()

            if not item:
                continue

            normalized = item.lower()

            if normalized in seen:
                continue

            seen.add(normalized)
            results.append(item)

            if len(results) >= max_queries + 1:
                break

        return results

    except (json.JSONDecodeError, TypeError, ValueError):
        return [original_query]
    except Exception:
        return [original_query]
