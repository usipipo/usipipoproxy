from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

from ..domain.enums.key_type import KeyType
from ..domain.enums.key_status import KeyStatus


class VpnKeyResponse(BaseModel):
    """Respuesta de clave VPN."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    key_type: KeyType
    status: KeyStatus
    config: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    data_used_gb: float = Field(ge=0)
    data_limit_gb: float = Field(ge=0)


class CreateVpnKeyRequest(BaseModel):
    """Solicitud para crear clave VPN."""
    name: str = Field(..., min_length=1, max_length=50)
    key_type: KeyType  # ← Changed from vpn_type: VpnType
    data_limit_gb: float = Field(default=5.0, ge=0.1, le=100.0)


class UpdateVpnKeyRequest(BaseModel):
    """Solicitud para actualizar clave VPN."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    data_limit_gb: Optional[float] = Field(None, ge=0.1, le=100.0)
