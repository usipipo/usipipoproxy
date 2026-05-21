from enum import Enum


class InvoiceStatus(str, Enum):
    """Estados posibles de una factura de consumo."""

    PENDING = "pending"  # Factura generada, esperando pago
    PAID = "paid"  # Factura pagada exitosamente
    EXPIRED = "expired"  # Factura vencida
    CANCELLED = "cancelled"  # Factura cancelada manualmente
