from enum import Enum


class KeyStatus(str, Enum):
    """Estados de una clave VPN."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"
