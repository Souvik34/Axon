
from app.services.agent.tool_registry import register_tool, unregister_tool

def unregister_mcp_tools(tool_names: list[str]):
    for name in tool_names:
        unregister_tool(name)
        
def register_mcp_tools(client, tools):
    """
    Register tools discovered from an MCP server
    in Cortex's existing tool registry.
    """

    registered_tools = []

    for tool in tools:

        tool_name = tool.name

        def create_executor(name):
            async def executor(**arguments):
                from app.services.agent.mcp_client import (
                    execute_mcp_tool
                )

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
            function=create_executor(tool_name)
        )

        registered_tools.append(tool_name)

    return registered_tools