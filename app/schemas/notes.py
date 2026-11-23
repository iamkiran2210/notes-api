import uuid
from typing import Optional, TypeVar, Generic

from pydantic import BaseModel, ConfigDict

from app.schemas.tags import TagModel

T = TypeVar("T")


class NoteCreate(BaseModel):
    title: str
    content: str
    is_archived: bool = False
    tags: list[str]


class NoteResponse(NoteCreate):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_archived: Optional[bool] = None
    tags: Optional[list["TagModel"]] = None


class PageResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
