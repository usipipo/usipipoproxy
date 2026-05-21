"""Auth schemas for email/password authentication."""

from pydantic import BaseModel, EmailStr, Field


class EmailRegisterRequest(BaseModel):
    """Solicitud de registro con email/password."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    display_name: str = Field(..., min_length=1, max_length=50)


class EmailLoginRequest(BaseModel):
    """Solicitud de login con email/password."""

    email: EmailStr
    password: str


class TelegramCodeRequest(BaseModel):
    """Solicitud de código de autenticación vía Telegram."""

    telegram_id: int


class TelegramAutoRegisterRequest(BaseModel):
    """Solicitud de registro automático desde Telegram Bot.

    Usado para autenticación invisible sin intervención del usuario.

    Attributes:
        telegram_id: ID único de Telegram del usuario
        username: Username de Telegram (opcional, puede cambiar)
        first_name: Nombre del usuario (opcional)
        last_name: Apellido del usuario (opcional)
    """

    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None

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


class TelegramVerifyRequest(BaseModel):
    """Verificación de código de Telegram."""

    telegram_id: int
    code: str = Field(..., min_length=6, max_length=6)


class RefreshTokenRequest(BaseModel):
    """Solicitud de refresh de token."""

    refresh_token: str


class AuthResponse(BaseModel):
    """Respuesta de autenticación con tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires
    user_id: str


class CodeSentResponse(BaseModel):
    """Respuesta cuando se envía código de verificación."""

    success: bool
    message: str
    expires_in: int  # seconds until code expires
