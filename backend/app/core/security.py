import hashlib
import hmac
import os
import secrets

from fastapi import Header, HTTPException, status

from app.core.config import settings

_N, _R, _P = 2**14, 8, 1


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=_N, r=_R, p=_P)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split("$")
        digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=_N, r=_R, p=_P)
    except ValueError:
        return False
    return hmac.compare_digest(digest.hex().encode(), digest_hex.encode())


def new_session_token() -> str:
    return secrets.token_urlsafe(32)


def require_api_token(x_api_token: str = Header(default="")) -> None:
    """Per-launch secret: only the desktop app that started us knows it."""
    if not hmac.compare_digest(x_api_token.encode(), settings.token.encode()):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid API token")
