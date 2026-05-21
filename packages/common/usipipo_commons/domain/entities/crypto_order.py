from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from ..enums.crypto_order_status import CryptoOrderStatus


@dataclass
class CryptoOrder:
    """Entidad de orden crypto."""
    id: UUID
    user_id: UUID
    package_type: str
    amount_usdt: float
    wallet_address: str
    tron_dealer_order_id: Optional[str]
    status: CryptoOrderStatus
    created_at: datetime
    expires_at: datetime
    tx_hash: Optional[str]
    confirmed_at: Optional[datetime]

    @classmethod
    def create(
        cls,
        user_id: UUID,
        package_type: str,
        amount_usdt: float,
        wallet_address: str,
    ) -> "CryptoOrder":
        """Crea una nueva orden crypto."""
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            user_id=user_id,
            package_type=package_type,
            amount_usdt=amount_usdt,
            wallet_address=wallet_address,
            tron_dealer_order_id=None,
            status=CryptoOrderStatus.PENDING,
            created_at=now,
            expires_at=now,
            tx_hash=None,
            confirmed_at=None,
        )

    def to_dict(self) -> dict:
        """Convierte a diccionario para serialización."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "package_type": self.package_type,
            "amount_usdt": self.amount_usdt,
            "wallet_address": self.wallet_address,
            "tron_dealer_order_id": self.tron_dealer_order_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "tx_hash": self.tx_hash,
            "confirmed_at": self.confirmed_at.isoformat() if self.confirmed_at else None,
        }
