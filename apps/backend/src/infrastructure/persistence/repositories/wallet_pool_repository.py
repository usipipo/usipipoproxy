"""Repositorio de pool de wallets con SQLAlchemy."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from usipipo_commons.domain.entities.wallet import WalletPool
from usipipo_commons.domain.enums.wallet_status import WalletStatus
from usipipo_commons.domain.interfaces.i_wallet_pool_repository import IWalletPoolRepository

from src.infrastructure.persistence.database import get_execute_rowcount
from src.infrastructure.persistence.models.wallet_pool_model import WalletPoolModel


class WalletPoolRepository(IWalletPoolRepository):
    """Implementación de repositorio de pool de wallets con SQLAlchemy."""

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[WalletPool]:
        """
        Obtiene todas las entradas del pool.

        Returns:
            Lista de todas las entradas del pool
        """
        result = self.session.execute(select(WalletPoolModel))
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    def get_by_id(self, pool_id: UUID) -> WalletPool | None:
        """
        Obtiene entrada del pool por ID.

        Args:
            pool_id: UUID de la entrada

        Returns:
            WalletPool o None si no existe
        """
        result = self.session.execute(
            select(WalletPoolModel).where(WalletPoolModel.id == pool_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    def get_by_address(self, wallet_address: str) -> WalletPool | None:
        """
        Obtiene entrada del pool por dirección de wallet.

        Args:
            wallet_address: Dirección de la wallet

        Returns:
            WalletPool o None si no existe
        """
        result = self.session.execute(
            select(WalletPoolModel).where(WalletPoolModel.wallet_address == wallet_address)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    def get_available_wallets(self) -> list[WalletPool]:
        """
        Obtiene todas las wallets disponibles en el pool.

        Returns:
            Lista de wallets disponibles
        """

        result = self.session.execute(
            select(WalletPoolModel)
            .where(WalletPoolModel.status == WalletStatus.AVAILABLE.value)
            .where(WalletPoolModel.expires_at > datetime.now(UTC))
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    def get_expired_wallets(self) -> list[WalletPool]:
        """
        Obtiene todas las wallets expiradas del pool.

        Returns:
            Lista de wallets expiradas
        """

        result = self.session.execute(
            select(WalletPoolModel).where(WalletPoolModel.expires_at < datetime.now(UTC))
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    def create(self, pool_entry: WalletPool) -> WalletPool:
        """
        Crea una nueva entrada en el pool.

        Args:
            pool_entry: Entidad de WalletPool

        Returns:
            WalletPool creada
        """
        model = WalletPoolModel.from_entity(pool_entry)
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        return model.to_entity()

    def update(self, pool_entry: WalletPool) -> WalletPool:
        """
        Actualiza entrada del pool existente.

        Args:
            pool_entry: Entidad de WalletPool actualizada

        Returns:
            WalletPool actualizada
        """
        model = self.session.get(WalletPoolModel, pool_entry.id)
        if not model:
            raise ValueError(f"WalletPool {pool_entry.id} not found")

        model.status = pool_entry.status.value
        model.reused_by_user_id = pool_entry.reused_by_user_id
        model.reused_at = pool_entry.reused_at

        self.session.flush()
        self.session.refresh(model)
        return model.to_entity()

    def delete(self, pool_id: UUID) -> bool:
        """
        Elimina entrada del pool.

        Args:
            pool_id: UUID de la entrada

        Returns:
            True si se eliminó, False si no existía
        """
        model = self.session.get(WalletPoolModel, pool_id)
        if not model:
            return False

        self.session.delete(model)
        self.session.flush()
        return True

    def get_reusable_for_user(self, user_id: UUID) -> WalletPool | None:
        """
        Obtiene wallet reutilizable de un usuario específico.

        Busca wallets expiradas que pertenecieron al usuario.

        Args:
            user_id: UUID del usuario

        Returns:
            WalletPool o None
        """

        result = self.session.execute(
            select(WalletPoolModel)
            .where(WalletPoolModel.original_user_id == user_id)
            .where(WalletPoolModel.status == WalletStatus.AVAILABLE.value)
            .where(WalletPoolModel.expires_at > datetime.now(UTC))
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    def get_any_available(self) -> WalletPool | None:
        """
        Obtiene cualquier wallet disponible en el pool.

        Busca cualquier wallet expirada no en uso.

        Returns:
            WalletPool o None
        """

        result = self.session.execute(
            select(WalletPoolModel)
            .where(WalletPoolModel.status == WalletStatus.AVAILABLE.value)
            .where(WalletPoolModel.expires_at > datetime.now(UTC))
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    def cleanup_expired(self) -> int:
        """
        Limpia wallets expiradas del pool.

        Retorna la cantidad de entradas eliminadas.

        Returns:
            Cantidad de entradas eliminadas
        """

        result = self.session.execute(
            delete(WalletPoolModel).where(WalletPoolModel.expires_at < datetime.now(UTC))
        )
        self.session.flush()
        return get_execute_rowcount(result)
