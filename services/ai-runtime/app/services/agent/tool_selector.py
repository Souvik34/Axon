
import re

from app.services.agent.tool_registry import list_tools


INTENTS = {
    "issues": {
        "keywords": {"issue", "issues", "bug", "bugs", "ticket", "tickets"},
        "tools": {"list_issues", "search_issues"},
    },
    "pull_requests": {
        "keywords": {"pr", "prs", "pull", "pull_request", "pull_requests"},
        "tools": {"list_pull_requests", "search_pull_requests", "pull_request_read"},
    },
    "files": {
        "keywords": {"file", "files", "readme", "content", "contents", "document"},
        "tools": {"get_file_contents"},
    },
    "commits": {
        "keywords": {"commit", "commits", "history"},
        "tools": {"list_commits", "search_commits", "get_commit"},
    },
}


STOPWORDS = {
    "find", "get", "show", "list", "read", "fetch",
    "in", "on", "at", "for", "from", "the", "a", "an",
    "of", "and", "to", "me", "my", "please",
    "recent", "latest", "open", "closed", "all",
    "summarize", "summary", "explain", "review",
}


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9_]+", text.lower()))


def select_relevant_tools(
    user_request: str,
    max_tools: int = 5,
) -> list[dict]:
    if not user_request or not user_request.strip():
        raise ValueError("User request cannot be empty.")

    query_terms = tokenize(user_request) - STOPWORDS
    selected_names = set()

    for intent in INTENTS.values():
        if query_terms.intersection(intent["keywords"]):
            selected_names.update(intent["tools"])

    available_tools = list_tools()

    if selected_names:
        return [
            tool for tool in available_tools
            if tool["name"] in selected_names
        ][:max_tools]

    # Fallback for requests outside the known categories.
    scored_tools = []

    for tool in available_tools:
        searchable_text = f'{tool["name"]} {tool["description"]}'
        tool_terms = tokenize(searchable_text) - STOPWORDS

        score = len(query_terms.intersection(tool_terms))

        if score > 0:
            scored_tools.append((score, tool))

    scored_tools.sort(key=lambda item: item[0], reverse=True)

    return [tool for _, tool in scored_tools[:max_tools]]
