
from app.services.agent.tool_registry import (
    execute_tool,
    execute_tool_async,
    get_tool,
)


def _build_step_result(step: dict) -> dict:
    return {
        "step": step.get("step"),
        "description": step.get("description"),
        "tool": step.get("tool"),
        "arguments": step.get("arguments", {}),
        "status": "skipped",
        "output": None,
        "error": None,
    }


def _build_execution_summary(results: list) -> dict:
    completed = sum(r["status"] == "completed" for r in results)
    failed = sum(r["status"] == "failed" for r in results)

    return {
        "total_steps": len(results),
        "completed": completed,
        "failed": failed,
    }


def execute_plan(plan: dict) -> dict:
    if not isinstance(plan, dict) or not isinstance(plan.get("steps"), list):
        raise ValueError("Invalid execution plan.")

    results = []

    for step in plan["steps"]:
        result = _build_step_result(step)

        if not step.get("requires_tool", False):
            result["status"] = "completed"
            result["output"] = None
            results.append(result)
            continue

        tool_name = step.get("tool")

        if not tool_name or get_tool(tool_name) is None:
            result["status"] = "failed"
            result["error"] = f"Unknown tool: {tool_name}"
            results.append(result)
            continue

        try:
            output = execute_tool(
                tool_name,
                step.get("arguments", {})
            )

            result["status"] = "completed"
            result["output"] = output

        except Exception as exc:
            result["status"] = "failed"
            result["error"] = str(exc)

        results.append(result)

    return {
        "goal": plan.get("goal"),
        "results": results,
        "summary": _build_execution_summary(results),
    }


async def execute_plan_async(plan: dict) -> dict:
    if not isinstance(plan, dict) or not isinstance(plan.get("steps"), list):
        raise ValueError("Invalid execution plan.")

    results = []

    for step in plan["steps"]:
        result = _build_step_result(step)

        if not step.get("requires_tool", False):
            result["status"] = "completed"
            result["output"] = None
            results.append(result)
            continue

        tool_name = step.get("tool")

        if not tool_name or get_tool(tool_name) is None:
            result["status"] = "failed"
            result["error"] = f"Unknown tool: {tool_name}"
            results.append(result)
            continue

        try:
            output = await execute_tool_async(
                tool_name,
                step.get("arguments", {})
            )

            result["status"] = "completed"
            result["output"] = output

        except Exception as exc:
            result["status"] = "failed"
            result["error"] = str(exc)

        results.append(result)

    return {
        "goal": plan.get("goal"),
        "results": results,
        "summary": _build_execution_summary(results),
    }
