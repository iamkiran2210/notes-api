from datetime import timedelta, datetime, UTC
from typing import Any, Literal, Optional

import jwt

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.models.all import User

password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        password_hasher.verify(hashed_password, password)
        return True

    except VerifyMismatchError:
        return False


def create_token(
    user: User,
    token_type: Literal["access", "refresh"],
    expires_delta: Optional[timedelta] = None,
):
    if token_type == "access":
        expires = settings.ACCESS_TOKEN_EXPIRY_IN_MINUTES
    else:
        expires = settings.REFRESH_TOKEN_EXPIRY_IN_MINUTES
    payload = {
        "sub": str(user.username),
        "id": str(user.id),
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + (expires_delta or timedelta(minutes=expires)),
        "type": token_type,
    }

    return jwt.encode(payload, key=settings.JWT_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token, key=settings.JWT_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Request timed out.")

    except jwt.PyJWTError:
        raise UnauthorizedError("Invalid, try to login again.")
