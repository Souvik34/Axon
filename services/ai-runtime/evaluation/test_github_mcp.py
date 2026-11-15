
import asyncio
import os
import traceback

from mcp.shared.exceptions import MCPError

from app.services.agent.mcp_client import (
    connect_to_remote_mcp_server,
    discover_mcp_tools,
)


async def main():
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

    if not token:
        raise RuntimeError(
            "GITHUB_PERSONAL_ACCESS_TOKEN is not configured."
        )

    url = "https://api.githubcopilot.com/mcp/readonly/"

    try:
        async with connect_to_remote_mcp_server(
            url=url,
            token=token,
            toolsets="repos,issues,pull_requests",
        ) as client:

            print("\nCONNECTED TO GITHUB MCP")

            tools = await discover_mcp_tools(client)

            print("\nDISCOVERED GITHUB TOOLS:")

            for tool in tools:
                print(f"\nName: {tool.name}")
                print(f"Description: {tool.description}")
                print(f"Input schema: {tool.input_schema}")

            assert tools, "No GitHub tools discovered."

            print("\nGITHUB MCP CONNECTION SUCCESSFUL!")

    except BaseExceptionGroup as group:
        print("\nMCP CONNECTION FAILED")

        def inspect_exception(exc):
            print(f"\nException: {type(exc).__name__}")
            print(f"Details: {exc}")

            if isinstance(exc, MCPError):
                print(f"Error code: {exc.code}")
                print(f"Error data: {exc.data}")

            if isinstance(exc, BaseExceptionGroup):
                for nested in exc.exceptions:
                    inspect_exception(nested)

        inspect_exception(group)

    except Exception as exc:
        print("\nMCP CONNECTION FAILED")
        traceback.print_exc()

        if isinstance(exc, MCPError):
            print("Error code:", exc.code)
            print("Error data:", exc.data)


if __name__ == "__main__":
    asyncio.run(main())
