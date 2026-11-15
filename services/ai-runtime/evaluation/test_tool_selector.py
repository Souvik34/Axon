
import app.services.agent.tools

from app.services.agent.tool_selector import select_relevant_tools
from app.services.agent.mcp_client import connect_to_remote_mcp_server, discover_mcp_tools
from app.services.agent.mcp_tool_adapter import register_mcp_tools, unregister_mcp_tools


async def main():
    import os

    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    registered_tools = []

    async with connect_to_remote_mcp_server(
        url="https://api.githubcopilot.com/mcp/readonly",
        token=token,
        toolsets="repos,issues,pull_requests",
    ) as client:

        try:
            mcp_tools = await discover_mcp_tools(client)
            registered_tools = register_mcp_tools(client, mcp_tools)

            queries = [
                "Find open issues in Souvik34/Cortex",
                "Summarize recent pull requests in Cortex",
                "Read README.md from Cortex",
                "Find recent commits in Cortex",
            ]

            for query in queries:
                selected = select_relevant_tools(query)

                print(f"\nQUERY: {query}")
                print("SELECTED TOOLS:")
                for tool in selected:
                    print("-", tool["name"])

        finally:
            unregister_mcp_tools(registered_tools)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
