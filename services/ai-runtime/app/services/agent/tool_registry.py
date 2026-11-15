from typing import Callable, Any
import inspect

TOOLS: dict[str, dict[str, Any]] = {}

def unregister_tool(name: str):
    TOOLS.pop(name, None)
    
def register_tool(
    name: str,
    description: str,
    input_schema: dict,
    function: Callable
) -> None:
    if name in TOOLS:
        raise ValueError(f"Tool '{name}' is already registered.")

    if not callable(function):
        raise ValueError("Tool function must be callable.")

    TOOLS[name] = {
        "name": name,
        "description": description,
        "input_schema": input_schema,
        "function": function
    }


def get_tool(name: str) -> dict | None:
    return TOOLS.get(name)


def list_tools() -> list[dict]:
    return [
        {
            "name": tool["name"],
            "description": tool["description"],
            "input_schema": tool["input_schema"]
        }
        for tool in TOOLS.values()
    ]


def execute_tool(
    name: str,
    arguments: dict
) -> Any:
    tool = get_tool(name)

    if tool is None:
        raise ValueError(f"Unknown tool: {name}")

    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be a dictionary.")

    return tool["function"](**arguments)

async def execute_tool_async(name: str, arguments: dict):
    tool = get_tool(name)

    if tool is None:
        raise ValueError(f"Unknown tool: {name}")

    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be an object.")

    result = tool["function"](**arguments)

    if inspect.isawaitable(result):
        result = await result

    return result