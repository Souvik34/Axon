
from app.services.agent.tool_registry import (
    register_tool,
    execute_tool,
)

def add(a, b):
    return a + b


register_tool(
    name="validation_test_add",
    description="Adds two numbers.",
    input_schema={
        "type": "object",
        "properties": {
            "a": {"type": "number"},
            "b": {"type": "number"}
        },
        "required": ["a", "b"],
        "additionalProperties": False
    },
    function=add
)

tests = [
    ("Valid arguments", {"a": 10, "b": 20}),
    ("Missing required argument", {"a": 10}),
    ("Invalid data type", {"a": "ten", "b": 20}),
    ("Unexpected argument", {"a": 10, "b": 20, "c": 30}),
]

for description, arguments in tests:
    try:
        result = execute_tool("validation_test_add", arguments)
        print(f"PASS: {description} -> {result}")
    except ValueError as error:
        print(f"REJECTED: {description} -> {error}")
