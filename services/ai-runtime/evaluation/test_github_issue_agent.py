
import os
import asyncio

import app.services.agent.tools

from app.services.agent.mcp_client import (
    connect_to_remote_mcp_server,
    discover_mcp_tools,
)
from app.services.agent.mcp_tool_adapter import (
    register_mcp_tools,
    unregister_mcp_tools,
)
from app.services.agent.planner import create_plan
from app.services.agent.executor import execute_plan_async


async def main():
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

    if not token:
        raise RuntimeError("GitHub token is not configured.")

    registered_tools = []

    async with connect_to_remote_mcp_server(
        url="https://api.githubcopilot.com/mcp/readonly",
        token=token,
        toolsets="repos,issues,pull_requests",
    ) as client:
        try:
            mcp_tools = await discover_mcp_tools(client)
            registered_tools = register_mcp_tools(client, mcp_tools)

            request = "Find open issues in Souvik34/Cortex"

            plan = create_plan(request)

            print("\nGENERATED PLAN:")
            for step in plan:
                print(step)

            execution = await execute_plan_async(plan)

            print("\nEXECUTION RESULT:")
            print(execution)

        finally:
            unregister_mcp_tools(registered_tools)


if __name__ == "__main__":
    asyncio.run(main())
