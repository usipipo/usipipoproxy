"""Modelo SQLAlchemy para roles de personal."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.infrastructure.persistence.database import Base


class StaffRoleModel(Base):
    """Modelo SQLAlchemy para roles de personal."""

    __tablename__ = "staff_roles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    admin_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), unique=True, nullable=False, index=True
    )
    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger, unique=True, nullable=True, index=True
    )
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, server_default="support")
    granted_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=func.true())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def to_entity(self) -> dict:
        """Convert model to dictionary entity.

        Returns:
            Dictionary representation of staff role.
        """
        return {
            "id": self.id,
            "admin_id": self.admin_id,
            "telegram_id": self.telegram_id,
            "username": self.username,
            "role": self.role,
            "granted_by": self.granted_by,
            "granted_at": self.granted_at,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StaffRoleModel":
        """Create model from dictionary.

        Args:
            data: Dictionary with staff role data.

        Returns:
            StaffRoleModel instance.
        """
        return cls(
            id=data.get("id", uuid4()),
            admin_id=data["admin_id"],
            telegram_id=data.get("telegram_id"),
            username=data.get("username"),
            role=data.get("role", "support"),
            granted_by=data.get("granted_by"),
            granted_at=data.get("granted_at", datetime.now()),
            is_active=data.get("is_active", True),
        )
