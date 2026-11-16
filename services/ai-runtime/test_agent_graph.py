
import asyncio
from unittest.mock import patch

from app.services.agent.agent_graph import build_agent_graph


async def main():
    valid_plan = {
        "goal": "Test execution recovery",
        "steps": [
            {
                "step": 1,
                "description": "Run test tool",
                "requires_tool": True,
                "tool": "calculator",
                "arguments": {"expression": "1 / 0"},
            }
        ],
    }

    failed_execution = {
        "goal": "Test execution recovery",
        "results": [
            {
                "step": 1,
                "tool": "calculator",
                "status": "failed",
                "error": "Division by zero",
            }
        ],
        "summary": {
            "total_steps": 1,
            "completed": 0,
            "failed": 1,
            "skipped": 0,
        },
    }

    successful_execution = {
        "goal": "Test execution recovery",
        "results": [
            {
                "step": 1,
                "tool": "calculator",
                "status": "completed",
                "output": 42,
                "error": None,
            }
        ],
        "summary": {
            "total_steps": 1,
            "completed": 1,
            "failed": 0,
            "skipped": 0,
        },
    }

    with (
        patch(
            "app.services.agent.agent_graph.create_plan",
            return_value=valid_plan,
        ),
        patch(
            "app.services.agent.agent_graph.execute_plan_async",
            side_effect=[failed_execution, successful_execution],
        ),
        patch(
            "app.services.agent.agent_graph.synthesize_response",
            return_value="Execution recovered successfully.",
        ),
    ):
        graph = build_agent_graph()

        result = await graph.ainvoke({
            "user_request": "Test execution recovery",
            "memories": [],
            "retry_count": 0,
            "attempts": [],
        })

    print("\n--- AXON EXECUTION HISTORY TEST ---")
    print("Answer:", result.get("answer"))
    print("Retry count:", result.get("retry_count"))

    print("\nAttempt History:")

    for attempt in result.get("attempts", []):
        print({
            "attempt": attempt.get("attempt"),
            "status": attempt.get("status"),
            "error": attempt.get("error"),
            "execution_summary": (
                attempt.get("execution", {}).get("summary")
            ),
        })


if __name__ == "__main__":
    asyncio.run(main())
