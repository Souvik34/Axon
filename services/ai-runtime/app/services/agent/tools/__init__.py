from app.services.agent.tool_registry import register_tool
from app.services.agent.tools.calculator import calculate
from app.services.agent.tools.extract_identifiers import extract_github_commits
from app.services.agent.tool_registry import register_tool
from app.services.gmail.gmail_tools import search_emails, read_email
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
)

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
    function=extract_github_commits
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
)
