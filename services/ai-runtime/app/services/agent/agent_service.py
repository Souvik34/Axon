import app.services.agent.tools

from app.services.agent.planner import create_plan
from app.services.agent.executor import execute_plan


def run_agent(
    user_request: str,
    memories: list[str] | None = None,
    max_retries: int = 2
) -> dict:

    execution_feedback = None
    attempts = []

    for attempt in range(max_retries + 1):

        # 1. Generate or revise the plan
        plan = create_plan(
            user_request=user_request,
            memories=memories,
            execution_feedback=execution_feedback
        )

        # 2. Execute the plan
        execution = execute_plan(plan)

        attempts.append({
            "attempt": attempt + 1,
            "plan": plan["steps"],
            "execution": execution
        })

        # 3. Stop if all steps succeeded
        if execution["summary"]["failed"] == 0:
            break

        # 4. Prepare feedback for the planner
        execution_feedback = str(execution["results"])

    return {
        "goal": plan["goal"],
        "attempts": attempts,
        "final_execution": execution,
        "retry_count": len(attempts) - 1
    }