
import uuid

from sqlalchemy import String, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class GmailConnection(Base):
    __tablename__ = "gmail_connections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    email_address: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    access_token: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    refresh_token: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    token_expiry: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    scopes: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="connected",
        nullable=False,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
