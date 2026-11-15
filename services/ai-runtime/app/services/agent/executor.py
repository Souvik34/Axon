
import re

from app.services.agent.tool_registry import (
    execute_tool,
    execute_tool_async,
    get_tool,
)


REFERENCE_PATTERN = re.compile(
    r"^\$steps\.(\d+)\.output(?:\.(.+))?$"
)


class DependencyError(Exception):
    """Raised when a step depends on unavailable output."""


def _build_step_result(step: dict) -> dict:
    return {
        "step": step.get("step"),
        "description": step.get("description"),
        "tool": step.get("tool"),
        "arguments": step.get("arguments", {}),
        "status": "pending",
        "output": None,
        "error": None,
    }


def _build_execution_summary(results: list) -> dict:
    return {
        "total_steps": len(results),
        "completed": sum(
            r["status"] == "completed" for r in results
        ),
        "failed": sum(
            r["status"] == "failed" for r in results
        ),
        "skipped": sum(
            r["status"] == "skipped" for r in results
        ),
    }


def _validate_references(value, available_steps, current_position):
    if isinstance(value, str):
        match = REFERENCE_PATTERN.fullmatch(value)

        if match:
            step_number = int(match.group(1))
            path = match.group(2)

            if step_number not in available_steps:
                raise ValueError(
                    f"Reference to nonexistent step: {step_number}"
                )

            if available_steps[step_number] >= current_position:
                raise ValueError(
                    f"Step {step_number} is not an earlier step."
                )

            if path and any(not part for part in path.split(".")):
                raise ValueError(
                    f"Invalid output reference: {value}"
                )

        elif value.startswith("$steps."):
            raise ValueError(
                f"Malformed output reference: {value}"
            )

    elif isinstance(value, dict):
        for item in value.values():
            _validate_references(
                item, available_steps, current_position
            )

    elif isinstance(value, list):
        for item in value:
            _validate_references(
                item, available_steps, current_position
            )


def _validate_plan(plan: dict):
    if (
        not isinstance(plan, dict)
        or not isinstance(plan.get("steps"), list)
        or not plan["steps"]
    ):
        raise ValueError("Invalid execution plan.")

    available_steps = {}

    for position, step in enumerate(plan["steps"]):
        if not isinstance(step, dict):
            raise ValueError("Invalid step in execution plan.")

        step_number = step.get("step")

        if (
            not isinstance(step_number, int)
            or isinstance(step_number, bool)
            or step_number < 1
        ):
            raise ValueError("Invalid step number.")

        if step_number in available_steps:
            raise ValueError(
                f"Duplicate step number: {step_number}"
            )

        if not isinstance(step.get("description"), str):
            raise ValueError("Step description is missing.")

        requires_tool = step.get("requires_tool", False)

        if not isinstance(requires_tool, bool):
            raise ValueError("Invalid requires_tool value.")

        arguments = step.get("arguments", {})

        if not isinstance(arguments, dict):
            raise ValueError("Step arguments must be an object.")

        if requires_tool:
            tool_name = step.get("tool")

            if not isinstance(tool_name, str) or not tool_name:
                raise ValueError("Tool name is missing.")

            if get_tool(tool_name) is None:
                raise ValueError(f"Unknown tool: {tool_name}")

        _validate_references(
            arguments,
            available_steps,
            position,
        )

        available_steps[step_number] = position


def _resolve_value(value, results_by_step):
    if isinstance(value, str):
        match = REFERENCE_PATTERN.fullmatch(value)

        if not match:
            if value.startswith("$steps."):
                raise ValueError(
                    f"Malformed output reference: {value}"
                )
            return value

        step_number = int(match.group(1))
        path = match.group(2)

        source = results_by_step.get(step_number)

        if source is None:
            raise DependencyError(
                f"Step {step_number} has not executed."
            )

        if source["status"] != "completed":
            raise DependencyError(
                f"Step {step_number} did not complete."
            )

        resolved = source["output"]

        if path:
            for part in path.split("."):
                if isinstance(resolved, dict) and part in resolved:
                    resolved = resolved[part]

                elif (
                    isinstance(resolved, list)
                    and part.isdigit()
                    and int(part) < len(resolved)
                ):
                    resolved = resolved[int(part)]

                else:
                    raise ValueError(
                        f"Invalid output reference: {value}"
                    )

        if resolved is None:
            raise DependencyError(
                f"Output reference resolved to None: {value}"
            )

        return resolved

    if isinstance(value, dict):
        return {
            key: _resolve_value(item, results_by_step)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            _resolve_value(item, results_by_step)
            for item in value
        ]

    return value


def _record_result(result, results, results_by_step):
    results.append(result)
    results_by_step[result["step"]] = result


def execute_plan(plan: dict) -> dict:
    _validate_plan(plan)

    results = []
    results_by_step = {}

    for step in plan["steps"]:
        result = _build_step_result(step)
        step_number = step["step"]

        if not step.get("requires_tool", False):
            result["status"] = "completed"
            _record_result(result, results, results_by_step)
            continue

        try:
            arguments = _resolve_value(
                step.get("arguments", {}),
                results_by_step,
            )

            result["arguments"] = arguments

            output = execute_tool(
                step["tool"],
                arguments,
            )

            result["status"] = "completed"
            result["output"] = output

        except DependencyError as exc:
            result["status"] = "skipped"
            result["error"] = str(exc)

        except Exception as exc:
            result["status"] = "failed"
            result["error"] = str(exc)

        _record_result(result, results, results_by_step)

    return {
        "goal": plan.get("goal"),
        "results": results,
        "summary": _build_execution_summary(results),
    }


async def execute_plan_async(plan: dict) -> dict:
    _validate_plan(plan)

    results = []
    results_by_step = {}

    for step in plan["steps"]:
        result = _build_step_result(step)
        step_number = step["step"]

        if not step.get("requires_tool", False):
            result["status"] = "completed"
            _record_result(result, results, results_by_step)
            continue

        try:
            arguments = _resolve_value(
                step.get("arguments", {}),
                results_by_step,
            )

            result["arguments"] = arguments

            output = await execute_tool_async(
                step["tool"],
                arguments,
            )

            result["status"] = "completed"
            result["output"] = output

        except DependencyError as exc:
            result["status"] = "skipped"
            result["error"] = str(exc)

        except Exception as exc:
            result["status"] = "failed"
            result["error"] = str(exc)

        _record_result(result, results, results_by_step)

    return {
        "goal": plan.get("goal"),
        "results": results,
        "summary": _build_execution_summary(results),
    }
