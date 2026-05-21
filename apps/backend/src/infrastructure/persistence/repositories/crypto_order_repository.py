"""Implementación de CryptoOrderRepository con SQLAlchemy."""

from datetime import UTC
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session
from usipipo_commons.domain.entities.crypto_order import CryptoOrder
from usipipo_commons.domain.enums.crypto_order_status import CryptoOrderStatus

from src.core.domain.interfaces.i_crypto_order_repository import ICryptoOrderRepository
from src.infrastructure.persistence.database import get_execute_rowcount
from src.infrastructure.persistence.models.crypto_order_model import CryptoOrderModel


class CryptoOrderRepository(ICryptoOrderRepository):
    """Implementación de repositorio de crypto orders con SQLAlchemy."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, order: CryptoOrder) -> CryptoOrder:
        """Guarda una crypto order."""
        model = CryptoOrderModel.from_entity(order)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model.to_entity()

    def get_by_id(self, order_id: UUID) -> CryptoOrder | None:
        """Obtiene una orden por ID."""
        result = self.session.execute(
            select(CryptoOrderModel).where(CryptoOrderModel.id == order_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    def get_by_wallet(self, wallet_address: str) -> CryptoOrder | None:
        """Obtiene una orden por dirección de wallet."""
        result = self.session.execute(
            select(CryptoOrderModel)
            .where(CryptoOrderModel.wallet_address == wallet_address)
            .where(CryptoOrderModel.status == CryptoOrderStatus.PENDING)
            .order_by(CryptoOrderModel.created_at.desc())
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    def get_by_user_id(self, user_id: UUID, limit: int = 50) -> list[CryptoOrder]:
        """Obtiene órdenes de un usuario."""
        result = self.session.execute(
            select(CryptoOrderModel)
            .where(CryptoOrderModel.user_id == user_id)
            .order_by(CryptoOrderModel.created_at.desc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    def mark_completed(self, order_id: UUID, tx_hash: str) -> bool:
        """Marca una orden como completada."""
        from datetime import datetime

        result = self.session.execute(
            update(CryptoOrderModel)
            .where(CryptoOrderModel.id == order_id)
            .values(
                status=CryptoOrderStatus.COMPLETED,
                tx_hash=tx_hash,
                confirmed_at=datetime.now(UTC),
            )
        )
        self.session.commit()
        rowcount = get_execute_rowcount(result)
        return rowcount > 0

    def mark_failed(self, order_id: UUID) -> bool:
        """Marca una orden como fallida."""
        result = self.session.execute(
            update(CryptoOrderModel)
            .where(CryptoOrderModel.id == order_id)
            .values(status=CryptoOrderStatus.FAILED)
        )
        self.session.commit()
        rowcount = get_execute_rowcount(result)
        return rowcount > 0

    def mark_expired(self, order_id: UUID) -> bool:
        """Marca una orden como expirada."""
        result = self.session.execute(
            update(CryptoOrderModel)
            .where(CryptoOrderModel.id == order_id)
            .values(status=CryptoOrderStatus.EXPIRED)
        )
        self.session.commit()
        rowcount = get_execute_rowcount(result)
        return rowcount > 0

    def cleanup_expired(self) -> int:
        """Limpia órdenes expiradas."""
        from datetime import datetime

        result = self.session.execute(
            update(CryptoOrderModel)
            .where(CryptoOrderModel.status == CryptoOrderStatus.PENDING)
            .where(CryptoOrderModel.expires_at < datetime.now(UTC))
            .values(status=CryptoOrderStatus.EXPIRED)
        )
        self.session.commit()
        return get_execute_rowcount(result)
