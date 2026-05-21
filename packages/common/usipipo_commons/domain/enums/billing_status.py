from enum import Enum


class BillingStatus(str, Enum):
    """Estados posibles de un ciclo de facturación por consumo."""

    ACTIVE = "active"  # Ciclo en curso, consumiendo
    CLOSED = "closed"  # Ciclo cerrado, esperando pago
    PAID = "paid"  # Ciclo pagado, completado
    CANCELLED = "cancelled"  # Ciclo cancelado
