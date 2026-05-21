"""Crypto transaction status enum."""

from enum import Enum


class CryptoTransactionStatus(str, Enum):
    """Estado de una transacción de criptomoneda."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
