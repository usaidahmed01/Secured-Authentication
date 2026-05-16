from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import JWTError, jwt

from app.core.config import settings


def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "token_type": "access",
        "jti": str(uuid4()),
        "iat": datetime.now(timezone.utc),
        "exp": expires_at,
    }

    token = jwt.encode(
        payload,
        settings.access_token_secret,
        algorithm=settings.jwt_algorithm,
    )

    return token


def create_refresh_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )

    payload = {
        "sub": str(user_id),
        "token_type": "refresh",
        "jti": str(uuid4()),
        "iat": datetime.now(timezone.utc),
        "exp": expires_at,
    }

    token = jwt.encode(
        payload,
        settings.refresh_token_secret,
        algorithm=settings.jwt_algorithm,
    )

    return token


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.access_token_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as error:
        raise ValueError("Invalid access token") from error

    if payload.get("token_type") != "access":
        raise ValueError("Invalid access token type")

    return payload


def decode_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.refresh_token_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as error:
        raise ValueError("Invalid refresh token") from error

    if payload.get("token_type") != "refresh":
        raise ValueError("Invalid refresh token type")

    return payload