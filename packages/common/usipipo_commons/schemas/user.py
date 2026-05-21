from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class UserResponse(BaseModel):
    """Respuesta de usuario."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    balance_gb: float = Field(ge=0)
    total_purchased_gb: float = Field(ge=0)
    referral_code: str
    referred_by: Optional[UUID]


class UserCreateRequest(BaseModel):
    """Solicitud para crear usuario."""
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    referral_code: Optional[str] = None


class UserUpdateRequest(BaseModel):
    """Solicitud para actualizar usuario."""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
