"""Schemas para VPN."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field
from usipipo_commons.domain.enums.key_status import KeyStatus
from usipipo_commons.domain.enums.key_type import KeyType


class VpnKeyResponse(BaseModel):
    """Respuesta de clave VPN."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    server_id: UUID | None = None
    server_name: str | None = None
    name: str
    key_type: KeyType
    status: KeyStatus = KeyStatus.ACTIVE
    config: str | None = None
    deeplink: str = ""
    created_at: datetime
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    data_used_gb: float = 0.0
    data_limit_gb: float

    @computed_field  # type: ignore[prop-decorator]
    @property
    def vpn_type(self) -> KeyType:
        """Alias para key_type (compatibilidad con API)."""
        return self.key_type


class CreateVpnKeyRequest(BaseModel):
    """Solicitud para crear clave VPN."""

    name: str = Field(..., min_length=1, max_length=50, description="Nombre de la clave")
    vpn_type: KeyType = Field(..., description="Tipo de VPN")
    data_limit_gb: float = Field(default=5.0, ge=0.1, le=100.0, description="Límite de datos en GB")
    server_id: UUID | None = Field(
        default=None, description="ID del servidor seleccionado (opcional)"
    )


class UpdateVpnKeyRequest(BaseModel):
    """Solicitud para actualizar clave VPN."""

    name: str | None = Field(None, min_length=1, max_length=50)
    data_limit_gb: float | None = Field(None, ge=0.1, le=100.0)


class VpnServerResponse(BaseModel):
    """User-facing VPN server response schema."""

    id: UUID
    name: str
    country_code: str
    country_name: str
    city: str | None
    load_percentage: int = Field(..., ge=0, le=100, description="Server load percentage (0-100)")
    status: str  # "online", "offline", "maintenance"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def load_level(self) -> Literal["low", "medium", "high"]:
        """Determine load level: low (0-50%), medium (51-80%), high (81-100%)."""
        if self.load_percentage <= 50:
            return "low"
        elif self.load_percentage <= 80:
            return "medium"
        return "high"


class VpnServersListResponse(BaseModel):
    """Response for list of available VPN servers."""

    servers: list[VpnServerResponse]
    recommended: list[VpnServerResponse]  # Top 5 lowest load


# (Outline and TrustTunnel schemas removed - WireGuard only)
