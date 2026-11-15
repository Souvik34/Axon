from contextlib import asynccontextmanager

from mcp import Client, StdioServerParameters


@asynccontextmanager
async def connect_to_mcp_server(
    command: str,
    args: list[str]
):
    """
    Establish a connection to an MCP server over stdio.
    """

    server_params = StdioServerParameters(
        command=command,
        args=args
    )

    async with Client(server_params) as client:
        yield client


async def discover_mcp_tools(client):
    """
    Discover tools exposed by the connected MCP server.
    """

    result = await client.list_tools()

    return result.tools

async def execute_mcp_tool(client, tool_name: str, arguments: dict):
    result = await client.call_tool(tool_name, arguments)

    if result.is_error:
        raise RuntimeError(f"MCP tool execution failed: {tool_name}")

    if result.structured_content:
        return result.structured_content

    return "\n".join(
        item.text
        for item in result.content
        if hasattr(item, "text")
    )