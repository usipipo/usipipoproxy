"""SQLAlchemy model for agent API keys."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.vpn_server_model import VpnServerModel


class AgentApiKeyModel(Base):
    """Model for agent API keys.

    Stores hashed API keys for agent authentication and registration.
    Each key can only be used once for registration.
    """

    __tablename__ = "agent_api_keys"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    api_key_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    # Values: active, used, revoked, expired

    server_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vpn_servers.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    used_at: Mapped[datetime | None] = mapped_column(nullable=True)

    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)

    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    # Relationships
    server: Mapped[Optional["VpnServerModel"]] = relationship(
        "VpnServerModel", back_populates="agent_api_key_rel", uselist=False
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('active', 'used', 'revoked', 'expired')", name="chk_status"),
    )

    def __repr__(self) -> str:
        return f"<AgentApiKey {self.id} - {self.status}>"
