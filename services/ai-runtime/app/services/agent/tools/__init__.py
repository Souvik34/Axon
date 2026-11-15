from app.services.agent.tool_registry import register_tool
from app.services.agent.tools.calculator import calculate


register_tool(
    name="calculator",
    description="Evaluates basic mathematical expressions.",
    input_schema={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to evaluate."
            }
        },
        "required": ["expression"]
    },
    function=calculate
)