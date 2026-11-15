import app.services.agent.tools
from app.services.agent.planner import create_plan

plan = create_plan(
    "Calculate the total cost of 5 items costing 250 each."
)

print("\nGOAL:")
print(plan["goal"])

print("\nEXECUTION PLAN:")
for step in plan["steps"]:
    print(
        f'{step["step"]}. {step["description"]} '
        f'| Requires tool: {step["requires_tool"]} '
        f'| Tool: {step.get("tool")} '
        f'| Arguments: {step.get("arguments", {})}'
    )

calculator_steps = [
    step for step in plan["steps"]
    if step.get("tool") == "calculator"
]

assert calculator_steps, "Planner did not select the calculator tool."

print("\nCalculator planning test successful!")