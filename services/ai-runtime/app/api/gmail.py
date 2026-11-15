
import json
import logging
import secrets
from datetime import timezone

from cryptography.fernet import Fernet, InvalidToken
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from googleapiclient.discovery import build

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.gmail_connection import GmailConnection
from app.services.gmail.oauth import (
    get_authorization_url,
    exchange_authorization_code,
)
from app.services.gmail.token_storage import encrypt_token

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/connectors/gmail",
    tags=["Gmail Connector"],
)


def get_state_cipher():
    key = settings.GOOGLE_TOKEN_ENCRYPTION_KEY

    if not key:
        raise RuntimeError("Google token encryption key is not configured.")

    return Fernet(key.encode())


@router.get("/connect")
async def connect_gmail():
    try:
        code_verifier = secrets.token_urlsafe(64)

        state_payload = json.dumps({
            "purpose": "gmail-connect",
            "code_verifier": code_verifier,
        }).encode()

        state = get_state_cipher().encrypt(state_payload).decode()

        authorization_url = get_authorization_url(
            code_verifier=code_verifier,
            state=state,
        )

        return RedirectResponse(authorization_url)

    except Exception as exc:
        logger.exception("Failed to initiate Gmail OAuth")
        raise HTTPException(
            status_code=500,
            detail=f"Could not start Gmail authorization: {type(exc).__name__}",
        )


@router.get("/callback")
async def gmail_callback(
    code: str = Query(...),
    state: str = Query(...),
    error: str | None = Query(default=None),
):
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"Google authorization was denied: {error}",
        )

    try:
        state_payload = get_state_cipher().decrypt(
            state.encode(),
            ttl=600,
        )

        state_data = json.loads(state_payload)

        if state_data.get("purpose") != "gmail-connect":
            raise HTTPException(
                status_code=400,
                detail="Invalid OAuth state.",
            )

        code_verifier = state_data["code_verifier"]

        credentials = exchange_authorization_code(
            code=code,
            code_verifier=code_verifier,
        )

        if not credentials.refresh_token:
            raise RuntimeError(
                "Google did not provide a refresh token. Reconnect with consent."
            )

        gmail_service = build(
            "gmail",
            "v1",
            credentials=credentials,
            cache_discovery=False,
        )

        profile = gmail_service.users().getProfile(
            userId="me"
        ).execute()

        email_address = profile["emailAddress"]

        encrypted_access_token = encrypt_token(credentials.token)
        encrypted_refresh_token = encrypt_token(credentials.refresh_token)

        token_expiry = credentials.expiry

        if token_expiry and token_expiry.tzinfo is None:
            token_expiry = token_expiry.replace(tzinfo=timezone.utc)

        # Temporary identity for local development.
        user_id = "local-development-user"

        db = SessionLocal()

        try:
            connection = db.query(GmailConnection).filter_by(
                user_id=user_id,
                email_address=email_address,
            ).first()

            if connection:
                connection.access_token = encrypted_access_token
                connection.refresh_token = encrypted_refresh_token
                connection.token_expiry = token_expiry
                connection.scopes = " ".join(credentials.scopes or [])
                connection.status = "connected"
            else:
                connection = GmailConnection(
                    user_id=user_id,
                    email_address=email_address,
                    access_token=encrypted_access_token,
                    refresh_token=encrypted_refresh_token,
                    token_expiry=token_expiry,
                    scopes=" ".join(credentials.scopes or []),
                    status="connected",
                )
                db.add(connection)

            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

        logger.info("Gmail account connected successfully: %s", email_address)

        return {
            "status": "authorized",
            "message": "Gmail account connected and credentials stored securely.",
            "email_address": email_address,
            "scopes": credentials.scopes,
            "token_received": credentials.token is not None,
            "refresh_token_received": credentials.refresh_token is not None,
            "credentials_persisted": True,
        }

    except InvalidToken:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OAuth state. Start a fresh connection.",
        )

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("Gmail OAuth callback failed")
        raise HTTPException(
            status_code=400,
            detail=f"Gmail authorization failed: {type(exc).__name__}",
        )
