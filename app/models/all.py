import re
from datetime import datetime, UTC
import uuid
from app.database.base import Base
from sqlalchemy import Text, String, DATETIME, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DATETIME,
        default=datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DATETIME, default=datetime.now(UTC), onupdate=datetime.now(UTC)
    )

    notes: Mapped[list["Note"]] = relationship("Note", back_populates="user")


note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_archived: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DATETIME, default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DATETIME, default=datetime.now(UTC), onupdate=datetime.now(UTC)
    )
    user: Mapped["User"] = relationship(back_populates="notes")
    tags: Mapped[list["Tag"]] = relationship(
        secondary=note_tags, back_populates="notes", lazy="selectin"
    )


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DATETIME, default=datetime.now(UTC))
    notes: Mapped[list["Note"]] = relationship(
        "Note", secondary=note_tags, back_populates="tags"
    )
