
import re

import app.services.agent.tools
from app.services.agent.tool_registry import list_tools


INTENTS = {
    "issues": {
        "keywords": {
            "issue", "issues", "bug", "bugs", "ticket", "tickets"
        },
        "tools": {"list_issues", "search_issues"},
    },
    "pull_requests": {
        "keywords": {
            "pr", "prs", "pull", "pull_request", "pull_requests"
        },
        "tools": {
            "list_pull_requests",
            "search_pull_requests",
            "pull_request_read",
        },
    },
    "files": {
        "keywords": {
            "file", "files", "readme", "content", "contents"
        },
        "tools": {"get_file_contents"},
    },
    "document_search": {
        "keywords": {
            "document", "documents", "uploaded", "upload",
            "uploads", "ingestion", "chunk", "chunks",
            "embedding", "embeddings", "pdf", "knowledge",
            "knowledge_base",
        },
        "tools": {"search_documents"},
    },
    "commits": {
        "keywords": {"commit", "commits", "history"},
        "tools": {"list_commits", "search_commits", "get_commit"},
    },
    "gmail": {
        "keywords": {
            "email", "emails", "gmail", "inbox", "mail",
            "message", "messages", "thread", "threads",
            "sender", "subject",
        },
        "tools": {"search_emails", "read_email"},
    },
    "commit_extraction": {
        "keywords": {
            "extract", "sha", "identifier", "commit_url",
            "commit_link", "commit_sha", "hash",
        },
        "tools": {"extract_github_commits"},
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
    max_tools: int = 15,
) -> list[dict]:

    if not user_request or not user_request.strip():
        raise ValueError("User request cannot be empty.")

    available_tools = list_tools()

    query_terms = tokenize(user_request) - STOPWORDS
    selected_names = set()
    matched_intents = set()

    for intent_name, intent in INTENTS.items():
        if query_terms.intersection(intent["keywords"]):
            matched_intents.add(intent_name)
            selected_names.update(intent["tools"])

    # Cross-source handoff:
    # Gmail may contain a GitHub commit URL or SHA.
    # Make identifier extraction available automatically.
    if "gmail" in matched_intents and "commits" in matched_intents:
        selected_names.add("extract_github_commits")

    def matches_selected_tool(tool: dict) -> bool:
        tool_name = tool["name"]
        base_name = tool_name.split("__")[-1]

        return (
            tool_name in selected_names
            or base_name in selected_names
        )

    if selected_names:
        selected = [
            tool for tool in available_tools
            if matches_selected_tool(tool)
        ]
    else:
        selected = []

        for tool in available_tools:
            searchable_text = (
                f'{tool["name"]} {tool.get("description", "")}'
            )

            tool_terms = tokenize(searchable_text) - STOPWORDS
            score = len(query_terms.intersection(tool_terms))

            if score > 0:
                selected.append((score, tool))

        selected.sort(key=lambda item: item[0], reverse=True)
        selected = [tool for _, tool in selected]

    return selected[:max_tools]
