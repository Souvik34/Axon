
from app.services.agent.tool_registry import register_tool, unregister_tool


def unregister_mcp_tools(tool_names: list[str]):
    for name in tool_names:
        unregister_tool(name)


def register_mcp_tools(client, tools, namespace: str | None = None):
    """Register MCP tools, optionally using a provider namespace."""

    registered_tools = []

    for tool in tools:
        original_name = tool.name
        tool_name = (
            f"{namespace}__{original_name}"
            if namespace
            else original_name
        )

        def create_executor(name):
            async def executor(**arguments):
                from app.services.agent.mcp_client import execute_mcp_tool

                return await execute_mcp_tool(
                    client,
                    name,
                    arguments
                )

            return executor

        register_tool(
            name=tool_name,
            description=tool.description or "",
            input_schema=tool.input_schema,
            function=create_executor(original_name)
        )

        registered_tools.append(tool_name)

    return registered_tools
