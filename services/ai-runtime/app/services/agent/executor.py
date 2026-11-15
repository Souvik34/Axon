
from app.services.agent.tool_registry import execute_tool, get_tool


def execute_plan(plan: dict) -> dict:
    if not isinstance(plan, dict) or not isinstance(plan.get("steps"), list):
        raise ValueError("Invalid execution plan.")

    results = []

    for step in plan["steps"]:
        step_number = step.get("step")
        description = step.get("description")
        tool_name = step.get("tool")
        requires_tool = step.get("requires_tool", False)

        result = {
            "step": step_number,
            "description": description,
            "status": "skipped",
            "output": None,
            "error": None
        }

        if not requires_tool:
            result["status"] = "completed"
            result["output"] = "No tool execution required."
            results.append(result)
            continue

        if not tool_name:
            result["status"] = "failed"
            result["error"] = "No tool specified for this step."
            results.append(result)
            continue

        if get_tool(tool_name) is None:
            result["status"] = "failed"
            result["error"] = f"Unknown tool: {tool_name}"
            results.append(result)
            continue

        arguments = step.get("arguments", {})

        try:
            output = execute_tool(tool_name, arguments)

            result["status"] = "completed"
            result["output"] = str(output)

        except Exception as exc:
            result["status"] = "failed"
            result["error"] = str(exc)

        results.append(result)

    completed = sum(
        item["status"] == "completed"
        for item in results
    )

    failed = sum(
        item["status"] == "failed"
        for item in results
    )

    return {
        "goal": plan.get("goal"),
        "results": results,
        "summary": {
            "total_steps": len(results),
            "completed": completed,
            "failed": failed
        }
    }
