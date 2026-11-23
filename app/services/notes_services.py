from math import ceil
from typing import Optional
from uuid import UUID

from fastapi_pagination import Params, Page, paginate
from sqlalchemy import select, func, update, or_, any_, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.all import Note, Tag
from app.schemas.notes import NoteCreate, NoteResponse, PageResponse, NoteUpdate
from app.services.tag_services import get_or_create_tag


async def create_note(
    db: AsyncSession, note_data: NoteCreate, user_id: UUID
) -> NoteResponse:
    note_dict = note_data.model_dump()
    note_dict["user_id"] = user_id
    tags = note_dict.pop("tags")
    note = Note(**note_dict)

    for tag_name in tags:
        tag = await get_or_create_tag(db, name=tag_name)
        note.tags.append(tag)

    db.add(note)
    await db.commit()
    await db.refresh(note)

    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        is_archived=note.is_archived,
        tags=[tag.name for tag in note.tags],
    )


async def get_note(db: AsyncSession, note_id: UUID, user_id: UUID) -> NoteResponse:
    note = await db.scalar(
        select(Note).where(
            Note.user_id == user_id,
            Note.id == note_id
        )
    )

    if not note:
        raise NotFoundError("Note doesn't exist.")

    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        is_archived=note.is_archived,
        tags=[tag.name for tag in note.tags],
    )


async def get_user_notes_with_fastapi_pagination(
    db: AsyncSession, user_id: UUID, params: Params
) -> Page[NoteResponse]:
    query = select(Note).where(Note.user_id == user_id)

    notes = await db.scalars(query)

    formatted_notes = []

    for note in notes:
        current_note = NoteResponse(
            id=note.id,
            title=note.title,
            content=note.content,
            is_archived=note.is_archived,
            tags=[tag.name for tag in note.tags],
        )

        formatted_notes.append(current_note)

    return paginate(formatted_notes, params=params)


async def get_user_notes_with_manual_pagination(
    db: AsyncSession, user_id: UUID, page: int = 1, size: int = 10
) -> PageResponse:
    count_stmt = select(func.count()).select_from(Note).where(Note.user_id == user_id)
    total_result = await db.execute(count_stmt)

    total = total_result.scalar_one()

    offset = (page - 1) * size

    query = select(Note).where(Note.user_id == user_id).offset(offset).limit(10)

    result = await db.execute(query)
    notes = [NoteResponse.model_validate(x) for x in result.scalars().all()]
    pages = ceil(total / size) if total else 0

    return PageResponse(items=notes, total=total, page=page, size=size, pages=pages)


async def get_notes_with_given_keyword(
    db: AsyncSession, user_id: UUID, keyword: str, params: Params
) -> Page[NoteResponse]:
    query = (
        select(Note)
        .where(
            Note.user_id == user_id,
        )
        .filter(
            or_(Note.title.ilike(f"%{keyword.casefold()}%"), Note.content.ilike(f"%{keyword.casefold()}%"))
        )
    )

    notes = await db.scalars(query)

    formatted_notes = []

    for note in notes:
        current_note = NoteResponse(
            id=note.id,
            title=note.title,
            content=note.content,
            is_archived=note.is_archived,
            tags=[tag.name for tag in note.tags],
        )

        formatted_notes.append(current_note)

    return paginate(formatted_notes, params=params)


async def get_notes_with_given_tag(
    db: AsyncSession, tag: str, user_id: UUID, params: Params
) -> Page[NoteResponse]:
    query = (
        select(Note)
        .where(
            Note.user_id == user_id,
        ).filter(
           Note.tags.any(Tag.name == tag)
        )
        )

    notes = await db.scalars(query)

    formatted_notes = []

    for note in notes:
        current_note = NoteResponse(
            id=note.id,
            title=note.title,
            content=note.content,
            is_archived=note.is_archived,
            tags=[tag.name for tag in note.tags],
        )

        formatted_notes.append(current_note)

    return paginate(formatted_notes, params=params)


async def _get_notes(
    db: AsyncSession,
    user_id: UUID,
    search: Optional[str],
    tag: Optional[str],
    id: Optional[UUID],
    params: Params,
):
    if search:
        return await get_notes_with_given_keyword(db, user_id, search, params)

    if tag:
        return await get_notes_with_given_tag(db, tag, user_id, params)

    if id:
        return paginate([await get_note(db, note_id=id, user_id=user_id)])

    return await get_user_notes_with_fastapi_pagination(
        db, user_id=user_id, params=params
    )


async def update_note(
    db: AsyncSession, note_data: NoteUpdate, user_id: UUID, note_id: UUID
) -> Page[NoteResponse]:
    note = await get_note(db, note_id, user_id)

    note_dict = note_data.model_dump(exclude_none=True)
    note_tags: list[dict[str, str]] = note_dict.pop("tags")

    stmt = (
        update(Note)
        .where(Note.id == note_id, Note.user_id == user_id)
        .values(**note_dict)
    )

    for tag_dict in note_tags:
        tag = await get_or_create_tag(db, tag_dict["name"])
        note.tags.append(tag)

    await db.execute(stmt)
    await db.commit()

    await db.refresh(note)

    return paginate([note])


async def delete_note(db: AsyncSession, user_id: UUID, note_id: UUID):
    note = await get_note(db, note_id, user_id)

    await db.delete(note)
    await db.commit()

    return
