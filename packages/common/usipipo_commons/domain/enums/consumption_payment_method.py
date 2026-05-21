from enum import Enum


class ConsumptionPaymentMethod(str, Enum):
    """Métodos de pago para facturas de consumo."""

    STARS = "stars"  # Pago con Telegram Stars
    CRYPTO = "crypto"  # Pago con USDT (BSC)
