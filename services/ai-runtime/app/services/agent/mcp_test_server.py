from mcp.server import MCPServer

mcp = MCPServer("Cortex Test Server")


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


@mcp.tool()
def get_project_status(project_name: str) -> str:
    """Get the status of a sample project."""
    return f"{project_name}: In Progress"


if __name__ == "__main__":
    mcp.run()