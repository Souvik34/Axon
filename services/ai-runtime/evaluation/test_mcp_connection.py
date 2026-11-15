import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters


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
        args=[str(server_path)]
    )

    async with Client(server_params) as client:

        # Discover tools exposed by the MCP server
        tools = await client.list_tools()

        print("\nDISCOVERED MCP TOOLS:")
        for tool in tools.tools:
            print(f"{tool.name}: {tool.description}")

        # Execute multiply
        result = await client.call_tool(
            "multiply",
            {"a": 12, "b": 8}
        )

        print("\nMULTIPLY RESULT:")
        print(result.content)

        assert not result.is_error
        assert "96" in str(result.content)

        # Execute project status
        result = await client.call_tool(
            "get_project_status",
            {"project_name": "Cortex"}
        )

        print("\nPROJECT STATUS RESULT:")
        print(result.content)

        assert not result.is_error

        print("\nMCP CONNECTION TEST SUCCESSFUL!")


if __name__ == "__main__":
    asyncio.run(main())