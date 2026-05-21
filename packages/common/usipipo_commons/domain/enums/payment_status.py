from enum import Enum


class PaymentStatus(str, Enum):
    """Estados de un pago."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
