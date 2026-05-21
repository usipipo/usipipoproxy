"""Interfaces de repositorio para gestión de wallets."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from usipipo_commons.domain.entities.wallet import Wallet


class IWalletRepository(ABC):
    """Contrato para repositorio de wallets."""

    @abstractmethod
    async def get_all(self) -> List[Wallet]:
        """Obtiene todas las wallets."""
        pass

    @abstractmethod
    async def get_by_id(self, wallet_id: UUID) -> Optional[Wallet]:
        """Obtiene wallet por ID."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Optional[Wallet]:
        """Obtiene wallet de un usuario."""
        pass

    @abstractmethod
    async def get_by_address(self, address: str) -> Optional[Wallet]:
        """Obtiene wallet por dirección."""
        pass

    @abstractmethod
    async def get_active_wallets(self) -> List[Wallet]:
        """Obtiene todas las wallets activas."""
        pass

    @abstractmethod
    async def create(self, wallet: Wallet) -> Wallet:
        """Crea una nueva wallet."""
        pass

    @abstractmethod
    async def update(self, wallet: Wallet) -> Wallet:
        """Actualiza wallet existente."""
        pass

    @abstractmethod
    async def delete(self, wallet_id: UUID) -> bool:
        """Elimina wallet."""
        pass

    @abstractmethod
    async def get_reusable_wallet_for_user(self, user_id: UUID) -> Optional[str]:
        """
        Obtiene dirección de wallet reutilizable de un usuario.
        
        Busca wallets de órdenes expiradas que puedan ser reutilizadas.
        """
        pass

    @abstractmethod
    async def get_any_reusable_wallet(self) -> Optional[str]:
        """
        Obtiene cualquier wallet reutilizable disponible.
        
        Busca wallets expiradas no en uso que puedan ser reasignadas.
        """
        pass
