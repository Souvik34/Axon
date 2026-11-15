
import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

from app.services.agent.mcp_client import discover_mcp_tools
from app.services.agent.mcp_tool_adapter import (
    register_mcp_tools,
    unregister_mcp_tools,
)
from app.services.agent.planner import create_plan
from app.services.agent.executor import execute_plan_async
from app.services.agent.tool_registry import get_tool


async def main():
    server_path = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "services"
        / "agent"
        / "mcp_test_server.py"
    )

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],
    )

    async with Client(server_params) as client:

        # 1. Discover tools exposed by the MCP server
        tools = await discover_mcp_tools(client)

        print("\nDISCOVERED TOOLS:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")

        # 2. Register MCP tools temporarily
        registered = register_mcp_tools(client, tools)

        try:
            print("\nREGISTERED TOOLS:", registered)

            # 3. Ask the planner to use the MCP multiply tool
            plan = create_plan(
                user_request=(
                    "Use the multiply tool to calculate 12 times 8. "
                    "Do not calculate mentally."
                )
            )

            print("\nGENERATED PLAN:")
            print(plan)

            # 4. Execute the plan while the MCP connection is alive
            execution = await execute_plan_async(plan)

            print("\nEXECUTION RESULT:")
            print(execution)

            # 5. Verify execution
            assert execution["summary"]["failed"] == 0
            assert execution["summary"]["completed"] == 1
            assert "96" in str(execution["results"])

            print("\nMCP AGENT EXECUTION SUCCESSFUL!")

        finally:
            # 6. Remove temporary MCP tools
            unregister_mcp_tools(registered)

            print("\nMCP TOOLS CLEANED UP:", registered)

            # 7. Verify tools were removed from the registry
            for tool_name in registered:
                assert get_tool(tool_name) is None

            print("REGISTRY CLEANUP VERIFIED!")


if __name__ == "__main__":
    asyncio.run(main())
