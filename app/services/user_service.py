from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas import UserCreate
from app.utils import hash_password, verify_password


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    return user


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    return user


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    hashed_password = hash_password(user_data.password)

    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User | None:
    user = await get_user_by_email(db, email)

    if not user:
        return None

    password_is_valid = verify_password(password, user.hashed_password)

    if not password_is_valid:
        return None

    if not user.is_active:
        return None

    return user