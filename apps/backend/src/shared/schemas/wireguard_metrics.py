"""WireGuard metrics response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WireGuardPeerMetricsResponse(BaseModel):
    """Response schema for individual WireGuard peer metrics."""

    model_config = ConfigDict(from_attributes=True)

    peer_public_key: str
    bytes_received: int | None = None
    bytes_sent: int | None = None
    last_handshake: datetime | None = None
    is_connected: bool | None = None
    collected_at: datetime


class WireGuardServerMetricsResponse(BaseModel):
    """Response schema for aggregated WireGuard server metrics."""

    model_config = ConfigDict(from_attributes=True)

    server_id: UUID
    peer_count: int
    connected_peers: int
    total_bytes_rx: int
    total_bytes_tx: int
    last_handshake: datetime | None = None
    peers: list[WireGuardPeerMetricsResponse]


class WireGuardMetricsTimeSeriesPoint(BaseModel):
    """Single point in WireGuard metrics time-series."""

    model_config = ConfigDict(from_attributes=True)

    timestamp: str
    peer_count: int | None = None
    connected_peers: int | None = None
    total_bytes_rx: int | None = None
    total_bytes_tx: int | None = None


class WireGuardMetricsResponse(BaseModel):
    """Response for WireGuard metrics endpoint."""

    model_config = ConfigDict(from_attributes=True)

    server_id: UUID
    time_range: str
    time_series: list[WireGuardMetricsTimeSeriesPoint]
    summary: dict
