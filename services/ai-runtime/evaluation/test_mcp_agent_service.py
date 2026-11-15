
import asyncio
import sys
from pathlib import Path

from app.services.agent.agent_service import run_agent_with_mcp


async def main():
    server_path = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "services"
        / "agent"
        / "mcp_test_server.py"
    )

    result = await run_agent_with_mcp(
        user_request=(
            "Use the multiply tool to calculate 12 times 8. "
            "Do not calculate mentally."
        ),
        command=sys.executable,
        args=[str(server_path)],
    )

    print("\nAGENT SERVICE RESULT:")
    print(result)

    # Verify the final execution
    final_execution = result["final_execution"]

    assert final_execution["summary"]["failed"] == 0
    assert final_execution["summary"]["completed"] == 1
    assert "96" in str(final_execution["results"])

    print("\nMCP AGENT SERVICE TEST PASSED!")


if __name__ == "__main__":
    asyncio.run(main())
