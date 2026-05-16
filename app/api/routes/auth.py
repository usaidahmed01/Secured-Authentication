from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import oauth2_scheme
from app.db.redis import get_redis
from app.db.session import get_db
from app.schemas import (
    StandardActionResponse,
    TokenExchangeResponse,
    TokenRefreshRequest,
    UserCreate,
    UserRegistrationResponse,
)
from app.services import (
    authenticate_user,
    blacklist_access_token,
    create_user,
    get_user_by_email,
    get_user_by_id,
)
from app.utils import (
    BEARER_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    get_token_remaining_seconds,
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
    "/register",
    response_model=UserRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    existing_user = await get_user_by_email(db, user_data.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = await create_user(db, user_data)

    return user


@router.post(
    "/login",
    response_model=TokenExchangeResponse,
)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(
        db=db,
        email=form_data.username,
        password=form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": BEARER_TOKEN_TYPE,
    }


@router.post(
    "/refresh",
    response_model=TokenExchangeResponse,
)
async def refresh_tokens(
    token_data: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = decode_refresh_token(token_data.refresh_token)
        user_id = int(payload.get("sub"))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    user = await get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": BEARER_TOKEN_TYPE,
    }


@router.post(
    "/logout",
    response_model=StandardActionResponse,
)
async def logout_user(
    token: str = Depends(oauth2_scheme),
    redis: Redis = Depends(get_redis),
):
    try:
        payload = decode_access_token(token)
        token_jti = payload.get("jti")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    if not token_jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    remaining_seconds = get_token_remaining_seconds(payload)

    if remaining_seconds > 0:
        await blacklist_access_token(
            redis=redis,
            token_jti=token_jti,
            expires_in_seconds=remaining_seconds,
        )

    return {
        "detail": "Revocation complete",
    }