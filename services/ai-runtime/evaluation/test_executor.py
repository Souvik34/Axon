
import asyncio

from app.services.agent.executor import execute_plan_async
from app.services.agent.tool_registry import register_tool


def add(a, b):
    return a + b


def fail_tool():
    raise RuntimeError("Simulated tool failure.")


register_tool(
    name="test_add",
    description="Adds two numbers.",
    input_schema={
        "type": "object",
        "properties": {
            "a": {"type": "number"},
            "b": {"type": "number"},
        },
        "required": ["a", "b"],
    },
    function=add,
)

register_tool(
    name="test_fail",
    description="Simulates a tool failure.",
    input_schema={
        "type": "object",
        "properties": {},
    },
    function=fail_tool,
)


async def main():
    plan = {
        "goal": "Test failure propagation and independent execution.",
        "steps": [
            {
                "step": 1,
                "description": "Simulate a runtime tool failure.",
                "requires_tool": True,
                "tool": "test_fail",
                "arguments": {},
            },
            {
                "step": 2,
                "description": "Use the failed step output.",
                "requires_tool": True,
                "tool": "test_add",
                "arguments": {
                    "a": "$steps.1.output",
                    "b": 5,
                },
            },
            {
                "step": 3,
                "description": "Perform an independent calculation.",
                "requires_tool": True,
                "tool": "test_add",
                "arguments": {
                    "a": 10,
                    "b": 20,
                },
            },
        ],
    }

    result = await execute_plan_async(plan)

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
