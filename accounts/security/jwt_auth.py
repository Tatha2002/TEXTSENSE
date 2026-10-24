import os
import uuid
import jwt
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from rest_framework.exceptions import AuthenticationFailed
from ..models import User
load_dotenv()


# ==========================================================
# ACCESS TOKEN: Short-lived token for protected API requests.
# ==========================================================

def create_access_token(user_id, role):
    now = datetime.now(timezone.utc)

    payload = {
        "user_id": user_id,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=5),
        "token_type": "access",
    }

    secret_key = os.getenv("JWT_SECRET_KEY")

    if not secret_key:
        raise RuntimeError("JWT_SECRET_KEY not found in .env")

    return jwt.encode(payload, secret_key, algorithm="HS256")


def decode_access_token(token):
    secret_key = os.getenv("JWT_SECRET_KEY")

    if not secret_key:
        raise RuntimeError("JWT_SECRET_KEY not found in .env")

    try:
        payload = jwt.decode(token,secret_key,algorithms=["HS256"],)

        if payload.get("token_type") != "access":
            raise AuthenticationFailed("Invalid access token type.")

        return payload["user_id"]

    except jwt.ExpiredSignatureError as e:
        raise AuthenticationFailed("Access token has expired.") from e

    except jwt.InvalidTokenError as e:
        raise AuthenticationFailed("Invalid access token.") from e

    except KeyError as e:
        raise AuthenticationFailed("Invalid access token payload.") from e


# ==========================================================
# REFRESH TOKEN: Long-lived token used to obtain a new
# access token without requiring the user to log in again.
# ==========================================================

def create_refresh_token(user_id, role):
    now = datetime.now(timezone.utc)

    payload = {
        "user_id": user_id,
        "role": role,
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + timedelta(days=7),
        "token_type": "refresh",
    }

    secret_key = os.getenv("JWT_REFRESH_SECRET_KEY")

    if not secret_key:
        raise RuntimeError(
            "JWT_REFRESH_SECRET_KEY not found in .env"
        )

    return jwt.encode(
        payload,
        secret_key,
        algorithm="HS256",
    )


# This is useful for logout and refresh operations
def decode_refresh_token_payload(token):
    """
    Validate the refresh token and return its complete payload.
    The logout API can use jti and exp to revoke the token.
    """
    secret_key = os.getenv("JWT_REFRESH_SECRET_KEY")

    if not secret_key:
        raise RuntimeError("JWT_REFRESH_SECRET_KEY not found in .env")

    try:
        payload = jwt.decode(token,secret_key,algorithms=["HS256"],)

        if payload.get("token_type") != "refresh":
            raise AuthenticationFailed("Invalid refresh token type.")

        if not payload.get("jti"):
            raise AuthenticationFailed("Refresh token ID is missing.")

        if "user_id" not in payload:
            raise AuthenticationFailed("Refresh token user ID is missing.")

        return payload

    except jwt.ExpiredSignatureError as e:
        raise AuthenticationFailed("Refresh token has expired.") from e

    except jwt.InvalidTokenError as e:
        raise AuthenticationFailed("Invalid refresh token.") from e


def decode_refresh_token(token):
    """
    Preserve the original function's return value:
    the user ID, not the complete payload.
    """
    payload = decode_refresh_token_payload(token)
    return payload["user_id"]

