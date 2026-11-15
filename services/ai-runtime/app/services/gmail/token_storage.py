
from cryptography.fernet import Fernet

from app.core.config import settings


def get_fernet():
    key = settings.GOOGLE_TOKEN_ENCRYPTION_KEY

    if not key:
        raise RuntimeError("Google token encryption key is not configured.")

    return Fernet(key.encode())


def encrypt_token(token: str) -> str:
    return get_fernet().encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    return get_fernet().decrypt(encrypted_token.encode()).decode()
