import app.services.agent.tools

from app.services.agent.executor import execute_plan


plan = {
    "goal": "Calculate total expenses",
    "steps": [
        {
            "step": 1,
            "description": "Calculate expenses",
            "requires_tool": True,
            "tool": "calculator",
            "arguments": {
                "expression": "500 + 300 + 200"
            }
        },
        {
            "step": 2,
            "description": "Test unknown tool handling",
            "requires_tool": True,
            "tool": "unknown_tool",
            "arguments": {}
        }
    ]
}

result = execute_plan(plan)

print("EXECUTION RESULTS:")

for item in result["results"]:
    print(item)

print("\nSUMMARY:")
print(result["summary"])

assert result["summary"]["completed"] == 1
assert result["summary"]["failed"] == 1

print("\nExecutor test successful!")