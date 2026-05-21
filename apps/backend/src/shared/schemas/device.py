"""Device schemas for push notification management."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DeviceRegisterRequest(BaseModel):
    """Solicitud de registro de dispositivo."""

    platform: str = Field(..., pattern="^(android|ios|windows|linux|telegram)$")
    push_token: str | None = Field(None, max_length=500)
    app_version: str | None = Field(None, max_length=20)
    device_name: str | None = Field(None, max_length=100)


class DeviceResponse(BaseModel):
    """Respuesta de dispositivo registrado."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    platform: str
    push_token: str | None = None
    app_version: str | None = None
    device_name: str | None = None
    created_at: datetime
    last_active_at: datetime | None = None
    is_active: bool


class DeviceListResponse(BaseModel):
    """Lista de dispositivos."""

    devices: list[DeviceResponse]
    total: int
