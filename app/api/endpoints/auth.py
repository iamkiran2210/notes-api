from fastapi import APIRouter, Depends

from app.api.deps import db_session, form_data, current_user
from app.core.security import create_token
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.services.user_services import create_user, verify_user

router = APIRouter()


@router.post("/register")
async def register(db: db_session, user_data: UserCreate) -> UserResponse:
    return await create_user(db, user_data)


@router.post("/login")
async def login(db: db_session, user_data: form_data) -> Token:
    user = await verify_user(db, user_data.username, user_data.password)

    return Token(
        access_token=create_token(user, "access"),
        refresh_token=create_token(user, "refresh"),
    )


@router.get("/me")
async def get_current_user_details(user: current_user):
    return user
