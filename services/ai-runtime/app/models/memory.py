import uuid
from datetime import datetime, timezone
from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    embedding: Mapped[list[float] | None] = mapped_column(
    Vector(384),
    nullable=True
    )

    memory_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )