"""Validadores compartidos."""
import re
from typing import Optional


# VPN key name validation constants
VPN_KEY_NAME_MIN_LENGTH = 3
VPN_KEY_NAME_MAX_LENGTH = 50
VPN_KEY_NAME_PATTERN = r'^[a-zA-Z0-9\s\-_]{3,50}$'


def validate_telegram_id(telegram_id: int) -> bool:
    """Valida que el Telegram ID sea válido."""
    return telegram_id > 0 and telegram_id < 2**63


def validate_referral_code(code: Optional[str]) -> bool:
    """Valida formato de código de referido."""
    if not code:
        return True  # Optional, puede ser None

    # Alfanumérico, 4-16 caracteres
    pattern = r'^[a-zA-Z0-9]{4,16}$'
    return bool(re.match(pattern, code))


def validate_vpn_key_name(name: str) -> bool:
    """
    Valida nombre de clave VPN con reglas estrictas.

    Reglas:
    - Longitud: 3-50 caracteres
    - Permitidos: alfanuméricos (a-zA-Z0-9), espacios, guiones (-), guiones bajos (_)
    - Bloqueados: Emoji, unicode confusables, caracteres especiales de shell

    Args:
        name: Nombre a validar

    Returns:
        True si es válido, False en caso contrario
    """
    if not name:
        return False

    # Check length
    if len(name) < VPN_KEY_NAME_MIN_LENGTH or len(name) > VPN_KEY_NAME_MAX_LENGTH:
        return False

    # Check pattern (strict alphanumeric + spaces, hyphens, underscores only)
    pattern = re.compile(VPN_KEY_NAME_PATTERN)
    return bool(pattern.match(name))
