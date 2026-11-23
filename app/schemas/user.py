import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
