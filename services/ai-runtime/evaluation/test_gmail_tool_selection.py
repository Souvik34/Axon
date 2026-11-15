
from app.services.agent.tool_selector import select_relevant_tools

queries = [
    "Find emails from my manager",
    "Search my inbox for interview updates",
    "Read this email message",
    "Find open issues in Souvik34/Cortex",
    "Summarize recent pull requests in Cortex",
]

for query in queries:
    selected = select_relevant_tools(query)

    print(f"\nQUERY: {query}")
    print("SELECTED TOOLS:")
    for tool in selected:
        print(f"- {tool['name']}")
