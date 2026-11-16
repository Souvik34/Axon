
import re
import time
from app.services.agent.tool_registry import (
    execute_tool,
    execute_tool_async,
    get_tool,
)


REFERENCE_PATTERN = re.compile(
    r"^\$steps\.(\d+)\.output((?:\.[A-Za-z0-9_-]+|\[\d+\])*)$"
)


PATH_TOKEN_PATTERN = re.compile(
    r"\.([A-Za-z0-9_-]+)|\[(\d+)\]"
)


class DependencyError(Exception):
    """Raised when a step depends on unavailable output."""


def _parse_reference_path(path: str) -> list:
    tokens = []
    position = 0

    for match in PATH_TOKEN_PATTERN.finditer(path):
        if match.start() != position:
            raise ValueError(f"Invalid reference path: {path}")

        key, index = match.groups()

        if key is not None:
            tokens.append(key)
        else:
            tokens.append(int(index))

        position = match.end()

    if position != len(path):
        raise ValueError(f"Invalid reference path: {path}")

    return tokens


def _build_step_result(step: dict) -> dict:
    return {
        "step": step.get("step"),
        "description": step.get("description"),
        "tool": step.get("tool"),
        "arguments": step.get("arguments", {}),
        "status": "pending",
        "output": None,
        "error": None,
        "duration_ms": None,
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

            if path:
                _parse_reference_path(path)

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
            for part in _parse_reference_path(path):
                if (
                    isinstance(resolved, dict)
                    and isinstance(part, str)
                    and part in resolved
                ):
                    resolved = resolved[part]

                elif (
                    isinstance(resolved, list)
                    and isinstance(part, int)
                    and part < len(resolved)
                ):
                    resolved = resolved[part]

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

            start_time = time.perf_counter()

            output = execute_tool(
                step["tool"],
                arguments,
            )

            result["duration_ms"] = round(
                (time.perf_counter() - start_time) * 1000,
                2,
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

            start_time = time.perf_counter()

            output = await execute_tool_async(
                step["tool"],
                arguments,
            )
            if step["tool"] == "github__get_commit":
                print("\n========== RAW GITHUB COMMIT RESPONSE ==========")
                print("Arguments:", arguments)
                print("Output type:", type(output).__name__)
                print("Raw output:", repr(output))
                print("===============================================\n")
            result["duration_ms"] = round(
                (time.perf_counter() - start_time) * 1000,
                2,
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
