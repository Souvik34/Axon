from app.services.agent.planner import create_plan


plan = create_plan(
    user_request=(
        "Research three AI agent frameworks, compare their "
        "features and pricing, and recommend the best one "
        "for an open-source project with a zero budget."
    )
)

print("\nGOAL:")
print(plan["goal"])

print("\nEXECUTION PLAN:")

for step in plan["steps"]:
    print(
        f'{step["step"]}. {step["description"]} '
        f'| Requires tool: {step["requires_tool"]} '
        f'| Tool: {step["tool"]}'
    )