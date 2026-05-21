from enum import Enum


class PaymentMethod(str, Enum):
    """Métodos de pago soportados."""
    TELEGRAM_STARS = "telegram_stars"
    CRYPTO_USDT = "crypto_usdt"
    CRYPTO_BSC = "crypto_bsc"
