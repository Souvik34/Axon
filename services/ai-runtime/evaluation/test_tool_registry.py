import app.services.agent.tools  # Registers calculator

from app.services.agent.tool_registry import (
    list_tools,
    execute_tool
)


print("AVAILABLE TOOLS:")

for tool in list_tools():
    print(tool["name"], "-", tool["description"])


print("\nCALCULATOR TEST:")

result = execute_tool(
    name="calculator",
    arguments={"expression": "(250 * 4) + 150"}
)

print("Result:", result)

assert result == 1150

print("\nTool execution successful!")