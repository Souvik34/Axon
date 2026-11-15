
import json

from app.services.llm.provider import generate_response
from app.services.agent.tool_selector import select_relevant_tools


def create_plan(
    user_request: str,
    memories: list[str] | None = None,
    execution_feedback: str | None = None
) -> dict:

    if not user_request or not user_request.strip():
        raise ValueError("User request cannot be empty.")

    memory_context = "\n".join(
        f"- {memory}" for memory in (memories or [])
    )

    available_tools = select_relevant_tools(user_request)

    prompt = f"""
You are Cortex's task planning component.

Break the user's request into logical, actionable steps.

AVAILABLE TOOLS:
{json.dumps(available_tools, indent=2)}

Rules:
- Identify the user's actual goal.
- Create small, ordered steps.
- Use an available tool when the step requires computation or another registered capability.
- Never invent tools.
- If no available tool can perform a step, set requires_tool to false.
- Provide valid arguments matching the tool's input schema.
- Simple questions should have one step.
- Do not execute any tools.
- Return ONLY valid JSON.

Expected format:
{{
    "goal": "The user's intended outcome",
    "steps": [
        {{
            "step": 1,
            "description": "What needs to be done",
            "requires_tool": true,
            "tool": "calculator",
            "arguments": {{
                "expression": "250 * 4"
            }}
        }}
    ]
}}

RELEVANT MEMORIES:
{memory_context or "None"}

PREVIOUS EXECUTION FEEDBACK:
{execution_feedback or "This is the initial plan. No previous execution failures."}

IMPORTANT:
- If previous execution failed, analyze the failure.
- Generate a revised plan that addresses the failure.
- Do not repeat the same failed approach.
- Only select tools listed under AVAILABLE TOOLS.
USER REQUEST:
{user_request}
"""

    response = generate_response([
        {
            "role": "user",
            "content": prompt
        }
    ])

    try:
        plan = json.loads(response)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError(
            "The agent planner returned invalid JSON."
        ) from exc

    if (
        not isinstance(plan, dict)
        or not isinstance(plan.get("goal"), str)
        or not isinstance(plan.get("steps"), list)
        or not plan["steps"]
    ):
        raise ValueError("The agent planner returned an invalid plan.")

    registered_tools = {
        tool["name"] for tool in available_tools
    }

    for index, step in enumerate(plan["steps"], start=1):
        if not isinstance(step, dict):
            raise ValueError("Invalid step in agent plan.")

        if not isinstance(step.get("description"), str):
            raise ValueError("Agent step description is missing.")

        requires_tool = step.get("requires_tool", False)

        if not isinstance(requires_tool, bool):
            raise ValueError("Invalid requires_tool value.")

        if requires_tool:
            tool_name = step.get("tool")

            if tool_name not in registered_tools:
                raise ValueError(
                    f"Planner selected an unavailable tool: {tool_name}"
                )

            if not isinstance(step.get("arguments"), dict):
                raise ValueError("Tool arguments must be an object.")

        step["step"] = index

    return plan
