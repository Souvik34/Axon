import json
import app.services.agent.tools
from app.services.agent.agent_graph import build_agent_graph
from mcp import Client, StdioServerParameters
import os

from app.services.agent.mcp_client import (
    discover_mcp_tools,
    connect_to_remote_mcp_server,
)
from app.services.agent.response_synthesizer import synthesize_response
from app.services.agent.planner import create_plan
from app.services.agent.executor import (
    execute_plan,
    execute_plan_async,
)
from app.services.agent.mcp_client import discover_mcp_tools
from app.services.agent.mcp_tool_adapter import (
    register_mcp_tools,
    unregister_mcp_tools,
)


def run_agent(
    user_request: str,
    memories: list[str] | None = None,
    max_retries: int = 2
) -> dict:

    execution_feedback = None
    attempts = []

    for attempt in range(max_retries + 1):

        plan = create_plan(
            user_request=user_request,
            memories=memories,
            execution_feedback=execution_feedback
        )

        execution = execute_plan(plan)

        attempts.append({
            "attempt": attempt + 1,
            "plan": plan["steps"],
            "execution": execution
        })

        if execution["summary"]["failed"] == 0:
            break

        execution_feedback = str(execution["results"])

    return {
        "goal": plan["goal"],
        "attempts": attempts,
        "final_execution": execution,
        "retry_count": len(attempts) - 1
    }


async def run_agent_with_mcp(
    user_request: str,
    command: str,
    args: list[str],
    memories: list[str] | None = None,
    max_retries: int = 2
) -> dict:

    execution_feedback = None
    attempts = []

    server_params = StdioServerParameters(
        command=command,
        args=args
    )

    async with Client(server_params) as client:

        # 1. Discover tools from the MCP server
        mcp_tools = await discover_mcp_tools(client)

        # 2. Temporarily register discovered tools
        registered_tools = register_mcp_tools(client, mcp_tools)

        try:
            # 3. Plan and execute with retry support
            for attempt in range(max_retries + 1):

                plan = create_plan(
                    user_request=user_request,
                    memories=memories,
                    execution_feedback=execution_feedback
                )

                execution = await execute_plan_async(plan)

                attempts.append({
                    "attempt": attempt + 1,
                    "plan": plan["steps"],
                    "execution": execution
                })

                if execution["summary"]["failed"] == 0:
                    break

                execution_feedback = (
    "The previous execution failed. Review these exact errors "
    "and correct the plan:\n"
    f"{json.dumps(execution['results'], indent=2, default=str)}\n"
    "IMPORTANT: Do not repeat invalid output references. "
    "Use the actual output object structure and documented fields."
)

            return {
                "goal": plan["goal"],
                "attempts": attempts,
                "final_execution": execution,
                "retry_count": len(attempts) - 1
            }

        finally:
            # 4. Remove MCP tools before closing the connection
            unregister_mcp_tools(registered_tools)


async def run_github_agent(
    user_request: str,
    memories: list[str] | None = None,
    max_retries: int = 2
) -> dict:

    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

    if not token:
        raise RuntimeError("GitHub access token is not configured.")

    execution_feedback = None
    attempts = []
    registered_tools = []

    async with connect_to_remote_mcp_server(
        url="https://api.githubcopilot.com/mcp/readonly",
        token=token,
        toolsets="repos,issues,pull_requests",
    ) as client:

        mcp_tools = await discover_mcp_tools(client)
        registered_tools = register_mcp_tools(client, mcp_tools)

        try:
            for attempt in range(max_retries + 1):

                plan = create_plan(
                    user_request=user_request,
                    memories=memories,
                    execution_feedback=execution_feedback
                )

                execution = await execute_plan_async(plan)

                attempts.append({
                    "attempt": attempt + 1,
                    "plan": plan["steps"],
                    "execution": execution
                })

                if execution["summary"]["failed"] == 0:
                    break

                execution_feedback = str(execution["results"])

            answer = synthesize_response(
                user_request=user_request,
                execution=execution
            )

            return {
                "goal": plan["goal"],
                "attempts": attempts,
                "final_execution": execution,
                "retry_count": len(attempts) - 1,
                "answer": answer
            }

        finally:
            unregister_mcp_tools(registered_tools)



async def run_gmail_agent(
    user_request: str,
    memories: list[str] | None = None,
    max_retries: int = 2,
) -> dict:

    execution_feedback = None
    attempts = []

    for attempt in range(max_retries + 1):

        plan = create_plan(
            user_request=user_request,
            memories=memories,
            execution_feedback=execution_feedback,
        )

        execution = await execute_plan_async(plan)

        attempts.append({
            "attempt": attempt + 1,
            "plan": plan["steps"],
            "execution": execution,
        })

        if execution["summary"]["failed"] == 0:
            break

        execution_feedback = str(execution["results"])

    answer = synthesize_response(
        user_request=user_request,
        execution=execution,
    )

    return {
        "goal": plan["goal"],
        "attempts": attempts,
        "final_execution": execution,
        "retry_count": len(attempts) - 1,
        "answer": answer,
    }



async def run_multi_source_agent(
    user_request: str,
    memories: list[str] | None = None,
    max_retries: int = 2,
) -> dict:
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

    if not token:
        raise RuntimeError("GitHub access token is not configured.")

    registered_tools = []

    async with connect_to_remote_mcp_server(
        url="https://api.githubcopilot.com/mcp/readonly",
        token=token,
        toolsets="repos,issues,pull_requests",
    ) as github_client:

        github_tools = await discover_mcp_tools(github_client)

        registered_tools = register_mcp_tools(
            github_client,
            github_tools,
            namespace="github",
        )
        from app.services.agent.tool_registry import list_tools

        print("\n========== AXON REGISTERED TOOLS ==========")

        for tool in list_tools():
            print(tool["name"])

        print("===========================================\n")

        try:
            graph = build_agent_graph()

            result = await graph.ainvoke({
                "user_request": user_request,
                "memories": memories or [],
                "retry_count": 0,
                "attempts": [],
            })

            plan = result.get("plan") or {}
            execution = result.get("execution") or {
                "summary": {
                    "total_steps": 0,
                    "completed": 0,
                    "failed": 0,
                    "skipped": 0,
                },
                "results": [],
                "status": "planning_failed",
            }

            # Preserve the existing attempt structure for chat.py.
            attempts = []

            for item in result.get("attempts", []):
                attempt_plan = item.get("plan")

                attempts.append({
                    "attempt": item.get("attempt"),
                    "plan": (
                        attempt_plan.get("steps")
                        if isinstance(attempt_plan, dict)
                        else None
                    ),
                    "execution": item.get("execution") or {
                        "status": item.get("status"),
                        "error": item.get("error"),
                    },
                    "status": item.get("status"),
                    "error": item.get("error"),
                })

            return {
                "goal": plan.get("goal", user_request),
                "attempts": attempts,
                "final_execution": execution,
                "retry_count": result.get("retry_count", 0),
                "answer": result.get("answer", ""),
            }

        finally:
            unregister_mcp_tools(registered_tools)
