
from app.services.agent.response_synthesizer import synthesize_response


def main():

    execution = {
        "goal": "Retrieve the five latest Cortex commits",
        "results": [
            {
                "step": 1,
                "description": "Retrieve recent commits",
                "tool": "list_commits",
                "status": "completed",
                "output": [
                    {
                        "sha": "023ae88",
                        "html_url": "https://github.com/Souvik34/Cortex/commit/023ae88",
                        "commit": {
                            "message": "Implement asynchronous MCP execution",
                            "author": {
                                "name": "Souvik Sural",
                                "date": "2026-11-15T07:53:03Z"
                            }
                        }
                    }
                ],
                "error": None
            }
        ],
        "summary": {
            "total_steps": 1,
            "completed": 1,
            "failed": 0
        }
    }

    answer = synthesize_response(
        user_request="Summarize the latest commit in Cortex.",
        execution=execution
    )

    print("\nSYNTHESIZED ANSWER:\n")
    print(answer)


if __name__ == "__main__":
    main()
