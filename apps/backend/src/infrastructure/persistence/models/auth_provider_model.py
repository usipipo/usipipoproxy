"""Modelo SQLAlchemy para proveedores de autenticación."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.infrastructure.persistence.database import Base


class AuthProviderModel(Base):
    """
    Modelo para proveedores de autenticación.

    Desacopla el método de autenticación del usuario, permitiendo:
    - Múltiples métodos de auth por usuario (Telegram, email, Google, etc.)
    - Usuarios sin Telegram (Android, Desktop, Web)
    - Migración gradual de Telegram a otros métodos
    """

    __tablename__ = "auth_providers"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="Provider type: telegram, email, google, apple"
    )
    provider_user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Unique identifier within provider (email, telegram_id, google_sub)",
    )
    password_hash: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Hashed password (only for email provider)"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Last successful authentication"
    )

    # Unique constraint: one provider_user_id per provider type
    __table_args__ = (
        Index("ix_auth_providers_provider_user_id", "provider", "provider_user_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<AuthProvider(id={self.id}, user_id={self.user_id}, provider={self.provider})>"
