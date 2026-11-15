
import asyncio
import os
import httpx2


async def main():
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

    if not token:
        raise RuntimeError("GitHub PAT is not configured.")

    url = "https://api.githubcopilot.com/mcp/"

    headers = {
    "Authorization": f"Bearer {token}",
    "X-MCP-Toolsets": "repos,issues,pull_requests",
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "MCP-Protocol-Version": "2025-06-18",
    }
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {
                "name": "cortex",
                "version": "1.0.0",
            },
        },
    }

    try:
        async with httpx2.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
        ) as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
            )

            print("HTTP STATUS:", response.status_code)
            print("CONTENT TYPE:", response.headers.get("content-type"))
            print("RESPONSE BODY:", response.text[:3000])

    except Exception as exc:
        print("EXCEPTION TYPE:", type(exc).__name__)
        print("EXCEPTION:", str(exc))


if __name__ == "__main__":
    asyncio.run(main())
