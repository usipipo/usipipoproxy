"""Modelo SQLAlchemy para dispositivos de usuarios."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.infrastructure.persistence.database import Base


class DeviceModel(Base):
    """
    Modelo para dispositivos registrados de usuarios.

    Permite enviar notificaciones push a múltiples dispositivos por usuario.
    Soporta Android, iOS, Windows, Linux y Telegram.
    """

    __tablename__ = "devices"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="UUID del usuario propietario",
    )
    platform: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="Plataforma: android, ios, windows, linux, telegram"
    )
    push_token: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="FCM token para push notifications (null para Telegram)"
    )
    app_version: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="Versión de la aplicación"
    )
    device_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Nombre del dispositivo (ej: 'iPhone 14', 'Windows PC')"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_active_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Última actividad del dispositivo"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="True si el dispositivo está activo"
    )

    def __repr__(self) -> str:
        return f"<Device(id={self.id}, user_id={self.user_id}, platform={self.platform})>"
