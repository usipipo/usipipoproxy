"""Repositorio de wallets con SQLAlchemy."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from usipipo_commons.domain.entities.wallet import Wallet
from usipipo_commons.domain.enums.wallet_status import WalletStatus
from usipipo_commons.domain.interfaces.i_wallet_repository import IWalletRepository

from src.infrastructure.persistence.models.wallet_model import WalletModel


class WalletRepository(IWalletRepository):
    """Implementación de repositorio de wallets con SQLAlchemy."""

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Wallet]:
        """
        Obtiene todas las wallets.

        Returns:
            Lista de todas las wallets
        """
        result = self.session.execute(select(WalletModel))
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    def get_by_id(self, wallet_id: UUID) -> Wallet | None:
        """
        Obtiene wallet por ID.

        Args:
            wallet_id: UUID de la wallet

        Returns:
            Wallet o None si no existe
        """
        result = self.session.execute(select(WalletModel).where(WalletModel.id == wallet_id))
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    def get_by_user_id(self, user_id: UUID) -> Wallet | None:
        """
        Obtiene wallet de un usuario.

        Args:
            user_id: UUID del usuario

        Returns:
            Wallet o None si no existe
        """
        result = self.session.execute(
            select(WalletModel).where(WalletModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    def get_by_address(self, address: str) -> Wallet | None:
        """
        Obtiene wallet por dirección.

        Args:
            address: Dirección de la wallet

        Returns:
            Wallet o None si no existe
        """
        result = self.session.execute(
            select(WalletModel).where(WalletModel.address == address)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    def get_active_wallets(self) -> list[Wallet]:
        """
        Obtiene todas las wallets activas.

        Returns:
            Lista de wallets activas
        """
        result = self.session.execute(
            select(WalletModel).where(WalletModel.status == WalletStatus.ACTIVE.value)
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    def create(self, wallet: Wallet) -> Wallet:
        """
        Crea una nueva wallet.

        Args:
            wallet: Entidad de wallet

        Returns:
            Wallet creada
        """
        model = WalletModel.from_entity(wallet)
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        return model.to_entity()

    def update(self, wallet: Wallet) -> Wallet:
        """
        Actualiza wallet existente.

        Args:
            wallet: Entidad de wallet actualizada

        Returns:
            Wallet actualizada
        """
        model = self.session.get(WalletModel, wallet.id)
        if not model:
            raise ValueError(f"Wallet {wallet.id} not found")

        model.address = wallet.address
        model.label = wallet.label
        model.status = wallet.status.value
        model.balance_usdt = wallet.balance_usdt
        model.last_used_at = wallet.last_used_at
        model.total_received_usdt = wallet.total_received_usdt
        model.transaction_count = wallet.transaction_count

        self.session.flush()
        self.session.refresh(model)
        return model.to_entity()

    def delete(self, wallet_id: UUID) -> bool:
        """
        Elimina wallet.

        Args:
            wallet_id: UUID de la wallet

        Returns:
            True si se eliminó, False si no existía
        """
        model = self.session.get(WalletModel, wallet_id)
        if not model:
            return False

        self.session.delete(model)
        self.session.flush()
        return True

    def get_reusable_wallet_for_user(self, user_id: UUID) -> str | None:
        """
        Obtiene dirección de wallet reutilizable de un usuario.

        Busca wallets de órdenes expiradas que puedan ser reutilizadas.

        Args:
            user_id: UUID del usuario

        Returns:
            Dirección de wallet o None
        """
        # Buscar en crypto_orders una orden expirada del usuario con wallet_address
        from usipipo_commons.domain.enums.crypto_order_status import CryptoOrderStatus

        from src.infrastructure.persistence.models.crypto_order_model import CryptoOrderModel

        result = self.session.execute(
            select(CryptoOrderModel)
            .where(CryptoOrderModel.user_id == user_id)
            .where(CryptoOrderModel.status == CryptoOrderStatus.EXPIRED.value)
            .where(CryptoOrderModel.wallet_address.isnot(None))
            .limit(1)
        )
        order = result.scalar_one_or_none()

        if order and order.wallet_address:
            # Verificar que la wallet no esté en uso
            wallet_model = self.session.get(WalletModel, order.wallet_address)
            if not wallet_model or wallet_model.status == WalletStatus.INACTIVE.value:
                return order.wallet_address

        return None

    def get_any_reusable_wallet(self) -> str | None:
        """
        Obtiene cualquier wallet reutilizable disponible.

        Busca wallets expiradas no en uso que puedan ser reasignadas.

        Args:
            user_id: UUID del usuario

        Returns:
            Dirección de wallet o None
        """
        from usipipo_commons.domain.enums.crypto_order_status import CryptoOrderStatus

        from src.infrastructure.persistence.models.crypto_order_model import CryptoOrderModel

        result = self.session.execute(
            select(CryptoOrderModel)
            .where(CryptoOrderModel.status == CryptoOrderStatus.EXPIRED.value)
            .where(CryptoOrderModel.wallet_address.isnot(None))
            .limit(1)
        )
        order = result.scalar_one_or_none()

        if order and order.wallet_address:
            # Verificar que la wallet no esté en uso
            wallet_model = self.session.get(WalletModel, order.wallet_address)
            if not wallet_model or wallet_model.status == WalletStatus.INACTIVE.value:
                return order.wallet_address

        return None
