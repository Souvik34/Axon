
import asyncio
import os

from app.services.agent.planner import create_plan
from app.services.agent.executor import execute_plan_async
from app.services.agent.mcp_client import (
    connect_to_remote_mcp_server,
    discover_mcp_tools,
)
from app.services.agent.mcp_tool_adapter import (
    register_mcp_tools,
    unregister_mcp_tools,
)


async def main():
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

    if not token:
        raise RuntimeError("GitHub PAT is not configured.")

    registered_tools = []

    async with connect_to_remote_mcp_server(
        url="https://api.githubcopilot.com/mcp/readonly",
        token=token,
        toolsets="repos,issues,pull_requests",
    ) as client:

        try:
            # 1. Discover GitHub MCP tools
            mcp_tools = await discover_mcp_tools(client)

            print("\nDISCOVERED GITHUB TOOLS:")
            for tool in mcp_tools:
                print(f"- {tool.name}: {tool.description}")

            # 2. Register tools
            registered_tools = register_mcp_tools(client, mcp_tools)

            print("\nREGISTERED TOOLS:")
            print(registered_tools)

            # 3. Generate an agent plan
            user_request = (
            "Find the 5 most recent commits "
            "in the Souvik34/Cortex GitHub repository."
)

            plan = create_plan(
                user_request,
                memories=None,
            )

            print("\nGENERATED PLAN:")
            print(plan)

            # 4. Execute the plan
            execution = await execute_plan_async(plan)

            print("\nAGENT EXECUTION:")
            print(execution)

            # 5. Validate execution
            summary = execution.get("summary", {})

            if summary.get("failed", 0) > 0:
                raise RuntimeError("GitHub agent execution failed.")

            if summary.get("completed", 0) == 0:
                raise RuntimeError("No GitHub tools were executed.")

        finally:
            # 6. Clean up registered tools
            unregister_mcp_tools(registered_tools)

    print("\nGITHUB PULL REQUEST AGENT TEST PASSED.")


if __name__ == "__main__":
    asyncio.run(main())
