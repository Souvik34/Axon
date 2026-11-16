
from typing import Callable, Any
import inspect
import re


TOOLS: dict[str, dict[str, Any]] = {}


def unregister_tool(name: str):
    TOOLS.pop(name, None)


def register_tool(
    name: str,
    description: str,
    input_schema: dict,
    function: Callable,
    output_schema: dict | None = None,
) -> None:
    if name in TOOLS:
        raise ValueError(f"Tool '{name}' is already registered.")

    if not callable(function):
        raise ValueError("Tool function must be callable.")

    if not isinstance(input_schema, dict):
        raise ValueError("Tool input_schema must be a dictionary.")

    TOOLS[name] = {
        "name": name,
        "description": description,
        "input_schema": input_schema,
        "function": function,
        "output_schema": output_schema,
    }


def get_tool(name: str) -> dict | None:
    return TOOLS.get(name)


def list_tools() -> list[dict]:
    return [
        {
            "name": tool["name"],
            "description": tool["description"],
            "input_schema": tool["input_schema"],
            "output_schema": tool.get("output_schema"),
        }
        for tool in TOOLS.values()
    ]


def _validate_value(value: Any, schema: dict, path: str):
    if not isinstance(schema, dict):
        raise ValueError(f"Invalid schema at {path}.")

    expected_type = schema.get("type")

    if isinstance(expected_type, list):
        valid_types = expected_type
    elif expected_type:
        valid_types = [expected_type]
    else:
        valid_types = []

    type_checks = {
        "object": lambda v: isinstance(v, dict),
        "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
        "boolean": lambda v: isinstance(v, bool),
        "null": lambda v: v is None,
    }

    if valid_types:
        matches = any(
            type_name in type_checks and type_checks[type_name](value)
            for type_name in valid_types
        )

        if not matches:
            raise ValueError(
                f"{path} must be of type {', '.join(valid_types)}."
            )

    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(
            f"{path} must be one of: {schema['enum']}."
        )

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        for field in required:
            if field not in value:
                raise ValueError(
                    f"Missing required argument: {path}.{field}"
                )

        for field, field_value in value.items():
            if field in properties:
                _validate_value(
                    field_value,
                    properties[field],
                    f"{path}.{field}"
                )
            elif schema.get("additionalProperties") is False:
                raise ValueError(
                    f"Unexpected argument: {path}.{field}"
                )
            elif isinstance(schema.get("additionalProperties"), dict):
                _validate_value(
                    field_value,
                    schema["additionalProperties"],
                    f"{path}.{field}"
                )

    if isinstance(value, list):
        item_schema = schema.get("items")

        if item_schema:
            for index, item in enumerate(value):
                _validate_value(
                    item,
                    item_schema,
                    f"{path}[{index}]"
                )

        if "minItems" in schema and len(value) < schema["minItems"]:
            raise ValueError(f"{path} has too few items.")

        if "maxItems" in schema and len(value) > schema["maxItems"]:
            raise ValueError(f"{path} has too many items.")

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            raise ValueError(f"{path} is too short.")

        if "maxLength" in schema and len(value) > schema["maxLength"]:
            raise ValueError(f"{path} is too long.")

        if "pattern" in schema and not re.search(schema["pattern"], value):
            raise ValueError(f"{path} does not match the required pattern.")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            raise ValueError(f"{path} is below the minimum.")

        if "maximum" in schema and value > schema["maximum"]:
            raise ValueError(f"{path} exceeds the maximum.")


def validate_tool_arguments(name: str, arguments: dict) -> None:
    tool = get_tool(name)

    if tool is None:
        raise ValueError(f"Unknown tool: {name}")

    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be a dictionary.")

    _validate_value(
        arguments,
        tool["input_schema"],
        "arguments"
    )


def execute_tool(name: str, arguments: dict) -> Any:
    tool = get_tool(name)

    if tool is None:
        raise ValueError(f"Unknown tool: {name}")

    validate_tool_arguments(name, arguments)

    return tool["function"](**arguments)


async def execute_tool_async(name: str, arguments: dict):
    tool = get_tool(name)

    if tool is None:
        raise ValueError(f"Unknown tool: {name}")

    validate_tool_arguments(name, arguments)

    result = tool["function"](**arguments)

    if inspect.isawaitable(result):
        result = await result

    return result
