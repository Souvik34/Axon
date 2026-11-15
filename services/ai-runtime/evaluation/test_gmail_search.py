
import app.services.agent.tools

from app.services.gmail.gmail_tools import search_emails


if __name__ == "__main__":
    result = search_emails(
        query="newer_than:30d",
        max_results=5,
    )

    print("GMAIL CONNECTION: SUCCESS")
    print("SEARCH QUERY:", result["query"])
    print("EMAILS FOUND:", result["result_count"])
    print("MESSAGE IDS:", [
        email["message_id"] for email in result["emails"]
    ])
