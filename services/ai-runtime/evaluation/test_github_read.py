
import asyncio
import os

from app.services.agent.mcp_client import (
    connect_to_remote_mcp_server,
)


async def main():
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

    if not token:
        raise RuntimeError("GitHub PAT is not configured.")

    async with connect_to_remote_mcp_server(
        url="https://api.githubcopilot.com/mcp/readonly",
        token=token,
        toolsets="repos,issues,pull_requests",
    ) as client:

        result = await client.call_tool(
            "get_file_contents",
            {
                "owner": "Souvik34",
                "repo": "Cortex",
                "path": "/",
            },
        )

        if result.is_error:
            raise RuntimeError(
                f"GitHub read failed: {result.content}"
            )

        print("\nCORTEX REPOSITORY ROOT:")
        print(result.structured_content or result.content)


if __name__ == "__main__":
    asyncio.run(main())
