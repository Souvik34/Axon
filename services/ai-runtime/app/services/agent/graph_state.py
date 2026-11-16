
from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    # Original user request and intended outcome
    user_request: str
    goal: str

    # Relevant long-term memory
    memories: list[dict[str, Any]]

    # Dynamically discovered providers and capabilities
    providers: list[dict[str, Any]]

    # Generated execution plan
    plan: dict[str, Any]

    # Shared information accessible across agents
    shared_context: dict[str, Any]

    # Normalized evidence collected from all sources
    evidence: list[dict[str, Any]]

    # Individual agent execution results
    agent_results: list[dict[str, Any]]

    # Tasks delegated to other agents/providers
    pending_handoffs: list[dict[str, Any]]

    # Information still missing after research
    research_gaps: list[str]

    # Existing executor result
    execution: dict[str, Any]

    # Planning/execution feedback
    execution_feedback: str

    # Retry and autonomous research limits
    retry_count: int
    follow_up_count: int
    research_complete: bool

    # Final response
    answer: str

    # Execution history and observability
    attempts: list[dict[str, Any]]

    # Error information
    error: str | None
