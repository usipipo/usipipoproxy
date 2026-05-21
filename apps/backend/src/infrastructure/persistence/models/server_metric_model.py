"""SQLAlchemy model for server metrics."""

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.infrastructure.persistence.database import Base


class ServerMetricModel(Base):
    """SQLAlchemy model for VPN server metrics."""

    __tablename__ = "server_metrics"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    server_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vpn_servers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    # System metrics
    cpu_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    memory_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    disk_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    network_rx_bytes: Mapped[int] = mapped_column(BigInteger, nullable=True)
    network_tx_bytes: Mapped[int] = mapped_column(BigInteger, nullable=True)

    # VPN metrics
    wireguard_active_peers: Mapped[int] = mapped_column(nullable=True)
    total_bytes_transferred: Mapped[int] = mapped_column(BigInteger, nullable=True)

    # Latency metrics
    latency_avg_ms: Mapped[float] = mapped_column(Numeric(8, 2), nullable=True)
    latency_p95_ms: Mapped[float] = mapped_column(Numeric(8, 2), nullable=True)
    latency_p99_ms: Mapped[float] = mapped_column(Numeric(8, 2), nullable=True)

    # Composite index for efficient time-series queries
    __table_args__ = (Index("idx_server_timestamp", "server_id", timestamp.desc()),)

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "server_id": str(self.server_id),
            "timestamp": self.timestamp.isoformat(),
            "cpu_percent": float(self.cpu_percent) if self.cpu_percent else None,
            "memory_percent": float(self.memory_percent) if self.memory_percent else None,
            "disk_percent": float(self.disk_percent) if self.disk_percent else None,
            "network_rx_bytes": self.network_rx_bytes,
            "network_tx_bytes": self.network_tx_bytes,
            "wireguard_active_peers": self.wireguard_active_peers,
            "total_bytes_transferred": self.total_bytes_transferred,
            "latency_avg_ms": float(self.latency_avg_ms) if self.latency_avg_ms else None,
            "latency_p95_ms": float(self.latency_p95_ms) if self.latency_p95_ms else None,
            "latency_p99_ms": float(self.latency_p99_ms) if self.latency_p99_ms else None,
        }
