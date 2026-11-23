from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import hash_password, verify_password
from app.models.all import User
from app.schemas.user import UserCreate, UserResponse
from app.core.exceptions import AlreadyExistsError, UnauthorizedError, NotFoundError


async def create_user(db: AsyncSession, user_data: UserCreate) -> UserResponse:
    user = user_data.model_dump()

    current_user = await get_user(db, user["username"])
    if current_user:
        raise AlreadyExistsError("User already exists.")

    user["password_hash"] = hash_password(user.pop("password"))
    user = User(**user)

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


async def verify_user(
    db: AsyncSession, username: str, password: str
) -> dict[str, str] | None | Any:
    user = await get_user(db, username)

    if not user:
        raise NotFoundError("No account found, try registering into a new account.")

    if not verify_password(password, str(user.password_hash)):
        raise UnauthorizedError("Invalid credentials.")

    return user


async def get_user(db: AsyncSession, username: str) -> Optional[User]:
    statement = select(User).where(User.username == username)
    user = await db.scalar(statement=statement)

    return user
