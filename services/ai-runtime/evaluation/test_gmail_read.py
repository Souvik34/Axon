
from app.services.gmail.gmail_tools import read_email

if __name__ == "__main__":
    result = read_email(
        message_id="1a1de69d346d3f7f"
    )

    print("EMAIL READ: SUCCESS")
    print("SUBJECT:", result["subject"])
    print("FROM:", result["from"])
    print("BODY LENGTH:", len(result["body"]))
    print("BODY RETRIEVED:", bool(result["body"]))
