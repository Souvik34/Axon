
from app.services.gmail.gmail_client import get_gmail_client
import base64
from html.parser import HTMLParser
from html import unescape
def search_emails(
    query: str,
    max_results: int = 10,
    user_id: str = "local-development-user",
):
    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not 1 <= max_results <= 50:
        raise ValueError("max_results must be between 1 and 50.")

    service = get_gmail_client(user_id)

    response = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=max_results,
    ).execute()

    messages = response.get("messages", [])
    results = []

    for message in messages:
        details = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"],
        ).execute()

        headers = {
            header["name"].lower(): header["value"]
            for header in details.get("payload", {}).get("headers", [])
        }

        results.append({
            "message_id": message["id"],
            "thread_id": details.get("threadId"),
            "url": f"https://mail.google.com/mail/u/0/#all/{message['id']}",
            "from": headers.get("from"),
            "to": headers.get("to"),
            "subject": headers.get("subject"),
            "date": headers.get("date"),
            "snippet": details.get("snippet"),
        })

    return {
        "query": query,
        "result_count": len(results),
        "emails": results,
    }


class EmailHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.skip_content = False

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip_content = True
        elif tag in {"p", "div", "br", "tr", "li"}:
            self.text_parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.skip_content = False
        elif tag in {"p", "div", "tr", "li"}:
            self.text_parts.append("\n")

    def handle_data(self, data):
        if not self.skip_content:
            self.text_parts.append(data)

    def get_text(self):
        return unescape("".join(self.text_parts)).strip()


def extract_email_body(payload):
    import base64

    plain_parts = []
    html_parts = []

    mime_type = payload.get("mimeType", "")
    data = payload.get("body", {}).get("data")

    if data:
        decoded = base64.urlsafe_b64decode(data)
        content = decoded.decode("utf-8", errors="replace")

        if mime_type == "text/plain":
            plain_parts.append(content)
        elif mime_type == "text/html":
            html_parts.append(content)

    for part in payload.get("parts", []):
        plain, html = extract_email_body(part)
        plain_parts.extend(plain)
        html_parts.extend(html)

    return plain_parts, html_parts



def read_email(
    message_id: str,
    user_id: str = "local-development-user",
):
    if not message_id.strip():
        raise ValueError("Message ID cannot be empty.")

    service = get_gmail_client(user_id)

    message = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full",
    ).execute()

    payload = message.get("payload", {})

    headers = {
        header["name"].lower(): header["value"]
        for header in payload.get("headers", [])
    }

    plain_parts, html_parts = extract_email_body(payload)

    if plain_parts:
        body = "\n".join(plain_parts)

    elif html_parts:
        parser = EmailHTMLParser()
        parser.feed("\n".join(html_parts))
        body = parser.get_text()

    else:
        body = ""

    return {
        "message_id": message["id"],
        "thread_id": message.get("threadId"),
        "url": f"https://mail.google.com/mail/u/0/#all/{message['id']}",
        "from": headers.get("from"),
        "to": headers.get("to"),
        "subject": headers.get("subject"),
        "date": headers.get("date"),
        "body": body,
        "snippet": message.get("snippet"),
    }
