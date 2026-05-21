from enum import Enum


class CryptoOrderStatus(str, Enum):
    """Estados de una orden crypto."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
