"""Seguridad JWT para autenticación."""

import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
import redis

from ...shared.config import settings

logger = logging.getLogger(__name__)


def revoke_token(token: str, expires_in_seconds: int) -> None:
    """
    Añade token a blacklist en Redis.

    Crea una conexión nueva por llamada (seguro para multi-worker).
    Si Redis no está disponible, loggea warning y continúa (el token expirará naturalmente).

    Args:
        token: JWT token a revocar
        expires_in_seconds: Tiempo de expiración en segundos
    """
    try:
        r = redis.Redis.from_url(
            settings.REDIS_URL,
            socket_timeout=5,
            decode_responses=True,
        )
        r.setex(f"revoked_token:{token[:32]}", expires_in_seconds, "1")
        r.close()
    except (redis.ConnectionError, redis.TimeoutError) as e:
        logger.warning(f"Redis unavailable, token not revoked: {e}")


def is_token_revoked(token: str) -> bool:
    """
    Verifica si el token fue revocado.

    Crea una conexión nueva por llamada (seguro para multi-worker).
    Si Redis no está disponible, retorna False (fail-open) para no bloquear requests válidos.

    Args:
        token: JWT token a verificar

    Returns:
        bool: True si fue revocado, False si no
    """
    try:
        r = redis.Redis.from_url(
            settings.REDIS_URL,
            socket_timeout=5,
            decode_responses=True,
        )
        result = r.exists(f"revoked_token:{token[:32]}") > 0
        r.close()
        return result
    except (redis.ConnectionError, redis.TimeoutError) as e:
        logger.warning(f"Redis unavailable, cannot check token revocation: {e}")
        return False  # Fail-open: allow request if Redis is down


def create_jwt_token(
    user_id: UUID,
    telegram_id: int | None = None,
    expires_delta: timedelta | None = None,
    token_type: str = "access",
) -> str:
    """
    Crea JWT token para usuario.

    Args:
        user_id: UUID del usuario
        telegram_id: ID de Telegram del usuario (optional for email auth)
        expires_delta: Tiempo de expiración opcional
        token_type: Tipo de token (access o refresh)

    Returns:
        str: JWT token encoded
    """
    now = datetime.now(UTC)
    expire = now + (expires_delta or timedelta(hours=settings.JWT_EXPIRATION_HOURS))

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": now,
        "type": token_type,
    }

    if telegram_id is not None:
        payload["telegram_id"] = telegram_id

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_token_pair(user_id: UUID, telegram_id: int | None = None) -> tuple[str, str]:
    """
    Crea access token + refresh token para usuario.

    Args:
        user_id: UUID del usuario
        telegram_id: ID de Telegram del usuario (optional)

    Returns:
        tuple[str, str]: (access_token, refresh_token)
    """
    access_token = create_jwt_token(
        user_id=user_id,
        telegram_id=telegram_id,
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
    )
    refresh_token = create_jwt_token(
        user_id=user_id,
        telegram_id=telegram_id,
        expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
    )
    return access_token, refresh_token


def decode_jwt_token(token: str) -> dict:
    """
    Decodifica y valida JWT token.

    Args:
        token: JWT token a decodificar

    Returns:
        dict: Payload del token

    Raises:
        ValueError: Si el token es inválido o expiró
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired") from None
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token") from None


def verify_jwt_token(token: str) -> bool:
    """
    Verifica si un token es válido sin decodificarlo.

    Args:
        token: JWT token a verificar

    Returns:
        bool: True si es válido, False si no
    """
    try:
        decode_jwt_token(token)
        return True
    except ValueError:
        return False
