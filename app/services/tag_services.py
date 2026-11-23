from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.all import Tag


async def get_or_create_tag(db: AsyncSession, name: str) -> Tag:
    result = await db.execute(select(Tag).where(Tag.name == name))

    tag = result.scalar_one_or_none()

    if tag:
        return tag

    tag = Tag(name=name)

    db.add(tag)
    await db.flush()

    return tag
