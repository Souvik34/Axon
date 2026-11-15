
from contextlib import asynccontextmanager

import httpx2
from mcp import Client, StdioServerParameters
from mcp.client.streamable_http import streamable_http_client


@asynccontextmanager
async def connect_to_mcp_server(
    command: str,
    args: list[str],
):
    """
    Connect to an MCP server over stdio.
    """

    server_params = StdioServerParameters(
        command=command,
        args=args,
    )

    async with Client(server_params) as client:
        yield client


@asynccontextmanager
async def connect_to_remote_mcp_server(
    url: str,
    token: str,
    toolsets: str = "repos,issues,pull_requests",
):
    """
    Connect to a remote MCP server over Streamable HTTP.
    """

    headers = {
        "Authorization": f"Bearer {token}",
        "X-MCP-Toolsets": toolsets,
    }

    async with httpx2.AsyncClient(
        headers=headers,
        timeout=httpx2.Timeout(30.0, read=300.0),
    ) as http_client:

        transport = streamable_http_client(
            url,
            http_client=http_client,
        )

        async with Client(transport) as client:
            yield client


async def discover_mcp_tools(client):
    """
    Discover tools exposed by the connected MCP server.
    """

    result = await client.list_tools()
    return result.tools


async def execute_mcp_tool(
    client,
    tool_name: str,
    arguments: dict,
):
    """
    Execute a tool on the connected MCP server.
    """

    result = await client.call_tool(
        tool_name,
        arguments,
    )

    if result.is_error:
        raise RuntimeError(
            f"MCP tool execution failed: {tool_name}"
        )

    if result.structured_content:
        return result.structured_content

    return "\n".join(
        item.text
        for item in result.content
        if hasattr(item, "text")
    )
