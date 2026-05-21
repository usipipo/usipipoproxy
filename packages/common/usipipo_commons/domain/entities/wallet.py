"""Wallet and WalletPool domain entities."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from ..enums.wallet_status import WalletStatus


@dataclass
class Wallet:
    """
    Entidad de wallet BSC para gestión de pagos crypto.

    Representa una wallet BSC asignada a un usuario para recibir
    pagos mediante TronDealer API.
    """
    id: UUID
    user_id: UUID
    address: str
    label: Optional[str]
    status: WalletStatus
    balance_usdt: float
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None
    total_received_usdt: float = 0.0
    transaction_count: int = 0

    @classmethod
    def create(
        cls,
        user_id: UUID,
        address: str,
        label: Optional[str] = None,
    ) -> "Wallet":
        """Crea una nueva wallet para un usuario."""
        now = datetime.now(timezone.utc)  # ← Fixed: was datetime.utcnow()
        return cls(
            id=uuid4(),
            user_id=user_id,
            address=address,
            label=label,
            status=WalletStatus.ACTIVE,
            balance_usdt=0.0,
            created_at=now,
            updated_at=now,
            last_used_at=None,
            total_received_usdt=0.0,
            transaction_count=0,
        )

    def update_balance(self, amount_usdt: float) -> None:
        """Actualiza el balance de la wallet."""
        self.balance_usdt += amount_usdt
        self.total_received_usdt += amount_usdt
        self.transaction_count += 1
        self.updated_at = datetime.now(timezone.utc)  # ← Fixed
        self.last_used_at = datetime.now(timezone.utc)  # ← Fixed

    def deactivate(self) -> None:
        """Desactiva la wallet."""
        self.status = WalletStatus.INACTIVE
        self.updated_at = datetime.now(timezone.utc)  # ← Fixed

    def activate(self) -> None:
        """Activa la wallet."""
        self.status = WalletStatus.ACTIVE
        self.updated_at = datetime.now(timezone.utc)  # ← Fixed

    def to_dict(self) -> dict:
        """Convierte a diccionario para serialización."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "address": self.address,
            "label": self.label,
            "status": self.status.value,
            "balance_usdt": self.balance_usdt,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "total_received_usdt": self.total_received_usdt,
            "transaction_count": self.transaction_count,
        }


@dataclass
class WalletPool:
    """
    Entidad de pool de wallets reutilizables.

    Gestiona un pool de wallets expiradas que pueden ser
    reasignadas a nuevos usuarios para evitar crear wallets innecesarias.
    """
    id: UUID
    wallet_address: str
    original_user_id: UUID
    status: WalletStatus
    created_at: datetime
    released_at: datetime
    expires_at: datetime
    reused_by_user_id: Optional[UUID] = None
    reused_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None  # ← Added: field was missing

    @classmethod
    def create(
        cls,
        wallet_address: str,
        original_user_id: UUID,
        expires_at: datetime,
    ) -> "WalletPool":
        """Crea una nueva entrada de pool para una wallet expirada."""
        now = datetime.now(timezone.utc)  # ← Fixed: was datetime.utcnow()
        return cls(
            id=uuid4(),
            wallet_address=wallet_address,
            original_user_id=original_user_id,
            status=WalletStatus.AVAILABLE,
            created_at=now,
            released_at=now,
            expires_at=expires_at,
            reused_by_user_id=None,
            reused_at=None,
        )

    def mark_reused(self, user_id: UUID) -> None:
        """Marca la wallet como reutilizada por un usuario."""
        self.status = WalletStatus.IN_USE
        self.reused_by_user_id = user_id
        self.reused_at = datetime.now(timezone.utc)  # ← Fixed

    def mark_available(self) -> None:
        """Marca la wallet como disponible en el pool."""
        self.status = WalletStatus.AVAILABLE
        self.reused_by_user_id = None
        self.reused_at = None
        self.updated_at = datetime.now(timezone.utc)  # ← Fixed: now field exists

    def is_expired(self) -> bool:
        """Verifica si la wallet está expirada."""
        return datetime.now(timezone.utc) > self.expires_at  # ← Fixed

    def is_available(self) -> bool:
        """Verifica si la wallet está disponible para reuso."""
        return self.status == WalletStatus.AVAILABLE and not self.is_expired()

    def to_dict(self) -> dict:
        """Convierte a diccionario para serialización."""
        return {
            "id": str(self.id),
            "wallet_address": self.wallet_address,
            "original_user_id": str(self.original_user_id),
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "released_at": self.released_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "reused_by_user_id": str(self.reused_by_user_id) if self.reused_by_user_id else None,
            "reused_at": self.reused_at.isoformat() if self.reused_at else None,
        }
