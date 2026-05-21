"""SQLAlchemy model for VPN servers."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from usipipo_commons.domain.entities.server import Server

from src.infrastructure.persistence.database import Base
from src.shared.encryption import decrypt_sensitive_data, encrypt_sensitive_data

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.agent_api_key_model import AgentApiKeyModel


class VpnServerModel(Base):
    """SQLAlchemy model for VPN server registry."""

    __tablename__ = "vpn_servers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    country_name: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    region: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Agent configuration (encrypted at rest)
    agent_url: Mapped[str] = mapped_column(String(500), nullable=False)
    _agent_api_key: Mapped[str] = mapped_column("agent_api_key", String(512), nullable=False)

    # Supported protocols (WireGuard only)
    supports_wireguard: Mapped[bool] = mapped_column(Boolean, default=True)

    # Status and capacity
    status: Mapped[str] = mapped_column(String(20), default="online", index=True)
    max_connections: Mapped[int] = mapped_column(Integer, default=1000)
    current_connections: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    # Agent metadata (added for auto-registration)
    agent_version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    os_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    os_arch: Mapped[str | None] = mapped_column(String(20), nullable=True)
    last_registration_ip: Mapped[str | None] = mapped_column(INET, nullable=True)

    # Relationship to agent API key
    agent_api_key_rel: Mapped[Optional["AgentApiKeyModel"]] = relationship(
        "AgentApiKeyModel",
        back_populates="server",
        uselist=False,
        foreign_keys="AgentApiKeyModel.server_id",
    )

    # Unique constraint on country_code + region
    __table_args__ = (UniqueConstraint("country_code", "region", name="uq_country_region"),)

    @property
    def agent_api_key(self) -> str:
        """Decrypt API key when accessed."""
        try:
            return decrypt_sensitive_data(self._agent_api_key)
        except Exception:
            # Fallback for legacy unencrypted keys
            return self._agent_api_key

    @agent_api_key.setter
    def agent_api_key(self, value: str) -> None:
        """Encrypt API key when set."""
        try:
            self._agent_api_key = encrypt_sensitive_data(value)
        except RuntimeError:
            # Fallback if encryption not configured
            self._agent_api_key = value

    def to_entity(self) -> Server:
        """Convert model to domain entity."""
        return Server(
            id=self.id,
            name=self.name,
            country_code=self.country_code,
            country_name=self.country_name,
            city=self.city,
            region=self.region,
            agent_url=self.agent_url,
            agent_api_key=self.agent_api_key,  # Automatically decrypted
            supports_wireguard=self.supports_wireguard,
            status=self.status,
            max_connections=self.max_connections,
            current_connections=self.current_connections,
            created_at=self.created_at,
            updated_at=self.updated_at,
            last_heartbeat_at=self.last_heartbeat_at,
        )

    @classmethod
    def from_entity(cls, entity: Server) -> "VpnServerModel":
        """Create model from domain entity."""
        return cls(
            id=entity.id,
            name=entity.name,
            country_code=entity.country_code,
            country_name=entity.country_name,
            city=entity.city,
            region=entity.region,
            agent_url=entity.agent_url,
            agent_api_key=entity.agent_api_key,  # Automatically encrypted
            supports_wireguard=entity.supports_wireguard,
            status=entity.status,
            max_connections=entity.max_connections,
            current_connections=entity.current_connections,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            last_heartbeat_at=entity.last_heartbeat_at,
        )
