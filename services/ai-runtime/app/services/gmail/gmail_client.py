
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from app.core.database import SessionLocal
from app.models.gmail_connection import GmailConnection
from app.services.gmail.token_storage import (
    encrypt_token,
    decrypt_token,
)


def get_gmail_client(user_id: str = "local-development-user"):
    db = SessionLocal()

    try:
        connection = db.query(GmailConnection).filter_by(
            user_id=user_id,
            status="connected",
        ).first()

        if not connection:
            raise RuntimeError("No connected Gmail account found.")

        credentials = Credentials(
            token=decrypt_token(connection.access_token),
            refresh_token=decrypt_token(connection.refresh_token),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=None,
            client_secret=None,
            scopes=connection.scopes.split(),
        )

        # Supply OAuth client credentials for automatic token refresh.
        from app.core.config import settings

        credentials._client_id = settings.GOOGLE_CLIENT_ID
        credentials._client_secret = settings.GOOGLE_CLIENT_SECRET

        if credentials.expired:
            credentials.refresh(Request())

            connection.access_token = encrypt_token(credentials.token)
            connection.token_expiry = credentials.expiry
            db.commit()

        return build(
            "gmail",
            "v1",
            credentials=credentials,
            cache_discovery=False,
        )

    finally:
        db.close()
