"""WireGuard metrics database model."""

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.infrastructure.persistence.database import Base


class WireGuardMetricModel(Base):
    """Time-series metrics for WireGuard VPN peers.

    Stores per-peer metrics collected every 5 minutes.
    """

    __tablename__ = "wireguard_metrics"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    server_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vpn_servers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    peer_public_key: Mapped[str] = mapped_column(String, nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    # Peer metrics
    bytes_received: Mapped[int | None] = mapped_column(BigInteger, nullable=True, default=0)
    bytes_sent: Mapped[int | None] = mapped_column(BigInteger, nullable=True, default=0)
    last_handshake: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_connected: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_wg_metrics_server_peer_time", "server_id", "peer_public_key", timestamp.desc()),
        Index("idx_wg_metrics_timestamp", timestamp.desc()),
    )

    def __repr__(self) -> str:
        return (
            f"<WireGuardMetricModel(server_id={self.server_id}, "
            f"peer={self.peer_public_key[:10]}..., connected={self.is_connected})>"
        )

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "server_id": self.server_id,
            "peer_public_key": self.peer_public_key,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "bytes_received": self.bytes_received,
            "bytes_sent": self.bytes_sent,
            "last_handshake": self.last_handshake.isoformat() if self.last_handshake else None,
            "is_connected": self.is_connected,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
