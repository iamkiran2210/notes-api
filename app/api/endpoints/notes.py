from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query, Path, Depends
from fastapi_pagination import Page, Params
from fastapi_pagination.iterables import paginate

from starlette import status

from app.api.deps import db_session, current_user
from app.schemas.notes import NoteCreate, NoteResponse, NoteUpdate
from app.services.notes_services import (
    create_note,
    delete_note,
    update_note,
    get_note,
    _get_notes,
)

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_notes(
    user: current_user, db: db_session, notes: NoteCreate
) -> NoteResponse:
    return NoteResponse.model_validate(await create_note(db, notes, user.id))


@router.get("/{id}")
async def get_notes_based_on_id(
    user: current_user, db: db_session, id: UUID
) -> NoteResponse:
    return NoteResponse.model_validate(await get_note(db, note_id=id, user_id=user.id))


@router.get("/")
async def get_notes(
    user: current_user,
    db: db_session,
    id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None, min_length=2, max_length=30),
    tag: Optional[str] = Query(None, min_length=2, max_length=50),
    params: Params = Depends(),
) -> Page[NoteResponse]:
    return await _get_notes(
        db, user_id=user.id, tag=tag, search=search, id=id, params=params
    )


@router.patch("/{id}")
async def update_notes_based_on_id(
    user: current_user,
    db: db_session,
    note_data: NoteUpdate,
    id: UUID,
) -> Page[NoteResponse]:
    return await update_note(db, user_id=user.id, note_id=id, note_data=note_data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notes_based_on_id(
    user: current_user, db: db_session, id: UUID = Path()
):
    return await delete_note(db, user_id=user.id, note_id=id)
