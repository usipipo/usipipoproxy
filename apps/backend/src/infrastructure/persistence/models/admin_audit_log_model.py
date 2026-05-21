"""Modelo SQLAlchemy para logs de auditoría administrativa."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.infrastructure.persistence.database import Base


class AdminAuditLogModel(Base):
    """Modelo SQLAlchemy para logs de auditoría administrativa."""

    __tablename__ = "admin_audit_logs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    admin_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    admin_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    operation: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    target_user_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)  # IPv6 max length
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (Index("idx_audit_logs_target", "target_type", "target_id"),)

    def to_entity(self) -> dict:
        """Convert model to dictionary entity.

        Returns:
            Dictionary representation of audit log.
        """
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "admin_id": self.admin_id,
            "admin_username": self.admin_username,
            "operation": self.operation,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "target_user_id": self.target_user_id,
            "details": self.details,
            "ip_address": self.ip_address,
            "success": self.success,
            "error_message": self.error_message,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AdminAuditLogModel":
        """Create model from dictionary.

        Args:
            data: Dictionary with audit log data.

        Returns:
            AdminAuditLogModel instance.
        """
        return cls(
            id=data.get("id", uuid4()),
            timestamp=data.get("timestamp", datetime.now()),
            admin_id=data["admin_id"],
            admin_username=data.get("admin_username"),
            operation=data["operation"],
            target_type=data["target_type"],
            target_id=data["target_id"],
            target_user_id=data.get("target_user_id"),
            details=data.get("details"),
            ip_address=data.get("ip_address"),
            success=data["success"],
            error_message=data.get("error_message"),
        )
