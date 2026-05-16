from datetime import UTC, datetime, timedelta
from uuid import uuid4

from jose import JWTError, jwt

from app.core.config import settings

ACCESS_TOKEN_TYPE = "access"  # nosec B105
REFRESH_TOKEN_TYPE = "refresh"  # nosec B105
BEARER_TOKEN_TYPE = "bearer"  # nosec B105


def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "token_type": ACCESS_TOKEN_TYPE,
        "jti": str(uuid4()),
        "iat": datetime.now(UTC),
        "exp": expires_at,
    }

    token = jwt.encode(
        payload,
        settings.access_token_secret,
        algorithm=settings.jwt_algorithm,
    )

    return token


def create_refresh_token(user_id: int) -> str:
    expires_at = datetime.now(UTC) + timedelta(
        days=settings.refresh_token_expire_days
    )

    payload = {
        "sub": str(user_id),
        "token_type": REFRESH_TOKEN_TYPE,
        "jti": str(uuid4()),
        "iat": datetime.now(UTC),
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

    if payload.get("token_type") != ACCESS_TOKEN_TYPE:
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

    if payload.get("token_type") != REFRESH_TOKEN_TYPE:
        raise ValueError("Invalid refresh token type")

    return payload


def get_token_remaining_seconds(payload: dict) -> int:
    expires_at = payload.get("exp")

    if not expires_at:
        return 0

    current_timestamp = int(datetime.now(UTC).timestamp())
    remaining_seconds = int(expires_at) - current_timestamp

    if remaining_seconds < 0:
        return 0

    return remaining_seconds