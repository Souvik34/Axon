from app.services.agent.tool_registry import register_tool
from app.services.agent.tools.calculator import calculate
from app.services.agent.tools.extract_identifiers import extract_github_commits
from app.services.agent.tool_registry import register_tool
from app.services.agent.tools.search_documents import search_documents
from app.services.gmail.gmail_tools import (
    search_emails,
    read_email,
    SEARCH_EMAILS_OUTPUT_SCHEMA,
    READ_EMAIL_OUTPUT_SCHEMA,
)
register_tool(
    name="search_documents",
    description=(
        "Search the user's uploaded documents using query expansion, "
        "vector similarity, keyword search and hybrid ranking. "
        "Use this tool when answering questions requiring information "
        "from uploaded files."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Question or information to search for in uploaded documents."
            }
        },
        "required": ["query"]
    },
    function=search_documents,
    output_schema={
        "type": "object",
        "properties": {
            "answer": {"type": "string"},
            "sources": {
                "type": "array",
                "items": {
                    "type": "object"
                }
            },
            "expanded_queries": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["answer", "sources"]
    }
)
register_tool(
    name="calculator",
    description="Evaluates basic mathematical expressions.",
    input_schema={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to evaluate."
            }
        },
        "required": ["expression"]
    },
    function=calculate
)





register_tool(
    name="search_emails",
    description=(
        "Search the connected Gmail inbox using Gmail search syntax. "
        "Returns matching email metadata and snippets."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Gmail search query, such as from:example@gmail.com or subject:interview",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of emails to return, between 1 and 50.",
            },
        },
        "required": ["query"],
    },
    function=search_emails,
    output_schema=SEARCH_EMAILS_OUTPUT_SCHEMA,
)
EXTRACT_GITHUB_COMMITS_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "count": {
            "type": "integer"
        },
        "commits": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                    "sha": {"type": "string"}
                },
                "required": ["owner", "repo", "sha"]
            }
        }
    },
    "required": ["count", "commits"]
}
register_tool(
    name="extract_github_commits",
    description="Extract GitHub commit URLs, repository names, and commit SHAs from text.",
    input_schema={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Text containing GitHub commit URLs."
            }
        },
        "required": ["text"]
    },
    function=extract_github_commits,
    output_schema=EXTRACT_GITHUB_COMMITS_OUTPUT_SCHEMA
)
register_tool(
    name="read_email",
    description=(
        "Read the full plain-text content and metadata of a Gmail message "
        "using its message ID."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "message_id": {
                "type": "string",
                "description": "Gmail message ID returned by search_emails.",
            },
        },
        "required": ["message_id"],
    },
    function=read_email,
    output_schema=READ_EMAIL_OUTPUT_SCHEMA,
)
