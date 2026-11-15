
from google_auth_oauthlib.flow import Flow

from app.core.config import settings


GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]


def create_oauth_flow(code_verifier: str) -> Flow:
    """Create a Gmail OAuth flow with the original PKCE verifier."""

    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise RuntimeError("Google OAuth credentials are not configured.")

    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=GMAIL_SCOPES,
        code_verifier=code_verifier,
    )

    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    return flow


def get_authorization_url(code_verifier: str, state: str) -> str:
    flow = create_oauth_flow(code_verifier)

    authorization_url, _ = flow.authorization_url(
        state=state,
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    return authorization_url


def exchange_authorization_code(code: str, code_verifier: str):
    """Exchange the authorization code using the original PKCE verifier."""

    flow = create_oauth_flow(code_verifier)
    flow.fetch_token(code=code)

    return flow.credentials
