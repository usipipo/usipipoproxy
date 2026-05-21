"""Crypto transaction entity."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from usipipo_commons.domain.enums.crypto_transaction_status import CryptoTransactionStatus


@dataclass
class CryptoTransaction:
    """
    Entidad de transacción de criptomoneda.

    Representa una transacción detectada en la blockchain.
    """

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    user_id: Optional[uuid.UUID] = None
    wallet_address: str = ""
    amount: float = 0.0
    token_symbol: str = "USDT"
    tx_hash: str = ""
    status: CryptoTransactionStatus = CryptoTransactionStatus.PENDING
    confirmations: int = 0
    confirmed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    raw_payload: dict = field(default_factory=dict)

    @property
    def is_confirmed(self) -> bool:
        """Verifica si la transacción está confirmada."""
        return self.status == CryptoTransactionStatus.CONFIRMED

    @property
    def is_pending(self) -> bool:
        """Verifica si la transacción está pendiente."""
        return self.status == CryptoTransactionStatus.PENDING

    def confirm(self) -> None:
        """Marca la transacción como confirmada."""
        self.status = CryptoTransactionStatus.CONFIRMED
        self.confirmed_at = datetime.now(timezone.utc)

    def fail(self) -> None:
        """Marca la transacción como fallida."""
        self.status = CryptoTransactionStatus.FAILED

    @classmethod
    def create(
        cls,
        wallet_address: str,
        amount: float,
        tx_hash: str,
        token_symbol: str = "USDT",
        raw_payload: Optional[dict] = None,
    ) -> "CryptoTransaction":
        """Factory method para crear una transacción."""
        return cls(
            wallet_address=wallet_address,
            amount=amount,
            tx_hash=tx_hash,
            token_symbol=token_symbol,
            raw_payload=raw_payload or {},
        )


@dataclass
class WebhookToken:
    """
    Token para validar webhooks.

    Se usa para verificar que los webhooks vienen de fuentes confiables.
    """

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    token_hash: str = ""
    purpose: str = "tron_dealer"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    used_at: Optional[datetime] = None
    extra_data: dict = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        """Verifica si el token expiró."""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_used(self) -> bool:
        """Verifica si el token ya fue usado."""
        return self.used_at is not None

    def mark_used(self) -> None:
        """Marca el token como usado."""
        self.used_at = datetime.now(timezone.utc)

    @classmethod
    def create(cls, token_hash: str, purpose: str = "tron_dealer") -> "WebhookToken":
        """Factory method para crear un token."""
        return cls(token_hash=token_hash, purpose=purpose)
