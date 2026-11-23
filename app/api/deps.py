from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.core.security import decode_token
from app.database.session import get_db
from app.models.all import User
from app.services.user_services import get_user

db_session = Annotated[AsyncSession, Depends(get_db)]
form_data = Annotated[OAuth2PasswordRequestForm, Depends()]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(db: db_session, token: str = Depends(oauth2_scheme)) -> User:
    payload = decode_token(token)
    if (
        not payload
        or not payload.get("id")
        or not payload.get("sub")
        or payload.get("type") != "access"
    ):
        raise UnauthorizedError("Invalid token, please try to login again.")

    user = await get_user(db, payload.get("sub"))

    if not user:
        raise UnauthorizedError("Invalid token, please try to login again.")

    return user


current_user = Annotated[User, Depends(get_current_user)]
