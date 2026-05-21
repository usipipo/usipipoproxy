"""Schemas para gestión de usuarios."""

from pydantic import BaseModel, Field


class TelegramProfileSyncRequest(BaseModel):
    """
    Solicitud para sincronizar perfil de Telegram.

    Attributes:
        telegram_id: ID de Telegram del usuario
        username: Username actual de Telegram
        first_name: Nombre actual del usuario
        last_name: Apellido actual del usuario
    """

    telegram_id: int = Field(..., description="Telegram user ID")
    username: str | None = Field(None, description="Telegram username")
    first_name: str | None = Field(None, description="User first name")
    last_name: str | None = Field(None, description="User last name")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "telegram_id": 123456789,
                    "username": "develop",
                    "first_name": "Developer",
                    "last_name": "User",
                }
            ]
        }
    }


class ProfileSyncResponse(BaseModel):
    """
    Respuesta de sincronización de perfil.

    Attributes:
        success: Si la sincronización fue exitosa
        user_id: ID del usuario actualizado
        updated: Si se actualizaron datos (True) o ya estaban actualizados (False)
    """

    success: bool
    user_id: str
    updated: bool

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "updated": True,
                }
            ]
        }
    }
